"""load_data.py
NOTE: Uses sattern functions for now.
This module deals with all data loading using the yfinance api."""

from sattern.src.get_stock_data import store_multiple
from typing import List

def load_stock_data(stocks: List[str], period: int = 2):
    store_multiple(ticker=stocks, period=period)