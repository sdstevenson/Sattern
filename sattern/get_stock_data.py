import yfinance as yf
import json
import pprint
import os
from pathlib import Path
import pandas as pd

"""get_stock_data.py

Interaction with the stock data api. Will return requested stock data as a json object. 

Abstracted away to enable use of different api's, the only requirement being this returns a standardized output
regardless of the API. 
"""

def store_history_data(ticker: str = "AAPL", period: str = "1mo", save_to_file: bool = False):
    data = yf.Ticker(ticker)
    historical_data = data.history(period=period)

    historical_data.index = historical_data.index.strftime('%Y-%m-%d')
    filtered_data = historical_data[['Open', 'High', 'Low', 'Close']].to_dict(orient='index')

    print(filtered_data)

    if save_to_file:
        with open(f'{Path("./sattern/data")}/{ticker}_{period}_history_data.json', 'w') as file:
            json.dump(filtered_data, file, indent=4)

def load_data_from_file(ticker: str = "AAPL", period: str = "1mo", type: str = "history", file_path: str = None):
    if (not file_path or not os.path.exists(file_path)):
        file_path = f'{Path("./sattern/data")}/{ticker}_{period}_{type}_data.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            history = json.load(file)
        return(history)
    else:
        print(f"File {file_path} does not exist.")
