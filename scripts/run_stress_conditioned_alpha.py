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


STRESS_2020 = (pd.Timestamp("2020-02-19"), pd.Timestamp("2020-03-23"))
STRESS_2022 = (pd.Timestamp("2022-01-04"), pd.Timestamp("2022-09-30"))
STRESS_EXPOSURE_SCALE = 0.75


class StressExposureRiskWrapper:
    def __init__(self, base_risk_engine, stress_exposure_scale: float = STRESS_EXPOSURE_SCALE):
        self.base_risk_engine = base_risk_engine
        self.stress_exposure_scale = stress_exposure_scale

    def apply_risk_controls(self, weights: pd.Series, macro_features: pd.Series, sector_mapping: dict) -> tuple[pd.Series, list[dict]]:
        final_weights, interventions = self.base_risk_engine.apply_risk_controls(weights, macro_features, sector_mapping)
        is_stress = (macro_features.get("vix_percentile_1y", 0.0) >= 0.80) or (macro_features.get("spy_drawdown", 0.0) <= -0.10)
        if is_stress:
            old_gross = float(final_weights.sum())
            final_weights = final_weights * self.stress_exposure_scale
            interventions.append(
                {
                    "trigger": "STRESS_EXPOSURE_SCALE",
                    "old_gross": old_gross,
                    "new_gross": float(final_weights.sum()),
                    "details": f"scale={self.stress_exposure_scale:.2f}",
                }
            )
        return final_weights, interventions


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
    targets = TargetGenerator(
        data_dict,
        forward_horizon=21,
        sector_mapping=sector_mapping,
    ).generate()
    pit_mask = pd.read_parquet(universe_config.pit_mask_path) if (not universe_config.is_static and universe_config.pit_mask_path) else None
    return base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask


def build_stress_mask(macro_features: pd.DataFrame) -> pd.Series:
    stress = (macro_features["vix_percentile_1y"] >= 0.80) | (macro_features["spy_drawdown"] <= -0.10)
    return stress.fillna(False)


def apply_stress_conditioning(
    score_frame: pd.DataFrame,
    stress_mask: pd.Series,
    sector_mapping: dict[str, str],
    variant: str,
) -> pd.DataFrame:
    out = score_frame.copy()
    out["alpha_score"] = out["volatility_score"]
    stress_by_row = out.index.get_level_values("date").map(stress_mask).fillna(False)

    if variant == "baseline":
        pass
    elif variant == "sector_neutral_stress":
        tmp = out[["volatility_score"]].copy()
        tmp["_sector"] = tmp.index.get_level_values("ticker").map(sector_mapping)
        sector_mean = tmp.groupby(["date", "_sector"])["volatility_score"].transform("mean")
        sector_std = tmp.groupby(["date", "_sector"])["volatility_score"].transform("std").replace(0.0, np.nan)
        sector_zscore = ((tmp["volatility_score"] - sector_mean) / sector_std).fillna(0.0)
        out.loc[stress_by_row, "alpha_score"] = sector_zscore.loc[stress_by_row]
    elif variant == "stress_cash_exposure":
        pass
    elif variant == "dampened_stress":
        out.loc[stress_by_row, "alpha_score"] = out.loc[stress_by_row, "volatility_score"] * 0.5
    else:
        raise ValueError(f"Unknown variant: {variant}")

    out["alpha_score"] = out["alpha_score"].astype(float)
    out["stress_regime"] = stress_by_row
    return out


def evaluate_conditional_ic(
    conditioned_scores: pd.DataFrame,
    targets: pd.DataFrame,
    rebalance_dates: list[pd.Timestamp],
) -> pd.DataFrame:
    rows = []
    dates = conditioned_scores.index.get_level_values("date").unique().sort_values()
    panel = conditioned_scores[["alpha_score", "stress_regime"]].join(targets[["target_fwd_ret"]], how="left")

    for signal_date in rebalance_dates:
        idx = dates.get_indexer([signal_date], method="ffill")[0]
        if idx < 0:
            continue
        feature_date = dates[idx]
        grp = panel.xs(feature_date, level="date").dropna(subset=["alpha_score", "target_fwd_ret"])
        if len(grp) < 10:
            continue
        stress = bool(grp["stress_regime"].iloc[0])
        ic = grp["alpha_score"].rank().corr(grp["target_fwd_ret"].rank())
        q80 = grp["alpha_score"].quantile(0.8)
        q20 = grp["alpha_score"].quantile(0.2)
        spread = grp.loc[grp["alpha_score"] >= q80, "target_fwd_ret"].mean() - grp.loc[grp["alpha_score"] <= q20, "target_fwd_ret"].mean()
        n = min(20, len(grp))
        pred_top = set(grp["alpha_score"].nlargest(n).index)
        actual_top = set(grp["target_fwd_ret"].nlargest(n).index)
        rows.append(
            {
                "date": feature_date,
                "regime": "stress" if stress else "normal",
                "rank_ic": float(ic),
                "spread": float(spread),
                "precision_at_20": float(len(pred_top & actual_top) / n),
                "n_tickers": int(len(grp)),
            }
        )

    if not rows:
        return pd.DataFrame(columns=["regime", "mean_ic", "ic_sharpe", "spread", "precision_at_20", "n_dates"])

    date_level = pd.DataFrame(rows)
    return (
        date_level.groupby("regime")
        .agg(
            mean_ic=("rank_ic", "mean"),
            ic_sharpe=("rank_ic", lambda x: x.mean() / (x.std(ddof=0) + 1e-9)),
            spread=("spread", "mean"),
            precision_at_20=("precision_at_20", "mean"),
            n_dates=("date", "count"),
        )
        .reset_index()
    )


def run_variant(
    name: str,
    conditioned_scores: pd.DataFrame,
    base_config,
    universe_config,
    stock_features: pd.DataFrame,
    macro_features: pd.DataFrame,
    targets: pd.DataFrame,
    prices_dict: dict,
    pit_mask: pd.DataFrame | None,
) -> dict:
    engine = WalkForwardEngine(
        config=base_config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices_dict=prices_dict,
        pit_mask=pit_mask,
    )
    if name == "stress_cash_exposure":
        engine.risk_engine = StressExposureRiskWrapper(engine.risk_engine)
    history, _, diagnostics = engine.run(
        use_optimizer=True,
        use_risk_engine=True,
        top_n_equal_weight=None,
        alpha_score_provider=build_alpha_score_provider(conditioned_scores, "alpha_score"),
    )
    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    return {
        "variant": name,
        "history": history,
        "diagnostics": diagnostics,
        "metrics": metrics,
    }


def drawdown_depth(history: pd.DataFrame, start: pd.Timestamp, trough: pd.Timestamp) -> float:
    nav = history["nav"].sort_index()
    window = nav.loc[(nav.index >= start) & (nav.index <= trough)]
    if window.empty:
        return np.nan
    base = nav.loc[:start].iloc[-1] if not nav.loc[:start].empty else window.iloc[0]
    return float(window.min() / base - 1.0)


def max_drawdown_period(history: pd.DataFrame) -> float:
    nav = history["nav"].sort_index()
    return float((nav / nav.cummax() - 1.0).min()) if not nav.empty else np.nan


def render_report(backtest_df: pd.DataFrame, ic_df: pd.DataFrame, criteria_df: pd.DataFrame) -> str:
    lines = [
        "# Stress-Conditioned Alpha",
        "",
        "- Baseline: `baseline_v1_volatility_score_sp100`",
        "- Stress rule: `vix_percentile_1y >= 0.8 OR spy_drawdown <= -10%`",
        "- Strategy constraints unchanged: no inversion, no new features, no optimizer changes, RL disabled",
        f"- `stress_cash_exposure` keeps alpha unchanged and scales post-risk gross exposure to `{STRESS_EXPOSURE_SCALE:.0%}` during stress.",
        "- Because the optimizer normalizes alpha per rebalance, scalar dampening before the optimizer does not materially change rankings or allocations.",
        "- If dampening should matter, it must be applied as exposure scaling, risk-aversion increase, or an alpha-confidence weight inside the optimizer objective before normalization.",
        "",
        "## Backtest Comparison",
        "",
        backtest_df.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Conditional IC",
        "",
        ic_df.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Success Criteria",
        "",
        criteria_df.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Interpretation",
        "",
    ]

    sector_row = criteria_df[criteria_df["variant"].eq("sector_neutral_stress")]
    damp_row = criteria_df[criteria_df["variant"].eq("dampened_stress")]
    if not sector_row.empty:
        passed = bool(sector_row["all_pass"].iloc[0])
        lines.append(
            "- `sector_neutral_stress` is the only variant here that actually changes cross-sectional ordering under the current optimizer."
        )
        lines.append(
            f"- `sector_neutral_stress` {'passes' if passed else 'does not pass'} the full gate."
        )
    if not damp_row.empty:
        lines.append(
            "- `dampened_stress` should be interpreted mainly as a control because optimizer alpha normalization removes most uniform scaling effects."
        )
    lines.append(
        "- The broad stress rule does not reproduce the narrower drawdown-window alpha inversion by itself: baseline stress IC is positive in this test, while prior top drawdown windows had negative rebalance IC."
    )
    lines.append(
        "- Sector-neutral stress conditioning lowers stress IC and spread, so this formulation is not supported."
    )
    lines.append(
        "- Stress exposure scaling improves the 2020 and 2022 drawdowns but still misses the MaxDD gate; it is a risk-control lead, not an alpha-conditioning win."
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Stress-conditioned volatility alpha analysis")
    parser.add_argument("--config", type=str, default="config/baseline_v1_volatility_score_sp100.yaml")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml")
    args = parser.parse_args()

    base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask = load_inputs(
        args.config, args.universe
    )
    base_scores = compute_volatility_score_frame(stock_features)
    stress_mask = build_stress_mask(macro_features)

    variants = ["baseline", "sector_neutral_stress", "stress_cash_exposure", "dampened_stress"]
    score_frames = {
        variant: apply_stress_conditioning(base_scores, stress_mask, dict(universe_config.tickers), variant)
        for variant in variants
    }

    rebalance_dates = WalkForwardEngine(
        config=base_config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices_dict=prices_dict,
        pit_mask=pit_mask,
    ).generate_rebalance_dates()

    ic_rows = []
    results = []
    for variant in variants:
        cond_ic = evaluate_conditional_ic(score_frames[variant], targets, rebalance_dates)
        cond_ic.insert(0, "variant", variant)
        ic_rows.append(cond_ic)
        results.append(
            run_variant(
                variant,
                score_frames[variant],
                base_config,
                universe_config,
                stock_features,
                macro_features,
                targets,
                prices_dict,
                pit_mask,
            )
        )

    baseline_stress_ic = (
        pd.concat(ic_rows, ignore_index=True)
        .query("variant == 'baseline' and regime == 'stress'")["mean_ic"]
        .iloc[0]
    )

    backtest_rows = []
    criteria_rows = []
    for result in results:
        metrics = result["metrics"]
        history = result["history"]
        variant = result["variant"]
        dd_2020 = drawdown_depth(history, *STRESS_2020)
        dd_2022 = drawdown_depth(history, *STRESS_2022)
        stress_ic = (
            pd.concat(ic_rows, ignore_index=True)
            .query("variant == @variant and regime == 'stress'")["mean_ic"]
            .iloc[0]
        )
        backtest_rows.append(
            {
                "variant": variant,
                "cagr": metrics.get("CAGR"),
                "sharpe": metrics.get("Sharpe"),
                "max_dd": metrics.get("Max Drawdown"),
                "dd_2020": dd_2020,
                "dd_2022": dd_2022,
                "stress_ic": stress_ic,
            }
        )

    backtest_df = pd.DataFrame(backtest_rows)
    baseline = backtest_df[backtest_df["variant"].eq("baseline")].iloc[0]
    for row in backtest_df.to_dict("records"):
        criteria_rows.append(
            {
                "variant": row["variant"],
                "maxdd_lt_32pct": bool(row["max_dd"] > -0.32),
                "cagr_gt_16pct": bool(row["cagr"] > 0.16),
                "sharpe_ge_0_9": bool(row["sharpe"] >= 0.9),
                "stress_ic_improves": bool(row["stress_ic"] > baseline_stress_ic) if row["variant"] != "baseline" else True,
                "dd_2020_reduces": bool(row["dd_2020"] > baseline["dd_2020"]) if row["variant"] != "baseline" else True,
                "dd_2022_reduces": bool(row["dd_2022"] > baseline["dd_2022"]) if row["variant"] != "baseline" else True,
            }
        )
    criteria_df = pd.DataFrame(criteria_rows)
    criteria_df["all_pass"] = criteria_df.drop(columns=["variant"]).all(axis=1)

    ic_df = pd.concat(ic_rows, ignore_index=True)
    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "stress_conditioned_alpha.md").write_text(render_report(backtest_df, ic_df, criteria_df))


if __name__ == "__main__":
    main()
