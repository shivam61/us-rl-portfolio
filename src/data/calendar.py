import pandas as pd
import pandas_market_calendars as mcal
from typing import List

def get_trading_calendar(start_date: str, end_date: str) -> List[pd.Timestamp]:
    """
    Returns a list of valid trading dates for the NYSE calendar.
    """
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=start_date, end_date=end_date)
    return schedule.index.tolist()

def get_next_trading_day(date: str, calendar_dates: List[pd.Timestamp]) -> pd.Timestamp:
    """
    Given a date, returns the next valid trading day.
    """
    date_ts = pd.Timestamp(date)
    future_dates = [d for d in calendar_dates if d > date_ts]
    if not future_dates:
        raise ValueError(f"No valid trading days found after {date}")
    return future_dates[0]

def is_trading_day(date: str, calendar_dates: List[pd.Timestamp]) -> bool:
    """
    Check if a date is a valid trading day.
    """
    date_ts = pd.Timestamp(date).normalize()
    return any(d.normalize() == date_ts for d in calendar_dates)
