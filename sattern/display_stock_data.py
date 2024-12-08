from matplotlib import pyplot
import matplotlib.dates as mdates
from datetime import datetime
from sattern.get_stock_data import history_data

"""display_stock_data.py

All stock visualization and graphing is done here. 
"""

def highlight_pattern(data: history_data, start_index: int, end_index: int):
    fig, ax = display_stock_price(data=data, show=False)

    ax.axvspan(start_index, end_index, color="blue", alpha=0.3)
    pyplot.show()


def display_stock_price(data: history_data, show: bool = True):
    # Create a figure and axes
    fig, ax = pyplot.subplots()
    
    # Use the index of the data points for consistent spacing
    x_values = range(len(data.date))
    
    # Plot the data
    ax.plot(x_values, data.close)
    
    # Optionally set custom x-tick labels to display dates at specific intervals
    tick_positions = x_values[::5]  # Adjust the step as needed
    tick_labels = [datetime.fromtimestamp(int(data.date[i])).strftime('%m-%d') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Set labels and title
    ax.set_xlabel('Data Points')
    ax.set_ylabel('Close Value')
    ax.set_title(f'Stock Price Plot ({data.period})')
    
    # Adjust layout to prevent label cutoff
    fig.tight_layout()
    
    # Show the plot only if specified
    if show:
        pyplot.show()

    return fig, ax