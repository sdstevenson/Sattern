from matplotlib import pyplot
import matplotlib.dates as mdates
from datetime import datetime
from sattern.get_stock_data import history_data
from sattern.process_data import extracted_data
from typing import List

"""display_stock_data.py

All stock visualization and graphing is done here."""

def highlight_pattern(history_data: history_data, extracted_data: extracted_data, min_confidence: float = 0.0, color: str = "blue"):
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
    fig, ax = display_stock_price(data=history_data, show=False)

    for start, end, difference in zip(extracted_data.start_indicies, extracted_data.end_indicies, extracted_data.difference):
        # print(f"Start: {start}, End: {end}, Difference: {difference}")
        if (end == extracted_data.end_indicies[-1]):
            ax.axvspan(start, end, color="red", alpha=0.3)
        elif (abs(difference) >= min_confidence):
            ax.axvspan(start, end, color=color, alpha=(abs(difference) / 2))

    pyplot.show()


def display_stock_price(data: history_data):
    """
    Plots stock data.
    Args:
        data (history_data): All relevent stock data.
    Returns:
        tuple: A tuple containing the figure and axes objects of the plot.
    This function plots the historical stock data provided and optionally displays the plot.
    """
    # Create a figure and axes
    fig, ax = pyplot.subplots()
    
    # Use the index of the data points for consistent spacing
    x_values = range(len(data.date))
    
    # Plot the data
    ax.plot(x_values, data.close)
    
    # Adjust the x-tick labels to display dates at specific intervals
    if (data.period == "1mo"):
        tick_positions = x_values[::10]
    elif (data.period == "1y"):
        tick_positions = x_values[::100]
    else:
        tick_positions = x_values[::500]

    tick_labels = [datetime.fromtimestamp(int(data.date[i])).strftime('%m-%d') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Set labels and title
    ax.set_xlabel('Data Points')
    ax.set_ylabel('Close Value')
    ax.set_title(f'{data.ticker} Stock Price Plot ({data.period})')
    
    # Adjust layout to prevent label cutoff
    fig.tight_layout()
    
    pyplot.show()

    return fig, ax