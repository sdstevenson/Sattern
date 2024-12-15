from matplotlib import pyplot
import matplotlib.dates as mdates
from datetime import datetime
from sattern.get_stock_data import history_data
from sattern.process_data import extracted_data
from typing import List

"""display_stock_data.py

All stock visualization and graphing is done here."""

def highlight_pattern(history_data: history_data, extracted_data: extracted_data, min_confidence: float = 0.0):
    """highlight_pattern
    Args:
    Returns:
    """
    fig, ax = display_stock_price(data=history_data, show=False)

    for start, end, difference in zip(extracted_data.start_indicies, extracted_data.end_indicies, extracted_data.difference):
        # print(f"Start: {start}, End: {end}, Difference: {difference}")
        if (end == extracted_data.end_indicies[-1]):
            ax.axvspan(start, end, color="red", alpha=0.3)
        elif (abs(difference) >= min_confidence):
            ax.axvspan(start, end, color="blue", alpha=(abs(difference) / 2))

    pyplot.show()


def display_stock_price(data: history_data, show: bool = True):
    """display_stock_price
    Args:
        data (history_data): The historical stock data to be plotted.
        show (bool): Whether to display the plot immediately. Defaults to True.
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
    
    # Show the plot only if specified
    if show:
        pyplot.show()

    return fig, ax