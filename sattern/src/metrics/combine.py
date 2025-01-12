"""Collect and combine all metrics"""
from sattern.src.metrics.sattern import sattern
from sattern.src.metrics.process import analyze_news, analyze_insider_transactions
from sattern.src.tools.api import get_news
import pandas as pd
from typing import Dict, Tuple
from pathlib import Path
from datetime import datetime, timedelta

def combine(ticker: str, df: pd.DataFrame, start_date: datetime, end_date: datetime, period: int, max_diff: int = 2, cache: bool = False) -> Tuple[pd.DataFrame, Dict]:
    actions: Dict[str, str] = {}
    sattern_df, actions["sattern"] = sattern(df, period, max_diff)
    news_data = get_news(ticker, start_date, end_date)
    actions["news"] = analyze_news(news_data)
    actions["insider_trades"] = analyze_insider_transactions(df)
    # ... add other metrics here
    df = pd.concat([sattern_df, df], axis=1)
    df.sort_index(inplace=True)

    if cache:
        file_path = f'{Path("./sattern/src/data")}/{ticker}_stock_data.json'
        df.to_json(path_or_buf=file_path, orient='columns', date_format='iso')

    return (df, actions)