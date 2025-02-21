from matplotlib import pyplot
import matplotlib.dates as mdates
from typing import List
import pandas as pd

class custom_plot():
    def __init__(self, ticker:str, prices:pd.DataFrame):
        self.ticker:str = ticker
        # self.tickers = []
        self.prices:pd.DataFrame = prices
        self.fig, self.ax = pyplot.subplots()
        self.plot(prices, "prices", "blue")
        self.ax.set_title(f"{ticker} prices")

    def highlight(self, data_to_highlight: pd.DataFrame, period:int, max_diff:int, color:str):
        df = data_to_highlight.dropna(axis=0, inplace=False)
        for i in range(len(df.index)):
            if not pd.isna(df.iloc[i]):
                end_date = df.index[i] + pd.Timedelta(days=period)
                self.ax.axvspan(
                    df.index[i],
                    end_date,
                    color=color,
                    alpha=( (max_diff - abs(df.iloc[i])) / max_diff )**20/3 + 0.1
                )

        # Highlight the final period
        self.ax.axvspan(
            self.prices.index[period],
            self.prices.index[0],
            color="red",
            alpha=0.3
        )

    def plot(self, data_to_plot:pd.DataFrame, metric:str, color:str):
        df = data_to_plot.dropna(axis=0, inplace=False)
        self.ax.plot(df.index, df.values, color=color, label=metric)

        # Format x-axis as dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        self.fig.autofmt_xdate()

        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Value')

    def show(self):
        self.ax.legend()
        pyplot.show()