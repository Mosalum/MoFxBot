from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Signal:
    symbol: str
    timeframe: str
    side: str
    confidence: float
    reason: str
    score: dict[str, float] = field(default_factory=dict)
    entry: float = 0.0
    sl: float = 0.0
    tp: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Position:
    ticket: int
    symbol: str
    side: str
    volume: float
    entry: float
    sl: float
    tp: float
    open_time: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BotSettings:
    symbol: str = "XAUUSD"
    timeframe: str = "M15"
    risk_percent: float = 1.0
    confirmations_required: int = 4
    confidence_threshold: float = 0.6
    dry_run: bool = True
    no_trade_mode: bool = False
    max_spread_points: int = 60
    cooldown_minutes: int = 15
    session_london: bool = True
    session_ny: bool = True
    enabled_modules: dict[str, bool] = field(
        default_factory=lambda: {
            "support_resistance": True,
            "breakout_retest": True,
            "ema": True,
            "rsi": True,
            "candlestick": True,
            "bos_choch": True,
            "fvg": True,
            "order_block": True,
            "liquidity_sweep": True,
            "rsi_divergence": True,
        }
    )


@dataclass
class BotState:
    running: bool = False
    last_signal: Signal | None = None
    last_trade_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
