import pandas as pd
from typing import List, Tuple

def sattern(financial_metrics: pd.DataFrame, period: int = 10):
    # Find periods where the data is similar
    datapoints_per_period = period * 8
    stock_prices = financial_metrics["prices"]
    comp_start_index = len(stock_prices) - period - 1

    print(stock_prices.iloc[0])

    curr_period_diff = []
    for i in range(comp_start_index, len(stock_prices)-1):
        curr_period_diff.append(stock_prices.iloc[i+1] - stock_prices.iloc[i])

    curr_comp_start = 0
    curr_comp_length = 0
    curr_comp_diff = 0
    similar_periods: List[Tuple[int, float]] = []   # Store start index and difference of each period
    index = 0

    while(index < (comp_start_index - datapoints_per_period)):
        curr_diff = curr_period_diff[curr_comp_length] - (stock_prices.iloc[curr_comp_start + curr_comp_length + 1] - stock_prices.iloc[curr_comp_start + curr_comp_length])
        curr_diff_squared = curr_diff * abs(curr_diff)
        curr_comp_diff += curr_diff_squared

        curr_comp_length += 1
        index += 1

        if curr_diff_squared > 15 or abs(curr_comp_diff) > 15:
            curr_comp_start += 1
            index = curr_comp_start
            curr_comp_length = 0
            curr_comp_diff = 0
        elif curr_comp_length >= datapoints_per_period:
            similar_periods.append( (curr_comp_start, curr_comp_diff) )
            index = curr_comp_start + datapoints_per_period // 2
            curr_comp_start = index
            curr_comp_length = 0
            curr_comp_diff = 0
    
    if len(similar_periods) == 0:
        print(f"No periodicity found.")
        return

    # Use similar periods to predict the next stock price
    hourwise_difference: List[float] = []
    for i in range(datapoints_per_period):
        hourwise_difference.append(0.0)
        for x in range(len(similar_periods)):
            index = similar_periods[x][0] + i
            # Weight by the difference
            hourwise_difference[i] += (stock_prices.iloc[index + 1] - stock_prices.iloc[index]) * similar_periods[x][1]

    # Normalize
    total_difference = sum([similar_periods[i][1] for i in range(len(similar_periods))])
    hourwise_difference = [price/total_difference for price in hourwise_difference]

    # Calculate price movements and dates
    hourwise_price_prediction: List[float] = []