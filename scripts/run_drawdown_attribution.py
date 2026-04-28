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


def find_drawdown_periods(nav: pd.Series, top_n: int = 5) -> pd.DataFrame:
    running_max = nav.cummax()
    drawdown = nav / running_max - 1.0
    periods = []
    in_dd = False
    start = None
    trough = None
    trough_depth = 0.0

    for date, depth in drawdown.items():
        if not in_dd and depth < 0:
            in_dd = True
            start_idx = nav.index.get_loc(date) - 1
            start = nav.index[max(start_idx, 0)]
            trough = date
            trough_depth = float(depth)
        elif in_dd:
            if depth < trough_depth:
                trough = date
                trough_depth = float(depth)
            if depth >= 0:
                periods.append((start, trough, date, trough_depth))
                in_dd = False

    if in_dd and start is not None and trough is not None:
        periods.append((start, trough, nav.index[-1], trough_depth))

    rows = []
    for idx, (start, trough, recovery, depth) in enumerate(periods, start=1):
        rows.append(
            {
                "period_id": idx,
                "start_date": start,
                "trough_date": trough,
                "recovery_date": recovery,
                "duration_days": int((trough - start).days),
                "recovery_days": int((recovery - start).days),
                "depth": depth,
            }
        )
    return pd.DataFrame(rows).sort_values("depth").head(top_n).reset_index(drop=True)


def replay_positions(
    history: pd.DataFrame,
    trades: pd.DataFrame,
    prices: pd.DataFrame,
    initial_capital: float,
) -> tuple[pd.DataFrame, dict[pd.Timestamp, pd.Series]]:
    trades_by_date = {
        pd.Timestamp(date): grp
        for date, grp in trades.groupby("date")
    } if not trades.empty else {}
    holdings = pd.Series(dtype=float)
    cash = float(initial_capital)
    exposure_rows = []
    weights_by_date = {}

    for date in history.index:
        if date in trades_by_date:
            for _, trade in trades_by_date[date].iterrows():
                ticker = trade["ticker"]
                shares = float(trade["shares"])
                price = float(trade["price"])
                cost = float(trade.get("cost_usd", 0.0))
                holdings.loc[ticker] = holdings.get(ticker, 0.0) + shares
                cash -= shares * price + cost
            holdings = holdings[holdings.abs() > 1e-8]

        px = prices.loc[date].reindex(holdings.index).dropna()
        values = holdings.reindex(px.index).fillna(0.0) * px
        nav = float(values.sum() + cash)
        weights = values / nav if nav > 0 else pd.Series(dtype=float)
        weights_by_date[date] = weights
        exposure_rows.append(
            {
                "date": date,
                "gross_exposure": float(weights.abs().sum()) if not weights.empty else 0.0,
                "net_exposure": float(weights.sum()) if not weights.empty else 0.0,
                "cash_exposure_replayed": float(cash / nav) if nav > 0 else 1.0,
                "num_positions": int((weights.abs() > 1e-6).sum()),
            }
        )

    exposure = pd.DataFrame(exposure_rows).set_index("date")
    return exposure, weights_by_date


def sector_stats(weights_by_date: dict[pd.Timestamp, pd.Series], sector_mapping: dict[str, str]) -> pd.DataFrame:
    rows = []
    for date, weights in weights_by_date.items():
        if weights.empty:
            rows.append({"date": date, "max_sector_weight": 0.0, "sector_hhi": 0.0, "top_sector": ""})
            continue
        sector_weights = weights.groupby(weights.index.map(lambda t: sector_mapping.get(t, "_other"))).sum()
        rows.append(
            {
                "date": date,
                "max_sector_weight": float(sector_weights.max()),
                "sector_hhi": float((sector_weights ** 2).sum()),
                "top_sector": str(sector_weights.idxmax()),
            }
        )
    return pd.DataFrame(rows).set_index("date")


def beta_series(weights_by_date: dict[pd.Timestamp, pd.Series], stock_features: pd.DataFrame) -> pd.Series:
    dates = stock_features.index.get_level_values("date").unique().sort_values()
    rows = {}
    for date, weights in weights_by_date.items():
        if weights.empty:
            rows[date] = np.nan
            continue
        idx = dates.get_indexer([date], method="ffill")[0]
        if idx < 0:
            rows[date] = np.nan
            continue
        feature_date = dates[idx]
        beta = stock_features.xs(feature_date, level="date")["beta_to_spy_63d"].reindex(weights.index)
        rows[date] = float((weights * beta).sum())
    return pd.Series(rows, name="portfolio_beta")


def period_position_losses(period: pd.Series, weights_by_date: dict[pd.Timestamp, pd.Series], prices: pd.DataFrame) -> pd.DataFrame:
    start = pd.Timestamp(period["start_date"])
    trough = pd.Timestamp(period["trough_date"])
    weights = weights_by_date.get(start, pd.Series(dtype=float))
    if weights.empty:
        return pd.DataFrame(columns=["ticker", "start_weight", "return", "contribution"])
    start_px = prices.loc[start].reindex(weights.index)
    trough_px = prices.loc[trough].reindex(weights.index)
    rets = trough_px / start_px - 1.0
    contrib = weights * rets
    out = pd.DataFrame(
        {
            "ticker": weights.index,
            "start_weight": weights.values,
            "return": rets.values,
            "contribution": contrib.values,
        }
    ).dropna()
    return out.sort_values("contribution")


def mean_rebalance_ic(alpha_quality: list[dict], start: pd.Timestamp, trough: pd.Timestamp) -> float:
    vals = []
    for row in alpha_quality:
        date = pd.Timestamp(row.get("date"))
        if start <= date <= trough and "rank_ic" in row:
            vals.append(float(row["rank_ic"]))
    return float(np.mean(vals)) if vals else np.nan


def main():
    parser = argparse.ArgumentParser(description="Run baseline drawdown attribution")
    parser.add_argument("--config", type=str, default="config/baseline_v1_volatility_score_sp100.yaml")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml")
    args = parser.parse_args()

    base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask = load_inputs(
        args.config, args.universe
    )
    score_frame = compute_volatility_score_frame(stock_features)
    engine = WalkForwardEngine(
        config=base_config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices_dict=prices_dict,
        pit_mask=pit_mask,
    )
    history, trades, diagnostics = engine.run(
        use_optimizer=True,
        use_risk_engine=True,
        top_n_equal_weight=None,
        alpha_score_provider=build_alpha_score_provider(score_frame, "volatility_score"),
    )

    prices = prices_dict["adj_close"].ffill()
    history = history.sort_index()
    drawdown_periods = find_drawdown_periods(history["nav"], top_n=5)
    exposure, weights_by_date = replay_positions(
        history,
        trades,
        prices,
        initial_capital=base_config.portfolio.initial_capital,
    )
    sectors = sector_stats(weights_by_date, dict(universe_config.tickers))
    beta = beta_series(weights_by_date, stock_features)
    daily = history.join(exposure, how="left").join(sectors, how="left").join(beta, how="left")
    daily["drawdown"] = daily["nav"] / daily["nav"].cummax() - 1.0
    daily = daily.join(macro_features[["vix_level", "spy_drawdown"]], how="left")

    period_rows = []
    top_loser_lines = []
    drawdown_mask = pd.Series(False, index=daily.index)
    top10_contributions = []

    for display_id, period in enumerate(drawdown_periods.itertuples(index=False), start=1):
        start = pd.Timestamp(period.start_date)
        trough = pd.Timestamp(period.trough_date)
        mask = (daily.index >= start) & (daily.index <= trough)
        drawdown_mask |= mask
        losses = period_position_losses(pd.Series(period._asdict()), weights_by_date, prices)
        top_losers = losses.head(10)
        top10_contribution = float(top_losers["contribution"].sum()) if not top_losers.empty else np.nan
        top10_contributions.append(top10_contribution)
        top_loser_lines.append((display_id, top_losers))

        period_rows.append(
            {
                "period_id": display_id,
                "start_date": start.date(),
                "trough_date": trough.date(),
                "recovery_date": pd.Timestamp(period.recovery_date).date(),
                "duration_days": int(period.duration_days),
                "recovery_days": int(period.recovery_days),
                "depth": float(period.depth),
                "avg_gross_exposure": float(daily.loc[mask, "gross_exposure"].mean()),
                "avg_net_exposure": float(daily.loc[mask, "net_exposure"].mean()),
                "avg_sector_concentration": float(daily.loc[mask, "max_sector_weight"].mean()),
                "max_sector_concentration": float(daily.loc[mask, "max_sector_weight"].max()),
                "avg_turnover": float(daily.loc[mask, "turnover"].mean()),
                "avg_vix": float(daily.loc[mask, "vix_level"].mean()),
                "max_vix": float(daily.loc[mask, "vix_level"].max()),
                "avg_spy_drawdown": float(daily.loc[mask, "spy_drawdown"].mean()),
                "min_spy_drawdown": float(daily.loc[mask, "spy_drawdown"].min()),
                "avg_beta": float(daily.loc[mask, "portfolio_beta"].mean()),
                "top10_loser_contribution": top10_contribution,
                "mean_rebalance_ic": mean_rebalance_ic(diagnostics.get("alpha_quality", []), start, trough),
            }
        )

    periods_df = pd.DataFrame(period_rows)
    normal = daily.loc[~drawdown_mask]
    drawdown = daily.loc[drawdown_mask]

    normal_exposure = float(normal["gross_exposure"].mean())
    dd_exposure = float(drawdown["gross_exposure"].mean())
    normal_turnover = float(normal["turnover"].mean())
    dd_turnover = float(drawdown["turnover"].mean())
    dd_beta = float(drawdown["portfolio_beta"].mean())
    avg_top10_loss = float(np.nanmean(top10_contributions))

    market_crash = periods_df["min_spy_drawdown"].min() < -0.15 or periods_df["max_vix"].max() > 30
    concentration = periods_df["max_sector_concentration"].max() > 0.30
    factor_failure = periods_df["mean_rebalance_ic"].mean() < 0
    whipsaw = dd_turnover > normal_turnover * 1.5

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    periods_df.to_csv(reports_dir / "drawdown_periods.csv", index=False)

    lines = [
        "# Drawdown Attribution",
        "",
        f"- Config: `{args.config}`",
        f"- Universe: `{args.universe}`",
        f"- Strategy unchanged: `volatility_score + optimizer + risk`, RL disabled",
        "",
        "## Top 5 Drawdown Periods",
        "",
        periods_df.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Aggregate Comparison",
        "",
        f"- Average gross exposure during drawdowns: `{dd_exposure:.2%}`",
        f"- Average gross exposure during normal periods: `{normal_exposure:.2%}`",
        f"- Average beta during drawdowns: `{dd_beta:.3f}`",
        f"- Average turnover during drawdowns: `{dd_turnover:.4f}`",
        f"- Average turnover during normal periods: `{normal_turnover:.4f}`",
        f"- Average top-10 loser contribution across top drawdowns: `{avg_top10_loss:.2%}`",
        "",
        "## Top Losing Positions",
        "",
    ]
    for period_id, losers in top_loser_lines:
        lines.append(f"### Period {period_id}")
        if losers.empty:
            lines.append("No position losses reconstructed.")
        else:
            lines.append(losers.head(10).to_markdown(index=False, floatfmt=".4f"))
        lines.append("")

    lines.extend(
        [
            "## Cause Assessment",
            "",
            f"- A. Market crashes: {'YES' if market_crash else 'NO'}",
            f"- B. Concentration: {'YES' if concentration else 'NO'}",
            f"- C. Factor failure: {'YES' if factor_failure else 'NO'}",
            f"- D. Turnover/whipsaw: {'YES' if whipsaw else 'NO'}",
            "",
            "## Interpretation",
            "",
        ]
    )
    if market_crash:
        lines.append("- Drawdowns overlap with broad market stress: VIX spikes and SPY drawdowns are material in the worst periods.")
    if concentration:
        lines.append("- Sector concentration contributes: peak sector weights breach the 30% diagnostic threshold in at least one major drawdown.")
    else:
        lines.append("- Sector concentration is not the primary explanation under the 30% diagnostic threshold.")
    if factor_failure:
        lines.append("- Factor quality deteriorates during the top drawdowns based on negative mean rebalance IC.")
    else:
        lines.append("- Factor IC is mixed but not broadly negative across the top drawdowns.")
    if whipsaw:
        lines.append("- Turnover is materially higher in drawdowns than normal periods, consistent with whipsaw pressure.")
    else:
        lines.append("- Turnover does not appear to be the dominant drawdown source.")

    (reports_dir / "drawdown_attribution.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
