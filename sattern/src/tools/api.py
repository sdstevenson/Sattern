import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Union, Optional

def get_financial_metrics(
    ticker: str,
    start_date: Optional[Union[str, datetime]] = None, 
    end_date: Optional[Union[str, datetime]] = None,
    load_new: bool = False,
    cache: bool = False
) -> pd.DataFrame:
    """Fetch all metrics and combine to a single DataFrame"""
    file_path = f'{Path("./sattern/src/data")}/{ticker}_stock_data.json'
    if not load_new:
        try:
            return pd.read_json(file_path, orient='columns')
        except Exception as e:
            print(f"Error loading cached data: {e}")
            pass

    if start_date is None or end_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    prices_df = get_prices(ticker, start_date, end_date).copy()

    # Add more as needed
    financial_metrics = pd.DataFrame(
        {
            "prices": prices_df["Close"]
        },
        index=prices_df.index
    )
    financial_metrics.sort_index(inplace=True)

    if cache:
        financial_metrics.to_json(path_or_buf=file_path, orient='columns', date_format='iso')

    return financial_metrics

def get_prices(
    ticker: str, 
    start_date: datetime, 
    end_date: datetime
) -> pd.DataFrame:
    api_obj = yf.Ticker(ticker=ticker)

    history = api_obj.history(start=start_date, end=end_date, interval="1d")

    return history