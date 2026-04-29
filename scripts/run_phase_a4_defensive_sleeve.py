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
DEF_SPECS = [
    ("defensive_stability_top_30_equal_weight", 30, None),
    ("defensive_stability_top_50_equal_weight", 50, None),
    ("defensive_stability_top_30_beta_0_6", 30, 0.6),
    ("defensive_stability_top_50_beta_0_6", 50, 0.6),
    ("defensive_stability_top_30_beta_0_8", 30, 0.8),
    ("defensive_stability_top_50_beta_0_8", 50, 0.8),
]
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
        cache_key=universe_config.name,
    )
    fund_features = FundamentalFeatureGenerator(data_dict, fundamentals_df=fundamentals).generate()
    if not fund_features.empty:
        stock_features = stock_features.join(fund_features, how="left")

    data_audit = audit_feature_availability(stock_features, list(universe_config.tickers.keys()))
    return {
        "base_config": base_config,
        "universe_config": universe_config,
        "prices": prices_dict["adj_close"].ffill(),
        "stock_features": stock_features,
        "vol_scores": compute_volatility_score_frame(stock_features),
        "defensive_scores": compute_defensive_stability_score_frame(stock_features, sector_mapping),
        "pit_mask": pit_mask,
        "sector_mapping": sector_mapping,
        "data_audit": data_audit,
    }


def audit_feature_availability(panel: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    fields = [
        "roe",
        "eps_growth_yoy",
        "pe_ratio",
        "pb_ratio",
        "debt_to_assets",
        "debt_to_equity",
        "interest_coverage",
        "ocf_to_net_income",
        "accruals_proxy",
        "gross_margin",
        "asset_turnover",
        "beta_to_spy_63d",
        "downside_vol_63d",
        "max_drawdown_63d",
        "mom_stability_3m",
    ]
    rows = []
    ticker_set = set(tickers)
    panel = panel[panel.index.get_level_values("ticker").isin(ticker_set)]
    for field in fields:
        if field not in panel.columns:
            rows.append({"feature": field, "coverage_pct": 0.0, "ticker_coverage_pct": 0.0})
            continue
        values = panel[field].replace([np.inf, -np.inf], np.nan)
        rows.append(
            {
                "feature": field,
                "coverage_pct": float(values.notna().mean()),
                "ticker_coverage_pct": float(values.dropna().index.get_level_values("ticker").nunique() / max(len(tickers), 1)),
            }
        )
    unavailable = ["analyst_revisions"]
    rows.extend({"feature": feature, "coverage_pct": 0.0, "ticker_coverage_pct": 0.0} for feature in unavailable)
    return pd.DataFrame(rows)


def _sector_zscore(panel: pd.DataFrame, col: str, sector_mapping: dict) -> pd.Series:
    tickers = panel.index.get_level_values("ticker")
    sectors = pd.Series(tickers.map(sector_mapping), index=panel.index)
    values = panel[col].astype(float).replace([np.inf, -np.inf], np.nan)
    mean = values.groupby([panel.index.get_level_values("date"), sectors]).transform("mean")
    std = values.groupby([panel.index.get_level_values("date"), sectors]).transform("std").replace(0.0, np.nan)
    return ((values - mean) / std).replace([np.inf, -np.inf], np.nan)


def _rolling_stability(series: pd.Series, window: int = 252, min_periods: int = 63) -> pd.Series:
    clean = series.replace([np.inf, -np.inf], np.nan)
    return -clean.groupby(level="ticker").rolling(window, min_periods=min_periods).std().droplevel(0)


def compute_defensive_stability_score_frame(panel: pd.DataFrame, sector_mapping: dict) -> pd.DataFrame:
    defensive = pd.DataFrame(index=panel.index)

    if "roe" in panel.columns:
        roe = panel["roe"].replace([np.inf, -np.inf], np.nan).clip(-1.0, 1.0)
        defensive["profitability_survival"] = roe
        defensive["profitability_stability"] = _rolling_stability(roe)
    else:
        defensive["profitability_survival"] = np.nan
        defensive["profitability_stability"] = np.nan

    if "eps_growth_yoy" in panel.columns:
        eps_growth = panel["eps_growth_yoy"].replace([np.inf, -np.inf], np.nan).clip(-5.0, 5.0)
        defensive["earnings_stability"] = _rolling_stability(eps_growth)
        defensive["earnings_survival"] = -eps_growth.clip(upper=0.0).abs()
    else:
        defensive["earnings_stability"] = np.nan
        defensive["earnings_survival"] = np.nan

    if "pb_ratio" in panel.columns:
        pb = panel["pb_ratio"].replace([np.inf, -np.inf], np.nan)
        defensive["valuation_buffer_pb"] = -np.log1p(pb.clip(lower=0.0, upper=50.0))
    else:
        defensive["valuation_buffer_pb"] = np.nan

    if "pe_ratio" in panel.columns:
        pe = panel["pe_ratio"].replace([np.inf, -np.inf], np.nan)
        defensive["valuation_buffer_pe"] = -np.log1p(pe.where(pe > 0.0).clip(upper=100.0))
    else:
        defensive["valuation_buffer_pe"] = np.nan

    if "debt_to_assets" in panel.columns:
        defensive["low_debt_to_assets"] = -panel["debt_to_assets"].replace([np.inf, -np.inf], np.nan).clip(-1.0, 3.0)
    else:
        defensive["low_debt_to_assets"] = np.nan

    if "debt_to_equity" in panel.columns:
        defensive["low_debt_to_equity"] = -panel["debt_to_equity"].replace([np.inf, -np.inf], np.nan).clip(-5.0, 10.0)
    else:
        defensive["low_debt_to_equity"] = np.nan

    if "interest_coverage" in panel.columns:
        defensive["interest_coverage_survival"] = np.log1p(
            panel["interest_coverage"].replace([np.inf, -np.inf], np.nan).clip(lower=0.0, upper=100.0)
        )
    else:
        defensive["interest_coverage_survival"] = np.nan

    if "ocf_to_net_income" in panel.columns:
        defensive["cashflow_quality"] = panel["ocf_to_net_income"].replace([np.inf, -np.inf], np.nan).clip(-5.0, 5.0)
    else:
        defensive["cashflow_quality"] = np.nan

    if "accruals_proxy" in panel.columns:
        defensive["low_accruals"] = -panel["accruals_proxy"].replace([np.inf, -np.inf], np.nan).abs().clip(upper=1.0)
    else:
        defensive["low_accruals"] = np.nan

    if "gross_margin" in panel.columns:
        gross_margin = panel["gross_margin"].replace([np.inf, -np.inf], np.nan).clip(-1.0, 1.0)
        defensive["gross_margin_survival"] = gross_margin
        defensive["gross_margin_stability"] = _rolling_stability(gross_margin)
    else:
        defensive["gross_margin_survival"] = np.nan
        defensive["gross_margin_stability"] = np.nan

    if "asset_turnover" in panel.columns:
        defensive["asset_efficiency"] = panel["asset_turnover"].replace([np.inf, -np.inf], np.nan).clip(-5.0, 5.0)
    else:
        defensive["asset_efficiency"] = np.nan

    downside = panel.get("downside_vol_63d", pd.Series(np.nan, index=panel.index))
    drawdown = panel.get("max_drawdown_63d", pd.Series(np.nan, index=panel.index))
    beta = panel.get("beta_to_spy_63d", pd.Series(np.nan, index=panel.index))
    consistency = panel.get("mom_stability_3m", pd.Series(np.nan, index=panel.index))

    defensive["low_downside_vol"] = -downside
    defensive["low_max_drawdown"] = drawdown
    defensive["beta_survivability"] = -((beta - 0.65).abs())
    defensive["return_stability"] = -((consistency - 0.52).abs())

    rank_frames = []
    for col in defensive.columns:
        defensive[f"{col}_sector_z"] = _sector_zscore(defensive, col, sector_mapping)
        rank_frames.append(
            defensive.groupby(level="date")[f"{col}_sector_z"].rank(ascending=True, pct=True).rename(f"rank_{col}")
        )

    result = pd.DataFrame(index=panel.index)
    result["defensive_stability_score"] = pd.concat(rank_frames, axis=1).mean(axis=1, skipna=True)
    result["defensive_stability_score_rank"] = result.groupby(level="date")["defensive_stability_score"].rank(pct=True)
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


def latest_feature(panel: pd.DataFrame, date: pd.Timestamp, col: str) -> pd.Series:
    if col not in panel.columns:
        return pd.Series(dtype=float)
    dates = panel.index.levels[0]
    idx = dates.get_indexer([date], method="ffill")[0]
    if idx < 0:
        return pd.Series(dtype=float)
    return panel.xs(dates[idx], level="date")[col].replace([np.inf, -np.inf], np.nan).dropna()


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


def beta_target_weights(selected: list[str], betas: pd.Series, target_beta: float, max_weight: float = 0.15) -> pd.Series:
    selected = [ticker for ticker in selected if ticker in betas.index and np.isfinite(betas.loc[ticker])]
    if not selected:
        return pd.Series(dtype=float)
    beta = betas.reindex(selected).astype(float).clip(-1.0, 3.0)
    base = pd.Series(1.0 / len(selected), index=selected)
    current_beta = float((base * beta).sum())
    beta_range = float(beta.max() - beta.min())
    if beta_range < 1e-6 or abs(current_beta - target_beta) < 1e-6:
        return base

    low_beta = beta.sort_values(ascending=True)
    high_beta = beta.sort_values(ascending=False)
    weights = base.copy()
    if current_beta > target_beta:
        donors = high_beta.index.tolist()
        receivers = low_beta.index.tolist()
    else:
        donors = low_beta.index.tolist()
        receivers = high_beta.index.tolist()

    for donor in donors:
        for receiver in receivers:
            if donor == receiver:
                continue
            current_beta = float((weights * beta).sum())
            gap = current_beta - target_beta
            if abs(gap) < 1e-4:
                break
            beta_delta = float(beta.loc[donor] - beta.loc[receiver])
            if abs(beta_delta) < 1e-6 or np.sign(gap) != np.sign(beta_delta):
                continue
            movable = min(weights.loc[donor], max_weight - weights.loc[receiver], abs(gap / beta_delta))
            if movable <= 0:
                continue
            weights.loc[donor] -= movable
            weights.loc[receiver] += movable
        if abs(float((weights * beta).sum()) - target_beta) < 1e-4:
            break

    weights = weights.clip(lower=0.0, upper=max_weight)
    total = float(weights.sum())
    return weights / total if total > 0 else base


def build_sleeve_weight_paths(inputs: dict) -> dict[str, dict]:
    config = inputs["base_config"]
    rebalances = rebalance_dates(config, inputs["prices"])
    sector_mapping = inputs["sector_mapping"]
    paths: dict[str, dict] = {}

    for name, n in VOL_SPECS:
        weights_by_date = {}
        selected_by_date = {}
        realized_beta_by_date = {}
        for date in rebalances:
            candidates = active_tickers(inputs, date)
            scores = latest_scores(inputs["vol_scores"], date, "volatility_score").reindex(candidates)
            selected = select_top(scores, n)
            weights = equal_weights(selected)
            betas = latest_feature(inputs["stock_features"], date, "beta_to_spy_63d")
            weights_by_date[date] = weights
            selected_by_date[date] = selected
            realized_beta_by_date[date] = float((weights * betas.reindex(weights.index).fillna(1.0)).sum()) if not weights.empty else np.nan
        paths[name] = {
            "weights": weights_by_date,
            "selected": selected_by_date,
            "realized_beta": realized_beta_by_date,
            "sleeve_type": "volatility",
        }

    for name, n, beta_target in DEF_SPECS:
        weights_by_date = {}
        selected_by_date = {}
        realized_beta_by_date = {}
        for date in rebalances:
            candidates = active_tickers(inputs, date)
            scores = latest_scores(inputs["defensive_scores"], date, "defensive_stability_score").reindex(candidates)
            selected = select_sector_balanced(scores, n, sector_mapping)
            betas = latest_feature(inputs["stock_features"], date, "beta_to_spy_63d").reindex(selected)
            if beta_target is None:
                weights = equal_weights(selected)
            else:
                weights = beta_target_weights(selected, betas, beta_target)
            weights_by_date[date] = weights
            selected_by_date[date] = selected
            realized_beta_by_date[date] = float((weights * betas.reindex(weights.index).fillna(1.0)).sum()) if not weights.empty else np.nan
        paths[name] = {
            "weights": weights_by_date,
            "selected": selected_by_date,
            "realized_beta": realized_beta_by_date,
            "target_beta": beta_target,
            "sleeve_type": "defensive",
        }

    return paths


def combine_weight_paths(path_a: dict, path_b: dict, weight_a: float, weight_b: float) -> dict:
    weights = {}
    selected = {}
    realized_beta = {}
    for date in sorted(set(path_a["weights"]).intersection(path_b["weights"])):
        wa = path_a["weights"][date] * weight_a
        wb = path_b["weights"][date] * weight_b
        idx = wa.index.union(wb.index)
        weights[date] = wa.reindex(idx, fill_value=0.0) + wb.reindex(idx, fill_value=0.0)
        selected[date] = list(set(path_a["selected"][date]) | set(path_b["selected"][date]))
        ba = path_a.get("realized_beta", {}).get(date, np.nan)
        bb = path_b.get("realized_beta", {}).get(date, np.nan)
        realized_beta[date] = weight_a * ba + weight_b * bb if np.isfinite(ba) and np.isfinite(bb) else np.nan
    return {"weights": weights, "selected": selected, "realized_beta": realized_beta, "sleeve_type": "blend"}


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
    realized_betas = pd.Series(path.get("realized_beta", {}), dtype=float)
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
        "target_beta": path.get("target_beta", np.nan),
        "avg_realized_beta": float(realized_betas.mean()) if not realized_betas.dropna().empty else np.nan,
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
    def_names = [n for n, p in paths.items() if p["sleeve_type"] == "defensive"]
    for vol_name in vol_names:
        for def_name in def_names:
            ticker_overlaps = []
            sector_overlaps = []
            dates = sorted(set(paths[vol_name]["selected"]).intersection(paths[def_name]["selected"]))
            for date in dates:
                vol_sel = set(paths[vol_name]["selected"][date])
                def_sel = set(paths[def_name]["selected"][date])
                if vol_sel and def_sel:
                    ticker_overlaps.append(len(vol_sel & def_sel) / min(len(vol_sel), len(def_sel)))
                vol_sec = {sector_mapping.get(t, "_other") for t in vol_sel}
                def_sec = {sector_mapping.get(t, "_other") for t in def_sel}
                if vol_sec and def_sec:
                    sector_overlaps.append(len(vol_sec & def_sec) / min(len(vol_sec), len(def_sec)))
            rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "defensive_sleeve": def_name,
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
    drawdown = prices[benchmark] / prices[benchmark].expanding().max() - 1.0
    crisis_dates = drawdown[drawdown <= -0.15].index
    for vol_name in [n for n in names if n.startswith("vol_")]:
        for def_name in [n for n in names if n.startswith("defensive_")]:
            pair = aligned[[vol_name, def_name]].dropna()
            rolling = pair[vol_name].rolling(252, min_periods=63).corr(pair[def_name])
            crisis_pair = pair.loc[pair.index.intersection(crisis_dates)]
            rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "defensive_sleeve": def_name,
                    "full_correlation": float(pair[vol_name].corr(pair[def_name])) if len(pair) > 2 else np.nan,
                    "avg_rolling_252d_correlation": float(rolling.mean()) if not rolling.dropna().empty else np.nan,
                    "crisis_correlation": float(crisis_pair[vol_name].corr(crisis_pair[def_name])) if len(crisis_pair) > 2 else np.nan,
                }
            )
    return rows, corr_matrix


def render_report(
    sleeve_metrics: pd.DataFrame,
    blend_metrics: pd.DataFrame,
    correlations: pd.DataFrame,
    overlaps: pd.DataFrame,
    benchmarks: pd.DataFrame,
    data_audit: pd.DataFrame,
) -> str:
    lines = [
        "# Phase A.4 Defensive Sleeve Results",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Sleeve 1 unchanged: existing `volatility_score`.",
        "- Sleeve 2 rebuilt as `defensive_stability_score`: stability + survivability, not growth/momentum.",
        "- Defensive sleeve tests include equal weight and beta-targeted weights.",
        "- RL disabled.",
        "",
        "## Goal",
        "",
        "Create a more orthogonal alpha stream by changing the economic exposure of Sleeve 2 and controlling its beta inside the sleeve.",
        "",
        "## Data Availability",
        "",
        data_audit.to_markdown(index=False, floatfmt=".4f") if not data_audit.empty else "No data audit rows.",
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
            & (correlations["crisis_correlation"] < 0.6)
        ]
        lines.append(f"- sp500 CAGR >= equal-weight, Sharpe > equal-weight, MaxDD < 40%: {'PASS' if not candidates.empty else 'FAIL'}")
        lines.append(f"- sp500 vol-defensive full corr < 0.5 and crisis corr < 0.6: {'PASS' if not corr_pass.empty else 'FAIL'}")
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
            "- The score intentionally avoids positive growth and momentum as primary drivers.",
            "- True balance-sheet debt, cash-flow accruals, margins, and analyst revisions are unavailable in the current cached feature set.",
            "- Beta targeting is applied inside the defensive sleeve after sector-balanced selection.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.4 defensive sleeve experiment")
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
    audit_rows = []

    for universe_path in args.universes:
        logger.info("Running Phase A.4 defensive sleeve for %s", universe_path)
        inputs = load_inputs(args.config, universe_path)
        audit = inputs["data_audit"].copy()
        audit.insert(0, "universe", inputs["universe_config"].name)
        audit_rows.append(audit)

        paths = build_sleeve_weight_paths(inputs)
        returns_by_name = {}
        for name, path in paths.items():
            row, returns = backtest_weight_path(inputs, name, path)
            sleeve_rows.append(row)
            returns_by_name[name] = returns

        for vol_name in [n for n, p in paths.items() if p["sleeve_type"] == "volatility"]:
            for def_name in [n for n, p in paths.items() if p["sleeve_type"] == "defensive"]:
                for vol_weight, def_weight in BLEND_WEIGHTS:
                    blend_name = f"blend_{vol_name}_{def_name}_{int(vol_weight * 100)}_{int(def_weight * 100)}"
                    blend_path = combine_weight_paths(paths[vol_name], paths[def_name], vol_weight, def_weight)
                    row, returns = backtest_weight_path(inputs, blend_name, blend_path)
                    row["vol_sleeve"] = vol_name
                    row["defensive_sleeve"] = def_name
                    row["vol_weight"] = vol_weight
                    row["defensive_weight"] = def_weight
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
    data_audit = pd.concat(audit_rows, ignore_index=True) if audit_rows else pd.DataFrame()
    corr_matrix = pd.concat(corr_matrices, ignore_index=True) if corr_matrices else pd.DataFrame()

    sleeve_metrics.to_csv(reports_dir / "phase_a4_sleeve_metrics.csv", index=False)
    blend_metrics.to_csv(reports_dir / "phase_a4_blend_metrics.csv", index=False)
    correlations.to_csv(reports_dir / "phase_a4_correlation_matrix.csv", index=False)
    overlaps.to_csv(reports_dir / "phase_a4_overlap_report.csv", index=False)
    corr_matrix.to_csv(reports_dir / "phase_a4_sleeve_return_correlation_matrix.csv", index=False)
    benchmarks.to_csv(reports_dir / "phase_a4_benchmarks.csv", index=False)
    data_audit.to_csv(reports_dir / "phase_a4_data_availability.csv", index=False)
    (reports_dir / "phase_a4_defensive_sleeve_results.md").write_text(
        render_report(sleeve_metrics, blend_metrics, correlations, overlaps, benchmarks, data_audit)
    )
    logger.info("Saved Phase A.4 artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
