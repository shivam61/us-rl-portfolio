import argparse
import copy
import logging
import time
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("src.backtest.walk_forward").setLevel(logging.WARNING)
logging.getLogger("src.risk.risk_engine").setLevel(logging.WARNING)

PERIODS = [
    ("2006_2009", "2006-01-01", "2010-01-01"),
    ("2010_2014", "2010-01-01", "2015-01-01"),
    ("2015_2019", "2015-01-01", "2020-01-01"),
    ("2020_2022", "2020-01-01", "2023-01-01"),
    ("2023_2026", "2023-01-01", "2027-01-01"),
]

SELECTION_SPECS = [
    ("top_10", 10, False),
    ("top_20", 20, False),
    ("top_30", 30, False),
    ("top_50", 50, False),
    ("sector_balanced_top_20", 20, True),
    ("sector_balanced_top_50", 50, True),
]

DIRECTIONS = {
    "long_high_vol_rebound": "volatility_score",
    "long_low_vol_quality": "low_volatility_score",
}


def load_inputs(config_path: str, universe_path: str) -> dict:
    base_config, universe_config = load_config(config_path, universe_path)
    if not universe_config.is_static and universe_config.pit_mask_path:
        pit_mask = pd.read_parquet(universe_config.pit_mask_path)
    else:
        pit_mask = None

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
    scores = compute_volatility_score_frame(stock_features)
    scores["low_volatility_score"] = 1.0 - scores["volatility_score_rank"]

    return {
        "config_path": config_path,
        "universe_path": universe_path,
        "base_config": base_config,
        "universe_config": universe_config,
        "stock_features": stock_features,
        "macro_features": macro_features,
        "targets": targets,
        "scores": scores,
        "prices_dict": prices_dict,
        "pit_mask": pit_mask,
        "sector_mapping": sector_mapping,
    }


def join_scores_targets(inputs: dict) -> pd.DataFrame:
    panel = inputs["scores"].join(inputs["targets"][["target_fwd_ret"]], how="left")
    panel = panel.sort_index()
    return panel


def _ic_summary(values: list[float]) -> tuple[float, float, float, int]:
    series = pd.Series(values, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    if series.empty:
        return np.nan, np.nan, np.nan, 0
    return (
        float(series.mean()),
        float(series.mean() / (series.std(ddof=0) + 1e-9)),
        float((series > 0).mean()),
        int(len(series)),
    )


def _period_for(date: pd.Timestamp) -> str | None:
    for name, start, end in PERIODS:
        if pd.Timestamp(start) <= date < pd.Timestamp(end):
            return name
    return None


def classify_regimes(inputs: dict) -> pd.DataFrame:
    dates = inputs["prices_dict"]["adj_close"].index
    benchmark = inputs["universe_config"].benchmark
    vix_proxy = inputs["universe_config"].vix_proxy
    prices = inputs["prices_dict"]["adj_close"].reindex(dates).ffill()
    spy = prices[benchmark]
    if vix_proxy in prices.columns:
        vix = prices[vix_proxy]
    else:
        vix = pd.Series(np.nan, index=dates)

    spy_21d = spy.pct_change(21)
    spy_63d = spy.pct_change(63)
    spy_200d_ma = spy.rolling(200, min_periods=100).mean()
    drawdown = spy / spy.expanding().max() - 1.0
    vix_rank = vix.rolling(756, min_periods=126).rank(pct=True)

    regimes = pd.DataFrame(index=dates)
    regimes["low_vix"] = vix_rank <= 0.35
    regimes["high_vix"] = vix_rank >= 0.80
    regimes["crash"] = (spy_21d <= -0.10) | (drawdown <= -0.15)
    regimes["recovery"] = (spy_21d >= 0.06) & (drawdown.shift(21) <= -0.10)
    regimes["trending"] = (spy_63d >= 0.08) & (spy >= spy_200d_ma)
    regimes["sideways"] = spy_63d.abs() <= 0.04
    return regimes.fillna(False)


def evaluate_ic_by_period(inputs: dict, panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    universe = inputs["universe_config"].name
    for direction, score_col in DIRECTIONS.items():
        by_period: dict[str, list[float]] = {name: [] for name, _, _ in PERIODS}
        spreads: dict[str, list[float]] = {name: [] for name, _, _ in PERIODS}
        for date, group in panel.groupby(level="date"):
            period = _period_for(pd.Timestamp(date))
            if period is None:
                continue
            valid = group[[score_col, "target_fwd_ret"]].dropna()
            if len(valid) < 10:
                continue
            ic = valid[score_col].rank().corr(valid["target_fwd_ret"].rank())
            if pd.notna(ic):
                by_period[period].append(float(ic))
            q80 = valid[score_col].quantile(0.8)
            q20 = valid[score_col].quantile(0.2)
            spread = valid.loc[valid[score_col] >= q80, "target_fwd_ret"].mean() - valid.loc[
                valid[score_col] <= q20, "target_fwd_ret"
            ].mean()
            if pd.notna(spread):
                spreads[period].append(float(spread))

        for period, values in by_period.items():
            mean_ic, ic_sharpe, pct_positive, n_dates = _ic_summary(values)
            mean_spread = float(pd.Series(spreads[period]).mean()) if spreads[period] else np.nan
            rows.append(
                {
                    "universe": universe,
                    "direction": direction,
                    "period": period,
                    "mean_ic": mean_ic,
                    "ic_sharpe": ic_sharpe,
                    "pct_positive_ic": pct_positive,
                    "mean_top_bottom_spread": mean_spread,
                    "n_dates": n_dates,
                }
            )
    return pd.DataFrame(rows)


def evaluate_ic_by_regime(inputs: dict, panel: pd.DataFrame, regimes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    universe = inputs["universe_config"].name
    for direction, score_col in DIRECTIONS.items():
        buckets = {name: {"ic": [], "spread": []} for name in regimes.columns}
        for date, group in panel.groupby(level="date"):
            regime_date = regimes.index[regimes.index.get_indexer([date], method="ffill")[0]]
            active_regimes = [name for name in regimes.columns if bool(regimes.loc[regime_date, name])]
            if not active_regimes:
                continue
            valid = group[[score_col, "target_fwd_ret"]].dropna()
            if len(valid) < 10:
                continue
            ic = valid[score_col].rank().corr(valid["target_fwd_ret"].rank())
            q80 = valid[score_col].quantile(0.8)
            q20 = valid[score_col].quantile(0.2)
            spread = valid.loc[valid[score_col] >= q80, "target_fwd_ret"].mean() - valid.loc[
                valid[score_col] <= q20, "target_fwd_ret"
            ].mean()
            for regime in active_regimes:
                if pd.notna(ic):
                    buckets[regime]["ic"].append(float(ic))
                if pd.notna(spread):
                    buckets[regime]["spread"].append(float(spread))

        for regime, values in buckets.items():
            mean_ic, ic_sharpe, pct_positive, n_dates = _ic_summary(values["ic"])
            rows.append(
                {
                    "universe": universe,
                    "direction": direction,
                    "regime": regime,
                    "mean_ic": mean_ic,
                    "ic_sharpe": ic_sharpe,
                    "pct_positive_ic": pct_positive,
                    "mean_top_bottom_spread": float(pd.Series(values["spread"]).mean()) if values["spread"] else np.nan,
                    "n_dates": n_dates,
                }
            )
    return pd.DataFrame(rows)


def _sector_balanced_selection(scores: pd.Series, top_n: int, sector_mapping: dict) -> list[str]:
    ranked = scores.dropna().sort_values(ascending=False)
    if ranked.empty:
        return []
    per_sector_cap = max(1, int(np.ceil(top_n / max(1, len(set(sector_mapping.values()))))))
    selected = []
    counts: dict[str, int] = {}
    for ticker in ranked.index:
        sector = sector_mapping.get(ticker, "_other")
        if counts.get(sector, 0) >= per_sector_cap:
            continue
        selected.append(ticker)
        counts[sector] = counts.get(sector, 0) + 1
        if len(selected) >= top_n:
            break
    if len(selected) < top_n:
        for ticker in ranked.index:
            if ticker not in selected:
                selected.append(ticker)
            if len(selected) >= top_n:
                break
    return selected


def evaluate_selection_sweep(inputs: dict, panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    universe = inputs["universe_config"].name
    active_tickers = set(inputs["universe_config"].tickers.keys())
    sector_mapping = inputs["sector_mapping"]
    for direction, score_col in DIRECTIONS.items():
        for selection_name, top_n, sector_balanced in SELECTION_SPECS:
            returns = []
            benchmark_returns = []
            hit_rates = []
            for _, group in panel.groupby(level="date"):
                valid = group[[score_col, "target_fwd_ret"]].dropna()
                valid = valid.loc[valid.index.get_level_values("ticker").isin(active_tickers)]
                if len(valid) < max(10, min(top_n, 10)):
                    continue
                scores = valid[score_col].droplevel("date")
                labels = valid["target_fwd_ret"].droplevel("date")
                if sector_balanced:
                    selected = _sector_balanced_selection(scores, top_n, sector_mapping)
                else:
                    selected = scores.nlargest(top_n).index.tolist()
                selected = [ticker for ticker in selected if ticker in labels.index]
                if not selected:
                    continue
                top_ret = labels.loc[selected].mean()
                ew_ret = labels.mean()
                threshold = labels.quantile(0.8)
                returns.append(float(top_ret))
                benchmark_returns.append(float(ew_ret))
                hit_rates.append(float((labels.loc[selected] >= threshold).mean()))
            rets = pd.Series(returns, dtype=float)
            bench = pd.Series(benchmark_returns, dtype=float)
            rows.append(
                {
                    "universe": universe,
                    "direction": direction,
                    "selection": selection_name,
                    "top_n": top_n,
                    "sector_balanced": sector_balanced,
                    "mean_forward_return": float(rets.mean()) if not rets.empty else np.nan,
                    "mean_universe_forward_return": float(bench.mean()) if not bench.empty else np.nan,
                    "mean_excess_forward_return": float((rets - bench).mean()) if not rets.empty else np.nan,
                    "hit_rate_vs_top_quintile": float(pd.Series(hit_rates).mean()) if hit_rates else np.nan,
                    "n_rebalances": int(len(rets)),
                }
            )
    return pd.DataFrame(rows)


def _alpha_summary(diagnostics: dict) -> dict:
    rows = diagnostics.get("alpha_quality", [])
    if not rows:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "mean_spread": np.nan, "n_rebalances": 0}
    ic = pd.Series([row.get("rank_ic", np.nan) for row in rows], dtype=float).dropna()
    spread = pd.Series([row.get("spread", np.nan) for row in rows], dtype=float).dropna()
    return {
        "mean_ic": float(ic.mean()) if not ic.empty else np.nan,
        "ic_sharpe": float(ic.mean() / (ic.std(ddof=0) + 1e-9)) if not ic.empty else np.nan,
        "mean_spread": float(spread.mean()) if not spread.empty else np.nan,
        "n_rebalances": int(len(rows)),
    }


def _run_engine_variant(
    inputs: dict,
    *,
    name: str,
    score_col: str,
    use_optimizer: bool,
    use_risk_engine: bool,
    top_n_equal_weight: int | None,
) -> dict:
    config = copy.deepcopy(inputs["base_config"])
    config.rl.enabled = False
    config.intraperiod_risk.enabled = False
    engine = WalkForwardEngine(
        config=config,
        universe_config=inputs["universe_config"],
        stock_features=inputs["stock_features"],
        macro_features=inputs["macro_features"],
        targets=inputs["targets"],
        prices_dict=inputs["prices_dict"],
        pit_mask=inputs["pit_mask"],
    )
    history, trades, diagnostics = engine.run(
        use_optimizer=use_optimizer,
        use_risk_engine=use_risk_engine,
        top_n_equal_weight=top_n_equal_weight,
        alpha_score_provider=build_alpha_score_provider(inputs["scores"], score_col=score_col),
    )
    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    alpha = _alpha_summary(diagnostics)
    return {
        "universe": inputs["universe_config"].name,
        "variant": name,
        "direction": next(k for k, v in DIRECTIONS.items() if v == score_col),
        "top_n": top_n_equal_weight,
        "use_optimizer": use_optimizer,
        "use_risk_engine": use_risk_engine,
        "cagr": metrics.get("CAGR"),
        "sharpe": metrics.get("Sharpe"),
        "max_dd": metrics.get("Max Drawdown"),
        "volatility": metrics.get("Volatility"),
        "mean_ic": alpha["mean_ic"],
        "ic_sharpe": alpha["ic_sharpe"],
        "mean_spread": alpha["mean_spread"],
        "n_rebalances": alpha["n_rebalances"],
        "trade_count": int(len(trades)) if trades is not None else 0,
    }


def _benchmark_rows(inputs: dict) -> list[dict]:
    config = inputs["base_config"]
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    prices = inputs["prices_dict"]["adj_close"].ffill()
    benchmark = inputs["universe_config"].benchmark
    spy = prices[benchmark].loc[start:].dropna()
    rows = []
    if len(spy) > 2:
        spy_nav = spy / spy.iloc[0] * config.portfolio.initial_capital
        metrics = calculate_metrics(spy_nav)
        rows.append(
            {
                "universe": inputs["universe_config"].name,
                "variant": "spy_buy_hold",
                "direction": "benchmark",
                "top_n": np.nan,
                "use_optimizer": False,
                "use_risk_engine": False,
                "cagr": metrics.get("CAGR"),
                "sharpe": metrics.get("Sharpe"),
                "max_dd": metrics.get("Max Drawdown"),
                "volatility": metrics.get("Volatility"),
                "mean_ic": np.nan,
                "ic_sharpe": np.nan,
                "mean_spread": np.nan,
                "n_rebalances": 0,
                "trade_count": 0,
            }
        )
    ew = prices[list(inputs["universe_config"].tickers.keys())].loc[start:].pct_change().mean(axis=1).fillna(0.0)
    if not ew.empty:
        ew_nav = (1.0 + ew).cumprod() * config.portfolio.initial_capital
        metrics = calculate_metrics(ew_nav)
        rows.append(
            {
                "universe": inputs["universe_config"].name,
                "variant": "equal_weight_universe_daily",
                "direction": "benchmark",
                "top_n": np.nan,
                "use_optimizer": False,
                "use_risk_engine": False,
                "cagr": metrics.get("CAGR"),
                "sharpe": metrics.get("Sharpe"),
                "max_dd": metrics.get("Max Drawdown"),
                "volatility": metrics.get("Volatility"),
                "mean_ic": np.nan,
                "ic_sharpe": np.nan,
                "mean_spread": np.nan,
                "n_rebalances": 0,
                "trade_count": 0,
            }
        )
    return rows


def run_portfolio_backtests(inputs: dict) -> pd.DataFrame:
    rows = []
    for direction, score_col in DIRECTIONS.items():
        for top_n in [10, 20, 30, 50]:
            rows.append(
                _run_engine_variant(
                    inputs,
                    name=f"{direction}_top_{top_n}_ew",
                    score_col=score_col,
                    use_optimizer=False,
                    use_risk_engine=False,
                    top_n_equal_weight=top_n,
                )
            )
        rows.append(
            _run_engine_variant(
                inputs,
                name=f"{direction}_optimizer_no_risk",
                score_col=score_col,
                use_optimizer=True,
                use_risk_engine=False,
                top_n_equal_weight=None,
            )
        )
        rows.append(
            _run_engine_variant(
                inputs,
                name=f"{direction}_optimizer_risk",
                score_col=score_col,
                use_optimizer=True,
                use_risk_engine=True,
                top_n_equal_weight=None,
            )
        )
    rows.extend(_benchmark_rows(inputs))
    return pd.DataFrame(rows)


def directionality_summary(ic_df: pd.DataFrame, selection_df: pd.DataFrame, portfolio_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (universe, direction), period_rows in ic_df.groupby(["universe", "direction"]):
        sel_rows = selection_df[(selection_df["universe"] == universe) & (selection_df["direction"] == direction)]
        port_rows = portfolio_df[(portfolio_df["universe"] == universe) & (portfolio_df["direction"] == direction)]
        rows.append(
            {
                "universe": universe,
                "direction": direction,
                "mean_period_ic": period_rows["mean_ic"].mean(),
                "positive_period_count": int((period_rows["mean_ic"] > 0).sum()),
                "period_count": int(period_rows["mean_ic"].notna().sum()),
                "best_selection": sel_rows.sort_values("mean_excess_forward_return", ascending=False)["selection"].iloc[0]
                if not sel_rows.empty
                else None,
                "best_selection_excess_forward_return": sel_rows["mean_excess_forward_return"].max()
                if not sel_rows.empty
                else np.nan,
                "best_portfolio_variant": port_rows.sort_values(["sharpe", "cagr"], ascending=False)["variant"].iloc[0]
                if not port_rows.empty
                else None,
                "best_portfolio_cagr": port_rows["cagr"].max() if not port_rows.empty else np.nan,
                "best_portfolio_sharpe": port_rows["sharpe"].max() if not port_rows.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def _fmt(value: float, pct: bool = False) -> str:
    if pd.isna(value):
        return "nan"
    return f"{value:.2%}" if pct else f"{value:.3f}"


def render_report(
    *,
    universes: list[str],
    skipped: list[str],
    ic_period_df: pd.DataFrame,
    ic_regime_df: pd.DataFrame,
    selection_df: pd.DataFrame,
    direction_df: pd.DataFrame,
    portfolio_df: pd.DataFrame,
    wall_seconds: float,
) -> str:
    lines = [
        "# Phase A.1 Volatility Robustness",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- Universes tested: `{', '.join(universes)}`",
        f"- Optional universes skipped: `{', '.join(skipped) if skipped else 'none'}`",
        "- RL disabled for all portfolio tests.",
        "- Phase A remains conditionally passed: Mean IC passed previously; IC Sharpe remains below the original gate.",
        "- Current production alpha candidate: `volatility_score` / `volatility_only`.",
        f"- Wall time: {wall_seconds:.1f}s",
        "",
        "## Decision Frame",
        "",
        "- Do not continue momentum-first.",
        "- Treat high-vol/risk-premium and low-vol/quality directions as empirical alternatives.",
        "- Do not tune optimizer/RL if the volatility sleeve fails robustness on sp500 and recent periods.",
        "",
        "## Directionality",
        "",
        direction_df.to_markdown(index=False, floatfmt=".4f") if not direction_df.empty else "No directionality rows.",
        "",
        "## IC By Period",
        "",
        ic_period_df.to_markdown(index=False, floatfmt=".4f") if not ic_period_df.empty else "No IC period rows.",
        "",
        "## IC By Regime",
        "",
        ic_regime_df.to_markdown(index=False, floatfmt=".4f") if not ic_regime_df.empty else "No IC regime rows.",
        "",
        "## Selection Sweep",
        "",
        selection_df.to_markdown(index=False, floatfmt=".4f") if not selection_df.empty else "No selection rows.",
        "",
        "## Portfolio Backtests",
        "",
        portfolio_df.to_markdown(index=False, floatfmt=".4f") if not portfolio_df.empty else "No portfolio rows.",
        "",
        "## Success Criteria",
        "",
    ]

    high = ic_period_df[ic_period_df["direction"] == "long_high_vol_rebound"]
    for universe, rows in high.groupby("universe"):
        mean_ic = rows["mean_ic"].mean()
        positive_periods = int((rows["mean_ic"] > 0).sum())
        spread = rows["mean_top_bottom_spread"].mean()
        ic_gate = 0.03 if "sp100" in universe.lower() else 0.02
        lines.append(
            f"- `{universe}` high-vol direction mean period IC > {ic_gate:.2f}: "
            f"{'PASS' if mean_ic > ic_gate else 'FAIL'} ({_fmt(mean_ic)})"
        )
        lines.append(
            f"- `{universe}` positive in most periods: "
            f"{'PASS' if positive_periods >= 3 else 'FAIL'} ({positive_periods}/5)"
        )
        lines.append(
            f"- `{universe}` top-bottom spread > 1%: "
            f"{'PASS' if spread > 0.01 else 'FAIL'} ({_fmt(spread, pct=True)})"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Use `volatility_directionality.csv` to decide whether high-vol rebound or low-vol quality is stable enough to encode.",
            "- If sp500/recent-period robustness fails, stop production tuning and return to feature engineering: earnings quality, analyst revisions, value-quality, and regime-conditional factors.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.1 volatility robustness validation")
    parser.add_argument("--config", type=str, default="config/base.yaml")
    parser.add_argument(
        "--universes",
        nargs="+",
        default=[
            "config/universes/sp100.yaml",
            "config/universes/sp500.yaml",
            "config/universes/top_200_liquid.yaml",
        ],
    )
    args = parser.parse_args()

    started = time.perf_counter()
    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    tested = []
    skipped = []
    ic_period_frames = []
    ic_regime_frames = []
    selection_frames = []
    portfolio_frames = []

    def write_outputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        ic_period_df = pd.concat(ic_period_frames, ignore_index=True) if ic_period_frames else pd.DataFrame()
        ic_regime_df = pd.concat(ic_regime_frames, ignore_index=True) if ic_regime_frames else pd.DataFrame()
        selection_df = pd.concat(selection_frames, ignore_index=True) if selection_frames else pd.DataFrame()
        portfolio_df = pd.concat(portfolio_frames, ignore_index=True) if portfolio_frames else pd.DataFrame()
        direction_df = directionality_summary(ic_period_df, selection_df, portfolio_df)

        ic_period_df.to_csv(reports_dir / "volatility_ic_by_period.csv", index=False)
        ic_regime_df.to_csv(reports_dir / "volatility_ic_by_regime.csv", index=False)
        selection_df.to_csv(reports_dir / "volatility_selection_sweep.csv", index=False)
        direction_df.to_csv(reports_dir / "volatility_directionality.csv", index=False)
        portfolio_df.to_csv(reports_dir / "volatility_portfolio_backtests.csv", index=False)

        report = render_report(
            universes=tested,
            skipped=skipped,
            ic_period_df=ic_period_df,
            ic_regime_df=ic_regime_df,
            selection_df=selection_df,
            direction_df=direction_df,
            portfolio_df=portfolio_df,
            wall_seconds=time.perf_counter() - started,
        )
        (reports_dir / "phase_a1_volatility_robustness.md").write_text(report)
        return ic_period_df, ic_regime_df, selection_df, direction_df, portfolio_df

    for universe_path in args.universes:
        if not Path(universe_path).exists():
            logger.warning("Skipping missing universe config: %s", universe_path)
            skipped.append(universe_path)
            write_outputs()
            continue
        logger.info("Running Phase A.1 robustness for %s", universe_path)
        inputs = load_inputs(args.config, universe_path)
        tested.append(inputs["universe_config"].name)
        panel = join_scores_targets(inputs)
        regimes = classify_regimes(inputs)
        ic_period_frames.append(evaluate_ic_by_period(inputs, panel))
        ic_regime_frames.append(evaluate_ic_by_regime(inputs, panel, regimes))
        selection_frames.append(evaluate_selection_sweep(inputs, panel))
        portfolio_frames.append(run_portfolio_backtests(inputs))
        write_outputs()
        logger.info("Flushed Phase A.1 artifacts after %s", inputs["universe_config"].name)

    logger.info("Saved Phase A.1 report to %s", reports_dir / "phase_a1_volatility_robustness.md")


if __name__ == "__main__":
    main()
