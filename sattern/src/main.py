import sattern.src.tools.api as api 
from sattern.src.metrics.combine import combine
from sattern.src.tools.display import display
from sattern.src.tools.llm import run_llm
from sattern.src.tools.trader import portfolio
from typing import Dict
import pandas as pd
from datetime import datetime, timedelta, timezone

def run_sattern(ticker: str = "ERJ"):
    ticker = "BZ=F"
    period = 10
    max_diff = 5
    financial_metrics = api.get_financial_metrics(ticker=ticker, load_new=True, cache=True)
    financial_metrics, decision = combine(df=financial_metrics, period=period, max_diff=max_diff, cache=True, ticker=ticker)
    # print(f"{financial_metrics}\n***{decision}***")
    display(data=financial_metrics, metrics_to_plot=["prices", "sattern", "sattern_highlight"], ticker=ticker, max_diff=max_diff)
    return financial_metrics, decision

def run_fund_manager(ticker: str, portfolio: portfolio):
    end_date = datetime.now().replace(tzinfo=timezone.utc)
    start_date = (end_date - timedelta(days=7200)).replace(tzinfo=timezone.utc)
    # Get Data
    financial_metrics = api.get_financial_metrics(ticker, start_date, end_date, True)
    # Get Metrics
    df, actions = combine(ticker=ticker, df=financial_metrics, start_date=start_date, end_date=end_date, period=10)
    # Send to AI and retrieve decision
    llm_response = run_llm(ticker, df, actions, portfolio)
    print(llm_response)
    # Execute trade
    index = -1
    while True:
        curr_price = df.iloc[index]['prices']
        if not pd.isna(curr_price):
            break
        index -= 1
    portfolio.execute_trade(llm_response["action"], curr_price, llm_response["quantity"])
    print(portfolio)

def main():
    curr_portfolio = portfolio(10000, 0)
    run_fund_manager("ERJ", curr_portfolio)

if __name__ == "__main__":
    main()