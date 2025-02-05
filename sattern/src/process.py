"""Process various metrics"""
import pandas as pd
from typing import Dict, Tuple, List
from datetime import timedelta, timezone

def process_news(ticker: str, news_data: Dict) -> Dict:
    # Get the average sentiment, weighted by the relevance score
    total_relevance = 0
    total_sentiment = 0
    top_news = []
    for article in news_data["feed"]:
        # Only analyze articles from the past 30 days
        article_time = pd.to_datetime(article['time_published'], format='%Y%m%dT%H%M%S', utc=True)
        if article_time < pd.Timestamp.now(tz=timezone.utc) - timedelta(days=30):
            break
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

def process_insider_transactions(df: pd.DataFrame) -> Dict:
    a_count = 0
    d_count = 0
    total_money_moved = 0
    total_shares_moved = 0

    # Ensure columns exist
    required_cols = ["acquisition_or_disposal", "shares", "share_price"]
    if df is None or not all(col in df.columns for col in required_cols):
        return {"action": "Hold"}

    # Convert numeric columns to floats
    df["shares"] = pd.to_numeric(df["shares"], errors="coerce")
    df["share_price"] = pd.to_numeric(df["share_price"], errors="coerce")

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

    p_insider_transactions = {
        "action": action,
    }
    return p_insider_transactions

def sattern(df:pd.DataFrame, period:int=10, max_diff:int=2) -> Tuple[pd.DataFrame, Dict]:
    # For each element in the current period, find the difference to the previous element
    curr_period_diff: List[float] = []
    for i in range(period, -1, -1):
        # print(f"Start: {df.index[i+1]} End: {df.index[i]}")
        # print(f"Start Price: {df.iloc[i+1]} End Price: {df.iloc[i]}")
        # print(f"Diff: {df.iloc[i] - df.iloc[i+1]}")
        curr_period_diff.append(float(df.iloc[i] - df.iloc[i+1]))

    curr_comp_start:int = len(df) - 2
    curr_comp_length:int = 0
    curr_comp_diff:float = 0.0
    similar_periods: List[Tuple[int, float]] = []   # Store start index and difference of each period
    index:int = len(df) - 2

    while(index > period):
        curr_diff:float = curr_period_diff[curr_comp_length] - float(df.iloc[curr_comp_start - curr_comp_length - 1] - df.iloc[curr_comp_start - curr_comp_length])
        curr_comp_diff += curr_diff

        curr_comp_length += 1
        index -= 1

        if abs(curr_diff) > max_diff or abs(curr_comp_diff) > max_diff:
            curr_comp_start -= 1
            index = curr_comp_start
            curr_comp_length = 0
            curr_comp_diff = 0.0
        elif curr_comp_length >= period:
            similar_periods.append( (curr_comp_start, curr_comp_diff) )
            index = curr_comp_start - period // 2
            curr_comp_start = index
            curr_comp_length = 0
            curr_comp_diff = 0

    if len(similar_periods) == 0:
        print("No similar patterns found")
        return pd.DataFrame(columns=["sattern", "highlight"]), {"action": "Hold"}
    else:
        # Combine similar periods into a DataFrame of start of period + difference to the most recent <period> days
        diff_data = [diff for _, diff in similar_periods]
        index = [df.index[start] for start, _ in similar_periods]
        highlight_df = pd.DataFrame(data=diff_data, index=index, columns=["highlight"])
        highlight_df.sort_index(inplace=True)

    # Use similar periods to predict the next stock price
    period_difference: List[float] = []
    for i in range(period):
        period_difference.append(0.0)
        for x in range(len(similar_periods)):
            index = similar_periods[x][0] - i
            # Weight by how similar the period is to the to the most recent <period> days
            period_difference[i] += (df.iloc[index] - df.iloc[index + 1]) * (max_diff - similar_periods[x][1])

    # Normalize
    total_difference = sum([abs(similar_periods[i][1]) for i in range(len(similar_periods))])
    sim_period_difference = [price/total_difference for price in period_difference]

    # Calculate price movements and dates
    sim_period_price_prediction: List[float] = []
    sim_period_dates = pd.date_range(start=df.index[0], end=df.index[0] + timedelta(days=2*period), tz=timezone.utc, freq='B')
    sim_period_dates = sim_period_dates[0:period+1]

    sim_period_price_prediction.append(df.iloc[0])
    for i in range(len(sim_period_difference)):
        sim_period_price_prediction.append(sim_period_price_prediction[i] + sim_period_difference[i])

    percent_change = (sim_period_price_prediction[-1] - df.iloc[0]) / df.iloc[0]
    sattern_action = {
        "sim_periods": similar_periods,
        "price_prediction": sim_period_price_prediction[-1]
    }
    if abs(percent_change) < 0.02:
        sattern_action["action"] = "Hold"
    elif percent_change > 0.02:
        if percent_change > 0.10:
            sattern_action["action"] = "Strong Buy"
        else:
            sattern_action["action"] = "Buy"
    elif percent_change < 0.02:
        if percent_change < 0.10:
            sattern_action["action"] = "Strong Sell"
        else:
            sattern_action["action"] = "Sell"

    prediction_df = pd.DataFrame(
        {"sattern": sim_period_price_prediction},
        index=sim_period_dates
    )
    combined_df = pd.concat([highlight_df, prediction_df], axis=1)

    return (combined_df, sattern_action)
