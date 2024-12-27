from typing import List, Tuple
from sattern.src.get_stock_data import stock_data

"""process_data.py

All data processing will originate in here."""

def extract_curves(stock_data: stock_data, max_difference: int = 15, comp_period: int = 10, granularity: int = 1):
    """
    Extracts pattern data by comparing past stock movement to current stock movement and predicting the next moves.
    Args:
        data (history_data): All relevent stock data.
        max_deviance (int): The maximum allowed deviance for a pattern match. Defaults to 20.
        comp_period (int): The period over which to compare stock movements in business days. Defaults to 10.
        granularity (int): The step size for the sliding window comparison. Defaults to 1.
    Returns:
        extracted_data: An object containing the start indices, end indices, and differences of the extracted patterns.
    """
    if (granularity > comp_period):
        return
    comp_period = int(comp_period * 7.5)

    stock_data.max_difference = max_difference

    # Calculate the indices of the period we are comparing to (most recent <period> elements)
    comp_end = len(stock_data.close) - 1
    comp_start = comp_end - comp_period

    # Start the running comparison here
    curr_length = 0     # Current length of period we are comparing
    difference = 0      # Count of the added difference compared to reference period
    curr_start = 0      # Start of the current period we are comparing
    i = 0
    while (i < (comp_start - (comp_period + granularity))):
        # Find the difference between the change in price over current period and the period we are comparing to
        curr_diff = ( stock_data.close[comp_start + curr_length + granularity]
                    - stock_data.close[comp_start + curr_length]
                    -(stock_data.close[curr_start + curr_length + granularity]
                    - stock_data.close[curr_start + curr_length])
                    )
        difference += curr_diff * abs(curr_diff)    # Square but keep the sign
        # Increment the length of current comparison period and our i index
        curr_length += granularity
        i = i + granularity
        if (abs(curr_diff * abs(curr_diff)) > max_difference) or (abs(difference) > max_difference): 
            # Difference is too great, reset and begin comparing again at curr_start + granularity
            curr_start += granularity
            i = curr_start
            difference = 0
            curr_length = 0
        elif curr_length >= (comp_period*granularity):
            # Store this period and start again at curr_start + comp_period/2
            stock_data.start_indicies.append(curr_start)
            stock_data.end_indicies.append(curr_start + comp_period)
            stock_data.difference.append(difference)
            i = curr_start + int(comp_period / 2)
            difference = 0
            curr_start = i
            curr_length = 0

    # Store the most recent period
    stock_data.start_index = comp_start
    stock_data.end_index = comp_end
    stock_data.difference.append(0)


def predict_next_movement(stock_data: stock_data, comp_period: int = 10) -> Tuple[List[int], List[float]]:
    """
    Takes in extracted curves and averages out, weighted by data, the stock movement comp_period after the end of each curve. 
    Predicts next stock price based on this.
    Args:
        data (history_data): All relevent stock data.
        extracted_data (extracted_data): Periods to compare.
        comp_period (int): Period over which we are comparing in business days. Default is 10. 
    Returns:
        Tuple[
            predicted_datas (List[int]): Arbitrary dates for plotting.
            predicted_prices (List[float]): Predicted prices.
        ]
    """
    if not stock_data.processed:
        extract_curves(stock_data=stock_data, comp_period=comp_period)
        stock_data.processed = True

    comp_period = int(comp_period * 7.5)   # Days * data points/day
    averaged_difference: List[float] = []

    """
    Calculating stock price instead of stock difference. Recalculate with the same formula, calculating stock difference. 
    """

    for i in range(comp_period):
        averaged_difference.append(0.0)
        for x in range(len(stock_data.end_indicies)):
            index = stock_data.end_indicies[x] + i
            averaged_difference[i] += (stock_data.close[index + 1] - stock_data.close[index]) * stock_data.difference[x]

    # Now divide by the overall weights
    total_difference = sum(stock_data.difference)
    if total_difference != 0:
        averaged_difference = [price/total_difference for price in averaged_difference]
    else:
        print("Sum of extracted_data.difference is zero, cannot divide by zero.")

    # And calculate price movements
    predicted_prices = []
    for i in range(len(averaged_difference)):
        if i != 0:
            predicted_prices.append(predicted_prices[i-1] + averaged_difference[i])
        else:
            predicted_prices.append(stock_data.close[-1] + averaged_difference[0])

    # Set a generic data value
        # TO DO: Update this to return actual dates
    predicted_dates = [stock_data.date[-1] for _ in range(len(predicted_prices))]

    print(f"{stock_data.ticker} will hit {predicted_prices[-1]} in {comp_period/7.5} business days")

    stock_data.predicted_dates = predicted_dates
    stock_data.predicted_prices = predicted_prices