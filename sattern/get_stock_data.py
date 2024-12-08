import yfinance as yf
import json
import pprint
import os
from pathlib import Path
import pandas as pd
from typing import List

"""get_stock_data.py

Interaction with the stock data api. Will return requested stock data as a custom python class (object).

Abstracted away to enable use of different api's, the only requirement being this returns a standardized output
regardless of the API. 
"""

class history_data:
    def __init__(self):
        self.date: List[int] = []
        self.open: List[float] = []
        self.high: List[float] = []
        self.low: List[float] = []
        self.close: List[float] = []

def store_history_data(ticker: str = "AAPL", period: str = "1mo", interval: str = "1h", save_to_file: bool = True):
    """
    Collect and store historical stock data for a given ticker symbol.
    This function retrieves historical stock data for a specified ticker symbol, period, and interval.
    The data is then filtered to include only the 'Open', 'High', 'Low', and 'Close' columns.
    Optionally, the filtered data can be saved to a JSON file.
    Args:
        ticker (str): The stock ticker symbol to retrieve data for. Default is "AAPL".
        period (str): The period over which to retrieve historical data. Default is "1mo".
        interval (str): The interval at which to retrieve historical data. Default is "1h".
        save_to_file (bool): Whether to save the filtered data to a JSON file. Default is True.
    Returns:
        data (yf.Ticker): The yfinance Ticker object containing the stock data.

    """
    print(f"Collecting {ticker} stock data. Period: {period}. Interval: {interval}")
    data = yf.Ticker(ticker)
    historical_data = data.history(period=period, interval=interval)
    # historical_data = data.history(period=period)

    # print(f"***Raw data***\n{historical_data}")

    # print(f"***Only relevent columns***\n{historical_data[['Open', 'High', 'Low', 'Close']]}")

    # Convert Timestamp object to unix time

    # print(f"***Filtered data***\n{filtered_data}")

    # Only filter the data if we are saving it to a file, otherwise just return whatever the API gives us for now.
    if save_to_file:
        # historical_data.index = historical_data.index.strftime('%Y-%m-%d-%H-%M')
        historical_data.index = historical_data.index.astype(int) // 10**9
        filtered_data = historical_data[['Open', 'High', 'Low', 'Close']].to_dict(orient='index')
        with open(f'{Path("./sattern/data")}/{ticker}_{period}_history_data.json', 'w') as file:
            json.dump(filtered_data, file, indent=4)

    return data

def load_history_data(ticker: str = "AAPL", period: str = "1mo", file_path: str = None) -> history_data:
    """Returns stock history data as a list of lists, each sublist containing data like 'Open', 'High', ...'"""
    if (not file_path or not os.path.exists(file_path)):
        file_path = f'{Path("./sattern/data")}/{ticker}_{period}_history_data.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            history = json.load(file)
    else:
        print(f"File {file_path} does not exist.")
        return

    return_data = history_data()
    for date, data in history.items():
        return_data.date.append(date)
        return_data.open.append(data['Open'])
        return_data.high.append(data['High'])
        return_data.low.append(data['Low'])
        return_data.close.append(data['Close'])

    return return_data
