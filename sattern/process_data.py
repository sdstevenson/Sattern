from typing import List
from sattern.get_stock_data import history_data

"""process_data.py

All data processing will originate in here."""

class extracted_data:
    def __init__(self):
        self.start_indicies: List[int] = []
        self.end_indicies: List[int] = []
        self.difference: List[float] = []

def extract_curves(data: history_data, max_deviance: int = 20, comp_period: int = 10, granularity: int = 1) -> extracted_data:
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
    comp_period = int(comp_period * 7.5)
    if (granularity > comp_period):
        return

    return_data = extracted_data()

    # Calculate the indices of the period we are comparing to (most recent <period> elements)
    comp_end = len(data.close) - 1
    comp_start = comp_end - comp_period

    # Start the running comparison here
    curr_length = 0
    difference = 0
    curr_start = 0
    i = 0
    while (i < (comp_start - (comp_period + granularity))):
        curr_diff = (data.close[comp_start + curr_length + granularity] - data.close[comp_start + curr_length]) - (data.close[curr_start + curr_length + granularity] - data.close[curr_start + curr_length])
        difference += curr_diff * abs(curr_diff)    # Square but keep the sign
        curr_length = curr_length + 1
        i = i + granularity
        if abs(difference) > max_deviance: 
            i = curr_start + granularity
            difference = 0
            curr_start = i
            curr_length = 0
        elif curr_length >= comp_period:
            return_data.start_indicies.append(curr_start)
            return_data.end_indicies.append(curr_start + comp_period)
            return_data.difference.append(difference / max_deviance)    # Get confidence as a percentage
            i = curr_start + int(comp_period / 2)
            # i = curr_start + period
            difference = 0
            curr_start = i
            curr_length = 0

    # Finally, append the most recent pattern to the end
    return_data.start_indicies.append(comp_start)
    return_data.end_indicies.append(comp_end)
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
    # Well take in a extracted_data object, containing all the similar periods of the stock. 
    # For each similar period, average the next period data points
    comp_period = int(comp_period * 7.5)   # Normalize to the number of data points in this period
    averaged_difference: List[int] = []
    for i in range(0, len(extracted_data.end_indicies) - 2):
        # Calculate an average value over the next period
        sum = 0
        for x in range(0, comp_period):
            sum += data.close[extracted_data.start_indicies[i] + x]
        averaged_difference.append(data.close[i] - (sum / comp_period))
        # Print the average for each period
        # print(f"{i}: {averaged_values[-1]}\n")
    # Combine the next period averages into one number weighted by confidence
    overall_difference: int = 0
    for i in range(0, len(averaged_difference)):
        overall_difference += averaged_difference[i] * extracted_data.difference[i]
    # Print this
    print(f"Stock should hit {data.close[-1] + (overall_difference / comp_period)} in {comp_period} business days.")