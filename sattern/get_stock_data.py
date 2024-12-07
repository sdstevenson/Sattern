import yfinance as yf
import json
import pprint
import os
from pathlib import Path
import pandas as pd
from typing import List

"""get_stock_data.py

Interaction with the stock data api. Will return requested stock data as specified below. 

Abstracted away to enable use of different api's, the only requirement being this returns a standardized output
regardless of the API. 
"""

class history_data:
    def __init__(self):
        self.date: List = []
        self.open: List[float] = []
        self.high: List[float] = []
        self.low: List[float] = []
        self.close: List[float] = []

def store_history_data(ticker: str = "AAPL", period: str = "1mo", save_to_file: bool = False):
    data = yf.Ticker(ticker)
    historical_data = data.history(period=period)

    historical_data.index = historical_data.index.strftime('%Y-%m-%d')
    filtered_data = historical_data[['Open', 'High', 'Low', 'Close']].to_dict(orient='index')

    print(filtered_data)

    if save_to_file:
        with open(f'{Path("./sattern/data")}/{ticker}_{period}_history_data.json', 'w') as file:
            json.dump(filtered_data, file, indent=4)

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
