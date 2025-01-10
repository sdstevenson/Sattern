import pandas as pd
from typing import List, Tuple
import sattern.src.tools.weekday as weekday
from datetime import datetime

def sattern(financial_metrics: pd.DataFrame, period: int = 10, max_diff: int = 2) -> Tuple[pd.DataFrame, str]:
    # Find periods where the data is similar
    stock_prices = financial_metrics["prices"]
    comp_start_index = len(stock_prices) - period - 1

    # For each element in the current period, find the difference to the previous element
    curr_period_diff = []
    for i in range(comp_start_index-1, len(stock_prices)-1):
        curr_period_diff.append(stock_prices.iloc[i+1] - stock_prices.iloc[i])

    curr_comp_start = 0
    curr_comp_length = 0
    curr_comp_diff = 0
    similar_periods: List[Tuple[int, float]] = []   # Store start index and difference of each period
    index = 0

    while(index < (comp_start_index - period)):
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
        elif curr_comp_length >= period:
            similar_periods.append( (curr_comp_start, curr_comp_diff) )
            index = curr_comp_start + period // 2
            curr_comp_start = index
            curr_comp_length = 0
            curr_comp_diff = 0
    
    if len(similar_periods) == 0:
        return pd.DataFrame(columns=["sattern", "sattern_highlight"]), "Hold"
    else:
        diff_data = [diff for _, diff in similar_periods]
        index = [stock_prices.index[start] for start, _ in similar_periods]
        highlight_df = pd.DataFrame(data=diff_data, index=index, columns=["sattern_highlight"])

    # Use similar periods to predict the next stock price
    sim_period_difference: List[float] = []
    for i in range(period):
        sim_period_difference.append(0.0)
        for x in range(len(similar_periods)):
            index = similar_periods[x][0] + i
            # Weight by the difference
            sim_period_difference[i] += (stock_prices.iloc[index + 1] - stock_prices.iloc[index]) * (max_diff - similar_periods[x][1])

    # Normalize
    total_difference = sum([similar_periods[i][1] for i in range(len(similar_periods))])
    sim_period_difference = [price/total_difference for price in sim_period_difference]

    # Calculate price movements and dates
    sim_period_price_prediction: List[float] = []
    weekday_tool = weekday.weekday(increment_hours=24)
    sim_period_dates: List[datetime] = [stock_prices.index[-1]] + weekday_tool.get_next_n_datetimes(n=period, start=stock_prices.index[-1])

    sim_period_price_prediction.append(stock_prices.iloc[-1])
    for i in range(len(sim_period_difference)):
        sim_period_price_prediction.append(sim_period_price_prediction[i] + sim_period_difference[i])

    percent_change = (sim_period_price_prediction[-1] - stock_prices.iloc[-1]) / stock_prices.iloc[-1]
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

    prediction_df = pd.DataFrame(data=sim_period_price_prediction, index=sim_period_dates, columns=["sattern"])
    highlight_df = highlight_df[~highlight_df.index.duplicated(keep='first')]
    prediction_df = prediction_df[~prediction_df.index.duplicated(keep='first')]
    combined_df = pd.concat([highlight_df, prediction_df], axis=1)

    return (combined_df, action)