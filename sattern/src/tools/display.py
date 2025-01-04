from matplotlib import pyplot
import matplotlib.dates as mdates
from datetime import datetime
from sattern.src.tools.api import get_financial_metrics
from typing import List
import pandas as pd

def display(data:pd.DataFrame, metrics_to_plot:List[str], ticker:str, period:int=10):
    fig, ax = None, None
    for metric in metrics_to_plot:
        if "highlight" in metric:
            fig, ax = highlight(data[metric], fig, ax, period)
        else:
            if metric == "prices":
                color = "blue"
            elif metric == "sattern":
                color = "green"
            fig, ax = plot_metric(data[metric], fig, ax, color)

    ax.set_title(f"{ticker} Stock")
    pyplot.show()

def highlight(data: pd.DataFrame, fig=None, ax=None, period:int=10):
    if fig is None or ax is None:
        fig, ax = pyplot.subplots()

    datapoint_per_period = period * 10
    for i in range(len(data)):
        if not pd.isna(data.iloc[i]):
            ax.axvspan(
                data.index[i],
                data.index[i + datapoint_per_period],
                color="green",
                alpha=( (15 - abs(data.iloc[i])) / 15 )**20/3
            )

    return fig, ax

def plot_metric(data:pd.DataFrame, fig=None, ax=None, color:str="blue"):
    if fig is None or ax is None:
        fig, ax = pyplot.subplots()

    # Plot the DataFrame values using its index for the x-axis
    ax.plot(data.index, data.values, color=color, label='Metric')

    # Format x-axis as dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()

    ax.set_xlabel('Date')
    ax.set_ylabel('Value')

    # Return the figure and axes to allow further plotting
    return fig, ax
