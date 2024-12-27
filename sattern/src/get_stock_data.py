import yfinance as yf
import json
import os
from pathlib import Path
from typing import List
import datetime

"""get_stock_data.py

Interaction with the stock data api. Will return requested stock data as a custom python class (object).

Abstracted away to enable use of different api's, the only requirement being this returns a standardized output
regardless of the API. 
"""

def store_stock_data(ticker: str = "AAPL", period: int = 1, interval: str = "1h"):
    """
    Collect and store historical stock data for a given ticker symbol.
    This function retrieves historical stock data for a specified ticker symbol, period, and interval.
    The data is then filtered to include only the 'Open', 'High', 'Low', and 'Close' columns.
    Optionally, the filtered data can be saved to a JSON file.

    Args:
        ticker (str): The stock ticker symbol to retrieve data for. Default is "AAPL".
        period (int): The period over which to retrieve historical data in years. Default is 1.
        interval (str): The interval between data. Must be > 1h for periods longer than two years. Default is 1d.
    Returns:
        final_data (json): JSON formatted stock data.
    """

    if period > 2:
        if interval == "1h":
            interval = "1d"

    print(f"Collecting {ticker} stock data. Period: {period}y. Interval: {interval}")

    y_finance = yf.Ticker(ticker)
    historical_data = y_finance.history(period=f"{period}y", interval=interval)

    historical_data.index = historical_data.index.astype(int) // 10**9
    filtered_data = historical_data[['Open', 'High', 'Low', 'Close']].to_dict(orient='index')

    with open(f'{Path("./sattern/src/data")}/{ticker}_{period}y_history_data.json', 'w') as file:
        json.dump(filtered_data, file, indent=4)

def store_multiple(ticker: List[str], period: int = 1):
    """
    Call store_history_data for multiple stocks.

    Args:
        ticker (List[str]): A list of stock ticker symbols.
        period (int, optional): The period for which to store the historical data. Defaults to 1.
    Returns:
        None
    """

    for stock in ticker:
        store_stock_data(ticker=stock, period=period)

class stock_data:
    def __init__(self, ticker: str, period: int = 2):
        self.ticker: str = ticker
        self.period: int = period

        self.date: List[int] = []
        self.open: List[float] = []
        self.high: List[float] = []
        self.low: List[float] = []
        self.close: List[float] = []

        # If this stock has been processed yet
        self.processed: bool = False

        # Now add some values for extracted data
        self.start_index: int
        self.end_index: int
        self.max_difference: int
        self.start_indicies: List[int] = []
        self.end_indicies: List[int] = []
        self.difference: List[float] = []

        # And the stock predictions
        self.predicted_dates: List[int] = []
        self.predicted_prices: List[float] = []

        self.load_stock_data()

    def load_stock_data(self, ticker: str = "AAPL", period: int = 1, file_path: str = None):
        """
        Reads stock data from a json (as formatted by store_history_data).
        Converts data to a history_data object

        Args:
            ticker (str): The stock ticker to retrieve data for. Default is "AAPL".
            period (str): The period over which the data was recieved in years. Default is 1.
            file_path (str): Optional file path to specify a data file to read from. Default is None.
        Returns:
            history_data: history_data object holding relevent stock data.
        """
        if (file_path is None or not os.path.exists(file_path)):
            file_path = f'{Path("./sattern/src/data")}/{self.ticker}_{self.period}y_history_data.json'

        if not os.path.exists(file_path):
            print(f"Data for {self.ticker}, period {self.period} does not exist.")
            store_stock_data(ticker=self.ticker, period=self.period)

        with open(file_path, 'r') as file:
            history = json.load(file)

        for date, data in history.items():
            self.date.append(date)
            self.open.append(data['Open'])
            self.high.append(data['High'])
            self.low.append(data['Low'])
            self.close.append(data['Close'])
