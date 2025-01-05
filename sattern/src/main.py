import sattern.src.tools.api as api 
from sattern.src.metrics.sattern import sattern
import sattern.src.tools.weekday as weekday
from sattern.src.tools.display import display
from typing import Dict, List
from datetime import datetime
import pandas as pd

def run_sattern(portfolio: Dict):
    ticker="TSM"
    max_diff = 2
    financial_metrics = api.get_financial_metrics(ticker=ticker)
    sattern_df = sattern(financial_metrics=financial_metrics, max_diff=max_diff)
    financial_metrics = pd.concat([financial_metrics, sattern_df], axis=1)
    # print(financial_metrics)
    display(data=financial_metrics, metrics_to_plot=["prices", "sattern", "sattern_highlight"], ticker=ticker, max_diff=max_diff)

def main():
    portfolio = {
        "cash": 100000.0,
        "stock": 0
    }
    run_sattern(portfolio)

if __name__ == "__main__":
    main()