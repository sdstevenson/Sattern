from sattern.src import api, display, llm, trader, process
from typing import Dict
import pandas as pd
from datetime import datetime, timedelta, timezone

def run_fund_manager(ticker: str, start_date: datetime, end_date: datetime):
    period, max_diff = 10, 2

    portfolio = trader.portfolio(10000, 0)
    prices = api.get_prices(ticker)
    news = api.get_news(ticker, start_date, end_date)
    insider_trades = api.get_insider_transactions(ticker)
    # financial_metrics = api.get_financial_metrics(ticker, start_date, end_date)

    p_news = process.process_news(ticker, news)
    p_insider_transactions = process.process_insider_transactions(insider_trades)
    p_sattern, sattern_action = process.sattern(prices["prices"], period, max_diff)
    display_obj = display.custom_plot(ticker, prices["prices"])
    display_obj.highlight(p_sattern["highlight"], period, max_diff, "yellow")
    display_obj.plot(p_sattern["sattern"], "sattern", "green")
    display_obj.show()

    actions = {
        "news": p_news,
        "insider_transactions": p_insider_transactions,
        "sattern": sattern_action
    }

    p_llm = llm.run_llm(ticker, prices, actions, portfolio)
    print(f"AI Decision: {p_llm['action']} {p_llm['quantity']}, prediction {p_llm['prediction']}")

    # Execute trade
    portfolio.execute_trade(p_llm['action'], prices['prices'].iloc[0], p_llm['quantity'], True)
    print(portfolio)

def main():
    ticker = "ERJ"
    end_date = datetime.now().replace(tzinfo=timezone.utc)
    start_date = (end_date - timedelta(days=7200)).replace(tzinfo=timezone.utc)
    run_fund_manager(ticker, start_date, end_date)

if __name__ == "__main__":
    main()