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


def run_engine(config_path: str, universe_path: str, shared_inputs: tuple | None = None) -> dict:
    if shared_inputs is None:
        base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask = load_inputs(
            config_path, universe_path
        )
    else:
        _, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask = shared_inputs
        base_config, _ = load_config(config_path, universe_path)

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
    return {
        "config": base_config,
        "history": history,
        "trades": trades,
        "diagnostics": diagnostics,
        "metrics": calculate_metrics(history["nav"]) if not history.empty else {},
    }


def drawdown_depth(nav: pd.Series, start: pd.Timestamp, trough: pd.Timestamp) -> float:
    window = nav.loc[(nav.index >= start) & (nav.index <= trough)]
    if window.empty:
        return np.nan
    base = nav.loc[:start].iloc[-1] if not nav.loc[:start].empty else window.iloc[0]
    return float(window.min() / base - 1.0)


def summarize(name: str, result: dict, baseline_2020: float | None = None) -> dict:
    history = result["history"]
    metrics = result["metrics"]
    events = pd.DataFrame(result["diagnostics"].get("intraperiod_risk", []))
    hedge_days = int((history["cash_exposure"] > history["cash_exposure"].median() + 0.10).sum()) if not history.empty else 0
    dd_2020 = drawdown_depth(history["nav"], *DD_2020)
    return {
        "variant": name,
        "cagr": metrics.get("CAGR"),
        "sharpe": metrics.get("Sharpe"),
        "max_dd": metrics.get("Max Drawdown"),
        "dd_2020": dd_2020,
        "dd_2022": drawdown_depth(history["nav"], *DD_2022),
        "overlay_events": len(events),
        "overlay_enter_events": int((events.get("event", pd.Series(dtype=str)) == "overlay_enter").sum()),
        "overlay_rebalance_scaled": int((events.get("event", pd.Series(dtype=str)) == "rebalance_scaled").sum()),
        "avg_cash_exposure": float(history["cash_exposure"].mean()) if not history.empty else np.nan,
        "high_cash_days_proxy": hedge_days,
        "total_cost": float(history["cost"].sum()) if not history.empty else np.nan,
        "trade_count": int(len(result["trades"])),
        "maxdd_lt_32pct": bool(metrics.get("Max Drawdown", -1.0) > -0.32),
        "cagr_gt_16pct": bool(metrics.get("CAGR", 0.0) > 0.16),
        "sharpe_ge_0_9": bool(metrics.get("Sharpe", 0.0) >= 0.9),
        "dd_2020_reduces": bool(dd_2020 > baseline_2020) if baseline_2020 is not None else True,
    }


def first_event_lag(events: pd.DataFrame, start: pd.Timestamp) -> int | None:
    if events.empty or "date" not in events.columns:
        return None
    dated = events.copy()
    dated["date"] = pd.to_datetime(dated["date"])
    active = dated[dated["date"] >= start]
    if active.empty:
        return None
    return int((active["date"].iloc[0] - start).days)


def render_report(results: pd.DataFrame, events: pd.DataFrame) -> str:
    criteria = results[
        ["variant", "maxdd_lt_32pct", "cagr_gt_16pct", "sharpe_ge_0_9", "dd_2020_reduces", "all_pass"]
    ]
    lines = [
        "# Production Intraperiod Overlay",
        "",
        "- Baseline: `baseline_v1_volatility_score_sp100`",
        "- Production variant: `baseline_v1_intraperiod_overlay_sp100`",
        "- Alpha rankings unchanged",
        "- Optimizer unchanged",
        "- RL disabled",
        "- Signal timing: SPY/VIX shock is measured at prior close and executed at the next trading day's open.",
        "- Execution mechanics: target stock weights are scaled to 60% while overlay is active; residual remains cash.",
        "",
        "## Comparison",
        "",
        results[
            [
                "variant",
                "cagr",
                "sharpe",
                "max_dd",
                "dd_2020",
                "dd_2022",
                "overlay_events",
                "avg_cash_exposure",
                "total_cost",
                "trade_count",
            ]
        ].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Hedge Timing",
        "",
        f"- First production overlay event lag vs 2020 crash start: `{first_event_lag(events, DD_2020[0])}` days",
        f"- First production overlay event lag vs 2022 drawdown start: `{first_event_lag(events, DD_2022[0])}` days",
        "",
        "## Success Criteria",
        "",
        criteria.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
    ]
    overlay = results[results["variant"] == "production_intraperiod_overlay"].iloc[0]
    baseline = results[results["variant"] == "baseline_v1"].iloc[0]
    if bool(overlay["all_pass"]):
        lines.append("- Production intraperiod overlay passes the current gate.")
    else:
        lines.append("- Production intraperiod overlay does not pass the full current gate.")
    lines.append(
        f"- MaxDD changed from `{baseline['max_dd']:.2%}` to `{overlay['max_dd']:.2%}`, "
        f"while Sharpe changed from `{baseline['sharpe']:.3f}` to `{overlay['sharpe']:.3f}`."
    )
    lines.append(
        f"- Trade count increased from `{int(baseline['trade_count'])}` to `{int(overlay['trade_count'])}` "
        f"and total costs increased from `${baseline['total_cost']:,.0f}` to `${overlay['total_cost']:,.0f}`."
    )
    lines.append(
        "- Main failure mode: the one-day trigger enters and exits frequently, so execution friction erodes much "
        "of the post-hoc overlay benefit."
    )
    lines.append(
        "- Recommended next test: add hysteresis/min-hold rules or implement the overlay as a SPY hedge sleeve "
        "instead of repeatedly scaling the entire stock book."
    )
    lines.append("- This run uses actual simulator rebalances, cash, transaction costs, and slippage; it is no longer a post-hoc NAV multiplier.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run production intraperiod overlay comparison")
    parser.add_argument("--baseline-config", type=str, default="config/baseline_v1_volatility_score_sp100.yaml")
    parser.add_argument("--overlay-config", type=str, default="config/baseline_v1_intraperiod_overlay_sp100.yaml")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml")
    args = parser.parse_args()

    shared_inputs = load_inputs(args.baseline_config, args.universe)
    baseline = run_engine(args.baseline_config, args.universe, shared_inputs)
    overlay = run_engine(args.overlay_config, args.universe, shared_inputs)
    baseline_2020 = drawdown_depth(baseline["history"]["nav"], *DD_2020)
    rows = [
        summarize("baseline_v1", baseline),
        summarize("production_intraperiod_overlay", overlay, baseline_2020),
    ]
    results = pd.DataFrame(rows)
    results["all_pass"] = results[
        ["maxdd_lt_32pct", "cagr_gt_16pct", "sharpe_ge_0_9", "dd_2020_reduces"]
    ].all(axis=1)

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    events = pd.DataFrame(overlay["diagnostics"].get("intraperiod_risk", []))
    events.to_csv(reports_dir / "production_intraperiod_overlay_events.csv", index=False)
    results.to_csv(reports_dir / "production_intraperiod_overlay_summary.csv", index=False)
    (reports_dir / "production_intraperiod_overlay.md").write_text(render_report(results, events))


if __name__ == "__main__":
    main()
