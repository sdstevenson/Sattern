from matplotlib import pyplot
import matplotlib.dates as mdates
from datetime import datetime
import sattern.get_stock_data as get_stock_data

"""display_stock_data.py

All stock visualization will goes here. Expects a json as formatted by get_stock_data.py.
"""

def display_stock_price(ticker: str = "AAPL", period: str = "1mo"):
    data = get_stock_data.load_history_data(ticker, period)
    
    # Create a figure and axes
    fig, ax = pyplot.subplots()
    
    # Use the index of the data points for consistent spacing
    x_values = range(len(data.date))
    
    # Plot the data
    ax.plot(x_values, data.close, marker='o')
    
    # Optionally set custom x-tick labels to display dates at specific intervals
    tick_positions = x_values[::5]  # Adjust the step as needed
    tick_labels = [datetime.fromtimestamp(int(data.date[i])).strftime('%m-%d') for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Set labels and title
    ax.set_xlabel('Data Points')
    ax.set_ylabel('Close Value')
    ax.set_title(f'Stock Price Plot ({period})')
    
    # Adjust layout to prevent label cutoff
    fig.tight_layout()
    
    # Show the plot
    pyplot.show()