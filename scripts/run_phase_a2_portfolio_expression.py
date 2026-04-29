import argparse
import logging
from pathlib import Path

import cvxpy as cp
import numpy as np
import pandas as pd

from src.alpha import compute_volatility_score_frame
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.stock_features import StockFeatureGenerator
from src.reporting.metrics import calculate_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TOP_N_SPECS = [
    ("top_10", 10, False),
    ("top_20", 20, False),
    ("top_30", 30, False),
    ("sector_balanced_top_20", 20, True),
    ("sector_balanced_top_30", 30, True),
]
VOL_METHODS = ["equal_weight", "inverse_vol", "alpha_over_vol"]
BETA_TARGETS = [1.0, 0.7, 0.5]
EXPOSURE_MULTIPLIERS = {
    "crash": 0.60,
    "high_vix": 0.70,
    "trending": 0.90,
    "normal": 1.00,
}


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
    scores = compute_volatility_score_frame(stock_features)

    return {
        "base_config": base_config,
        "universe_config": universe_config,
        "prices": prices_dict["adj_close"].ffill(),
        "scores": scores,
        "pit_mask": pit_mask,
        "sector_mapping": sector_mapping,
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


def latest_score(inputs: dict, date: pd.Timestamp) -> pd.Series:
    score_dates = inputs["scores"].index.levels[0]
    idx = score_dates.get_indexer([date], method="ffill")[0]
    if idx < 0:
        return pd.Series(dtype=float)
    score_date = score_dates[idx]
    return inputs["scores"].xs(score_date, level="date")["volatility_score"].dropna()


def rolling_beta_and_vol(prices: pd.DataFrame, benchmark: str, date: pd.Timestamp, window: int = 63) -> tuple[pd.Series, pd.Series]:
    returns = prices.pct_change()
    end_idx = returns.index.get_indexer([date], method="ffill")[0]
    if end_idx <= 0:
        return pd.Series(dtype=float), pd.Series(dtype=float)
    sample = returns.iloc[max(0, end_idx - window + 1) : end_idx + 1]
    bench = sample[benchmark].dropna()
    var = float(bench.var())
    vols = sample.std()
    if var <= 1e-12:
        beta = pd.Series(1.0, index=sample.columns)
    else:
        beta = sample.cov()[benchmark] / var
    return beta.replace([np.inf, -np.inf], np.nan), vols.replace([np.inf, -np.inf], np.nan)


def classify_regime(prices: pd.DataFrame, benchmark: str, vix_proxy: str, date: pd.Timestamp) -> str:
    idx = prices.index.get_indexer([date], method="ffill")[0]
    if idx < 1:
        return "normal"
    hist = prices.iloc[: idx + 1]
    spy = hist[benchmark].dropna()
    if len(spy) < 64:
        return "normal"
    spy_21d = spy.pct_change(21).iloc[-1]
    spy_63d = spy.pct_change(63).iloc[-1]
    drawdown = spy.iloc[-1] / spy.expanding().max().iloc[-1] - 1.0
    if vix_proxy in hist.columns and hist[vix_proxy].notna().sum() >= 126:
        vix_rank = hist[vix_proxy].rolling(756, min_periods=126).rank(pct=True).iloc[-1]
    else:
        vix_rank = np.nan

    if spy_21d <= -0.10 or drawdown <= -0.15:
        return "crash"
    if pd.notna(vix_rank) and vix_rank >= 0.80:
        return "high_vix"
    if spy_63d >= 0.08:
        return "trending"
    return "normal"


def select_tickers(scores: pd.Series, top_n: int, sector_balanced: bool, sector_mapping: dict) -> list[str]:
    ranked = scores.dropna().sort_values(ascending=False)
    if not sector_balanced:
        return ranked.head(top_n).index.tolist()

    sectors = sorted(set(sector_mapping.values()))
    per_sector_cap = max(1, int(np.ceil(top_n / max(len(sectors), 1))))
    selected: list[str] = []
    counts: dict[str, int] = {}
    for ticker in ranked.index:
        sector = sector_mapping.get(ticker, "_other")
        if counts.get(sector, 0) >= per_sector_cap:
            continue
        selected.append(ticker)
        counts[sector] = counts.get(sector, 0) + 1
        if len(selected) >= top_n:
            return selected

    for ticker in ranked.index:
        if ticker not in selected:
            selected.append(ticker)
        if len(selected) >= top_n:
            break
    return selected


def volatility_scaled_weights(
    selected: list[str],
    scores: pd.Series,
    vols: pd.Series,
    method: str,
    max_weight: float = 0.15,
) -> pd.Series:
    if not selected:
        return pd.Series(dtype=float)
    if method == "equal_weight":
        raw = pd.Series(1.0, index=selected)
    elif method == "inverse_vol":
        raw = 1.0 / vols.reindex(selected).replace(0.0, np.nan)
    elif method == "alpha_over_vol":
        alpha = scores.reindex(selected).clip(lower=0.0)
        raw = alpha / vols.reindex(selected).replace(0.0, np.nan)
    else:
        raise ValueError(f"Unknown vol method: {method}")
    raw = raw.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if raw.sum() <= 0:
        raw = pd.Series(1.0, index=selected)
    weights = raw / raw.sum()
    weights = weights.clip(upper=max_weight)
    if weights.sum() <= 0:
        return pd.Series(1.0 / len(selected), index=selected)
    return weights / weights.sum()


def beta_targeted_weights(
    selected: list[str],
    betas: pd.Series,
    target_beta: float,
    max_weight: float = 0.15,
) -> tuple[pd.Series, str]:
    if not selected:
        return pd.Series(dtype=float), "empty"
    beta = betas.reindex(selected).fillna(1.0).values.astype(float)
    n = len(selected)
    w = cp.Variable(n)
    objective = cp.Minimize(cp.square(beta @ w - target_beta))
    constraints = [cp.sum(w) == 1.0, w >= 0, w <= max_weight]
    problem = cp.Problem(objective, constraints)
    try:
        problem.solve(solver=cp.OSQP, warm_start=True, max_iter=10000)
    except Exception as exc:
        logger.warning("Beta targeting failed with exception: %s", exc)
        return pd.Series(1.0 / n, index=selected), "exception_equal_weight"
    if problem.status not in {"optimal", "optimal_inaccurate"} or w.value is None:
        return pd.Series(1.0 / n, index=selected), f"{problem.status}_equal_weight"
    weights = pd.Series(np.asarray(w.value).ravel(), index=selected).clip(lower=0.0)
    weights[weights < 1e-8] = 0.0
    if weights.sum() <= 0:
        return pd.Series(1.0 / n, index=selected), "zero_equal_weight"
    return weights / weights.sum(), str(problem.status)


def rebalance_dates(config, prices: pd.DataFrame) -> list[pd.Timestamp]:
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    end = pd.Timestamp(config.backtest.end_date) if config.backtest.end_date else prices.index[-1]
    raw_dates = pd.date_range(start=start, end=end, freq=config.backtest.rebalance_frequency)
    dates = []
    for date in raw_dates:
        idx = prices.index.get_indexer([date], method="bfill")[0]
        if idx >= 0:
            dates.append(prices.index[idx])
    return sorted(set(dates))


def run_research_backtest(inputs: dict, variant: dict) -> dict:
    config = inputs["base_config"]
    prices = inputs["prices"]
    benchmark = inputs["universe_config"].benchmark
    vix_proxy = inputs["universe_config"].vix_proxy
    returns = prices.pct_change().fillna(0.0)
    dates = [d for d in prices.index if d >= pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)]
    rebalances = set(rebalance_dates(config, prices))
    cost_rate = (config.portfolio.transaction_cost_bps + config.portfolio.slippage_bps) / 10000.0

    nav = config.portfolio.initial_capital
    nav_rows = []
    current_weights = pd.Series(dtype=float)
    realized_betas = []
    target_errors = []
    statuses = []
    multipliers = []
    turnover_sum = 0.0

    for date in dates:
        if date in rebalances:
            candidates = active_tickers(inputs, date)
            scores = latest_score(inputs, date).reindex(candidates).dropna()
            betas, vols = rolling_beta_and_vol(prices, benchmark, date)
            selected = select_tickers(
                scores,
                top_n=variant["top_n"],
                sector_balanced=variant["sector_balanced"],
                sector_mapping=inputs["sector_mapping"],
            )

            if variant["construction"] == "beta_target":
                base_weights, status = beta_targeted_weights(selected, betas, variant["target_beta"])
            else:
                base_weights = volatility_scaled_weights(selected, scores, vols, variant["vol_method"])
                status = "not_applicable"

            stock_beta = float((base_weights * betas.reindex(base_weights.index).fillna(1.0)).sum()) if not base_weights.empty else 0.0
            hedge_weight = 0.0
            if variant["construction"] == "spy_hedge":
                hedge_weight = float(variant["target_beta"] - stock_beta)

            regime = classify_regime(prices, benchmark, vix_proxy, date)
            multiplier = EXPOSURE_MULTIPLIERS[regime] if variant["use_exposure_scaling"] else 1.0
            target_weights = base_weights * multiplier
            if hedge_weight:
                target_weights.loc[benchmark] = target_weights.get(benchmark, 0.0) + hedge_weight * multiplier

            all_index = current_weights.index.union(target_weights.index)
            turnover = float((target_weights.reindex(all_index, fill_value=0.0) - current_weights.reindex(all_index, fill_value=0.0)).abs().sum())
            nav *= max(0.0, 1.0 - turnover * cost_rate)
            turnover_sum += turnover
            current_weights = target_weights

            realized_beta = float(stock_beta + hedge_weight) * multiplier
            realized_betas.append(realized_beta)
            target_errors.append(realized_beta - variant["target_beta"] * multiplier)
            statuses.append(status)
            multipliers.append(multiplier)

        day_ret = float((current_weights * returns.loc[date].reindex(current_weights.index).fillna(0.0)).sum()) if not current_weights.empty else 0.0
        nav *= 1.0 + day_ret
        nav_rows.append({"date": date, "nav": nav})

    history = pd.DataFrame(nav_rows).set_index("date")
    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    return {
        **variant,
        "universe": inputs["universe_config"].name,
        "cagr": metrics.get("CAGR", np.nan),
        "sharpe": metrics.get("Sharpe", np.nan),
        "max_dd": metrics.get("Max Drawdown", np.nan),
        "volatility": metrics.get("Volatility", np.nan),
        "avg_realized_beta": float(pd.Series(realized_betas).mean()) if realized_betas else np.nan,
        "avg_abs_beta_error": float(pd.Series(target_errors).abs().mean()) if target_errors else np.nan,
        "avg_exposure_multiplier": float(pd.Series(multipliers).mean()) if multipliers else np.nan,
        "turnover_sum": turnover_sum,
        "n_rebalances": len(realized_betas),
        "solver_statuses": ";".join(pd.Series(statuses).value_counts().astype(str).rename_axis("status").reset_index().apply(lambda r: f"{r['status']}={r['count']}", axis=1)) if statuses else "",
    }


def benchmark_rows(inputs: dict) -> list[dict]:
    config = inputs["base_config"]
    prices = inputs["prices"]
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    benchmark = inputs["universe_config"].benchmark
    rows = []
    spy = prices[benchmark].loc[start:].dropna()
    if len(spy) > 2:
        nav = spy / spy.iloc[0] * config.portfolio.initial_capital
        metrics = calculate_metrics(nav)
        rows.append({"universe": inputs["universe_config"].name, "variant": "spy_buy_hold", "cagr": metrics["CAGR"], "sharpe": metrics["Sharpe"], "max_dd": metrics["Max Drawdown"]})
    universe_rets = prices[list(inputs["universe_config"].tickers.keys())].loc[start:].pct_change().mean(axis=1).fillna(0.0)
    nav = (1.0 + universe_rets).cumprod() * config.portfolio.initial_capital
    metrics = calculate_metrics(nav)
    rows.append({"universe": inputs["universe_config"].name, "variant": "equal_weight_universe_daily", "cagr": metrics["CAGR"], "sharpe": metrics["Sharpe"], "max_dd": metrics["Max Drawdown"]})
    return rows


def build_variants() -> list[dict]:
    variants = []
    for selection, top_n, sector_balanced in TOP_N_SPECS:
        for vol_method in VOL_METHODS:
            variants.append(
                {
                    "variant": f"{selection}_{vol_method}_exposure_scaled",
                    "selection": selection,
                    "top_n": top_n,
                    "sector_balanced": sector_balanced,
                    "construction": "vol_scaling",
                    "vol_method": vol_method,
                    "target_beta": np.nan,
                    "use_exposure_scaling": True,
                }
            )
        for target_beta in BETA_TARGETS:
            variants.append(
                {
                    "variant": f"{selection}_beta_target_{target_beta:.1f}_exposure_scaled",
                    "selection": selection,
                    "top_n": top_n,
                    "sector_balanced": sector_balanced,
                    "construction": "beta_target",
                    "vol_method": "not_applicable",
                    "target_beta": target_beta,
                    "use_exposure_scaling": True,
                }
            )
            variants.append(
                {
                    "variant": f"{selection}_spy_hedge_beta_{target_beta:.1f}_exposure_scaled",
                    "selection": selection,
                    "top_n": top_n,
                    "sector_balanced": sector_balanced,
                    "construction": "spy_hedge",
                    "vol_method": "equal_weight",
                    "target_beta": target_beta,
                    "use_exposure_scaling": True,
                }
            )
    return variants


def render_report(results: pd.DataFrame, benchmarks: pd.DataFrame) -> str:
    lines = [
        "# Portfolio Expression Results",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Alpha definition unchanged: `volatility_score` high-vol/risk-premium direction.",
        "- RL disabled.",
        "- High-beta stocks are not removed; crash regimes scale exposure but do not disable the alpha.",
        "",
        "## Goal",
        "",
        "Convert the validated volatility alpha into an investable portfolio by testing beta-targeted weights, volatility-scaled weights, regime-aware exposure scaling, and explicit SPY hedges.",
        "",
        "## Expected Decision",
        "",
        "If a sp500 configuration reaches MaxDD < 40%, Sharpe above equal-weight, and CAGR close to simple Top-N, keep the standalone volatility sleeve as production-candidate. Otherwise move to multi-factor blending.",
        "",
        "## Best Variants",
        "",
    ]
    if not results.empty:
        best = results.sort_values(["universe", "sharpe", "cagr"], ascending=[True, False, False]).groupby("universe").head(8)
        lines.extend([best.to_markdown(index=False, floatfmt=".4f"), ""])
    lines.extend(["## Benchmarks", "", benchmarks.to_markdown(index=False, floatfmt=".4f") if not benchmarks.empty else "No benchmarks.", ""])

    sp500 = results[results["universe"].str.contains("sp500", case=False, na=False)]
    ew = benchmarks[(benchmarks["universe"].str.contains("sp500", case=False, na=False)) & (benchmarks["variant"] == "equal_weight_universe_daily")]
    lines.extend(["## Success Criteria", ""])
    if not sp500.empty and not ew.empty:
        ew_sharpe = float(ew.iloc[0]["sharpe"])
        candidates = sp500[(sp500["max_dd"] > -0.40) & (sp500["sharpe"] > ew_sharpe)]
        lines.append(f"- sp500 MaxDD < 40% and Sharpe > equal-weight: {'PASS' if not candidates.empty else 'FAIL'}")
        if not candidates.empty:
            lines.append(candidates.sort_values(["sharpe", "cagr"], ascending=False).head(5).to_markdown(index=False, floatfmt=".4f"))
        else:
            lines.append("- No sp500 variant met both hard gates in this run.")
    else:
        lines.append("- sp500 success criteria not evaluated.")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Long-only beta targeting reports realized beta error; do not accept a nominal target if realized beta misses materially.",
            "- SPY hedge variants allow negative benchmark exposure and are research-only until execution assumptions are finalized.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.2 portfolio-expression experiment")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml", "config/universes/sp500.yaml"])
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    variants = build_variants()
    result_rows = []
    benchmark_rows_all = []

    for universe_path in args.universes:
        logger.info("Running Phase A.2 portfolio expression for %s", universe_path)
        inputs = load_inputs(args.config, universe_path)
        benchmark_rows_all.extend(benchmark_rows(inputs))
        for idx, variant in enumerate(variants, start=1):
            logger.info("%s variant %d/%d: %s", inputs["universe_config"].name, idx, len(variants), variant["variant"])
            result_rows.append(run_research_backtest(inputs, variant))

    results = pd.DataFrame(result_rows)
    benchmarks = pd.DataFrame(benchmark_rows_all)
    beta_results = results[results["construction"] == "beta_target"].reset_index(drop=True)
    vol_results = results[results["construction"] == "vol_scaling"].reset_index(drop=True)
    hedge_results = results[results["construction"].isin(["beta_target", "spy_hedge"])].reset_index(drop=True)

    results.to_csv(reports_dir / "portfolio_expression_results.csv", index=False)
    beta_results.to_csv(reports_dir / "beta_targeting_results.csv", index=False)
    vol_results.to_csv(reports_dir / "vol_scaling_results.csv", index=False)
    hedge_results.to_csv(reports_dir / "hedge_comparison.csv", index=False)
    benchmarks.to_csv(reports_dir / "portfolio_expression_benchmarks.csv", index=False)
    (reports_dir / "portfolio_expression_results.md").write_text(render_report(results, benchmarks))
    logger.info("Saved Phase A.2 artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
