"""Collect and combine all metrics"""
from sattern.src.metrics.sattern import sattern
import pandas as pd
from typing import Dict, Tuple
from pathlib import Path

def combine(df: pd.DataFrame, period: int, max_diff: int = 2, cache: bool = False, ticker: str = None) -> Tuple[pd.DataFrame, Dict[str, str]]:
    actions: Dict[str, str] = {}
    sattern_df, actions["sattern"] = sattern(df, period, max_diff)
    # ... add other metrics here
    df = pd.concat([sattern_df, df], axis=1)
    df.sort_index(inplace=True)

    if cache:
        if ticker is None:
            raise ValueError("Ticker must be provided if cache is True")
        file_path = f'{Path("./sattern/src/data")}/{ticker}_stock_data.json'
        df.to_json(path_or_buf=file_path, orient='columns', date_format='iso')

    return (df, actions)