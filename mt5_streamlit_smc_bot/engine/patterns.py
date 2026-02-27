from __future__ import annotations

import pandas as pd


def bullish_engulfing(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    cur = df.iloc[-1]
    return prev["close"] < prev["open"] and cur["close"] > cur["open"] and cur["close"] > prev["open"]


def bearish_engulfing(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    cur = df.iloc[-1]
    return prev["close"] > prev["open"] and cur["close"] < cur["open"] and cur["close"] < prev["open"]


def detect_pattern(df: pd.DataFrame) -> str:
    if bullish_engulfing(df):
        return "bullish_engulfing"
    if bearish_engulfing(df):
        return "bearish_engulfing"
    return "none"
