import sattern.src.tools.api as api 
from sattern.src.metrics.sattern import sattern
import sattern.src.tools.weekday as weekday
from sattern.src.tools.display import display
from typing import Dict, List
from datetime import datetime
import pandas as pd

def run_sattern(portfolio: Dict):
    ticker="ERJ"
    max_diff = 5
    financial_metrics = api.get_financial_metrics(ticker=ticker)
    sattern_df = sattern(financial_metrics=financial_metrics, max_diff=max_diff)
    financial_metrics = pd.concat([financial_metrics, sattern_df], axis=1)
    print(financial_metrics)
    display(data=financial_metrics, metrics_to_plot=["prices", "sattern", "sattern_highlight"], ticker=ticker, max_diff=max_diff)

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