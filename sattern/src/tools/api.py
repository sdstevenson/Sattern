import requests
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Union, Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

def get_financial_metrics(
        ticker: str,
        start_date: Union[str, datetime], 
        end_date: Union[str, datetime],
        load_new: bool = False,
        cache: bool = False
    ) -> pd.DataFrame:
    file_path = f'{Path("./sattern/src/data")}/{ticker}_stock_data.json'
    if not load_new:
        try:
            return pd.read_json(file_path, orient='columns')
        except Exception as e:
            print(f"Error loading cached data: {e}")
            pass

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date = start_date.replace(tzinfo=timezone.utc)
    end_date = end_date.replace(tzinfo=timezone.utc)

    # Collect metrics
    prices_df = get_prices(ticker)
    insider_transactions = get_insider_transactions(ticker)

    # Combine metrics -- TO DO for more metrics
    if insider_transactions is not None:
        financial_metrics = pd.concat([prices_df, insider_transactions], axis=1)
    else:
        financial_metrics = prices_df
    financial_metrics = financial_metrics[(financial_metrics.index >= start_date) & (financial_metrics.index <= end_date)]

    if cache:
        financial_metrics.to_json(path_or_buf=file_path, orient='columns', date_format='iso')

    return financial_metrics

def get_prices(ticker: str) -> pd.DataFrame:
    # Note: Start and end dates not required. Gets past 20 years, select needed data.
    args = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "full",
    }
    url = construct_url(**args)
    history = requests.get(url).json()

    data = []
    for day in history["Time Series (Daily)"]:
        data.append(
            {
            "date": datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc),
            "prices": float(history["Time Series (Daily)"][day]["4. close"]),
            "volume": float(history["Time Series (Daily)"][day]["5. volume"]),
            }
        )
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)

    return df

def get_news(ticker: str, start_date: datetime, end_date: datetime) -> Dict:
    args = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "time_from": start_date.strftime("%Y%m%dT%H%M"),
        "time_to": end_date.strftime("%Y%m%dT%H%M"),
        "sort": "RELEVANCE",
        "limit": "1",
    }
    url = construct_url(**args)
    news = requests.get(url).json()
    # with open(f'{Path("./sattern/src/data")}/{ticker}_news.json', 'w') as f:
    #     json.dump(news, f)
    return news

def get_insider_transactions(ticker: str) -> pd.DataFrame:
    # Dates not needed, goes back 20 years
    args = {
        "function": "INSIDER_TRANSACTIONS",
        "symbol": ticker
    }
    url = construct_url(**args)
    insider_transactions = requests.get(url).json()
    if insider_transactions["data"] == []:
        return None

    data = []
    for transaction in insider_transactions["data"]:
        data.append(
            {
            "date": datetime.strptime(transaction["transaction_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc),
            "acquisition_or_disposal": transaction["acquisition_or_disposal"],
            "shares": transaction["shares"],
            "share_price": transaction["share_price"]
            }
        )
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df

def construct_url(**args):
    url = f'https://www.alphavantage.co/query?'
    for arg in args.keys():
        url += f"{arg}={args[arg]}&"
    url += f"apikey={os.getenv('STOCK_API_KEY')}"
    return url
