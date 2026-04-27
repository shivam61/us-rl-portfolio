import io
import pandas as pd
import yaml
import argparse
import logging
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECTOR_TO_ETF = {
    'Information Technology': 'XLK',
    'Financials': 'XLF',
    'Health Care': 'XLV',
    'Consumer Discretionary': 'XLY',
    'Consumer Staples': 'XLP',
    'Energy': 'XLE',
    'Industrials': 'XLI',
    'Utilities': 'XLU',
    'Materials': 'XLB',
    'Real Estate': 'XLRE',
    'Communication Services': 'XLC',
}


def fetch_sp500_constituents() -> pd.DataFrame:
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (research-bot)'}, timeout=20)
    resp.raise_for_status()
    tables = pd.read_html(io.StringIO(resp.text), flavor='lxml')
    df = tables[0].copy()
    df.columns = df.columns.str.strip()
    # Wikipedia column names can vary slightly between edits
    ticker_col = next(c for c in df.columns if 'symbol' in c.lower() or 'ticker' in c.lower())
    sector_col = next(c for c in df.columns if 'gics sector' in c.lower() or 'sector' in c.lower())
    return df[[ticker_col, sector_col]].rename(columns={ticker_col: 'ticker', sector_col: 'sector'})


def normalize_ticker(ticker: str) -> str:
    # yfinance uses - instead of . for tickers like BRK.B → BRK-B
    return ticker.replace('.', '-').strip()


def main():
    parser = argparse.ArgumentParser(description="Generate universe config from Wikipedia S&P 500 list")
    parser.add_argument("--output", type=str, default="config/universes/sp500.yaml")
    parser.add_argument("--pit-mask-path", type=str, default="data/artifacts/universe_mask_sp500.parquet")
    args = parser.parse_args()

    logger.info("Fetching S&P 500 constituents from Wikipedia...")
    sp500 = fetch_sp500_constituents()
    logger.info(f"Found {len(sp500)} raw constituents")

    sp500['etf'] = sp500['sector'].map(SECTOR_TO_ETF)
    unmapped = sp500[sp500['etf'].isna()]
    if not unmapped.empty:
        logger.warning(f"Unmapped GICS sectors (will be dropped): {unmapped['sector'].unique()}")
    sp500 = sp500.dropna(subset=['etf'])

    sp500['ticker'] = sp500['ticker'].apply(normalize_ticker)
    sp500 = sp500.drop_duplicates(subset='ticker')

    tickers_dict = dict(zip(sp500['ticker'], sp500['etf']))
    logger.info(f"Final universe: {len(tickers_dict)} tickers across {sp500['etf'].nunique()} sectors")

    config = {
        'name': 'sp500_dynamic',
        'description': f'S&P 500 universe ({len(tickers_dict)} tickers) with ADV-based PIT mask',
        'is_static': False,
        'pit_mask_path': args.pit_mask_path,
        'benchmark': 'SPY',
        'vix_proxy': '^VIX',
        'macro_etfs': ['SPY', 'QQQ', 'IWM'],
        'sector_etfs': ['XLK', 'XLF', 'XLV', 'XLY', 'XLP', 'XLE', 'XLI', 'XLU', 'XLB', 'XLRE', 'XLC'],
        'tickers': tickers_dict,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    logger.info(f"Written to {out_path}")

    logger.info("Sector breakdown:")
    for sector, etf in sorted(SECTOR_TO_ETF.items()):
        n = (sp500['etf'] == etf).sum()
        logger.info(f"  {etf}  {sector}: {n} tickers")


if __name__ == '__main__':
    main()
