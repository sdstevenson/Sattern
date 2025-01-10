import sattern.src.tools.api as api 
from sattern.src.metrics.sattern import sattern
from sattern.src.metrics.combine import combine
from sattern.src.tools.display import display
from sattern.src.tools.llm import run_llm
from sattern.src.tools.trader import portfolio
from typing import Dict
import pandas as pd

def run_sattern(ticker: str = "ERJ"):
    period = 10
    max_diff = 5
    financial_metrics = api.get_financial_metrics(ticker=ticker)
    financial_metrics, decision = sattern(financial_metrics=financial_metrics, period=period, max_diff=max_diff)
    # print(f"{financial_metrics}\n***{decision}***")
    display(data=financial_metrics, metrics_to_plot=["prices", "sattern", "sattern_highlight"], ticker=ticker, max_diff=max_diff)
    return financial_metrics, decision

def run_all(ticker: str, portfolio: portfolio):
    # Get Data
    financial_metrics = api.get_financial_metrics(ticker)
    # Get Metrics
    df, actions = combine(financial_metrics, 10, 2)
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
    # run_trader()
    # run_sattern(ticker="ERJ")
    curr_portfolio = portfolio(10000, 0)
    run_all("ERJ", curr_portfolio)

if __name__ == "__main__":
    main()