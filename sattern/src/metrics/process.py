"""Process various metrics"""
import pandas as pd
from typing import Dict

def analyze_news(data: Dict) -> Dict:
    # Get the average sentiment, weighted by the relevance score
    total_relevance = 0
    total_sentiment = 0
    top_news = []
    for article in data["feed"]:
        for rating in article["ticker_sentiment"]:
            if rating["ticker"] == data:
                relevance = float(rating["relevance_score"])
                sentiment = float(rating["ticker_sentiment_score"])
                total_relevance += relevance
                total_sentiment += sentiment * relevance
                if len(top_news <= 10):  # Only get the top 10 relevent stocks
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

    data = {
        "top_news": top_news,
        "action": action
    }
    return data

def analyze_insider_transactions(df: pd.DataFrame):
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