from __future__ import annotations

import pandas as pd


def detect_bos_choch(df: pd.DataFrame) -> str:
    if len(df) < 6:
        return "none"
    recent_high = df["high"].iloc[-1]
    prev_high = df["high"].iloc[-6:-1].max()
    recent_low = df["low"].iloc[-1]
    prev_low = df["low"].iloc[-6:-1].min()
    if recent_high > prev_high:
        return "bos_bull"
    if recent_low < prev_low:
        return "bos_bear"
    return "none"


def breakout_retest(df: pd.DataFrame, level: float, side: str, tolerance: float = 0.3) -> bool:
    if len(df) < 3:
        return False
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if side == "buy":
        return prev["close"] > level and abs(last["low"] - level) <= tolerance
    return prev["close"] < level and abs(last["high"] - level) <= tolerance
