from matplotlib import pyplot
import matplotlib.dates as mdates
from datetime import datetime
from sattern.src.get_stock_data import stock_data
from typing import List

"""display_stock_data.py

All stock visualization and graphing is done here."""

def highlight_pattern(stock_data: stock_data, show: bool = True):
    """
    Highlights selected curves on the plot with the color specified. Most recent data is highlighted red.
    Args:
        stock_data (stock_data): All relevent stock data.
        show (bool): Display stock data. Defaults to True.
    Returns:
        None
    """
    fig, ax = display_stock_price(stock_data=stock_data)

    for start, difference in zip(stock_data.comp.start_indicies, stock_data.comp.difference):
        end = start + stock_data.comp.comp_period * 7.5
        ax.axvspan(
            start, 
            end, 
            color="green", 
            alpha=( (stock_data.comp.max_difference - abs(difference)) / stock_data.comp.max_difference )**20/3
        )
    ax.axvspan(stock_data.comp.comp_start_index, len(stock_data.close)-1, color="red", alpha=0.3)

    if show:
        pyplot.show()

    return fig, ax


def display_stock_price(stock_data: stock_data, show: bool = False):
    """
    This function plots the historical stock data provided and optionally displays the plot.
    Args:
        stock_data (stock_data): All relevent stock data.
        show (bool): Display stock data. Defaults to False.
    Returns:
        tuple: A tuple containing the figure and axes objects of the plot.
    """
    fig, ax = pyplot.subplots()
    
    # Plot the actual stock prices
    x_values = range(len(stock_data.date))
    ax.plot(x_values, stock_data.close, color='blue', label='Actual Price')
    
    # Plot predicted prices if provided
    if stock_data.comp.processed:
        predicted_x = range(len(stock_data.date), len(stock_data.date) + len(stock_data.comp.predicted_dates))
        ax.plot(predicted_x, stock_data.comp.predicted_prices, color='green', label='Predicted Price')

    # Adjust the x-tick labels as needed
    if (stock_data.period == 1):
        tick_positions = x_values[::100]
    elif (stock_data.period == 2):
        tick_positions = x_values[::200]
    else:
        tick_positions = x_values[::500]
    tick_positions = list(tick_positions)

    # Add last date if not already included
    last_index = len(x_values) - 1
    if last_index not in tick_positions:
        tick_positions.append(last_index)
        tick_positions.sort()

    tick_labels = [datetime.fromtimestamp(int(stock_data.date[i])).strftime('%m-%d') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    ax.set_xlabel('Data Points')
    ax.set_ylabel('Close Value')
    ax.set_title(f'{stock_data.ticker} Stock Price Plot ({stock_data.period})')
    
    # Adjust layout to prevent label cutoff
    fig.tight_layout()
    
    if show:
        pyplot.show()

    return fig, ax