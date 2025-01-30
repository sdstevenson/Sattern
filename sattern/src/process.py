"""Process various metrics"""
import pandas as pd
from typing import Dict, Tuple, List
from datetime import datetime, timedelta

def process_news(ticker: str, news_data: Dict) -> Dict:
    # Get the average sentiment, weighted by the relevance score
    total_relevance = 0
    total_sentiment = 0
    top_news = []
    for article in news_data["feed"]:
        for rating in article["ticker_sentiment"]:
            if rating["ticker"] == ticker:
                relevance = float(rating["relevance_score"])
                sentiment = float(rating["ticker_sentiment_score"])
                total_relevance += relevance
                total_sentiment += sentiment * relevance
                if len(top_news) <= 10:  # Only get the top 10 relevent stocks
                    top_news.append({
                        "title": article["title"],
                        "url": article["url"],
                        "summary": article["summary"],
                        "sentiment": rating["ticker_sentiment_label"]
                    })
    if total_relevance == 0:
        weighted_sentiment = 0  # Avoid division by zero
    else:
        weighted_sentiment = total_sentiment / total_relevance

    if weighted_sentiment <= -0.35:
        action = "Strong Sell"
    elif weighted_sentiment <= -0.15:
        action = "Sell"
    elif weighted_sentiment < 0.15:
        action = "Hold"
    elif weighted_sentiment < 0.35:
        action = "Buy"
    else:
        action = "Strong Buy"

    p_news = {
        "top_news": top_news,
        "action": action
    }
    return p_news

def process_insider_transactions(df: pd.DataFrame):
    a_count = 0
    d_count = 0
    total_money_moved = 0
    total_shares_moved = 0

    if 'acquisition_or_disposal' not in df.columns or 'shares' not in df.columns or 'share_price' not in df.columns:
        return {"action": "Hold"}

    for _, row in df.iterrows():
        if pd.notnull(row["acquisition_or_disposal"]):
            shares = row["shares"]
            share_price = row["share_price"]
            money_moved = shares * share_price

            if row["acquisition_or_disposal"] == "A":
                a_count += 1
                total_shares_moved += shares
                total_money_moved += money_moved
            elif row["acquisition_or_disposal"] == "D":
                d_count += 1
                total_shares_moved -= shares
                total_money_moved -= money_moved

    if total_shares_moved < -1000 and total_money_moved < -100000:
        action = "Strong Sell"
    elif total_shares_moved < -500:
        action = "Sell"
    elif -500 <= total_shares_moved <= 500:
        action = "Hold"
    elif total_shares_moved > 1000 and total_money_moved > 100000:
        action = "Strong Buy"
    else:
        action = "Buy"


    result = {
        "action": action,
    }
    return result

def sattern(df: pd.DataFrame, period: int = 10, max_diff: int = 2) -> Tuple[pd.DataFrame, Dict]:
    df = df.sort_index()

    # For each element in the current period, find the difference to the previous element
    comp_start_index = len(df) - period - 1
    curr_period_diff = []
    for i in range(comp_start_index-1, len(df)-1):
        curr_period_diff.append(df.iloc[i+1] - df.iloc[i])

    curr_comp_start = 0
    curr_comp_length = 0
    curr_comp_diff = 0
    similar_periods: List[Tuple[int, float]] = []   # Store start index and difference of each period
    index = 0

    while(index < (comp_start_index - period)):
        curr_diff = curr_period_diff[curr_comp_length] - (df.iloc[curr_comp_start + curr_comp_length + 1] - df.iloc[curr_comp_start + curr_comp_length])
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
        index = [df.index[start] for start, _ in similar_periods]
        highlight_df = pd.DataFrame(data=diff_data, index=index, columns=["sattern_highlight"])

    # Use similar periods to predict the next stock price
    sim_period_difference: List[float] = []
    for i in range(period):
        sim_period_difference.append(0.0)
        for x in range(len(similar_periods)):
            index = similar_periods[x][0] + i
            # Weight by the difference
            sim_period_difference[i] += (df.iloc[index + 1] - df.iloc[index]) * (max_diff - similar_periods[x][1])

    # Normalize
    total_difference = sum([similar_periods[i][1] for i in range(len(similar_periods))])
    sim_period_difference = [price/total_difference for price in sim_period_difference]

    # Calculate price movements and dates
    sim_period_price_prediction: List[float] = []
    sim_period_dates = pd.date_range(start=datetime.strptime(df.index[-1]), end=datetime.strptime(df.index[-1]) + timedelta(days=period), periods=period, freq='B')

    sim_period_price_prediction.append(df.iloc[-1])
    for i in range(len(sim_period_difference)):
        sim_period_price_prediction.append(sim_period_price_prediction[i] + sim_period_difference[i])

    percent_change = (sim_period_price_prediction[-1] - df.iloc[-1]) / df.iloc[-1]
    data = {}

    if abs(percent_change) < 0.02:
        data["action"] = "Hold"
    elif percent_change > 0.02:
        if percent_change > 0.10:
            data["action"] = "Strong Buy"
        else:
            data["action"] = "Buy"
    elif percent_change < 0.02:
        if percent_change < 0.10:
            data["action"] = "Strong Sell"
        else:
            data["action"] = "Sell"

    prediction_df = pd.DataFrame(data=sim_period_price_prediction, index=sim_period_dates, columns=["sattern"])
    highlight_df = highlight_df[~highlight_df.index.duplicated(keep='first')]
    prediction_df = prediction_df[~prediction_df.index.duplicated(keep='first')]
    combined_df = pd.concat([highlight_df, prediction_df], axis=1)

    return (combined_df, data)
