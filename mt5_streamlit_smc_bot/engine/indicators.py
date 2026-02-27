from __future__ import annotations

import numpy as np
import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gains, index=series.index).rolling(period).mean()
    avg_loss = pd.Series(losses, index=series.index).rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def support_resistance(df: pd.DataFrame, window: int = 20) -> tuple[float, float]:
    return float(df["low"].tail(window).min()), float(df["high"].tail(window).max())
