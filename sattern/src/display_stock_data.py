from matplotlib import pyplot
import matplotlib.dates as mdates
from datetime import datetime
from sattern.src.get_stock_data import stock_data
from typing import List

"""display_stock_data.py

All stock visualization and graphing is done here."""

def highlight_pattern(stock_data: stock_data, min_confidence: float = 0.2, color: str = "blue", show: bool = True):
    """
    Highlights selected curves on the plot with the color specified. Most recent data is highlighted red.
    Args:
        history_data (history_data): All relevent stock data.
        extracted_data (extracted_data): Periods to highlight.
        min_confidence (int): Minimum confidence at which to highlight stock curve. Default is "0.0".
        color (str): Color to highlight periods. Default is "blue".
    Returns:
        None
    """
    fig, ax = display_stock_price(stock_data=stock_data)

    for start, end, difference in zip(stock_data.start_indicies, stock_data.end_indicies, stock_data.difference):
        if abs(difference) >= min_confidence:
            ax.axvspan(
                start, 
                end, 
                color=color, 
                alpha=( (stock_data.max_difference - abs(difference)) / stock_data.max_difference )**20/3
            )
    ax.axvspan(stock_data.start_index, stock_data.end_index, color="red", alpha=0.3)

    if show:
        pyplot.show()

    return fig, ax


def display_stock_price(stock_data: stock_data, show: bool = False):
    """
    Plots stock data.
    Args:
        data (history_data): All relevent stock data.
        show (bool): Display stock data. Defaults to True.
    Returns:
        tuple: A tuple containing the figure and axes objects of the plot.
    This function plots the historical stock data provided and optionally displays the plot.
    """
    # Create a figure and axes
    fig, ax = pyplot.subplots()
    
    # Plot the actual stock prices
    x_values = range(len(stock_data.date))
    ax.plot(x_values, stock_data.close)
    
    # Plot predicted prices if provided
    if stock_data.processed:
        predicted_x = range(len(stock_data.date), len(stock_data.date) + len(stock_data.predicted_dates))
        ax.plot(predicted_x, stock_data.predicted_prices, color='green', label='Predicted Price')


    # Adjust the x-tick labels to display dates at specific intervals
    if (stock_data.period == "1mo"):
        tick_positions = x_values[::10]
    elif (stock_data.period == "1y"):
        tick_positions = x_values[::100]
    else:
        tick_positions = x_values[::500]

    tick_labels = [datetime.fromtimestamp(int(stock_data.date[i])).strftime('%m-%d') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Set labels and title
    ax.set_xlabel('Data Points')
    ax.set_ylabel('Close Value')
    ax.set_title(f'{stock_data.ticker} Stock Price Plot ({stock_data.period})')
    
    # Adjust layout to prevent label cutoff
    fig.tight_layout()
    
    if show:
        pyplot.show()

    return fig, ax