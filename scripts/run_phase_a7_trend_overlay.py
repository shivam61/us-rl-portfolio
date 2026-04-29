import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.alpha import compute_volatility_score_frame
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.stock_features import StockFeatureGenerator
from src.reporting.metrics import calculate_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TREND_ASSETS = ["SPY", "TLT", "GLD", "UUP"]
VOL_SPECS = [("vol_top_10", 10), ("vol_top_20", 20)]
TREND_SPECS = [
    ("trend_3m_long_cash", 63, "long_cash"),
    ("trend_6m_long_cash", 126, "long_cash"),
    ("trend_3m_6m_long_cash", None, "long_cash"),
    ("trend_3m_long_short", 63, "long_short"),
    ("trend_6m_long_short", 126, "long_short"),
    ("trend_3m_6m_long_short", None, "long_short"),
]
BLEND_WEIGHTS = [(0.8, 0.2), (0.7, 0.3), (0.6, 0.4)]
PERIODS = {
    "gfc": ("2008-01-01", "2009-12-31"),
    "covid": ("2020-02-01", "2020-05-31"),
    "inflation_2022": ("2022-01-01", "2022-12-31"),
    "recent": ("2023-01-01", "2026-12-31"),
}


def load_inputs(config_path: str, universe_path: str, trend_assets: list[str]) -> dict:
    base_config, universe_config = load_config(config_path, universe_path)
    pit_mask = None
    if not universe_config.is_static and universe_config.pit_mask_path:
        pit_mask = pd.read_parquet(universe_config.pit_mask_path)

    ingestion = DataIngestion(
        cache_dir=base_config.data.cache_dir,
        force_download=False,
        fundamental_provider=base_config.fundamentals.provider,
        fundamental_path=base_config.fundamentals.path,
    )
    tickers = sorted(
        set(
            list(universe_config.tickers.keys())
            + universe_config.sector_etfs
            + universe_config.macro_etfs
            + [universe_config.benchmark, universe_config.vix_proxy]
            + trend_assets
        )
    )
    data_dict = ingestion.fetch_universe_data(tickers=tickers, start_date=base_config.backtest.start_date)
    prices = ingestion.build_all_matrices(data_dict)["adj_close"].ffill()
    stock_features = StockFeatureGenerator(
        data_dict,
        benchmark_ticker=universe_config.benchmark,
        sector_mapping=dict(universe_config.tickers),
    ).generate()
    return {
        "base_config": base_config,
        "universe_config": universe_config,
        "prices": prices,
        "stock_features": stock_features,
        "vol_scores": compute_volatility_score_frame(stock_features),
        "pit_mask": pit_mask,
        "trend_assets": [asset for asset in trend_assets if asset in prices.columns],
    }


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


def rebalance_dates(config, prices: pd.DataFrame) -> list[pd.Timestamp]:
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    end = pd.Timestamp(config.backtest.end_date) if config.backtest.end_date else prices.index[-1]
    dates = []
    for date in pd.date_range(start=start, end=end, freq=config.backtest.rebalance_frequency):
        idx = prices.index.get_indexer([date], method="bfill")[0]
        if idx >= 0:
            dates.append(prices.index[idx])
    return sorted(set(dates))


def latest_scores(scores: pd.DataFrame, date: pd.Timestamp, col: str) -> pd.Series:
    dates = scores.index.levels[0]
    idx = dates.get_indexer([date], method="ffill")[0]
    if idx < 0:
        return pd.Series(dtype=float)
    return scores.xs(dates[idx], level="date")[col].dropna()


def equal_weights(selected: list[str]) -> pd.Series:
    if not selected:
        return pd.Series(dtype=float)
    return pd.Series(1.0 / len(selected), index=selected)


def build_vol_weight_paths(inputs: dict) -> dict[str, dict]:
    paths = {}
    rebalances = rebalance_dates(inputs["base_config"], inputs["prices"])
    for name, n in VOL_SPECS:
        weights_by_date = {}
        selected_by_date = {}
        for date in rebalances:
            candidates = active_tickers(inputs, date)
            scores = latest_scores(inputs["vol_scores"], date, "volatility_score").reindex(candidates)
            selected = scores.dropna().sort_values(ascending=False).head(n).index.tolist()
            weights_by_date[date] = equal_weights(selected)
            selected_by_date[date] = selected
        paths[name] = {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": "volatility"}
    return paths


def momentum_signal(price_window: pd.DataFrame, lookback: int | None, mode: str) -> pd.Series:
    if lookback is None:
        ret_3m = price_window.iloc[-1] / price_window.shift(63).iloc[-1] - 1.0
        ret_6m = price_window.iloc[-1] / price_window.shift(126).iloc[-1] - 1.0
        raw = 0.5 * ret_3m + 0.5 * ret_6m
    else:
        raw = price_window.iloc[-1] / price_window.shift(lookback).iloc[-1] - 1.0
    signal = np.sign(raw).replace(0.0, np.nan)
    if mode == "long_cash":
        signal = signal.clip(lower=0.0).fillna(0.0)
    elif mode == "long_short":
        signal = signal.fillna(0.0)
    else:
        raise ValueError(f"Unsupported trend mode: {mode}")
    return signal


def trend_weights(
    prices: pd.DataFrame,
    date: pd.Timestamp,
    assets: list[str],
    lookback: int | None,
    mode: str,
    target_vol: float,
    gross_cap: float,
    vol_window: int,
) -> pd.Series:
    idx = prices.index.get_indexer([date], method="ffill")[0]
    if idx < max(126, vol_window):
        return pd.Series(dtype=float)
    hist = prices.iloc[: idx + 1][assets].dropna(axis=1, how="all").ffill()
    valid_assets = [asset for asset in assets if asset in hist.columns and hist[asset].notna().iloc[-1]]
    if not valid_assets:
        return pd.Series(dtype=float)
    hist = hist[valid_assets]
    signal = momentum_signal(hist, lookback, mode).reindex(valid_assets).fillna(0.0)
    if signal.abs().sum() == 0:
        return pd.Series(dtype=float)

    returns = hist.pct_change().dropna()
    trailing = returns.tail(vol_window)
    vol = trailing.std().replace(0.0, np.nan) * np.sqrt(252)
    inv_vol = 1.0 / vol.reindex(valid_assets)
    raw = signal * inv_vol
    raw = raw.replace([np.inf, -np.inf], np.nan).dropna()
    if raw.abs().sum() == 0:
        return pd.Series(dtype=float)
    weights = raw / raw.abs().sum()

    cov = trailing.reindex(columns=weights.index).cov() * 252
    sleeve_vol = float(np.sqrt(max(weights.values @ cov.values @ weights.values, 0.0))) if len(weights) else np.nan
    scale = min(gross_cap, target_vol / sleeve_vol) if sleeve_vol and np.isfinite(sleeve_vol) and sleeve_vol > 0 else 1.0
    return weights * scale


def build_trend_weight_paths(inputs: dict, target_vol: float, gross_cap: float, vol_window: int) -> dict[str, dict]:
    paths = {}
    rebalances = rebalance_dates(inputs["base_config"], inputs["prices"])
    prices = inputs["prices"]
    assets = inputs["trend_assets"]
    for name, lookback, mode in TREND_SPECS:
        weights_by_date = {}
        selected_by_date = {}
        for date in rebalances:
            weights = trend_weights(prices, date, assets, lookback, mode, target_vol, gross_cap, vol_window)
            weights_by_date[date] = weights
            selected_by_date[date] = weights[weights.abs() > 0].index.tolist()
        paths[name] = {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": "trend"}
    return paths


def backtest_path(inputs: dict, name: str, path: dict) -> tuple[dict, pd.Series, pd.Series]:
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
    gross_rows = []
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
        gross_rows.append((date, float(current_weights.abs().sum()) if not current_weights.empty else 0.0))

    nav_series = pd.Series(dict(nav_rows)).sort_index()
    ret_series = pd.Series(dict(daily_returns)).sort_index()
    gross_series = pd.Series(dict(gross_rows)).sort_index()
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
        "avg_gross": float(gross_series.mean()) if not gross_series.empty else np.nan,
        "max_gross": float(gross_series.max()) if not gross_series.empty else np.nan,
        "n_rebalances": len(rebalances),
    }
    return row, ret_series, nav_series


def combine_return_series(inputs: dict, vol_name: str, trend_name: str, vol_ret: pd.Series, trend_ret: pd.Series, vol_weight: float, trend_weight: float) -> tuple[dict, pd.Series]:
    returns = pd.concat([vol_ret.rename("vol"), trend_ret.rename("trend")], axis=1).fillna(0.0)
    combined_ret = returns["vol"] * vol_weight + returns["trend"] * trend_weight
    nav = (1.0 + combined_ret).cumprod() * inputs["base_config"].portfolio.initial_capital
    metrics = calculate_metrics(nav)
    name = f"blend_{vol_name}_{trend_name}_{int(vol_weight * 100)}_{int(trend_weight * 100)}"
    row = {
        "universe": inputs["universe_config"].name,
        "sleeve": name,
        "sleeve_type": "blend",
        "vol_sleeve": vol_name,
        "trend_sleeve": trend_name,
        "vol_weight": vol_weight,
        "trend_weight": trend_weight,
        "cagr": metrics.get("CAGR", np.nan),
        "sharpe": metrics.get("Sharpe", np.nan),
        "max_dd": metrics.get("Max Drawdown", np.nan),
        "volatility": metrics.get("Volatility", np.nan),
    }
    return row, combined_ret


def benchmark_rows(inputs: dict) -> list[dict]:
    prices = inputs["prices"]
    config = inputs["base_config"]
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    rows = []
    benchmark = inputs["universe_config"].benchmark
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


def correlation_reports(inputs: dict, returns_by_name: dict[str, pd.Series]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    aligned = pd.concat(returns_by_name, axis=1).dropna(how="all").fillna(0.0)
    prices = inputs["prices"]
    benchmark = inputs["universe_config"].benchmark
    drawdown = prices[benchmark] / prices[benchmark].expanding().max() - 1.0
    crisis_dates = drawdown[drawdown <= -0.15].index

    rows = []
    crisis_rows = []
    rolling_rows = []
    vol_names = [name for name in aligned.columns if name.startswith("vol_")]
    trend_names = [name for name in aligned.columns if name.startswith("trend_")]
    blend_names = [name for name in aligned.columns if name.startswith("blend_")]
    for vol_name in vol_names:
        for other_name in trend_names + blend_names:
            pair = aligned[[vol_name, other_name]].dropna()
            rolling = pair[vol_name].rolling(252, min_periods=63).corr(pair[other_name])
            crisis_pair = pair.loc[pair.index.intersection(crisis_dates)]
            rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "other_sleeve": other_name,
                    "other_type": "trend" if other_name in trend_names else "blend",
                    "full_correlation": float(pair[vol_name].corr(pair[other_name])) if len(pair) > 2 else np.nan,
                    "avg_rolling_252d_correlation": float(rolling.mean()) if not rolling.dropna().empty else np.nan,
                }
            )
            crisis_rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "other_sleeve": other_name,
                    "other_type": "trend" if other_name in trend_names else "blend",
                    "crisis_correlation": float(crisis_pair[vol_name].corr(crisis_pair[other_name])) if len(crisis_pair) > 2 else np.nan,
                    "crisis_observations": len(crisis_pair),
                }
            )
            rolling_rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "other_sleeve": other_name,
                    "other_type": "trend" if other_name in trend_names else "blend",
                    "rolling_corr_min": float(rolling.min()) if not rolling.dropna().empty else np.nan,
                    "rolling_corr_median": float(rolling.median()) if not rolling.dropna().empty else np.nan,
                    "rolling_corr_max": float(rolling.max()) if not rolling.dropna().empty else np.nan,
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(crisis_rows), pd.DataFrame(rolling_rows)


def period_drawdown_rows(inputs: dict, nav_by_name: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for name, nav in nav_by_name.items():
        for period, (start, end) in PERIODS.items():
            scoped = nav.loc[(nav.index >= pd.Timestamp(start)) & (nav.index <= pd.Timestamp(end))]
            if len(scoped) < 2:
                continue
            metrics = calculate_metrics(scoped)
            rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "sleeve": name,
                    "period": period,
                    "cagr": metrics.get("CAGR", np.nan),
                    "sharpe": metrics.get("Sharpe", np.nan),
                    "max_dd": metrics.get("Max Drawdown", np.nan),
                }
            )
    return pd.DataFrame(rows)


def gate_report(blend_metrics: pd.DataFrame, benchmarks: pd.DataFrame, crisis_corr: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for universe, group in blend_metrics.groupby("universe"):
        ew = benchmarks[(benchmarks["universe"] == universe) & (benchmarks["benchmark"] == "equal_weight_universe_daily")]
        ew_sharpe = float(ew.iloc[0]["sharpe"]) if not ew.empty else np.nan
        for _, row in group.iterrows():
            trend_crisis = crisis_corr[
                (crisis_corr["vol_sleeve"] == row["vol_sleeve"])
                & (crisis_corr["other_sleeve"] == row["trend_sleeve"])
                & (crisis_corr["other_type"] == "trend")
            ]["crisis_correlation"].min()
            blend_crisis = crisis_corr[
                (crisis_corr["vol_sleeve"] == row["vol_sleeve"])
                & (crisis_corr["other_sleeve"] == row["sleeve"])
                & (crisis_corr["other_type"] == "blend")
            ]["crisis_correlation"].min()
            rows.append(
                {
                    "universe": universe,
                    "sleeve": row["sleeve"],
                    "vol_sleeve": row["vol_sleeve"],
                    "trend_sleeve": row["trend_sleeve"],
                    "sharpe": row["sharpe"],
                    "max_dd": row["max_dd"],
                    "equal_weight_sharpe": ew_sharpe,
                    "trend_crisis_corr_vs_vol": trend_crisis,
                    "blend_crisis_corr_vs_vol": blend_crisis,
                    "passes_gate": bool(row["sharpe"] > ew_sharpe and row["max_dd"] > -0.40 and trend_crisis < 0.6),
                }
            )
    return pd.DataFrame(rows)


def render_report(
    metrics: pd.DataFrame,
    blend_metrics: pd.DataFrame,
    benchmarks: pd.DataFrame,
    corr: pd.DataFrame,
    crisis_corr: pd.DataFrame,
    gate: pd.DataFrame,
    period_dd: pd.DataFrame,
    trend_assets: list[str],
) -> str:
    passed = gate[gate["passes_gate"]] if not gate.empty else pd.DataFrame()
    gate_counts = gate.groupby("universe")["passes_gate"].sum().reset_index(name="passing_variants") if not gate.empty else pd.DataFrame()
    validation_pass = False
    if not gate.empty:
        sp500_gate = gate[gate["universe"].str.contains("sp500", case=False, na=False)]
        validation_pass = bool(sp500_gate["passes_gate"].any()) if not sp500_gate.empty else bool(passed.empty is False)
    lines = [
        "# Phase A.7 Trend Overlay Results",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Objective: introduce a true orthogonal hedge/trend sleeve for the volatility alpha.",
        "- `volatility_score` is unchanged.",
        "- Quality sleeve is not revisited.",
        "- RL disabled.",
        f"- Trend assets available: `{', '.join(trend_assets)}`",
        "",
        "## Standalone Metrics",
        "",
        metrics.to_markdown(index=False, floatfmt=".4f") if not metrics.empty else "No metrics.",
        "",
        "## Blend Metrics",
        "",
        blend_metrics.to_markdown(index=False, floatfmt=".4f") if not blend_metrics.empty else "No blend metrics.",
        "",
        "## Gate",
        "",
        gate.to_markdown(index=False, floatfmt=".4f") if not gate.empty else "No gate rows.",
        "",
        "Gate counts by universe:",
        "",
        gate_counts.to_markdown(index=False) if not gate_counts.empty else "No gate counts.",
        "",
        f"Validation gate result: {'PASS' if validation_pass else 'FAIL'}",
        "",
        "## Correlation",
        "",
        corr.to_markdown(index=False, floatfmt=".4f") if not corr.empty else "No correlation rows.",
        "",
        "## Crisis Correlation",
        "",
        crisis_corr.to_markdown(index=False, floatfmt=".4f") if not crisis_corr.empty else "No crisis correlation rows.",
        "",
        "## Period Drawdowns",
        "",
        period_dd.to_markdown(index=False, floatfmt=".4f") if not period_dd.empty else "No period rows.",
        "",
        "## Benchmarks",
        "",
        benchmarks.to_markdown(index=False, floatfmt=".4f") if not benchmarks.empty else "No benchmarks.",
        "",
        "## Decision",
        "",
    ]
    if validation_pass:
        lines.append("At least one trend-overlay blend passed on the validation universe. Review implementation details, costs, and robustness before any optimizer/RL work.")
    elif not passed.empty:
        lines.append("The trend overlay passed on the research universe but failed the validation universe. Do not promote it yet; improve drawdown control and rerun validation.")
    else:
        lines.append("No trend-overlay blend passed all gates. Inspect whether the issue is insufficient hedge strength, trend asset set, or blend sizing before expanding the experiment.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.7 trend hedge overlay experiment")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml"])
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    parser.add_argument("--target-vol", type=float, default=0.10)
    parser.add_argument("--gross-cap", type=float, default=1.5)
    parser.add_argument("--vol-window", type=int, default=63)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    metric_rows = []
    blend_rows = []
    benchmark_rows_all = []
    corr_frames = []
    crisis_corr_frames = []
    rolling_corr_frames = []
    period_frames = []
    gate_frames = []
    trend_assets_used = []

    for universe_path in args.universes:
        logger.info("Running Phase A.7 trend overlay for %s", universe_path)
        inputs = load_inputs(args.config, universe_path, args.trend_assets)
        trend_assets_used = sorted(set(trend_assets_used) | set(inputs["trend_assets"]))
        paths = {}
        paths.update(build_vol_weight_paths(inputs))
        paths.update(build_trend_weight_paths(inputs, args.target_vol, args.gross_cap, args.vol_window))

        returns_by_name = {}
        nav_by_name = {}
        for name, path in paths.items():
            row, returns, nav = backtest_path(inputs, name, path)
            metric_rows.append(row)
            returns_by_name[name] = returns
            nav_by_name[name] = nav

        for vol_name in [name for name, path in paths.items() if path["sleeve_type"] == "volatility"]:
            for trend_name in [name for name, path in paths.items() if path["sleeve_type"] == "trend"]:
                for vol_weight, trend_weight in BLEND_WEIGHTS:
                    row, combined_returns = combine_return_series(
                        inputs,
                        vol_name,
                        trend_name,
                        returns_by_name[vol_name],
                        returns_by_name[trend_name],
                        vol_weight,
                        trend_weight,
                    )
                    blend_rows.append(row)
                    returns_by_name[row["sleeve"]] = combined_returns
                    nav_by_name[row["sleeve"]] = (1.0 + combined_returns).cumprod() * inputs["base_config"].portfolio.initial_capital

        benchmarks = pd.DataFrame(benchmark_rows(inputs))
        benchmark_rows_all.extend(benchmarks.to_dict("records"))
        corr, crisis_corr, rolling_corr = correlation_reports(inputs, returns_by_name)
        corr_frames.append(corr)
        crisis_corr_frames.append(crisis_corr)
        rolling_corr_frames.append(rolling_corr)
        period_frames.append(period_drawdown_rows(inputs, nav_by_name))
        gate_frames.append(gate_report(pd.DataFrame([row for row in blend_rows if row["universe"] == inputs["universe_config"].name]), benchmarks, crisis_corr))

    metrics = pd.DataFrame(metric_rows)
    blend_metrics = pd.DataFrame(blend_rows)
    benchmarks = pd.DataFrame(benchmark_rows_all)
    corr = pd.concat(corr_frames, ignore_index=True) if corr_frames else pd.DataFrame()
    crisis_corr = pd.concat(crisis_corr_frames, ignore_index=True) if crisis_corr_frames else pd.DataFrame()
    rolling_corr = pd.concat(rolling_corr_frames, ignore_index=True) if rolling_corr_frames else pd.DataFrame()
    period_dd = pd.concat(period_frames, ignore_index=True) if period_frames else pd.DataFrame()
    gate = pd.concat(gate_frames, ignore_index=True) if gate_frames else pd.DataFrame()

    metrics.to_csv(reports_dir / "phase_a7_metrics.csv", index=False)
    blend_metrics.to_csv(reports_dir / "phase_a7_blend_metrics.csv", index=False)
    benchmarks.to_csv(reports_dir / "phase_a7_benchmarks.csv", index=False)
    corr.to_csv(reports_dir / "phase_a7_correlation_report.csv", index=False)
    crisis_corr.to_csv(reports_dir / "phase_a7_crisis_corr_report.csv", index=False)
    rolling_corr.to_csv(reports_dir / "phase_a7_rolling_corr_report.csv", index=False)
    period_dd.to_csv(reports_dir / "phase_a7_period_drawdowns.csv", index=False)
    gate.to_csv(reports_dir / "phase_a7_gate_report.csv", index=False)
    (reports_dir / "phase_a7_trend_results.md").write_text(
        render_report(metrics, blend_metrics, benchmarks, corr, crisis_corr, gate, period_dd, trend_assets_used)
    )
    logger.info("Saved Phase A.7 artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
