"""Collect and combine all metrics"""
from sattern.src.metrics.sattern import sattern
import sattern.src.tools.api as api
import pandas as pd
from typing import Dict, Tuple

def combine(df: pd.DataFrame, period: int, max_diff: int = 2) -> Tuple[pd.DataFrame, Dict[str, str]]:
    actions: Dict[str, str] = {}
    sattern_df, actions["sattern"] = sattern(df, period, max_diff)
    # ... add other metrics here
    df = pd.concat([sattern_df, df], axis=1)
    return (df, actions)