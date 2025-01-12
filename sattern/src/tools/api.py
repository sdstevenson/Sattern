import requests
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Union, Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

def get_financial_metrics(
    ticker: str,
    start_date: Optional[Union[str, datetime]] = None, 
    end_date: Optional[Union[str, datetime]] = None,
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

    if start_date is None or end_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Collect metrics
    news = get_news(ticker, start_date, end_date)
    return

    prices_df = get_prices(ticker, start_date, end_date)
    print(prices_df)

    # Combine metrics
    financial_metrics = prices_df

    if cache:
        financial_metrics.to_json(path_or_buf=file_path, orient='columns', date_format='iso')

    return financial_metrics

def get_prices(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
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
            "date": datetime.strptime(day, "%Y-%m-%d"),
            "close": history["Time Series (Daily)"][day]["4. close"],
            "volume": history["Time Series (Daily)"][day]["5. volume"],
            }
        )
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)

    return df

# def get_recommendations(ticker: str) -> pd.DataFrame:
#     yf = yfinance.Ticker(ticker)
#     return yf.get_recommendations()

def get_news(ticker: str, start_date: datetime, end_date: datetime):
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

    # Get the average sentiment, weighted by the relevance score
    total_relevance = 0
    total_sentiment = 0
    count = 0
    for article in news["feed"]:
        for rating in news[article]["ticker_sentiment"]:
            if rating["ticker"] == ticker:
                relevance = float(rating["ticker"]["relevance_score"])
                sentiment = float(rating["ticker"]["ticker_sentiment_score"])
                total_relevance += relevance
                total_sentiment += sentiment * relevance

    weighted_sentiment = total_sentiment / total_relevance

def get_insider_transactions(ticker: str, start_date: datetime, end_date: datetime):
    args = {
        "function": "INSIDER_TRANSACTIONS",
        "symbol": ticker
    }
    url = construct_url(**args)
    insider_transactions = requests.get(url).json()
    data = []
    for transaction in insider_transactions["data"]:
        data.append(
            {
            "date": datetime.strptime(transaction["transaction_date"], "%Y-%m-%d"),
            "acquisition_or_disposal": transaction["acquisition_or_disposal"],
            "shares": transaction["shares"],
            "share_price": transaction["share_price"]
            }
        )
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df

# def get_price_targets(ticker: str) -> Dict:
#     yf = yfinance.Ticker(ticker)
#     return yf.get_analyst_price_targets()

def construct_url(**args):
    url = f'https://www.alphavantage.co/query?'
    for arg in args.keys():
        url += f"{arg}={args[arg]}&"
    url += f"apikey={os.getenv('STOCK_API_KEY')}"
    print(url)
    return url
