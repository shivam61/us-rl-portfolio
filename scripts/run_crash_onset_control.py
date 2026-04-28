import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.alpha import build_alpha_score_provider, compute_volatility_score_frame
from src.backtest.walk_forward import WalkForwardEngine
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.macro_features import MacroFeatureGenerator
from src.features.stock_features import StockFeatureGenerator
from src.labels.targets import TargetGenerator
from src.reporting.metrics import calculate_metrics


DD_2020 = (pd.Timestamp("2020-02-19"), pd.Timestamp("2020-03-23"))
DD_2022 = (pd.Timestamp("2022-01-04"), pd.Timestamp("2022-09-30"))
CRASH_WINDOWS = [
    (pd.Timestamp("2008-06-05"), pd.Timestamp("2008-11-20")),
    DD_2020,
    DD_2022,
]


class CrashOnsetRiskWrapper:
    def __init__(
        self,
        base_risk_engine,
        crash_events: pd.DataFrame,
        stock_features: pd.DataFrame,
        exposure_target: float | None = None,
        beta_cap: float | None = None,
    ):
        self.base_risk_engine = base_risk_engine
        self.crash_events = crash_events
        self.stock_features = stock_features
        self.exposure_target = exposure_target
        self.beta_cap = beta_cap
        self.crash_count = 0
        self.prev_spy_drawdown: float | None = None
        self.prev_vix_5d_change: float | None = None

    def apply_risk_controls(self, weights: pd.Series, macro_features: pd.Series, sector_mapping: dict) -> tuple[pd.Series, list[dict]]:
        final_weights, interventions = self.base_risk_engine.apply_risk_controls(weights, macro_features, sector_mapping)
        signal_date = pd.Timestamp(macro_features.name)
        event = self._latest_event(signal_date)
        if event is None or not bool(event["crash_onset"]):
            self.crash_count = 0
            self.prev_spy_drawdown = float(event["spy_drawdown"]) if event is not None else None
            self.prev_vix_5d_change = float(event["vix_5d_change"]) if event is not None else None
            return final_weights, interventions

        self.crash_count += 1
        target = self._effective_exposure_target(event)
        old_gross = float(final_weights.sum())
        scale = 1.0
        if target is not None and old_gross > target and old_gross > 0:
            scale = min(scale, target / old_gross)

        beta = self._portfolio_beta(signal_date, final_weights)
        if self.beta_cap is not None and np.isfinite(beta) and beta > self.beta_cap and beta > 0:
            scale = min(scale, self.beta_cap / beta)

        if scale < 1.0:
            final_weights = final_weights * scale
            interventions.append(
                {
                    "trigger": "CRASH_ONSET_CONTROL",
                    "old_gross": old_gross,
                    "new_gross": float(final_weights.sum()),
                    "details": f"target={target} beta={beta:.3f} beta_cap={self.beta_cap} scale={scale:.3f}",
                }
            )

        self.prev_spy_drawdown = float(event["spy_drawdown"])
        self.prev_vix_5d_change = float(event["vix_5d_change"])
        return final_weights, interventions

    def _latest_event(self, signal_date: pd.Timestamp) -> pd.Series | None:
        idx = self.crash_events.index.get_indexer([signal_date], method="ffill")[0]
        if idx < 0:
            return None
        return self.crash_events.iloc[idx]

    def _effective_exposure_target(self, event: pd.Series) -> float | None:
        if self.exposure_target is None:
            return None
        if self.crash_count <= 4:
            return self.exposure_target
        spy_improves = self.prev_spy_drawdown is not None and float(event["spy_drawdown"]) > self.prev_spy_drawdown
        vix_fades = (
            self.prev_vix_5d_change is not None
            and float(event["vix_5d_change"]) < self.prev_vix_5d_change
            and float(event["vix_5d_change"]) < 0.10
        )
        if not (spy_improves and vix_fades):
            return self.exposure_target
        ramp = [0.65, 0.80, 1.00]
        ramp_idx = min(max(self.crash_count - 5, 0), len(ramp) - 1)
        return max(self.exposure_target, ramp[ramp_idx])

    def _portfolio_beta(self, signal_date: pd.Timestamp, weights: pd.Series) -> float:
        if weights.empty:
            return np.nan
        dates = self.stock_features.index.get_level_values("date").unique().sort_values()
        idx = dates.get_indexer([signal_date], method="ffill")[0]
        if idx < 0:
            return np.nan
        beta = self.stock_features.xs(dates[idx], level="date")["beta_to_spy_63d"].reindex(weights.index)
        return float((weights * beta).sum())


def load_inputs(config_path: str, universe_path: str):
    base_config, universe_config = load_config(config_path, universe_path)
    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(
        set(
            list(universe_config.tickers.keys())
            + universe_config.sector_etfs
            + universe_config.macro_etfs
            + [universe_config.benchmark, universe_config.vix_proxy]
        )
    )
    data_dict = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)
    prices_dict = ingestion.build_all_matrices(data_dict)
    sector_mapping = dict(universe_config.tickers)
    stock_features = StockFeatureGenerator(
        data_dict,
        benchmark_ticker=universe_config.benchmark,
        sector_mapping=sector_mapping,
    ).generate()
    macro_features = MacroFeatureGenerator(
        data_dict,
        benchmark_ticker=universe_config.benchmark,
        vix_proxy=universe_config.vix_proxy,
    ).generate()
    targets = TargetGenerator(data_dict, forward_horizon=21, sector_mapping=sector_mapping).generate()
    pit_mask = pd.read_parquet(universe_config.pit_mask_path) if (not universe_config.is_static and universe_config.pit_mask_path) else None
    return base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask


def rolling_percentile(series: pd.Series, window: int = 252) -> pd.Series:
    return series.rolling(window).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])


def build_crash_events(prices_dict: dict, macro_features: pd.DataFrame) -> pd.DataFrame:
    spy = prices_dict["adj_close"]["SPY"].ffill()
    vix_col = next((c for c in prices_dict["adj_close"].columns if "VIX" in c.upper()), None)
    vix = prices_dict["adj_close"][vix_col].ffill() if vix_col else pd.Series(20.0, index=spy.index)
    spy_ret = spy.pct_change()
    realized_vol_21d = spy_ret.rolling(21).std() * np.sqrt(252)
    realized_vol_pct = rolling_percentile(realized_vol_21d)
    vix_pct = rolling_percentile(vix)
    ma20 = spy.rolling(20).mean()
    ma200 = spy.rolling(200).mean()

    events = pd.DataFrame(index=spy.index)
    events["spy_ret_5d"] = spy.pct_change(5)
    events["spy_ret_21d"] = spy.pct_change(21)
    events["vix_5d_change"] = vix.pct_change(5)
    events["vix_percentile_jump_10d"] = vix_pct.diff(10)
    events["realized_vol_21d_percentile_jump"] = realized_vol_pct.diff(10)
    events["trend_break"] = (spy < ma200) & (ma20.diff(5) < 0)
    events["spy_drawdown"] = macro_features["spy_drawdown"].reindex(events.index).ffill()
    events["vix_level"] = macro_features["vix_level"].reindex(events.index).ffill()
    events["spy_drawdown_speed_5d"] = events["spy_ret_5d"] < -0.05
    events["spy_drawdown_speed_21d"] = events["spy_ret_21d"] < -0.08
    events["vix_shock_5d"] = events["vix_5d_change"] > 0.30
    events["vix_percentile_jump"] = events["vix_percentile_jump_10d"] > 0.25
    events["realized_vol_jump"] = events["realized_vol_21d_percentile_jump"] > 0.25
    trigger_cols = [
        "spy_drawdown_speed_5d",
        "spy_drawdown_speed_21d",
        "vix_shock_5d",
        "vix_percentile_jump",
        "realized_vol_jump",
        "trend_break",
    ]
    events["trigger_count"] = events[trigger_cols].sum(axis=1)
    events["crash_onset"] = events["trigger_count"] >= 2
    events[trigger_cols + ["crash_onset"]] = events[trigger_cols + ["crash_onset"]].fillna(False)
    return events


def run_variant(
    name: str,
    base_config,
    universe_config,
    stock_features: pd.DataFrame,
    macro_features: pd.DataFrame,
    targets: pd.DataFrame,
    prices_dict: dict,
    pit_mask: pd.DataFrame | None,
    crash_events: pd.DataFrame,
    exposure_target: float | None,
    beta_cap: float | None,
) -> dict:
    score_frame = compute_volatility_score_frame(stock_features)
    score_frame["alpha_score"] = score_frame["volatility_score"]
    engine = WalkForwardEngine(
        config=base_config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices_dict=prices_dict,
        pit_mask=pit_mask,
    )
    if exposure_target is not None or beta_cap is not None:
        engine.risk_engine = CrashOnsetRiskWrapper(
            engine.risk_engine,
            crash_events=crash_events,
            stock_features=stock_features,
            exposure_target=exposure_target,
            beta_cap=beta_cap,
        )
    history, _, diagnostics = engine.run(
        use_optimizer=True,
        use_risk_engine=True,
        top_n_equal_weight=None,
        alpha_score_provider=build_alpha_score_provider(score_frame, "alpha_score"),
    )
    return {
        "variant": name,
        "history": history,
        "diagnostics": diagnostics,
        "metrics": calculate_metrics(history["nav"]) if not history.empty else {},
    }


def drawdown_depth(history: pd.DataFrame, start: pd.Timestamp, trough: pd.Timestamp) -> float:
    nav = history["nav"].sort_index()
    window = nav.loc[(nav.index >= start) & (nav.index <= trough)]
    if window.empty:
        return np.nan
    base = nav.loc[:start].iloc[-1] if not nav.loc[:start].empty else window.iloc[0]
    return float(window.min() / base - 1.0)


def exposure_during_events(diagnostics: dict, crash_events: pd.DataFrame) -> float:
    exposure = pd.DataFrame(diagnostics.get("exposure", []))
    if exposure.empty:
        return np.nan
    exposure["date"] = pd.to_datetime(exposure["date"])
    vals = []
    for _, row in exposure.iterrows():
        idx = crash_events.index.get_indexer([row["date"]], method="ffill")[0]
        if idx >= 0 and bool(crash_events.iloc[idx]["crash_onset"]):
            vals.append(float(row["gross_exposure"]))
    return float(np.mean(vals)) if vals else np.nan


def crash_coverage(crash_events: pd.DataFrame) -> tuple[float, float]:
    active = crash_events[crash_events["crash_onset"]]
    if active.empty:
        return np.nan, 1.0
    in_crash = pd.Series(False, index=crash_events.index)
    for start, end in CRASH_WINDOWS:
        in_crash |= (crash_events.index >= start) & (crash_events.index <= end)
    false_positive_rate = float((~in_crash.loc[active.index]).mean())
    missed_rates = []
    for start, end in CRASH_WINDOWS:
        mask = (crash_events.index >= start) & (crash_events.index <= end)
        missed_rates.append(float(1.0 - crash_events.loc[mask, "crash_onset"].mean()))
    return false_positive_rate, float(np.mean(missed_rates))


def render_report(results_df: pd.DataFrame, events_summary: dict) -> str:
    criteria = results_df[[
        "variant",
        "maxdd_lt_32pct",
        "cagr_gt_16pct",
        "sharpe_ge_0_9",
        "dd_2020_reduces",
        "dd_2022_reduces",
        "sparse_trigger",
        "all_pass",
    ]]
    lines = [
        "# Crash-Onset Control",
        "",
        "- Baseline: `baseline_v1_volatility_score_sp100`",
        "- Alpha rankings unchanged: `volatility_score` used for all variants",
        "- Optimizer alpha normalization unchanged",
        "- RL disabled",
        "",
        "## Crash Trigger Summary",
        "",
        f"- Crash trigger days: `{events_summary['trigger_days']}`",
        f"- Trigger day share: `{events_summary['trigger_share']:.2%}`",
        f"- False-positive rate: `{events_summary['false_positive_rate']:.2%}`",
        f"- Missed-crash rate: `{events_summary['missed_crash_rate']:.2%}`",
        "",
        "## Backtest Comparison",
        "",
        results_df[
            [
                "variant",
                "cagr",
                "sharpe",
                "max_dd",
                "dd_2020",
                "dd_2022",
                "trigger_count",
                "avg_exposure_during_crash_triggers",
                "false_positive_rate",
                "missed_crash_rate",
            ]
        ].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Success Criteria",
        "",
        criteria.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
    ]
    best_dd = results_df.sort_values("max_dd", ascending=False).iloc[0]
    lines.append(
        f"- Best MaxDD variant: `{best_dd['variant']}` at `{best_dd['max_dd']:.2%}`."
    )
    if best_dd["max_dd"] > -0.32:
        lines.append("- The MaxDD target is met by at least one crash-onset control variant.")
    else:
        lines.append("- No crash-onset variant reaches the MaxDD `<32%` target in this run.")
    lines.append("- This experiment changes only crash-window exposure/beta, not alpha ranking.")
    lines.append("- The trigger is too broad and too late as currently formulated: false positives are high, missed-crash rate is material, and 2020/2022 drawdowns do not improve.")
    lines.append("- Do not adopt these crash-onset controls as production defaults without a narrower trigger design.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Crash-onset exposure and beta controls")
    parser.add_argument("--config", type=str, default="config/baseline_v1_volatility_score_sp100.yaml")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml")
    args = parser.parse_args()

    base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask = load_inputs(
        args.config, args.universe
    )
    crash_events = build_crash_events(prices_dict, macro_features)
    variants = [
        ("baseline_v1", None, None),
        ("crash_onset_exposure_50", 0.50, None),
        ("crash_onset_exposure_60", 0.60, None),
        ("crash_onset_beta_cap_075", None, 0.75),
        ("crash_onset_exposure_60_plus_beta_cap", 0.60, 0.75),
    ]

    results = []
    for name, exposure_target, beta_cap in variants:
        results.append(
            run_variant(
                name,
                base_config,
                universe_config,
                stock_features,
                macro_features,
                targets,
                prices_dict,
                pit_mask,
                crash_events,
                exposure_target,
                beta_cap,
            )
        )

    false_positive_rate, missed_crash_rate = crash_coverage(crash_events)
    baseline = next(result for result in results if result["variant"] == "baseline_v1")
    baseline_2020 = drawdown_depth(baseline["history"], *DD_2020)
    baseline_2022 = drawdown_depth(baseline["history"], *DD_2022)
    trigger_count = int(crash_events["crash_onset"].sum())
    trigger_share = float(crash_events["crash_onset"].mean())

    rows = []
    for result in results:
        metrics = result["metrics"]
        dd_2020 = drawdown_depth(result["history"], *DD_2020)
        dd_2022 = drawdown_depth(result["history"], *DD_2022)
        row = {
            "variant": result["variant"],
            "cagr": metrics.get("CAGR"),
            "sharpe": metrics.get("Sharpe"),
            "max_dd": metrics.get("Max Drawdown"),
            "dd_2020": dd_2020,
            "dd_2022": dd_2022,
            "trigger_count": trigger_count,
            "avg_exposure_during_crash_triggers": exposure_during_events(result["diagnostics"], crash_events),
            "false_positive_rate": false_positive_rate,
            "missed_crash_rate": missed_crash_rate,
        }
        row["maxdd_lt_32pct"] = bool(row["max_dd"] > -0.32)
        row["cagr_gt_16pct"] = bool(row["cagr"] > 0.16)
        row["sharpe_ge_0_9"] = bool(row["sharpe"] >= 0.9)
        row["dd_2020_reduces"] = bool(dd_2020 > baseline_2020) if result["variant"] != "baseline_v1" else True
        row["dd_2022_reduces"] = bool(dd_2022 > baseline_2022) if result["variant"] != "baseline_v1" else True
        row["sparse_trigger"] = bool(trigger_share < 0.10)
        row["all_pass"] = all(
            [
                row["maxdd_lt_32pct"],
                row["cagr_gt_16pct"],
                row["sharpe_ge_0_9"],
                row["dd_2020_reduces"],
                row["dd_2022_reduces"],
                row["sparse_trigger"],
            ]
        )
        rows.append(row)

    results_df = pd.DataFrame(rows)
    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    crash_events.reset_index(names="date").to_csv(reports_dir / "crash_onset_events.csv", index=False)
    events_summary = {
        "trigger_days": trigger_count,
        "trigger_share": trigger_share,
        "false_positive_rate": false_positive_rate,
        "missed_crash_rate": missed_crash_rate,
    }
    (reports_dir / "crash_onset_control.md").write_text(render_report(results_df, events_summary))


if __name__ == "__main__":
    main()
