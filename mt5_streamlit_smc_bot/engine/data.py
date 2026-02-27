from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd


def get_price_data(symbol: str, timeframe: str, bars: int = 300) -> pd.DataFrame:
    rng = pd.date_range(end=datetime.utcnow(), periods=bars, freq="min")
    base = 2300 + np.cumsum(np.random.normal(0, 0.4, size=bars))
    high = base + np.random.uniform(0.1, 0.8, size=bars)
    low = base - np.random.uniform(0.1, 0.8, size=bars)
    close = base + np.random.normal(0, 0.2, size=bars)
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    volume = np.random.randint(100, 1000, size=bars)
    return pd.DataFrame(
        {
            "time": rng,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "tick_volume": volume,
        }
    )
