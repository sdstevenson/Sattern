from typing import List
from sattern.get_stock_data import history_data

"""process_data.py

All data processing will originate in here."""

class extracted_data:
    def __init__(self):
        self.start_indicies: List[int] = []
        self.end_indicies: List[int] = []
        self.difference: List[int] = []

def extract_curves(data: history_data, max_deviance: int = 13, period: int = 200) -> extracted_data:
    """
    Core functionality of sattern will occur here.
    Extracts pattern data by comparing past stock movement to current stock movement and predicting the next moves.
    """
    return_data = extracted_data()

    # Calculate the indices of the most recent period we are looking at
    curr_end = len(data.close)
    curr_start = curr_end - period

    # print(f"curr start: {curr_start}, curr_end: {curr_end}\n")

    # Start running the 'sliding window' comparison with older data
    for i in range(0, curr_start - period, period // 2):
        difference = 0

        # Compare every fifth index
        for x in range(0, period - 10, 5):
            current_idx = i + x
            reference_idx = curr_start + x
            
            # Bounds checking
            if reference_idx + 5 >= curr_end or current_idx + 5 >= curr_end:
                difference = 10000
                break

            # Calculate difference between patterns
            difference += (data.close[reference_idx] - data.close[reference_idx + 5]) - (data.close[current_idx] - data.close[current_idx + 5])
            if abs(difference) > max_deviance:
                break

        # Check that we are not out of bounds and that the difference isnt larger than the deviance
        if (abs(difference) <= max_deviance) and ((i + period) < curr_end):
            # print(f"Data added from {i} to {i+period}")
            return_data.start_indicies.append(i)
            return_data.end_indicies.append(i + period)
            return_data.difference.append(difference)

    # Finally, append the most recent pattern to the end
    return_data.start_indicies.append(curr_start)
    return_data.end_indicies.append(curr_end)

    return return_data


