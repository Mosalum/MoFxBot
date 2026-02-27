from __future__ import annotations

import pandas as pd


def detect_fvg(df: pd.DataFrame) -> list[dict]:
    gaps: list[dict] = []
    for i in range(2, len(df)):
        c1 = df.iloc[i - 2]
        c3 = df.iloc[i]
        if c1["high"] < c3["low"]:
            gaps.append({"type": "bullish_fvg", "low": float(c1["high"]), "high": float(c3["low"])})
        elif c1["low"] > c3["high"]:
            gaps.append({"type": "bearish_fvg", "low": float(c3["high"]), "high": float(c1["low"])})
    return gaps[-5:]


def detect_order_blocks(df: pd.DataFrame) -> list[dict]:
    obs: list[dict] = []
    for i in range(1, len(df) - 1):
        cur = df.iloc[i]
        nxt = df.iloc[i + 1]
        if cur["close"] < cur["open"] and nxt["close"] > nxt["open"] and nxt["close"] > cur["high"]:
            obs.append({"type": "bullish_ob", "low": float(cur["low"]), "high": float(cur["high"])})
        if cur["close"] > cur["open"] and nxt["close"] < nxt["open"] and nxt["close"] < cur["low"]:
            obs.append({"type": "bearish_ob", "low": float(cur["low"]), "high": float(cur["high"])})
    return obs[-5:]


def detect_liquidity_sweep(df: pd.DataFrame) -> str:
    if len(df) < 10:
        return "none"
    recent = df.iloc[-1]
    prev_high = df["high"].iloc[-10:-1].max()
    prev_low = df["low"].iloc[-10:-1].min()
    if recent["high"] > prev_high and recent["close"] < prev_high:
        return "sell_side_sweep"
    if recent["low"] < prev_low and recent["close"] > prev_low:
        return "buy_side_sweep"
    return "none"


def detect_rsi_divergence(df: pd.DataFrame, rsi_col: str = "rsi") -> str:
    if len(df) < 20:
        return "none"
    p1 = df.iloc[-10]
    p2 = df.iloc[-1]
    if p2["close"] < p1["close"] and p2[rsi_col] > p1[rsi_col]:
        return "bullish_divergence"
    if p2["close"] > p1["close"] and p2[rsi_col] < p1[rsi_col]:
        return "bearish_divergence"
    return "none"
