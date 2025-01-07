from datetime import datetime, timedelta, timezone
from typing import Union
import pandas as pd
import matplotlib.pyplot as plt
from sattern.src.metrics.sattern import sattern
from sattern.src.tools.api import get_financial_metrics

STRONG_SIGNAL_QUANTITY = 10
NORMAL_SIGNAL_QUANTITY = 5

class Backtester:
    def __init__(self, ticker: str, start_date: Union[datetime, str], end_date: Union[datetime, str], init_capital: float):
        self.ticker = ticker

        if type(start_date) == str:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if type(end_date) == str:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        if end_date > datetime.now():
            end_date = datetime.now()
        self.start_date = start_date.replace(tzinfo=timezone.utc)
        self.end_date = end_date.replace(tzinfo=timezone.utc)

        self.init_capital = init_capital
        self.portfolio = {"cash": init_capital, "stock": 0}
        self.portfolio_value = 0
        self.portfolio_values = []

    def execute_trade(self, action: str, current_price: float) -> int:
        if "Buy" in action:
            if action == "Strong Buy":
                quantity = STRONG_SIGNAL_QUANTITY
            elif action == "Buy":
                quantity = NORMAL_SIGNAL_QUANTITY
            cost = quantity * current_price
            if cost <= self.portfolio["cash"]:
                self.portfolio["stock"] += quantity
                self.portfolio["cash"] -= cost
                return quantity
            else:
                max_quantity = self.portfolio["cash"] // current_price
                if max_quantity > 0:
                    self.portfolio["stock"] += max_quantity
                    self.portfolio["cash"] -= max_quantity * current_price
                    return max_quantity
                return 0
        elif "Sell" in action:
            if action == "Strong Sell":
                quantity = STRONG_SIGNAL_QUANTITY
            elif action == "Sell":
                quantity = NORMAL_SIGNAL_QUANTITY
            cost = quantity * current_price

            quantity = min(quantity, self.portfolio["stock"])
            if quantity > 0:
                self.portfolio["stock"] -= quantity
                self.portfolio["cash"] += quantity * current_price
            return quantity
        return 0

    def run_backtesting(self):
        dates = pd.date_range(self.start_date, self.end_date, freq="B")

        print("\nStarting backtest...")
        print(f"{'Date':<12} {'Ticker':<6} {'Action':<6} {'Quantity':>8} {'Price':>8} {'Cash':>12} {'Stock':>8} {'Total Value':>12}")
        print("-" * 100)

        df = get_financial_metrics(ticker=self.ticker, start_date=self.start_date-timedelta(days=730), end_date=self.end_date, load_new=True, cache=False)

        for curr_date in dates:
            curr_start_date = (curr_date - timedelta(days=730))
            # df = get_financial_metrics(ticker=self.ticker, start_date=curr_start_date, end_date=curr_date, load_new=True, cache=False)
            sattern_df = df.loc[curr_start_date:curr_date].copy()
            sattern_df, action = sattern(sattern_df)

            index = -1
            while True:
                curr_price = sattern_df.iloc[index]['prices']
                if not pd.isna(curr_price):
                    break
                index -= 1
            
            executed_quantity = self.execute_trade(action, curr_price)

            total_value = self.portfolio["cash"] + self.portfolio["stock"] * curr_price
            self.portfolio_values.append(
                {"Date": curr_date.strftime('%Y-%m-%d'), "Portfolio Value": total_value}
            )
            self.portfolio_value = total_value

            print(
                f"{curr_date.strftime('%Y-%m-%d'):<12} {self.ticker:<6} {action:<6} {executed_quantity:>8} {curr_price:>8.2f} "
                f"{self.portfolio['cash']:>12.2f} {self.portfolio['stock']:>8} {total_value:>12.2f}"
            )

    def analyze_performance(self):
        performance_df = pd.DataFrame(self.portfolio_values).set_index("Date")

        # Calculate total return
        total_return = (self.portfolio_value - self.init_capital) / self.init_capital
        print(f"Total Return: {total_return * 100:.2f}%")

        # Compute daily returns
        performance_df["Daily Return"] = performance_df["Portfolio Value"].pct_change()

        # Calculate Sharpe Ratio (assuming 252 trading days in a year)
        mean_daily_return = performance_df["Daily Return"].mean()
        std_daily_return = performance_df["Daily Return"].std()
        sharpe_ratio = (mean_daily_return / std_daily_return) * (252 ** 0.5)
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

        # Calculate Maximum Drawdown
        rolling_max = performance_df["Portfolio Value"].cummax()
        drawdown = performance_df["Portfolio Value"] / rolling_max - 1
        max_drawdown = drawdown.min()
        print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")

        # Plot the portfolio value over time
        performance_df["Portfolio Value"].plot(
            title="Portfolio Value Over Time", figsize=(12, 6)
        )
        plt.ylabel("Portfolio Value ($)")
        plt.xlabel("Date")
        plt.show()

        return performance_df

def main():
    start = datetime.now() - timedelta(days=730)
    end = datetime.now()
    backtester = Backtester("ERJ", start, end, 10000)
    backtester.run_backtesting()
    backtester.analyze_performance()

if __name__ == "__main__":
    main()