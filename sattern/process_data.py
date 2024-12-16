from typing import List
from sattern.get_stock_data import history_data

"""process_data.py

All data processing will originate in here."""

class extracted_data:
    """
    A class used to represent extracted data with start and end indices and their differences.
    Attributes
    ----------
        start_indicies : List[int]
            A list to store the starting indices.
        end_indicies : List[int]
            A list to store the ending indices.
        difference : List[float]
            A list to store the differences between start and end indices.
    Methods
    -------
        __init__():
            Initializes the extracted_data class with empty lists for start_indicies, end_indicies, and difference.
    """

    def __init__(self):
        self.start_indicies: List[int] = []
        self.end_indicies: List[int] = []
        self.difference: List[float] = []

def extract_curves(data: history_data, max_deviance: int = 20, period: int = 100, granularity: int = 1) -> extracted_data:
    """extract_curves
    Args:
        data (history_data): The historical stock data containing closing prices.
        max_deviance (int): The maximum allowed deviance for a pattern match. Defaults to 20.
        period (int): The period over which to compare stock movements. Defaults to 100.
        granularity (int): The step size for the sliding window comparison. Defaults to 1.
    Returns:
        extracted_data: An object containing the start indices, end indices, and differences of the extracted patterns.
    
    Extracts pattern data by comparing past stock movement to current stock movement and predicting the next moves.
    """
    if (granularity > period):
        return

    return_data = extracted_data()

    # Calculate the indices of the period we are comparing to (most recent <period> elements)
    comp_end = len(data.close) - 1
    comp_start = comp_end - period

    # Start the running comparison here
    curr_length = 0
    difference = 0
    curr_start = 0
    i = 0
    while (i < (comp_start - (period + granularity))):
        curr_diff = (data.close[comp_start + curr_length + granularity] - data.close[comp_start + curr_length]) - (data.close[curr_start + curr_length + granularity] - data.close[curr_start + curr_length])
        difference += curr_diff * abs(curr_diff)    # Square but keep the sign
        curr_length = curr_length + 1
        i = i + granularity
        if abs(difference) > max_deviance: 
            i = curr_start + granularity
            difference = 0
            curr_start = i
            curr_length = 0
        elif curr_length >= period:
            return_data.start_indicies.append(curr_start)
            return_data.end_indicies.append(curr_start + period)
            return_data.difference.append(difference / max_deviance)    # Get confidence as a percentage
            i = curr_start + int(period / 2)
            # i = curr_start + period
            difference = 0
            curr_start = i
            curr_length = 0

    # Finally, append the most recent pattern to the end
    return_data.start_indicies.append(comp_start)
    return_data.end_indicies.append(comp_end)
    return_data.difference.append(0)

    return return_data


def predict_next_movement(data: history_data, extracted_data: extracted_data, period: int = 100):
    # Well take in a extracted_data object, containing all the similar periods of the stock. 
    # For each similar period, average the next period data points
    averaged_difference: List[int] = []
    for i in range(0, len(extracted_data.end_indicies) - 2):
        # Calculate an average value over the next period
        sum = 0
        for x in range(0, period):
            sum += data.close[extracted_data.start_indicies[i] + x]
        averaged_difference.append(data.close[i] - (sum / period))
        # Print the average for each period
        # print(f"{i}: {averaged_values[-1]}\n")
    # Combine the next period averages into one number weighted by confidence
    overall_difference: int = 0
    for i in range(0, len(averaged_difference)):
        overall_difference += averaged_difference[i] * extracted_data.difference[i]
    # Print this
    print(data.close[-1] + (overall_difference / period))