from matplotlib import pyplot
import matplotlib.dates as mdates
from datetime import datetime
from sattern.get_stock_data import history_data
from typing import List

"""display_stock_data.py

All stock visualization and graphing is done here."""

def highlight_pattern(data: history_data, start_indicies: List[int], end_indicies: List[int]):
    fig, ax = display_stock_price(data=data, show=False)

    for start, end in zip(start_indicies, end_indicies):
        color = "red" if end == end_indicies[-1] else "blue"
        ax.axvspan(start, end, color=color, alpha=0.3)

    pyplot.show()


def display_stock_price(data: history_data, show: bool = True):
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