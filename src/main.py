import src.tools.api as api 
import src.metrics.sattern as sattern
from typing import Dict

def run_sattern(portfolio: Dict):
    financial_metrics = api.get_financial_metrics(ticker="ERJ")
    sattern.sattern(financial_metrics=financial_metrics)


    # test_data = stock_data(ticker="ERJ", period=2)
    # # display_stock_data.display_stock_price(stock_data=test_data, show=False)
    # process_data.predict_next_movement(stock_data=test_data)
    # display_stock_data.highlight_pattern(stock_data=test_data)


def main():
    portfolio = {
        "cash": 100000.0,
        "stock": 0
    }
    run_sattern(portfolio)

if __name__ == "__main__":
    main()