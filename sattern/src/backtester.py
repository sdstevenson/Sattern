from datetime import datetime, timedelta, timezone
from typing import Union, Tuple, Dict, List
import pandas as pd
import matplotlib.pyplot as plt
from sattern.src import api, process, trader, display
from pathlib import Path
import json


class Backtester:
    def __init__(self, ticker: str, start_date: datetime, end_date: datetime, init_capital: float, display: bool, periods: List[int], commodity: bool = False):
        self.ticker = ticker
        self.display = display
        self.periods = periods

        if start_date > end_date:
            start_date, end_date = end_date, start_date
        if end_date > datetime.now():
            end_date = datetime.now()
        self.start_date = start_date.replace(tzinfo=timezone.utc)
        self.end_date = end_date.replace(tzinfo=timezone.utc)

        self.init_capital = init_capital
        self.portfolio: trader.portfolio = trader.portfolio(init_capital)
        self.portfolio_value = 0
        self.portfolio_values = []

        self.commodity: bool = commodity

        if commodity:
            self.prices: pd.DataFrame = api.get_commodity_prices(ticker)
        else:
            self.prices: pd.DataFrame = api.get_prices(ticker)
            self.news: Dict = api.get_news(ticker, start_date, end_date)

    def run_backtesting(self):
        dates = pd.date_range(self.start_date, self.end_date, freq="B")

        if self.display:
            print("\nStarting backtest...")
            print(f"{'Date':<12} {'Ticker':<6} {'Action':<6} {'Quantity':>8} {'Price':>8} {'Cash':>12} {'Stock':>8} {'Total Value':>12}")
            print("-" * 100)
        else:
            print(f"\nStarting Backtest on {self.ticker}...")

        for curr_date in dates:
            curr_start_date = (curr_date - timedelta(days=730))
            test_df = self.prices.loc[curr_date:curr_start_date].copy()

            actions = {}
            for period in self.periods:
                p_sattern, sattern_action = process.sattern(test_df["prices"], period)
                actions[f"sattern_{period}"] = sattern_action['action']
            if not self.commodity:
                # Commodoties dont have insider trading or news data
                filtered_news: Dict[str, List] = {"feed": []}
                for article in self.news["feed"]:
                    time_published = datetime.strptime(article["time_published"], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
                    if time_published < curr_date:
                        filtered_news["feed"].append(article)
                p_news = process.process_news(self.ticker, filtered_news)
                # p_insider_transactions = process.process_insider_transactions(insider_trades)
                actions['news'] = p_news['action']
                # actions['insider_transactions'] = p_insider_transactions['action']

            curr_price = test_df.iloc[0]['prices']
            executed_action, executed_quantity = self.portfolio.execute_trade(action=actions, current_price=curr_price)

            total_value = self.portfolio.cash + self.portfolio.stock * curr_price
            self.portfolio_values.append(
                {"Date": curr_date.strftime('%Y-%m-%d'), "Portfolio Value": total_value}
            )
            self.portfolio_value = total_value

            if self.display:
                print(
                    f"{curr_date.strftime('%Y-%m-%d'):<12} {self.ticker:<6} {executed_action:<6} {executed_quantity:>8} {curr_price:>8.2f} "
                    f"{self.portfolio.cash:>12.2f} {self.portfolio.stock:>8} {total_value:>12.2f}"
                )

    def analyze_performance(self) -> Tuple[pd.DataFrame, float]:
        performance_df = pd.DataFrame(self.portfolio_values)
        performance_df['Date'] = pd.to_datetime(performance_df['Date'], utc=True)
        performance_df.set_index('Date', inplace=True)

        # Calculate total return
        total_return = (self.portfolio_value - self.init_capital) / self.init_capital * 100
        print(f"Total Return: {total_return:.2f}%")

        # Calculate stock growth
        self.start_date = pd.to_datetime(self.start_date, utc=True).normalize()
        self.end_date = pd.to_datetime(self.end_date, utc=True).normalize()

        # Ensure dates are valid
        attempts = 0
        while attempts < 10:
            try:
                start_price = self.prices.loc[self.start_date]['prices']
                break
            except KeyError:
                self.start_date = self.start_date - timedelta(days=1)
                attempts += 1
        attempts = 0
        while attempts < 10:
            try:
                end_price = self.prices.loc[self.end_date]['prices']
                break
            except KeyError:
                self.end_date = self.end_date - timedelta(days=1)
                attempts += 1

        total_growth = (
            (end_price - start_price) / start_price
        )
        print(f"Stock Growth with No Trading: {total_growth*100:.2f}%")

        # Compute daily returns
        performance_df["Daily Return"] = performance_df["Portfolio Value"].pct_change()

        # Calculate Sharpe Ratio (assuming 252 trading days in a year)
        mean_daily_return = performance_df["Daily Return"].mean()
        std_daily_return = performance_df["Daily Return"].std()
        if std_daily_return != 0:
            sharpe_ratio = (mean_daily_return / std_daily_return) * (252 ** 0.5)
        else:
            sharpe_ratio = 0
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

        # Calculate Maximum Drawdown
        rolling_max = performance_df["Portfolio Value"].cummax()
        drawdown = performance_df["Portfolio Value"] / rolling_max - 1
        max_drawdown = drawdown.min()
        print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")

        if self.display:
            price_subset = self.prices.loc[self.end_date:self.start_date]['prices']
            price_subset = (price_subset / price_subset.iloc[-1]) * self.init_capital
            graph = display.custom_plot(self.ticker, price_subset)
            graph.plot(performance_df[["Portfolio Value"]], "Portfolio Value ($)", "green")
            graph.show()

        return performance_df, total_growth

def main():
    start = datetime.now() - timedelta(days=365*10)
    end = datetime.now()
    all_data = {}
    # stocks = ["AAPL", "NVDA", "MSFT", "AVGO", "ORCL", "CRM", "CSCO", "ACN", "NOW", "IBM"]
    # stocks = ["NG=F", "BZ=F", "KC=F"]
    # stocks = ["WTI", "NATURAL_GAS", "COFFEE"]
    stocks = ["ERJ"]
    # stocks = ["NG=F"]
    save_name = "Testing"
    avg_returns = 0
    for ticker in stocks:
        backtester = Backtester(ticker, start, end, 10000, display=True, periods=[5, 10, 20], commodity=False)
        backtester.run_backtesting()
        df, total_return = backtester.analyze_performance()
        avg_returns += total_return
        all_data[ticker] = df.dropna().to_dict()

    avg_returns = avg_returns / len(stocks)
    print(f"\nAverage returns: {avg_returns:.2f}%")

    with open(f'{Path("./sattern/src/backtesting_results")}/{save_name}.json', 'w') as f:
        json.dump(all_data, f)

if __name__ == "__main__":
    main()