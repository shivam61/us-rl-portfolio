import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.alpha import compute_volatility_score_frame
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.fundamental_features import FundamentalFeatureGenerator
from src.features.stock_features import StockFeatureGenerator
from src.reporting.metrics import calculate_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

VOL_SPECS = [("vol_top_10", 10), ("vol_top_20", 20)]
QUAL_SPECS = [("quality_sector_balanced_top_30", 30), ("quality_sector_balanced_top_50", 50)]
BLEND_WEIGHTS = [(0.6, 0.4), (0.5, 0.5), (0.7, 0.3), (0.4, 0.6)]


def load_inputs(config_path: str, universe_path: str) -> dict:
    base_config, universe_config = load_config(config_path, universe_path)
    pit_mask = None
    if not universe_config.is_static and universe_config.pit_mask_path:
        pit_mask = pd.read_parquet(universe_config.pit_mask_path)

    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    tickers = list(
        set(
            list(universe_config.tickers.keys())
            + universe_config.sector_etfs
            + universe_config.macro_etfs
            + [universe_config.benchmark, universe_config.vix_proxy]
        )
    )
    data_dict = ingestion.fetch_universe_data(tickers=tickers, start_date=base_config.backtest.start_date)
    prices_dict = ingestion.build_all_matrices(data_dict)
    sector_mapping = dict(universe_config.tickers)
    stock_features = StockFeatureGenerator(
        data_dict,
        benchmark_ticker=universe_config.benchmark,
        sector_mapping=sector_mapping,
    ).generate()
    fundamentals = ingestion.fetch_universe_fundamentals(
        tickers=list(universe_config.tickers.keys()),
        start_date=base_config.backtest.start_date,
    )
    fund_features = FundamentalFeatureGenerator(data_dict, fundamentals_df=fundamentals).generate()
    if not fund_features.empty:
        stock_features = stock_features.join(fund_features, how="left")

    return {
        "base_config": base_config,
        "universe_config": universe_config,
        "prices": prices_dict["adj_close"].ffill(),
        "stock_features": stock_features,
        "vol_scores": compute_volatility_score_frame(stock_features),
        "quality_scores": compute_quality_score_frame(stock_features, sector_mapping),
        "pit_mask": pit_mask,
        "sector_mapping": sector_mapping,
    }


def _sector_zscore(panel: pd.DataFrame, col: str, sector_mapping: dict) -> pd.Series:
    tickers = panel.index.get_level_values("ticker")
    sectors = pd.Series(tickers.map(sector_mapping), index=panel.index)
    values = panel[col].astype(float)
    mean = values.groupby([panel.index.get_level_values("date"), sectors]).transform("mean")
    std = values.groupby([panel.index.get_level_values("date"), sectors]).transform("std").replace(0.0, np.nan)
    return ((values - mean) / std).replace([np.inf, -np.inf], np.nan)


def compute_quality_score_frame(panel: pd.DataFrame, sector_mapping: dict) -> pd.DataFrame:
    quality = pd.DataFrame(index=panel.index)

    if "roe" in panel.columns:
        quality["roe_clipped"] = panel["roe"].clip(-1.0, 1.0)
    else:
        quality["roe_clipped"] = np.nan

    if "eps_growth_yoy" in panel.columns:
        eps = panel["eps_growth_yoy"].replace([np.inf, -np.inf], np.nan)
        quality["earnings_stability"] = -eps.groupby(level="ticker").rolling(252, min_periods=63).std().droplevel(0)
    else:
        quality["earnings_stability"] = np.nan

    # True balance-sheet leverage is not currently in cached fundamentals.
    # Low PB is used only as a value/financial-risk proxy for this research sleeve.
    if "pb_ratio" in panel.columns:
        quality["low_leverage_proxy"] = -panel["pb_ratio"].replace([np.inf, -np.inf], np.nan).clip(-50.0, 50.0)
    else:
        quality["low_leverage_proxy"] = np.nan

    quality["low_downside_vol"] = -panel.get("downside_vol_63d", pd.Series(np.nan, index=panel.index))
    quality["low_max_drawdown"] = panel.get("max_drawdown_63d", pd.Series(np.nan, index=panel.index))
    quality["return_consistency"] = panel.get("mom_stability_3m", pd.Series(np.nan, index=panel.index))

    rank_frames = []
    for col in quality.columns:
        quality[f"{col}_sector_z"] = _sector_zscore(quality, col, sector_mapping)
        rank_frames.append(
            quality.groupby(level="date")[f"{col}_sector_z"].rank(ascending=True, pct=True).rename(f"rank_{col}")
        )

    result = pd.DataFrame(index=panel.index)
    result["quality_score"] = pd.concat(rank_frames, axis=1).mean(axis=1, skipna=True)
    result["quality_score_rank"] = result.groupby(level="date")["quality_score"].rank(pct=True)
    return result


def active_tickers(inputs: dict, date: pd.Timestamp) -> list[str]:
    base = list(inputs["universe_config"].tickers.keys())
    pit_mask = inputs["pit_mask"]
    if pit_mask is None:
        return base
    idx = pit_mask.index.get_indexer([date], method="ffill")[0]
    if idx < 0:
        return base
    active = pit_mask.iloc[idx]
    return [ticker for ticker in base if bool(active.get(ticker, False))]


def latest_scores(scores: pd.DataFrame, date: pd.Timestamp, col: str) -> pd.Series:
    dates = scores.index.levels[0]
    idx = dates.get_indexer([date], method="ffill")[0]
    if idx < 0:
        return pd.Series(dtype=float)
    return scores.xs(dates[idx], level="date")[col].dropna()


def rebalance_dates(config, prices: pd.DataFrame) -> list[pd.Timestamp]:
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    end = pd.Timestamp(config.backtest.end_date) if config.backtest.end_date else prices.index[-1]
    dates = []
    for date in pd.date_range(start=start, end=end, freq=config.backtest.rebalance_frequency):
        idx = prices.index.get_indexer([date], method="bfill")[0]
        if idx >= 0:
            dates.append(prices.index[idx])
    return sorted(set(dates))


def select_top(scores: pd.Series, n: int) -> list[str]:
    return scores.dropna().sort_values(ascending=False).head(n).index.tolist()


def select_sector_balanced(scores: pd.Series, n: int, sector_mapping: dict) -> list[str]:
    ranked = scores.dropna().sort_values(ascending=False)
    sectors = sorted(set(sector_mapping.values()))
    cap = max(1, int(np.ceil(n / max(len(sectors), 1))))
    selected = []
    counts = {}
    for ticker in ranked.index:
        sector = sector_mapping.get(ticker, "_other")
        if counts.get(sector, 0) >= cap:
            continue
        selected.append(ticker)
        counts[sector] = counts.get(sector, 0) + 1
        if len(selected) >= n:
            return selected
    for ticker in ranked.index:
        if ticker not in selected:
            selected.append(ticker)
        if len(selected) >= n:
            break
    return selected


def equal_weights(selected: list[str]) -> pd.Series:
    if not selected:
        return pd.Series(dtype=float)
    return pd.Series(1.0 / len(selected), index=selected)


def build_sleeve_weight_paths(inputs: dict) -> dict[str, dict]:
    config = inputs["base_config"]
    rebalances = rebalance_dates(config, inputs["prices"])
    sector_mapping = inputs["sector_mapping"]
    paths: dict[str, dict] = {}

    for name, n in VOL_SPECS:
        weights_by_date = {}
        selected_by_date = {}
        for date in rebalances:
            candidates = active_tickers(inputs, date)
            scores = latest_scores(inputs["vol_scores"], date, "volatility_score").reindex(candidates)
            selected = select_top(scores, n)
            weights_by_date[date] = equal_weights(selected)
            selected_by_date[date] = selected
        paths[name] = {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": "volatility"}

    for name, n in QUAL_SPECS:
        weights_by_date = {}
        selected_by_date = {}
        for date in rebalances:
            candidates = active_tickers(inputs, date)
            scores = latest_scores(inputs["quality_scores"], date, "quality_score").reindex(candidates)
            selected = select_sector_balanced(scores, n, sector_mapping)
            weights_by_date[date] = equal_weights(selected)
            selected_by_date[date] = selected
        paths[name] = {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": "quality"}

    return paths


def combine_weight_paths(path_a: dict, path_b: dict, weight_a: float, weight_b: float) -> dict:
    weights = {}
    selected = {}
    for date in sorted(set(path_a["weights"]).intersection(path_b["weights"])):
        wa = path_a["weights"][date] * weight_a
        wb = path_b["weights"][date] * weight_b
        idx = wa.index.union(wb.index)
        weights[date] = wa.reindex(idx, fill_value=0.0) + wb.reindex(idx, fill_value=0.0)
        selected[date] = list(set(path_a["selected"][date]) | set(path_b["selected"][date]))
    return {"weights": weights, "selected": selected, "sleeve_type": "blend"}


def backtest_weight_path(inputs: dict, name: str, path: dict) -> tuple[dict, pd.Series]:
    config = inputs["base_config"]
    prices = inputs["prices"]
    returns = prices.pct_change().fillna(0.0)
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    dates = [d for d in prices.index if d >= start]
    rebalances = set(path["weights"].keys())
    cost_rate = (config.portfolio.transaction_cost_bps + config.portfolio.slippage_bps) / 10000.0

    current_weights = pd.Series(dtype=float)
    nav = config.portfolio.initial_capital
    nav_rows = []
    daily_returns = []
    turnover_sum = 0.0
    for date in dates:
        if date in rebalances:
            target = path["weights"][date]
            idx = current_weights.index.union(target.index)
            turnover = float((target.reindex(idx, fill_value=0.0) - current_weights.reindex(idx, fill_value=0.0)).abs().sum())
            nav *= max(0.0, 1.0 - turnover * cost_rate)
            turnover_sum += turnover
            current_weights = target
        ret = float((current_weights * returns.loc[date].reindex(current_weights.index).fillna(0.0)).sum()) if not current_weights.empty else 0.0
        nav *= 1.0 + ret
        daily_returns.append((date, ret))
        nav_rows.append((date, nav))

    nav_series = pd.Series(dict(nav_rows)).sort_index()
    ret_series = pd.Series(dict(daily_returns)).sort_index()
    metrics = calculate_metrics(nav_series)
    row = {
        "universe": inputs["universe_config"].name,
        "sleeve": name,
        "sleeve_type": path["sleeve_type"],
        "cagr": metrics.get("CAGR", np.nan),
        "sharpe": metrics.get("Sharpe", np.nan),
        "max_dd": metrics.get("Max Drawdown", np.nan),
        "volatility": metrics.get("Volatility", np.nan),
        "turnover_sum": turnover_sum,
        "n_rebalances": len(rebalances),
    }
    return row, ret_series


def benchmark_rows(inputs: dict) -> list[dict]:
    prices = inputs["prices"]
    config = inputs["base_config"]
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    benchmark = inputs["universe_config"].benchmark
    rows = []
    spy = prices[benchmark].loc[start:].dropna()
    if len(spy) > 2:
        nav = spy / spy.iloc[0] * config.portfolio.initial_capital
        metrics = calculate_metrics(nav)
        rows.append({"universe": inputs["universe_config"].name, "benchmark": "spy_buy_hold", "cagr": metrics["CAGR"], "sharpe": metrics["Sharpe"], "max_dd": metrics["Max Drawdown"], "volatility": metrics["Volatility"]})
    universe_rets = prices[list(inputs["universe_config"].tickers.keys())].loc[start:].pct_change().mean(axis=1).fillna(0.0)
    nav = (1.0 + universe_rets).cumprod() * config.portfolio.initial_capital
    metrics = calculate_metrics(nav)
    rows.append({"universe": inputs["universe_config"].name, "benchmark": "equal_weight_universe_daily", "cagr": metrics["CAGR"], "sharpe": metrics["Sharpe"], "max_dd": metrics["Max Drawdown"], "volatility": metrics["Volatility"]})
    return rows


def overlap_rows(inputs: dict, paths: dict[str, dict]) -> list[dict]:
    rows = []
    sector_mapping = inputs["sector_mapping"]
    vol_names = [n for n, p in paths.items() if p["sleeve_type"] == "volatility"]
    qual_names = [n for n, p in paths.items() if p["sleeve_type"] == "quality"]
    for vol_name in vol_names:
        for qual_name in qual_names:
            ticker_overlaps = []
            sector_overlaps = []
            dates = sorted(set(paths[vol_name]["selected"]).intersection(paths[qual_name]["selected"]))
            for date in dates:
                vol_sel = set(paths[vol_name]["selected"][date])
                qual_sel = set(paths[qual_name]["selected"][date])
                if vol_sel and qual_sel:
                    ticker_overlaps.append(len(vol_sel & qual_sel) / min(len(vol_sel), len(qual_sel)))
                vol_sec = {sector_mapping.get(t, "_other") for t in vol_sel}
                qual_sec = {sector_mapping.get(t, "_other") for t in qual_sel}
                if vol_sec and qual_sec:
                    sector_overlaps.append(len(vol_sec & qual_sec) / min(len(vol_sec), len(qual_sec)))
            rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "quality_sleeve": qual_name,
                    "ticker_overlap_pct": float(pd.Series(ticker_overlaps).mean()) if ticker_overlaps else np.nan,
                    "sector_overlap_pct": float(pd.Series(sector_overlaps).mean()) if sector_overlaps else np.nan,
                    "n_rebalances": len(dates),
                }
            )
    return rows


def correlation_rows(inputs: dict, returns_by_name: dict[str, pd.Series]) -> tuple[list[dict], pd.DataFrame]:
    names = sorted(returns_by_name)
    aligned = pd.concat({name: returns_by_name[name] for name in names}, axis=1).dropna(how="all").fillna(0.0)
    corr_matrix = aligned.corr()
    rows = []
    prices = inputs["prices"]
    benchmark = inputs["universe_config"].benchmark
    spy = prices[benchmark].pct_change()
    drawdown = prices[benchmark] / prices[benchmark].expanding().max() - 1.0
    crisis_dates = drawdown[drawdown <= -0.15].index
    for vol_name in [n for n in names if n.startswith("vol_")]:
        for qual_name in [n for n in names if n.startswith("quality_")]:
            pair = aligned[[vol_name, qual_name]].dropna()
            rolling = pair[vol_name].rolling(252, min_periods=63).corr(pair[qual_name])
            crisis_pair = pair.loc[pair.index.intersection(crisis_dates)]
            rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "quality_sleeve": qual_name,
                    "full_correlation": float(pair[vol_name].corr(pair[qual_name])) if len(pair) > 2 else np.nan,
                    "avg_rolling_252d_correlation": float(rolling.mean()) if not rolling.dropna().empty else np.nan,
                    "crisis_correlation": float(crisis_pair[vol_name].corr(crisis_pair[qual_name])) if len(crisis_pair) > 2 else np.nan,
                }
            )
    return rows, corr_matrix


def render_report(
    sleeve_metrics: pd.DataFrame,
    blend_metrics: pd.DataFrame,
    correlations: pd.DataFrame,
    overlaps: pd.DataFrame,
    benchmarks: pd.DataFrame,
) -> str:
    lines = [
        "# Multi-Sleeve Alpha Results",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Sleeve 1 unchanged: existing `volatility_score`.",
        "- Sleeve 2 independent: defensive `quality_score`.",
        "- RL disabled.",
        "- Scores are not merged into one model; sleeves are selected and blended as separate portfolios.",
        "",
        "## Goal",
        "",
        "Test whether strong but risky volatility alpha plus weaker defensive quality alpha can become an investable non-RL system.",
        "",
        "## Sleeve Metrics",
        "",
        sleeve_metrics.to_markdown(index=False, floatfmt=".4f") if not sleeve_metrics.empty else "No sleeve metrics.",
        "",
        "## Blend Metrics",
        "",
        blend_metrics.to_markdown(index=False, floatfmt=".4f") if not blend_metrics.empty else "No blend metrics.",
        "",
        "## Cross-Sleeve Correlation",
        "",
        correlations.to_markdown(index=False, floatfmt=".4f") if not correlations.empty else "No correlation rows.",
        "",
        "## Overlap",
        "",
        overlaps.to_markdown(index=False, floatfmt=".4f") if not overlaps.empty else "No overlap rows.",
        "",
        "## Benchmarks",
        "",
        benchmarks.to_markdown(index=False, floatfmt=".4f") if not benchmarks.empty else "No benchmarks.",
        "",
        "## Success Criteria",
        "",
    ]
    sp500_blends = blend_metrics[blend_metrics["universe"].str.contains("sp500", case=False, na=False)]
    sp500_ew = benchmarks[
        benchmarks["universe"].str.contains("sp500", case=False, na=False)
        & (benchmarks["benchmark"] == "equal_weight_universe_daily")
    ]
    if not sp500_blends.empty and not sp500_ew.empty:
        ew = sp500_ew.iloc[0]
        candidates = sp500_blends[
            (sp500_blends["cagr"] >= ew["cagr"])
            & (sp500_blends["sharpe"] > ew["sharpe"])
            & (sp500_blends["max_dd"] > -0.40)
        ]
        corr_pass = correlations[
            correlations["universe"].str.contains("sp500", case=False, na=False)
            & (correlations["full_correlation"] < 0.5)
        ]
        lines.append(f"- sp500 CAGR >= equal-weight, Sharpe > equal-weight, MaxDD < 40%: {'PASS' if not candidates.empty else 'FAIL'}")
        lines.append(f"- sp500 vol-quality full correlation < 0.5: {'PASS' if not corr_pass.empty else 'FAIL'}")
        if not candidates.empty:
            lines.append(candidates.sort_values(["sharpe", "cagr"], ascending=False).head(5).to_markdown(index=False, floatfmt=".4f"))
        else:
            lines.append("- No sp500 blend met all hard gates.")
    else:
        lines.append("- sp500 success criteria not evaluated.")
    lines.extend(
        [
            "",
            "## Implementation Notes",
            "",
            "- `low_leverage_proxy` uses low `pb_ratio` because true debt/leverage is not currently available in cached fundamentals.",
            "- Defensive quality is intentionally an independent sleeve; it is not merged into `volatility_score`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.3 multi-sleeve alpha experiment")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml", "config/universes/sp500.yaml"])
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    sleeve_rows = []
    blend_rows = []
    corr_rows_all = []
    overlap_rows_all = []
    benchmarks_all = []
    corr_matrices = []

    for universe_path in args.universes:
        logger.info("Running Phase A.3 multi-sleeve alpha for %s", universe_path)
        inputs = load_inputs(args.config, universe_path)
        paths = build_sleeve_weight_paths(inputs)
        returns_by_name = {}
        for name, path in paths.items():
            row, returns = backtest_weight_path(inputs, name, path)
            sleeve_rows.append(row)
            returns_by_name[name] = returns

        for vol_name in [n for n, p in paths.items() if p["sleeve_type"] == "volatility"]:
            for qual_name in [n for n, p in paths.items() if p["sleeve_type"] == "quality"]:
                for vol_weight, qual_weight in BLEND_WEIGHTS:
                    blend_name = f"blend_{vol_name}_{qual_name}_{int(vol_weight * 100)}_{int(qual_weight * 100)}"
                    blend_path = combine_weight_paths(paths[vol_name], paths[qual_name], vol_weight, qual_weight)
                    row, returns = backtest_weight_path(inputs, blend_name, blend_path)
                    row["vol_sleeve"] = vol_name
                    row["quality_sleeve"] = qual_name
                    row["vol_weight"] = vol_weight
                    row["quality_weight"] = qual_weight
                    blend_rows.append(row)
                    returns_by_name[blend_name] = returns

        corr_rows, corr_matrix = correlation_rows(inputs, returns_by_name)
        corr_rows_all.extend(corr_rows)
        corr_matrix.insert(0, "universe", inputs["universe_config"].name)
        corr_matrices.append(corr_matrix.reset_index(names="sleeve"))
        overlap_rows_all.extend(overlap_rows(inputs, paths))
        benchmarks_all.extend(benchmark_rows(inputs))

    sleeve_metrics = pd.DataFrame(sleeve_rows)
    blend_metrics = pd.DataFrame(blend_rows)
    correlations = pd.DataFrame(corr_rows_all)
    overlaps = pd.DataFrame(overlap_rows_all)
    benchmarks = pd.DataFrame(benchmarks_all)
    corr_matrix = pd.concat(corr_matrices, ignore_index=True) if corr_matrices else pd.DataFrame()

    sleeve_metrics.to_csv(reports_dir / "sleeve_metrics.csv", index=False)
    blend_metrics.to_csv(reports_dir / "blend_metrics.csv", index=False)
    correlations.to_csv(reports_dir / "correlation_matrix.csv", index=False)
    overlaps.to_csv(reports_dir / "overlap_report.csv", index=False)
    corr_matrix.to_csv(reports_dir / "sleeve_return_correlation_matrix.csv", index=False)
    benchmarks.to_csv(reports_dir / "multi_sleeve_benchmarks.csv", index=False)
    (reports_dir / "multi_sleeve_results.md").write_text(
        render_report(sleeve_metrics, blend_metrics, correlations, overlaps, benchmarks)
    )
    logger.info("Saved Phase A.3 artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
