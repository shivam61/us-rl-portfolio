"""
Regime-switch factor research, no LGBM and no RL.

Builds three independent factor sleeves:
  - mean_reversion_score
  - trend_score
  - volatility_score

Then classifies each date into:
  - high_vol
  - neutral
  - low_vol

And applies:
  high_vol -> mean_reversion_score
  low_vol  -> volatility_score
  neutral  -> trend_score

Outputs:
  artifacts/reports/regime_switch_results.md
  artifacts/reports/regime_ic.csv
"""

import argparse
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.backtest.walk_forward import WalkForwardEngine
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.macro_features import MacroFeatureGenerator
from src.features.stock_features import StockFeatureGenerator
from src.labels.targets import TargetGenerator
from src.reporting.metrics import calculate_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MEAN_REVERSION_FEATURES = [
    ("ret_3m_ex_1w", False),
    ("ret_6m_ex_1m", False),
    ("ret_12m_ex_1m", False),
    ("sector_rel_momentum_3m", False),
    ("pct_pos_months_6m", False),
]

TREND_FEATURES = [
    ("trend_consistency", True),
    ("sector_rel_momentum_6m", True),
]

VOL_FEATURES = [
    ("volatility_63d", True),
    ("downside_vol_63d", True),
    ("beta_to_spy_63d", True),
    ("max_drawdown_63d", False),
]

SCORE_COLUMNS = [
    "mean_reversion_score",
    "trend_score",
    "volatility_score",
    "regime_switch_score",
]


def _rank_feature(panel: pd.DataFrame, column: str, ascending: bool) -> pd.Series:
    return panel.groupby(level="date")[column].rank(ascending=ascending, pct=True)


def _composite_score(panel: pd.DataFrame, feature_defs: list[tuple[str, bool]], name: str) -> pd.Series:
    frames = []
    missing = []
    for column, ascending in feature_defs:
        if column not in panel.columns:
            missing.append(column)
            continue
        frames.append(_rank_feature(panel, column, ascending=ascending).rename(column))
    if missing:
        logger.warning("%s missing features: %s", name, ", ".join(sorted(missing)))
    if not frames:
        return pd.Series(np.nan, index=panel.index, name=name)
    return pd.concat(frames, axis=1).mean(axis=1).rename(name)


def compute_factor_scores(panel: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(index=panel.index)
    result["mean_reversion_score"] = _composite_score(panel, MEAN_REVERSION_FEATURES, "mean_reversion_score")
    result["trend_score"] = _composite_score(panel, TREND_FEATURES, "trend_score")
    result["volatility_score"] = _composite_score(panel, VOL_FEATURES, "volatility_score")

    for score_col in ["mean_reversion_score", "trend_score", "volatility_score"]:
        result[f"{score_col}_rank"] = result.groupby(level="date")[score_col].rank(pct=True)

    return result


def classify_regimes(macro_features: pd.DataFrame) -> pd.DataFrame:
    regime_df = macro_features[["vix_percentile_1y", "spy_drawdown", "realized_market_vol_63d"]].copy()
    regime_df["realized_vol_percentile_1y"] = regime_df["realized_market_vol_63d"].rolling(252).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1]
    )

    high_mask = (
        (regime_df["vix_percentile_1y"] >= 0.80)
        | (regime_df["spy_drawdown"] <= -0.10)
        | (regime_df["realized_vol_percentile_1y"] >= 0.80)
    )
    low_mask = (
        (regime_df["vix_percentile_1y"] <= 0.20)
        & (regime_df["spy_drawdown"] >= -0.05)
        & (regime_df["realized_vol_percentile_1y"] <= 0.20)
    )

    regime_df["regime"] = "neutral"
    regime_df.loc[high_mask, "regime"] = "high_vol"
    regime_df.loc[low_mask, "regime"] = "low_vol"
    return regime_df


def apply_regime_switch(scores: pd.DataFrame, regimes: pd.DataFrame) -> pd.DataFrame:
    result = scores.join(regimes[["regime"]], how="left")
    result["regime"] = result.index.get_level_values("date").map(regimes["regime"]).fillna("neutral")

    result["regime_switch_score"] = np.where(
        result["regime"].eq("high_vol"),
        result["mean_reversion_score_rank"],
        np.where(
            result["regime"].eq("low_vol"),
            result["volatility_score_rank"],
            result["trend_score_rank"],
        ),
    )
    return result


def evaluate_scores(
    panel: pd.DataFrame,
    eval_start: str,
    eval_end: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    dates = panel.index.get_level_values("date").unique().sort_values()
    eval_mask = (dates >= pd.Timestamp(eval_start)) & (dates < pd.Timestamp(eval_end))
    eval_dates = set(dates[eval_mask])

    for date, grp in panel.groupby(level="date"):
        if date not in eval_dates:
            continue
        regime = grp["regime"].dropna().iloc[0] if "regime" in grp and grp["regime"].notna().any() else "neutral"
        for score_col in SCORE_COLUMNS:
            valid = grp[[score_col, "target_fwd_ret"]].dropna()
            if len(valid) < 5:
                continue
            ic, _ = spearmanr(valid[score_col], valid["target_fwd_ret"])
            if np.isnan(ic):
                continue

            q80 = valid[score_col].quantile(0.8)
            q20 = valid[score_col].quantile(0.2)
            top_ret = valid.loc[valid[score_col] >= q80, "target_fwd_ret"].mean()
            bot_ret = valid.loc[valid[score_col] <= q20, "target_fwd_ret"].mean()

            rows.append(
                {
                    "date": date,
                    "regime": regime,
                    "score": score_col,
                    "ic": float(ic),
                    "top_bot_spread": float((top_ret - bot_ret) * 100.0),
                    "n_tickers": int(len(valid)),
                }
            )

    date_level = pd.DataFrame(rows).sort_values(["score", "date"]).reset_index(drop=True)
    summary = (
        date_level.groupby(["score", "regime"], dropna=False)
        .agg(
            mean_ic=("ic", "mean"),
            ic_sharpe=("ic", lambda x: x.mean() / (x.std() + 1e-9)),
            top_bot_spread=("top_bot_spread", "mean"),
            n_dates=("date", "count"),
        )
        .reset_index()
    )
    return date_level, summary


def make_alpha_provider(score_col: str):
    def _provider(signal_date: pd.Timestamp, active_tickers: list[str], engine: WalkForwardEngine) -> pd.Series:
        idx = engine.stock_features.index.levels[0].get_indexer([signal_date], method="ffill")[0]
        if idx < 0:
            return pd.Series(dtype=float)
        feature_date = engine.stock_features.index.levels[0][idx]
        latest = engine.stock_features.xs(feature_date, level="date")
        alpha = latest.reindex(active_tickers)[score_col].dropna()
        return alpha

    return _provider


def run_backtest_variant(
    base_config,
    universe_config,
    stock_features: pd.DataFrame,
    macro_features: pd.DataFrame,
    targets: pd.DataFrame,
    prices_dict: dict,
    pit_mask: pd.DataFrame | None,
    score_col: str,
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
    history, _, diagnostics = engine.run(
        use_optimizer=True,
        use_risk_engine=True,
        top_n_equal_weight=base_config.portfolio.top_n_stocks,
        alpha_score_provider=make_alpha_provider(score_col),
    )
    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    metrics["score"] = score_col
    metrics["mean_ic"] = float(np.mean([x["rank_ic"] for x in diagnostics["alpha_quality"]])) if diagnostics["alpha_quality"] else np.nan
    metrics["alpha_obs"] = len(diagnostics["alpha_quality"])
    return metrics


def load_inputs(config_path: str, universe_path: str):
    base_config, universe_config = load_config(config_path, universe_path)
    cache_dir = Path(base_config.data.cache_dir)

    pit_mask = None
    if not universe_config.is_static and universe_config.pit_mask_path:
        pit_mask = pd.read_parquet(universe_config.pit_mask_path)

    sector_mapping = dict(universe_config.tickers)
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

    return base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask


def render_markdown(
    summary_df: pd.DataFrame,
    backtest_df: pd.DataFrame,
    selected_row: pd.Series,
    best_single_factor_ic: pd.Series,
    best_single_factor_cagr: pd.Series,
    lowest_dd_single_factor: pd.Series,
    args,
    wall_seconds: float,
) -> str:
    score_summary = (
        summary_df.groupby("score")
        .agg(
            mean_ic=("mean_ic", "mean"),
            ic_sharpe=("ic_sharpe", "mean"),
            top_bot_spread=("top_bot_spread", "mean"),
        )
        .reset_index()
        .sort_values("ic_sharpe", ascending=False)
    )

    md_lines = [
        "# Regime Switch Results",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').date()}",
        f"- Universe: `{args.universe}`",
        f"- Eval window: `{args.eval_start}` to `{args.eval_end}`",
        f"- Regime rules: `high_vol` if VIX pct >= 0.80 or SPY drawdown <= -10% or realized vol pct >= 0.80; `low_vol` if VIX pct <= 0.20 and SPY drawdown >= -5% and realized vol pct <= 0.20; else `neutral`",
        f"- Selection map: `high_vol -> mean_reversion`, `low_vol -> volatility`, `neutral -> trend`",
        f"- Wall time: {wall_seconds:.1f}s",
        "",
        "## IC Summary",
        "",
        score_summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Regime-Wise IC",
        "",
        summary_df.sort_values(["score", "regime"]).to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Backtest",
        "",
        backtest_df.sort_values("Sharpe", ascending=False).to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Success Criteria",
        "",
        "| Criterion | Regime Switch | Baseline | Pass? |",
        "|---|---:|---:|---|",
        f"| IC Sharpe > 0.2 | {score_summary.loc[score_summary['score'] == 'regime_switch_score', 'ic_sharpe'].iloc[0]:.4f} | 0.2000 | {'✅' if score_summary.loc[score_summary['score'] == 'regime_switch_score', 'ic_sharpe'].iloc[0] > 0.2 else '❌'} |",
        f"| CAGR improves vs best single-factor | {selected_row['CAGR']:.4f} | {best_single_factor_cagr['CAGR']:.4f} ({best_single_factor_cagr['score']}) | {'✅' if selected_row['CAGR'] > best_single_factor_cagr['CAGR'] else '❌'} |",
        f"| Max drawdown improves vs best single-factor | {selected_row['Max Drawdown']:.4f} | {lowest_dd_single_factor['Max Drawdown']:.4f} ({lowest_dd_single_factor['score']}) | {'✅' if selected_row['Max Drawdown'] > lowest_dd_single_factor['Max Drawdown'] else '❌'} |",
        "",
        "## Notes",
        "",
        f"- Best single-factor IC Sharpe: `{best_single_factor_ic['score']}` at `{best_single_factor_ic['ic_sharpe']:.4f}`.",
        f"- Best single-factor CAGR: `{best_single_factor_cagr['score']}` at `{best_single_factor_cagr['CAGR']:.4f}`.",
        f"- Lowest single-factor drawdown: `{lowest_dd_single_factor['score']}` at `{lowest_dd_single_factor['Max Drawdown']:.4f}`.",
    ]
    return "\n".join(md_lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp100.yaml")
    parser.add_argument("--eval-start", default="2016-01-01")
    parser.add_argument("--eval-end", default="2026-01-01")
    args = parser.parse_args()

    start = time.perf_counter()
    (
        base_config,
        universe_config,
        stock_features,
        macro_features,
        targets,
        prices_dict,
        pit_mask,
    ) = load_inputs(args.config, args.universe)

    panel = stock_features.join(targets[["target_fwd_ret"]], how="inner")
    scores = compute_factor_scores(panel)
    regimes = classify_regimes(macro_features)
    scores = apply_regime_switch(scores, regimes)
    research_panel = panel.join(scores, how="inner")

    date_level_ic, summary_ic = evaluate_scores(research_panel, args.eval_start, args.eval_end)

    stock_features_for_backtest = stock_features.join(scores[SCORE_COLUMNS], how="left")
    backtest_rows = []
    for score_col in SCORE_COLUMNS:
        logger.info("Running backtest for %s...", score_col)
        backtest_rows.append(
            run_backtest_variant(
                base_config=base_config,
                universe_config=universe_config,
                stock_features=stock_features_for_backtest,
                macro_features=macro_features,
                targets=targets,
                prices_dict=prices_dict,
                pit_mask=pit_mask,
                score_col=score_col,
            )
        )

    backtest_df = pd.DataFrame(backtest_rows)

    out_dir = Path("artifacts/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    date_level_ic.to_csv(out_dir / "regime_ic.csv", index=False)

    score_summary = (
        summary_ic.groupby("score")
        .agg(mean_ic=("mean_ic", "mean"), ic_sharpe=("ic_sharpe", "mean"))
        .reset_index()
    )
    single_factor_scores = score_summary[score_summary["score"] != "regime_switch_score"]
    best_single_factor_ic = single_factor_scores.sort_values("ic_sharpe", ascending=False).iloc[0]

    selected_row = backtest_df[backtest_df["score"] == "regime_switch_score"].iloc[0]
    single_factor_backtests = backtest_df[backtest_df["score"] != "regime_switch_score"]
    best_single_factor_cagr = single_factor_backtests.sort_values("CAGR", ascending=False).iloc[0]
    lowest_dd_single_factor = single_factor_backtests.sort_values("Max Drawdown", ascending=False).iloc[0]

    wall_seconds = time.perf_counter() - start
    report = render_markdown(
        summary_df=summary_ic,
        backtest_df=backtest_df,
        selected_row=selected_row,
        best_single_factor_ic=best_single_factor_ic,
        best_single_factor_cagr=best_single_factor_cagr,
        lowest_dd_single_factor=lowest_dd_single_factor,
        args=args,
        wall_seconds=wall_seconds,
    )
    (out_dir / "regime_switch_results.md").write_text(report)

    logger.info("Saved %s", out_dir / "regime_ic.csv")
    logger.info("Saved %s", out_dir / "regime_switch_results.md")


if __name__ == "__main__":
    main()
