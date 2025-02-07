import requests
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Union, Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# TO DO: Finish up financial metrics
def get_financial_metrics(ticker: str, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> pd.DataFrame:

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

    return financial_metrics

def get_prices(ticker: str) -> pd.DataFrame:
    # Note: Start and end dates not required. Gets past 20 years, select needed data.
    args = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "full",
    }
    file_path = path_exists(ticker, "prices")
    if file_path is None:
        print("Fetching prices from API")
        url = construct_url(**args)
        history = requests.get(url).json()
        data = []
        for day in history["Time Series (Daily)"]:
            data.append(
                {
                "date": datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=timezone.utc),
                "prices": float(history["Time Series (Daily)"][day]["4. close"]),
                "volume": float(history["Time Series (Daily)"][day]["5. volume"]),
                }
            )
        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        with open(f'{Path("./sattern/src/data")}/{ticker}_prices_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            df.to_json(path_or_buf=f, orient='columns', date_format='iso')
    else:
        with open(file_path, 'r') as f:
            df = pd.read_json(path_or_buf=f, orient='columns')
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d').tz_convert(tz=timezone.utc)

    return df

def get_news(ticker: str, start_date: datetime, end_date: datetime) -> Dict:
    args = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "time_from": start_date.strftime("%Y%m%dT%H%M"),
        "time_to": end_date.strftime("%Y%m%dT%H%M"),
        "sort": "LATEST",
        "limit": 1000,
    }
    file_path = path_exists(ticker, "news")
    if file_path is None:
        print("Fetching news from API")
        url = construct_url(**args)
        news = requests.get(url).json()
        with open(f'{Path("./sattern/src/data")}/{ticker}_news_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            json.dump(news, f)
    else:
        with open(file_path, 'r') as f:
            news = json.load(f)
    return news

def get_insider_transactions(ticker: str) -> pd.DataFrame:
    # No date input
    args = {
        "function": "INSIDER_TRANSACTIONS",
        "symbol": ticker
    }
    file_path = path_exists(ticker, "insider_transactions")
    if file_path is None:
        print("Fetching insider transactions from API")
        url = construct_url(**args)
        insider_transactions = requests.get(url).json()
        if insider_transactions["data"] == []:
            print(f"No insider transactions found for {ticker}")
            with open(f'{Path("./sattern/src/data")}/{ticker}_insider_transactions_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
                pass
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
        with open(f'{Path("./sattern/src/data")}/{ticker}_insider_transactions_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            df.to_json(path_or_buf=f, orient='records', date_format='iso')
    else:
        with open(file_path, 'r') as f:
            if os.stat(file_path).st_size == 0:
                print(f"No insider transactions found for {ticker}")
                return None
            df = pd.read_json(path_or_buf=f, orient='records')
    return df

def get_commodity_prices(ticker: str) -> pd.DataFrame:
    args = {
        "function": ticker,
        "interval": "daily",
    }
    file_path = path_exists(ticker, "prices")
    if file_path is None:
        print("Fetching commodoties prices from API")
        url = construct_url(**args)
        prices = requests.get(url).json()
        data = []
        for day in prices["data"]:
            try:
                data.append(
                    {
                    "date": datetime.strptime(day['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc),
                    "prices": float(day['value']),
                    }
                )
            except ValueError:
                pass
        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        with open(f'{Path("./sattern/src/data")}/{ticker}_prices_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            df.to_json(path_or_buf=f, orient='columns', date_format='iso')
    else:
        with open(file_path, 'r') as f:
            df = pd.read_json(path_or_buf=f, orient='columns')
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d').tz_convert(tz=timezone.utc)

    return df

def construct_url(**args) -> str:
    url = f'https://www.alphavantage.co/query?'
    for arg in args.keys():
        url += f"{arg}={args[arg]}&"
    url += f"apikey={os.getenv('STOCK_API_KEY')}"
    return url

def path_exists(ticker: str, name: str) -> str:
    file_path = f'{Path("./sattern/src/data")}/{ticker}_{name}_'
    # {datetime.now().strftime("%Y%m%d")}.json
    date_range = [(datetime.now(timezone.utc) - timedelta(days=i)).strftime('%Y%m%d') for i in range(6)]
    for date in date_range:
        if os.path.exists(file_path + date + ".json"):
            return file_path + date + ".json"
    print(f"File not found: {ticker} // {name}")
    return None
