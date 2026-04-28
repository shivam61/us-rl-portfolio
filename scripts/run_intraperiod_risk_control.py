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


def run_baseline(base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask):
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
    history, _, diagnostics = engine.run(
        use_optimizer=True,
        use_risk_engine=True,
        top_n_equal_weight=None,
        alpha_score_provider=build_alpha_score_provider(score_frame, "alpha_score"),
    )
    return history.sort_index(), diagnostics


def build_intraperiod_signals(prices_dict: dict, history_index: pd.Index) -> pd.DataFrame:
    spy = prices_dict["adj_close"]["SPY"].ffill().reindex(history_index).ffill()
    vix_col = next((c for c in prices_dict["adj_close"].columns if "VIX" in c.upper()), None)
    vix = prices_dict["adj_close"][vix_col].ffill().reindex(history_index).ffill() if vix_col else pd.Series(20.0, index=history_index)
    signals = pd.DataFrame(index=history_index)
    signals["spy_5d_ret"] = spy.pct_change(5)
    signals["vix_3d_change"] = vix.pct_change(3)
    signals["hedge_active"] = (signals["spy_5d_ret"] < -0.06) | (signals["vix_3d_change"] > 0.40)
    return signals.fillna({"hedge_active": False})


def drawdown_depth(nav: pd.Series, start: pd.Timestamp, trough: pd.Timestamp) -> float:
    window = nav.loc[(nav.index >= start) & (nav.index <= trough)]
    if window.empty:
        return np.nan
    base = nav.loc[:start].iloc[-1] if not nav.loc[:start].empty else window.iloc[0]
    return float(window.min() / base - 1.0)


def entry_smoothing_multiplier(history: pd.DataFrame) -> pd.Series:
    multiplier = pd.Series(1.0, index=history.index)
    rebalance_dates = history.index[history["turnover"] > 0]
    for date in rebalance_dates:
        loc = history.index.get_loc(date)
        schedule = [0.70, 0.80, 0.90, 1.00]
        for offset, value in enumerate(schedule):
            idx = loc + offset
            if idx < len(multiplier):
                multiplier.iloc[idx] = min(multiplier.iloc[idx], value)
    return multiplier


def apply_overlay(
    history: pd.DataFrame,
    signals: pd.DataFrame,
    use_intraperiod_overlay: bool,
    use_drawdown_brake: bool,
    use_entry_smoothing: bool = False,
) -> tuple[pd.Series, pd.DataFrame]:
    base_returns = history["nav"].pct_change().fillna(0.0)
    nav = pd.Series(index=history.index, dtype=float)
    nav.iloc[0] = history["nav"].iloc[0]
    state_rows = []
    smoothing = entry_smoothing_multiplier(history) if use_entry_smoothing else pd.Series(1.0, index=history.index)

    for idx, date in enumerate(history.index):
        if idx == 0:
            state_rows.append(
                {
                    "date": date,
                    "exposure_multiplier": 1.0,
                    "hedge_active": False,
                    "drawdown_brake": "none",
                    "drawdown": 0.0,
                }
            )
            continue

        peak = float(nav.iloc[:idx].max())
        prev_nav = float(nav.iloc[idx - 1])
        current_dd = prev_nav / peak - 1.0 if peak > 0 else 0.0

        multiplier = float(smoothing.loc[date])
        brake = "none"
        if use_intraperiod_overlay and bool(signals.loc[date, "hedge_active"]):
            multiplier = min(multiplier, 0.60)
        if use_drawdown_brake:
            if current_dd < -0.15:
                multiplier = min(multiplier, 0.40)
                brake = "dd_lt_15"
            elif current_dd < -0.10:
                multiplier = min(multiplier, 0.60)
                brake = "dd_lt_10"

        nav.iloc[idx] = prev_nav * (1.0 + base_returns.iloc[idx] * multiplier)
        state_rows.append(
            {
                "date": date,
                "exposure_multiplier": multiplier,
                "hedge_active": bool(use_intraperiod_overlay and signals.loc[date, "hedge_active"]),
                "drawdown_brake": brake,
                "drawdown": current_dd,
            }
        )

    state = pd.DataFrame(state_rows).set_index("date")
    return nav, state


def hedge_activation_lag(signals: pd.DataFrame, start: pd.Timestamp) -> int | None:
    active = signals.loc[signals.index >= start]
    active = active[active["hedge_active"]]
    if active.empty:
        return None
    return int((active.index[0] - start).days)


def render_report(results: pd.DataFrame, activation: dict[str, int | None], note: str) -> str:
    criteria = results[
        [
            "variant",
            "maxdd_lt_32pct",
            "cagr_gt_16pct",
            "sharpe_ge_0_9",
            "dd_2020_reduces",
            "all_pass",
        ]
    ]
    best = results.sort_values("max_dd", ascending=False).iloc[0]
    lines = [
        "# Intraperiod Risk Control",
        "",
        "- Baseline: `baseline_v1_volatility_score_sp100`",
        "- Alpha rankings unchanged",
        "- Optimizer unchanged",
        "- No regime switching",
        "- RL disabled",
        f"- Implementation note: {note}",
        "- `entry_smoothing` is reported separately because it is a capital-deployment control, not a hedge trigger.",
        "",
        "## Backtest Comparison",
        "",
        results[
            [
                "variant",
                "cagr",
                "sharpe",
                "max_dd",
                "dd_2020",
                "dd_2022",
                "avg_hedge_usage",
                "avg_exposure_multiplier",
            ]
        ].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Hedge Timing",
        "",
        f"- First hedge activation lag vs 2020 crash start: `{activation['2020']}` days",
        f"- First hedge activation lag vs 2022 drawdown start: `{activation['2022']}` days",
        "",
        "## Success Criteria",
        "",
        criteria.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        f"- Best MaxDD variant: `{best['variant']}` at `{best['max_dd']:.2%}`.",
    ]
    if bool(results["all_pass"].any()):
        lines.append("- At least one intraperiod overlay passes the full gate.")
    else:
        lines.append("- No intraperiod overlay passes the full gate in this run.")
    lines.append("- This is an overlay test on daily realized baseline returns; it does not change portfolio construction.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Intraperiod risk-control overlay experiment")
    parser.add_argument("--config", type=str, default="config/baseline_v1_volatility_score_sp100.yaml")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml")
    args = parser.parse_args()

    base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask = load_inputs(
        args.config, args.universe
    )
    history, _ = run_baseline(base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask)
    signals = build_intraperiod_signals(prices_dict, history.index)
    variants = [
        ("baseline_v1", False, False, False),
        ("intraperiod_overlay", True, False, False),
        ("drawdown_brake", False, True, False),
        ("intraperiod_overlay_plus_drawdown_brake", True, True, False),
        ("entry_smoothing", False, False, True),
        ("all_controls", True, True, True),
    ]

    baseline_nav = history["nav"]
    baseline_2020 = drawdown_depth(baseline_nav, *DD_2020)
    rows = []
    states = {}

    for name, use_overlay, use_brake, use_smoothing in variants:
        if name == "baseline_v1":
            nav = baseline_nav.copy()
            state = pd.DataFrame(
                {
                    "exposure_multiplier": 1.0,
                    "hedge_active": False,
                    "drawdown_brake": "none",
                    "drawdown": nav / nav.cummax() - 1.0,
                },
                index=history.index,
            )
        else:
            nav, state = apply_overlay(history, signals, use_overlay, use_brake, use_smoothing)
        states[name] = state
        metrics = calculate_metrics(nav)
        dd_2020 = drawdown_depth(nav, *DD_2020)
        dd_2022 = drawdown_depth(nav, *DD_2022)
        rows.append(
            {
                "variant": name,
                "cagr": metrics.get("CAGR"),
                "sharpe": metrics.get("Sharpe"),
                "max_dd": metrics.get("Max Drawdown"),
                "dd_2020": dd_2020,
                "dd_2022": dd_2022,
                "avg_hedge_usage": float(state["hedge_active"].mean()),
                "avg_exposure_multiplier": float(state["exposure_multiplier"].mean()),
                "maxdd_lt_32pct": bool(metrics.get("Max Drawdown", -1.0) > -0.32),
                "cagr_gt_16pct": bool(metrics.get("CAGR", 0.0) > 0.16),
                "sharpe_ge_0_9": bool(metrics.get("Sharpe", 0.0) >= 0.9),
                "dd_2020_reduces": bool(dd_2020 > baseline_2020) if name != "baseline_v1" else True,
            }
        )

    results = pd.DataFrame(rows)
    results["all_pass"] = results[
        ["maxdd_lt_32pct", "cagr_gt_16pct", "sharpe_ge_0_9", "dd_2020_reduces"]
    ].all(axis=1)
    activation = {
        "2020": hedge_activation_lag(signals, DD_2020[0]),
        "2022": hedge_activation_lag(signals, DD_2022[0]),
    }
    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    note = (
        "daily return overlay reduces exposure by 40% on SPY/VIX shocks, "
        "applies portfolio drawdown brakes on adjusted NAV, and tests entry smoothing "
        "as 70/80/90/100% exposure over the first four trading days after each rebalance."
    )
    (reports_dir / "intraperiod_risk_control.md").write_text(render_report(results, activation, note))


if __name__ == "__main__":
    main()
