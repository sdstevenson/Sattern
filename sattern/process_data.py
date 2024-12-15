from typing import List
from sattern.get_stock_data import history_data

"""process_data.py

All data processing will originate in here."""

class extracted_data:
    def __init__(self):
        self.start_indicies: List[int] = []
        self.end_indicies: List[int] = []
        self.difference: List[float] = []

def extract_curves(data: history_data, max_deviance: int = 20, period: int = 100, granularity: int = 1) -> extracted_data:
    """
    Core functionality of sattern will occur here.
    Extracts pattern data by comparing past stock movement to current stock movement and predicting the next moves.
    Increments over the data in periods of size period.
    """
    if (granularity > period):
        return

    return_data = extracted_data()

    # Calculate the indices of the period we are comparing to (most recent <period> elements)
    comp_end = len(data.close) - 1
    comp_start = comp_end - period

    # Start running the 'sliding window' comparison with older data
    """
    Create a running average queue, searching through programatically until getting a good match.
    """
    curr_length = 0
    difference = 0
    curr_start = 0
    i = 0
    # for i in range(0, comp_start - (period + granularity), granularity):
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


