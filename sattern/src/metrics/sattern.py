import pandas as pd
from typing import List, Tuple
import sattern.src.tools.weekday as weekday
from datetime import datetime

def sattern(financial_metrics: pd.DataFrame, period: int = 10, max_diff: int = 2) -> Tuple[pd.DataFrame, str]:
    # Find periods where the data is similar
    datapoints_per_period = period * 8
    stock_prices = financial_metrics["prices"]
    comp_start_index = len(stock_prices) - datapoints_per_period - 1

    curr_period_diff = []
    for i in range(comp_start_index-1, len(stock_prices)-1):
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

        if abs(curr_diff_squared) > max_diff or abs(curr_comp_diff) > max_diff:
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
    else:
        # print(f"Similar Periods: {similar_periods}")
        data = [diff for _, diff in similar_periods]
        index = [stock_prices.index[start] for start, _ in similar_periods]
        highlight_df = pd.DataFrame(data=data, index=index, columns=["sattern_highlight"])

    # Use similar periods to predict the next stock price
    hourwise_difference: List[float] = []
    for i in range(datapoints_per_period):
        hourwise_difference.append(0.0)
        for x in range(len(similar_periods)):
            index = similar_periods[x][0] + i
            # Weight by the difference
            hourwise_difference[i] += (stock_prices.iloc[index + 1] - stock_prices.iloc[index]) * (max_diff - similar_periods[x][1])

    # Normalize
    total_difference = sum([similar_periods[i][1] for i in range(len(similar_periods))])
    hourwise_difference = [price/total_difference for price in hourwise_difference]
    # print(f"Hourwise difference: {hourwise_difference}")
    # print(f"Sum hourwise: {sum(hourwise_difference)}")

    # Calculate price movements and dates
    hourwise_price_prediction: List[float] = []
    weekday_tool = weekday.weekday()
    hourwise_dates: List[datetime] = weekday_tool.get_next_n_datetimes(n=datapoints_per_period, start=stock_prices.index[-1])

    for i in range(len(hourwise_difference)):
        if i != 0:
            hourwise_price_prediction.append(hourwise_price_prediction[i-1] + hourwise_difference[i])
        else:
            hourwise_price_prediction.append(stock_prices.iloc[-1] + hourwise_difference[0])

    percent_change = (hourwise_price_prediction[-1] - stock_prices.iloc[-1]) / stock_prices.iloc[-1]
    action = ""

    if abs(percent_change) < 0.02:
        action = "Hold"
    elif percent_change > 0.02:
        if percent_change > 0.10:
            action = "Strong Buy"
        else:
            action = "Buy"
    elif percent_change < 0.02:
        if percent_change < 0.10:
            action = "Strong Sell"
        else:
            action = "Sell"

    prediction_df = pd.DataFrame(data=hourwise_price_prediction, index=hourwise_dates, columns=["sattern"])
    highlight_df = highlight_df[~highlight_df.index.duplicated(keep='first')]
    prediction_df = prediction_df[~prediction_df.index.duplicated(keep='first')]
    
    combined_df = pd.concat([highlight_df, prediction_df], axis=1)
    return combined_df, action