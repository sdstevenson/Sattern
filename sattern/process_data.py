from typing import List
from sattern.get_stock_data import history_data

"""process_data.py

All data processing will originate in here."""

class extracted_data:
    def __init__(self):
        self.start_indicies: List[int] = []
        self.end_indicies: List[int] = []
        self.final_start: int
        self.final_end: int
        self.max_difference: int
        self.difference: List[float] = []

def extract_curves(data: history_data, max_difference: int = 15, comp_period: int = 10, granularity: int = 1) -> extracted_data:
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

    return_data = extracted_data()
    return_data.max_difference = max_difference

    # Calculate the indices of the period we are comparing to (most recent <period> elements)
    comp_end = len(data.close) - 1
    comp_start = comp_end - comp_period

    # Start the running comparison here
    curr_length = 0     # Current length of period we are comparing
    difference = 0      # Count of the added difference compared to reference period
    curr_start = 0      # Start of the current period we are comparing
    i = 0
    while (i < (comp_start - (comp_period + granularity))):
        # Find the difference between the change in price over current period and the period we are comparing to
        curr_diff = ( data.close[comp_start + curr_length + granularity]
                    - data.close[comp_start + curr_length]
                    -(data.close[curr_start + curr_length + granularity]
                    - data.close[curr_start + curr_length])
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
            return_data.start_indicies.append(curr_start)
            return_data.end_indicies.append(curr_start + comp_period)
            return_data.difference.append(difference)
            i = curr_start + int(comp_period / 2)
            difference = 0
            curr_start = i
            curr_length = 0

    # Store the most recent period
    return_data.final_start = comp_start
    return_data.final_end = comp_end
    return_data.difference.append(0)

    return return_data


def predict_next_movement(data: history_data, extracted_data: extracted_data, comp_period: int = 10):
    """
    Takes in extracted curves and averages out, weighted by data, the stock movement comp_period after the end of each curve. 
    Predicts next stock price based on this.
    Args:
        data (history_data): All relevent stock data.
        extracted_data (extracted_data): Periods to compare.
        comp_period (int): Period over which we are comparing in business days. Default is 10. 
    Returns:
        None
    """
    comp_period = int(comp_period * 7.5)   # Days * data points/day
    averaged_difference: List[float] = []

    """
    Calculating stock price isntead of stock difference. Recalculate with the same formula, calculating stock difference. 
    """

    for i in range(comp_period):
        averaged_difference.append(0.0)
        for x in range(len(extracted_data.end_indicies)):
            index = extracted_data.end_indicies[x] + i
            averaged_difference[i] += (data.close[index + 1] - data.close[index]) * extracted_data.difference[x]

    # Now divide by the overall weights
    averaged_difference = [price/sum(extracted_data.difference) for price in averaged_difference]

    # And calculate price movements
    predicted_prices = []
    for i in range(len(averaged_difference)):
        if i != 0:
            predicted_prices.append(predicted_prices[i-1] + averaged_difference[i])
        else:
            predicted_prices.append(data.close[-1] + averaged_difference[0])

    # Set a generic data value
    predicted_dates = [data.date[-1] for _ in range(len(predicted_prices))]

    print(f"{data.ticker} will hit {predicted_prices[-1]} in {comp_period/7.5} business days")

    return predicted_dates, predicted_prices