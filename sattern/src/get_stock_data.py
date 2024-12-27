import yfinance as yf
import json
import os
from pathlib import Path
from typing import List
import datetime

"""get_stock_data.py

Here is where all interaction with the chosen API will occur. 
This filters and stores data as a json and stock_data object. 
"""

def store_stock_data(ticker: str = "AAPL", period: int = 2, interval: str = "1h"):
    """
    Collect and store historical stock data for a given ticker symbol.
    The data is filtered to include only the 'Open', 'High', 'Low', and 'Close' columns.
    The filtered data is saved to a JSON file.

    Args:
        ticker (str): The stock ticker symbol to retrieve data for. Default is "AAPL".
        period (int): The period over which to retrieve historical data in years. Default is 1.
        interval (str): The interval between data. Must be > 1h for periods longer than two years. Default is 1d.
    Returns:
        None
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

def store_multiple(ticker: List[str], period: int = 2):
    """
    Given a list of stocks, call store_history_data for each.

    Args:
        ticker (List[str]): A list of stock ticker symbols.
        period (int, optional): The period (years) for which to store the historical data. Defaults to 2.
    Returns:
        None
    """

    for stock in ticker:
        store_stock_data(ticker=stock, period=period)


class comp_data:
    """
    Holds comparison data for a stock.
    Only used within stock_data objects
    
    Attributes
        processed (bool): Indicates if the stock data has been processed.
        comp_period (int): Period (days) stock data is compared to.
        comp_start_index (int): The starting index for the comparison data.
        max_difference (int): The maximum difference in stock prices.
        start_indicies (List[int]): List of starting indicies of similar data periods.
        difference (List[float]): List of differences in stock prices.
        predicted_dates (List[int]): List of predicted dates.
        predicted_prices (List[float]): List of predicted prices.
    """
    def __init__(self):
        # If this stock has been processed yet
        self.processed: bool = False

        self.comp_period: int
        self.comp_start_index: int      # Can be removed
        self.max_difference: int
        self.start_indicies: List[int] = []
        self.difference: List[float] = []

        # And the stock predictions
        self.predicted_dates: List[int] = []
        self.predicted_prices: List[float] = []


class stock_data:
    """
    Stores all data related to a given stock.

    Attributes:
        ticker (str): The stock ticker symbol.
        period (int): The period over which the data was received in years.
        date (List[int]): List of dates for the stock data.
        open (List[float]): List of opening prices.
        high (List[float]): List of highest prices.
        low (List[float]): List of lowest prices.
        close (List[float]): List of closing prices.
        comp (comp_data): Comparison data stored in a separate class.


    Methods:
        load_stock_data(ticker: str = "AAPL", period: int = 1, file_path: str = None):
            Reads stock data from a JSON file and converts it to a history_data object.
    """
    def __init__(self, ticker: str, period: int = 2):
        self.ticker: str = ticker
        self.period: int = period

        self.date: List[int] = []
        self.open: List[float] = []
        self.high: List[float] = []
        self.low: List[float] = []
        self.close: List[float] = []

        # Comparison data stored in a seperate class
        self.comp: comp_data = comp_data()

        self.load_stock_data()

    def load_stock_data(self, ticker: str = "AAPL", period: int = 2, file_path: str = None):
        """
        Reads stock data from a json (as formatted by store_stock_data) and stores the data in a stock_data object.

        Args:
            ticker (str): The stock ticker to retrieve data for. Default is "AAPL".
            period (str): The period over which the data was recieved in years. Default is 2.
            file_path (str): Optional file path to specify a data file to read from. Default is None.
        Returns:
            None
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
