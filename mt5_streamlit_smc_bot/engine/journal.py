from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from .config import STORAGE_DIR, TRADES_FILE
from .models import Position, Signal


def ensure_trade_file() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not TRADES_FILE.exists():
        pd.DataFrame(
            columns=[
                "time",
                "symbol",
                "side",
                "confidence",
                "entry",
                "sl",
                "tp",
                "volume",
                "ticket",
                "reason",
            ]
        ).to_csv(TRADES_FILE, index=False)


def append_trade(signal: Signal, position: Position, reason: str) -> None:
    ensure_trade_file()
    row = {
        "time": signal.timestamp.isoformat(),
        "symbol": signal.symbol,
        "side": signal.side,
        "confidence": signal.confidence,
        "entry": signal.entry,
        "sl": signal.sl,
        "tp": signal.tp,
        "volume": position.volume,
        "ticket": position.ticket,
        "reason": reason,
    }
    df = pd.DataFrame([row])
    df.to_csv(TRADES_FILE, mode="a", header=False, index=False)


def read_trades() -> pd.DataFrame:
    ensure_trade_file()
    return pd.read_csv(TRADES_FILE)
