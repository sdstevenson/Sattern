from matplotlib import pyplot
import sattern.get_stock_data as get_stock_data

"""display_stock_data.py

All stock visualization will goes here. Expects a json as formatted by get_stock_data.py.
"""

def display_stock_price(ticker: str = "AAPL", period: str = "1mo"):
    data = get_stock_data.load_history_data(ticker, period)
    # Create a figure and axes
    fig, ax = pyplot.subplots()

    # Plot the data
    ax.plot(data.date, data.close, marker='o')

    # Set labels
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Value')
    ax.set_title(f'Stock price plot ({period})')

    # Show the plot
    pyplot.show()