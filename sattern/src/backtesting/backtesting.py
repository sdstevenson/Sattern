
"""backtesting.py
This module serves as the entry point for the backtesting functionality in the Sattern project.
"""

from sattern.src.backtesting.load_data import load_stock_data
from sattern.src.backtesting.tester import backtesting_data
from sattern.src.backtesting.display import plot_comparison

def main():
    # load_stock_data(["INTC", "GOOG", "CELH"], 2)

    erj_backtesting = backtesting_data(ticker="ERJ")
    erj_backtesting.multi_period_compare()
    # plot_comparison(stock_data=erj_backtesting)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()