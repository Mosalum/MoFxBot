from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
STATE_FILE = STORAGE_DIR / "state.json"
TRADES_FILE = STORAGE_DIR / "trades.csv"
LOGS_FILE = STORAGE_DIR / "logs.txt"

DEFAULT_SYMBOL = "XAUUSD"
DEFAULT_TIMEFRAME = "M15"
XAUUSD_MAX_SPREAD = 70
XAUUSD_MIN_STOP_POINTS = 250
BROKER_MIN_STOP_POINTS = 150
