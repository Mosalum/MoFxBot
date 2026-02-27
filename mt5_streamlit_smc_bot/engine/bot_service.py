from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta

import pandas as pd

from .config import BROKER_MIN_STOP_POINTS, STATE_FILE, STORAGE_DIR, XAUUSD_MIN_STOP_POINTS
from .data import get_price_data
from .execute import Executor
from .journal import append_trade
from .logger import BotLogger
from .models import BotSettings, BotState, Position, Signal
from .mt5_utils import broker_min_stop_points, get_spread_points
from .risk import enforce_min_stop, position_size
from .strategy import build_signal


class BotService:
    def __init__(self) -> None:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.logger = BotLogger()
        self.executor = Executor()
        self.state = self._load_state()
        self.open_positions: list[Position] = []

    def _load_state(self) -> BotState:
        if not STATE_FILE.exists():
            return BotState()
        payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        last_trade = payload.get("last_trade_time")
        return BotState(
            running=payload.get("running", False),
            metadata=payload.get("metadata", {}),
            last_trade_time=datetime.fromisoformat(last_trade) if last_trade else None,
        )

    def _save_state(self) -> None:
        payload = {
            "running": self.state.running,
            "metadata": self.state.metadata,
            "last_trade_time": self.state.last_trade_time.isoformat() if self.state.last_trade_time else None,
        }
        STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def start(self) -> None:
        self.state.running = True
        self._save_state()
        self.logger.log("Bot started")

    def stop(self) -> None:
        self.state.running = False
        self._save_state()
        self.logger.log("Bot stopped")

    def _cooldown_active(self, settings: BotSettings) -> bool:
        if not self.state.last_trade_time:
            return False
        return datetime.utcnow() < self.state.last_trade_time + timedelta(minutes=settings.cooldown_minutes)

    def process_tick(self, settings: BotSettings, balance: float = 10000) -> Signal | None:
        if not self.state.running:
            return None
        if settings.no_trade_mode:
            self.logger.log("NO_TRADE_MODE active, skipping signal")
            return None
        if self._cooldown_active(settings):
            self.logger.log("Cooldown active, skipping signal")
            return None

        spread = get_spread_points(settings.symbol)
        if spread > settings.max_spread_points:
            self.logger.log(f"Spread too high: {spread:.2f} > {settings.max_spread_points}")
            return None

        df = get_price_data(settings.symbol, settings.timeframe)
        signal = build_signal(df, settings)
        if not signal:
            return None

        stop_points = abs(signal.entry - signal.sl) * 100
        broker_min = max(BROKER_MIN_STOP_POINTS, broker_min_stop_points(settings.symbol))
        stop_points = enforce_min_stop(stop_points, broker_min, XAUUSD_MIN_STOP_POINTS, settings.symbol)
        volume = position_size(balance, settings.risk_percent, stop_points)

        position = self.executor.execute(signal, volume, settings.dry_run)
        if position:
            self.open_positions.append(position)
            self.state.last_signal = signal
            self.state.last_trade_time = datetime.utcnow()
            self._save_state()
            append_trade(signal, position, signal.reason)
            self.logger.log(
                f"Trade {'simulated' if settings.dry_run else 'executed'}: {signal.side} {signal.symbol} vol={volume} confidence={signal.confidence}"
            )
        return signal

    def get_live_signals(self) -> pd.DataFrame:
        signal = self.state.last_signal
        if not signal:
            return pd.DataFrame(columns=["symbol", "side", "confidence", "entry", "sl", "tp", "reason", "time"])
        return pd.DataFrame(
            [
                {
                    "symbol": signal.symbol,
                    "side": signal.side,
                    "confidence": signal.confidence,
                    "entry": signal.entry,
                    "sl": signal.sl,
                    "tp": signal.tp,
                    "reason": signal.reason,
                    "time": signal.timestamp.isoformat(),
                }
            ]
        )

    def get_open_positions(self) -> pd.DataFrame:
        return pd.DataFrame([asdict(pos) for pos in self.open_positions])
