
"""backtesting.py
This module serves as the entry point for the backtesting functionality in the Sattern project.
"""

from sattern.src.backtesting.load_data import load_stock_data

def main():
    load_stock_data(["INTC", "GOOG", "CELH"], 2)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()