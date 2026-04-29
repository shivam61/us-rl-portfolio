import argparse
import logging
from pathlib import Path

import pandas as pd

from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.fundamental_features import FundamentalFeatureGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_SURVIVABILITY_RAW = [
    "eps",
    "book_value",
    "net_income",
    "shares_outstanding",
    "revenue",
    "gross_profit",
    "total_assets",
    "total_debt",
    "operating_income",
    "interest_expense",
    "operating_cash_flow",
]

EXPECTED_ENGINEERED = [
    "pe_ratio",
    "pb_ratio",
    "roe",
    "eps_growth_yoy",
    "debt_to_assets",
    "debt_to_equity",
    "asset_turnover",
    "accruals_proxy",
    "net_debt_to_assets",
    "interest_coverage",
    "ocf_to_net_income",
    "gross_margin",
]


def coverage_rows(df: pd.DataFrame, tickers: list[str], fields: list[str], source: str) -> list[dict]:
    rows = []
    ticker_set = set(tickers)
    scoped = df[df["ticker"].isin(ticker_set)] if "ticker" in df.columns else df.iloc[0:0]
    for field in fields:
        if field not in scoped.columns:
            rows.append(
                {
                    "source": source,
                    "field": field,
                    "row_coverage_pct": 0.0,
                    "ticker_coverage_pct": 0.0,
                    "available": False,
                }
            )
            continue
        values = scoped[field]
        covered_tickers = set(scoped.loc[values.notna(), "ticker"].astype(str).unique())
        rows.append(
            {
                "source": source,
                "field": field,
                "row_coverage_pct": float(values.notna().mean()) if len(values) else 0.0,
                "ticker_coverage_pct": float(len(covered_tickers) / max(len(ticker_set), 1)),
                "available": True,
            }
        )
    return rows


def main():
    parser = argparse.ArgumentParser(description="Audit Phase A.5 fundamental data and feature coverage")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml", "config/universes/sp500.yaml"])
    parser.add_argument("--force-download", action="store_true")
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    all_rows = []
    summary_rows = []
    for universe_path in args.universes:
        base_config, universe_config = load_config(args.config, universe_path)
        tickers = list(universe_config.tickers.keys())
        fundamental_ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=args.force_download)
        fundamentals = fundamental_ingestion.fetch_universe_fundamentals(
            tickers=tickers,
            start_date=base_config.backtest.start_date,
            end_date=base_config.backtest.end_date,
            cache_key=universe_config.name,
        )
        cached_tickers = set(fundamentals["ticker"].astype(str).unique()) if "ticker" in fundamentals.columns else set()

        ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
        data_dict = ingestion.fetch_universe_data(tickers=tickers, start_date=base_config.backtest.start_date)
        engineered = FundamentalFeatureGenerator(data_dict, fundamentals_df=fundamentals).generate()
        engineered_reset = engineered.reset_index() if not engineered.empty else pd.DataFrame(columns=["date", "ticker"])

        raw_rows = coverage_rows(fundamentals, tickers, REQUIRED_SURVIVABILITY_RAW, "raw_fundamentals")
        feature_rows = coverage_rows(engineered_reset, tickers, EXPECTED_ENGINEERED, "engineered_features")
        for row in raw_rows + feature_rows:
            row["universe"] = universe_config.name
            all_rows.append(row)

        summary_rows.append(
            {
                "universe": universe_config.name,
                "requested_tickers": len(tickers),
                "fundamental_tickers": len(cached_tickers & set(tickers)),
                "fundamental_ticker_coverage_pct": len(cached_tickers & set(tickers)) / max(len(tickers), 1),
                "raw_columns": ",".join(fundamentals.columns) if not fundamentals.empty else "",
                "engineered_columns": ",".join([c for c in engineered.columns]) if not engineered.empty else "",
            }
        )
        logger.info(
            "%s: fundamental ticker coverage %.2f%% (%d/%d)",
            universe_config.name,
            100.0 * summary_rows[-1]["fundamental_ticker_coverage_pct"],
            summary_rows[-1]["fundamental_tickers"],
            summary_rows[-1]["requested_tickers"],
        )

    coverage = pd.DataFrame(all_rows)
    summary = pd.DataFrame(summary_rows)
    coverage.to_csv(reports_dir / "phase_a5_data_feature_coverage.csv", index=False)
    summary.to_csv(reports_dir / "phase_a5_data_feature_summary.csv", index=False)

    lines = [
        "# Phase A.5 Data Feature Audit",
        "",
        "## Summary",
        "",
        summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Coverage",
        "",
        coverage.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Interpretation",
        "",
        "- Fundamental caches are universe-scoped through `cache_key=universe_config.name`.",
        "- Engineered survivability features are produced only when their raw fields exist.",
        "- This audit is a plumbing and coverage gate; synthetic provider output is not a substitute for real point-in-time fundamentals.",
    ]
    (reports_dir / "phase_a5_data_feature_audit.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
