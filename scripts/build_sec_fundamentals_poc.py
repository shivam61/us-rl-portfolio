import argparse
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from src.config.loader import load_config
from src.data.providers.canonical_fundamental_provider import (
    CanonicalFundamentalProvider,
    OPTIONAL_CANONICAL_COLUMNS,
    REQUIRED_CANONICAL_COLUMNS,
)


SEC_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

FORM_TYPES = {"10-K", "10-K/A", "10-Q", "10-Q/A"}
USD_UNITS = {"USD", "USD/shares"}
SHARE_UNITS = {"shares"}
EPS_UNITS = {"USD/shares"}

FIELD_TAGS = {
    "eps": [
        "EarningsPerShareDiluted",
        "EarningsPerShareBasic",
    ],
    "book_value": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        "CommonStocksIncludingAdditionalPaidInCapital",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "shares_outstanding": [
        "WeightedAverageNumberOfDilutedSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "EntityCommonStockSharesOutstanding",
    ],
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "total_assets": [
        "Assets",
    ],
    "total_debt": [
        "LongTermDebtAndFinanceLeaseObligations",
        "LongTermDebtAndFinanceLeaseObligationsCurrent",
        "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
        "LongTermDebtCurrent",
        "LongTermDebtNoncurrent",
        "ShortTermBorrowings",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "interest_expense": [
        "InterestExpenseNonOperating",
        "InterestExpense",
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ],
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
    ],
    "free_cash_flow": [],
    "ebitda": [],
}

ADDITIVE_FIELDS = {
    "total_debt",
}


def sec_get_json(url: str, headers: dict[str, str], cache_path: Path, force: bool = False) -> Any:
    if cache_path.exists() and not force:
        with open(cache_path, "r") as f:
            return json.load(f)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()
    with open(cache_path, "w") as f:
        json.dump(payload, f)
    return payload


def load_tickers(args: argparse.Namespace) -> list[str]:
    if args.tickers:
        tickers = args.tickers
    else:
        _, universe_config = load_config(args.config, args.universe)
        tickers = list(universe_config.tickers.keys())
    tickers = [ticker.upper().strip() for ticker in tickers if ticker.strip()]
    if args.max_tickers:
        tickers = tickers[: args.max_tickers]
    return tickers


def load_sec_ticker_map(cache_dir: Path, headers: dict[str, str], force: bool) -> dict[str, str]:
    payload = sec_get_json(SEC_TICKER_URL, headers, cache_dir / "company_tickers.json", force=force)
    result = {}
    for row in payload.values():
        ticker = str(row["ticker"]).upper().strip()
        result[ticker] = str(row["cik_str"]).zfill(10)
    return result


def unit_allowed(field: str, unit: str) -> bool:
    if field == "eps":
        return unit in EPS_UNITS
    if field == "shares_outstanding":
        return unit in SHARE_UNITS
    return unit in USD_UNITS or unit == "pure"


def fact_duration_days(fact: dict[str, Any]) -> int | None:
    start = fact.get("start")
    end = fact.get("end")
    if not start or not end:
        return None
    try:
        return int((pd.Timestamp(end) - pd.Timestamp(start)).days)
    except Exception:
        return None


def fact_quality_score(fact: dict[str, Any]) -> tuple[int, int, int, str]:
    form = str(fact.get("form", ""))
    frame = str(fact.get("frame", ""))
    duration = fact_duration_days(fact)
    has_frame = 1 if frame else 0
    amendment_penalty = -1 if form.endswith("/A") else 0
    quarterly_duration = 0
    if duration is not None:
        quarterly_duration = -abs(duration - 91)
    filed = str(fact.get("filed", ""))
    return has_frame, amendment_penalty, quarterly_duration, filed


def iter_tag_facts(company_facts: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    tag_payload = company_facts.get("facts", {}).get("us-gaap", {}).get(tag)
    if not tag_payload:
        return []
    rows = []
    for unit, facts in tag_payload.get("units", {}).items():
        for fact in facts:
            row = dict(fact)
            row["unit"] = unit
            row["tag"] = tag
            rows.append(row)
    return rows


def extract_field_values(company_facts: dict[str, Any], field: str) -> dict[pd.Timestamp, float]:
    by_filing: dict[pd.Timestamp, list[dict[str, Any]]] = {}
    for tag in FIELD_TAGS[field]:
        for fact in iter_tag_facts(company_facts, tag):
            if str(fact.get("form", "")) not in FORM_TYPES:
                continue
            if not unit_allowed(field, str(fact.get("unit", ""))):
                continue
            if "val" not in fact or not fact.get("filed"):
                continue
            filed = pd.Timestamp(fact["filed"])
            by_filing.setdefault(filed, []).append(fact)

    result = {}
    for filed, facts in by_filing.items():
        if field in ADDITIVE_FIELDS:
            tag_values = {}
            for fact in facts:
                tag_values[fact["tag"]] = float(fact["val"])
            result[filed] = float(sum(tag_values.values()))
            continue
        best = sorted(facts, key=fact_quality_score)[-1]
        result[filed] = float(best["val"])
    return result


def company_to_canonical_rows(ticker: str, company_facts: dict[str, Any], start: pd.Timestamp, end: pd.Timestamp | None) -> list[dict[str, Any]]:
    values_by_field = {
        field: extract_field_values(company_facts, field)
        for field in FIELD_TAGS
        if field in REQUIRED_CANONICAL_COLUMNS + OPTIONAL_CANONICAL_COLUMNS
    }
    filing_dates = sorted({date for values in values_by_field.values() for date in values})
    rows = []
    latest: dict[str, float] = {}

    for filing_date in filing_dates:
        for field, values in values_by_field.items():
            if filing_date in values:
                latest[field] = values[filing_date]
        if filing_date < start:
            continue
        if end is not None and filing_date > end:
            continue
        row = {"ticker": ticker, "filing_date": filing_date}
        for field in REQUIRED_CANONICAL_COLUMNS + OPTIONAL_CANONICAL_COLUMNS:
            if field in {"ticker", "filing_date"}:
                continue
            row[field] = latest.get(field)
        rows.append(row)
    return rows


def write_frame(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".parquet":
        df.to_parquet(path, index=False)
        return
    if path.suffix.lower() == ".csv":
        df.to_csv(path, index=False)
        return
    raise ValueError(f"Unsupported output type: {path}")


def coverage_summary(df: pd.DataFrame, expected_tickers: list[str]) -> pd.DataFrame:
    expected = set(expected_tickers)
    covered = set(df["ticker"].unique()) if not df.empty else set()
    rows = [{
        "metric": "ticker_coverage",
        "value": len(covered) / max(len(expected), 1),
        "covered_tickers": len(covered),
        "expected_tickers": len(expected),
    }]
    for column in REQUIRED_CANONICAL_COLUMNS:
        if column in {"ticker", "filing_date"}:
            continue
        rows.append({
            "metric": f"{column}_row_coverage",
            "value": float(df[column].notna().mean()) if len(df) else 0.0,
            "covered_tickers": int(df.loc[df[column].notna(), "ticker"].nunique()) if len(df) else 0,
            "expected_tickers": len(expected),
        })
    return pd.DataFrame(rows)


def write_report(df: pd.DataFrame, summary: pd.DataFrame, missing_cik: list[str], output: Path, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_table = summary.to_csv(index=False)
    lines = [
        "# Phase A.6.1 SEC Fundamentals POC",
        "",
        "## Purpose",
        "",
        "Build a small real point-in-time fundamentals file from SEC company facts before investing in a full fundamentals platform.",
        "",
        "## Output",
        "",
        f"- Canonical file: `{output}`",
        f"- Rows: `{len(df):,}`",
        f"- Tickers: `{df['ticker'].nunique() if len(df) else 0:,}`",
    ]
    if len(df):
        lines.extend([
            f"- Filing date range: `{df['filing_date'].min().date()}` to `{df['filing_date'].max().date()}`",
        ])
    if missing_cik:
        lines.extend([
            "",
            "## Missing SEC Ticker Map",
            "",
            ", ".join(missing_cik),
        ])
    lines.extend([
        "",
        "## Coverage",
        "",
        "```csv",
        coverage_table.strip(),
        "```",
        "",
        "## Caveats",
        "",
        "- This is a POC, not a final fundamentals platform.",
        "- Availability uses SEC filing dates from company facts.",
        "- SEC company facts can include amended filings and restatements; this script keeps the latest observed value per filing date.",
        "- Some duration fields, especially cash-flow fields, can be year-to-date in 10-Q filings. Treat A.4 results as a scale/no-scale signal, not a production decision.",
        "- Analyst revisions and earnings-surprise fields are unavailable from SEC company facts.",
        "",
        "## Next Step",
        "",
        "Switch `fundamentals.provider` to `canonical_local`, point `fundamentals.path` at this file, run A.5 audit, then rerun A.4 on the same limited universe.",
    ])
    report_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a small canonical PIT fundamentals POC from SEC company facts")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp100.yaml")
    parser.add_argument("--tickers", nargs="*", help="Optional explicit ticker list; overrides --universe")
    parser.add_argument("--max-tickers", type=int, help="Limit ticker count for quick POC runs")
    parser.add_argument("--start-date", default="2015-01-01")
    parser.add_argument("--end-date")
    parser.add_argument("--output", default="data/fundamentals/sec_poc_canonical_fundamentals.parquet")
    parser.add_argument("--cache-dir", default="data/sec/companyfacts")
    parser.add_argument("--report", default="artifacts/reports/phase_a6_1_sec_fundamentals_poc.md")
    parser.add_argument("--summary-csv", default="artifacts/reports/phase_a6_1_sec_fundamentals_coverage.csv")
    parser.add_argument("--user-agent", default=None, help="SEC User-Agent, e.g. 'name email@example.com'. Defaults to SEC_USER_AGENT env var.")
    parser.add_argument("--force-download", action="store_true")
    parser.add_argument("--sleep-seconds", type=float, default=0.12)
    args = parser.parse_args()

    user_agent = args.user_agent
    if user_agent is None:
        import os
        user_agent = os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        raise ValueError("SEC requires a descriptive User-Agent. Pass --user-agent or set SEC_USER_AGENT.")

    tickers = load_tickers(args)
    cache_dir = Path(args.cache_dir)
    output = Path(args.output)
    headers = {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate", "Host": "data.sec.gov"}
    ticker_headers = dict(headers)
    ticker_headers["Host"] = "www.sec.gov"

    ticker_map = load_sec_ticker_map(cache_dir, ticker_headers, force=args.force_download)
    start = pd.Timestamp(args.start_date)
    end = pd.Timestamp(args.end_date) if args.end_date else None

    all_rows = []
    missing_cik = []
    for idx, ticker in enumerate(tickers, start=1):
        cik = ticker_map.get(ticker)
        if not cik:
            missing_cik.append(ticker)
            continue
        facts = sec_get_json(
            SEC_FACTS_URL.format(cik=cik),
            headers,
            cache_dir / f"CIK{cik}.json",
            force=args.force_download,
        )
        all_rows.extend(company_to_canonical_rows(ticker, facts, start=start, end=end))
        if args.sleep_seconds and idx < len(tickers):
            time.sleep(args.sleep_seconds)

    df = pd.DataFrame(all_rows)
    if df.empty:
        raise ValueError("No SEC canonical rows were produced")
    df = df.sort_values(["ticker", "filing_date"]).drop_duplicates(["ticker", "filing_date"], keep="last")
    df = df[REQUIRED_CANONICAL_COLUMNS + [col for col in OPTIONAL_CANONICAL_COLUMNS if col in df.columns]]
    CanonicalFundamentalProvider.validate_schema(df)

    summary = coverage_summary(df, tickers)
    write_frame(df, output)
    Path(args.summary_csv).parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_csv, index=False)
    write_report(df, summary, missing_cik, output, Path(args.report))

    print(f"Wrote {len(df):,} rows for {df['ticker'].nunique():,} tickers to {output}")
    print(f"Wrote coverage summary to {args.summary_csv}")
    print(f"Wrote report to {args.report}")


if __name__ == "__main__":
    main()
