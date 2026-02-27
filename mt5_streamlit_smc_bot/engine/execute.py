from __future__ import annotations

from datetime import datetime

from .models import Position, Signal


class Executor:
    def __init__(self) -> None:
        self._ticket = 1000

    def execute(self, signal: Signal, volume: float, dry_run: bool = True) -> Position | None:
        if dry_run:
            return Position(
                ticket=self._ticket,
                symbol=signal.symbol,
                side=signal.side,
                volume=volume,
                entry=signal.entry,
                sl=signal.sl,
                tp=signal.tp,
                open_time=datetime.utcnow(),
            )
        self._ticket += 1
        return Position(
            ticket=self._ticket,
            symbol=signal.symbol,
            side=signal.side,
            volume=volume,
            entry=signal.entry,
            sl=signal.sl,
            tp=signal.tp,
            open_time=datetime.utcnow(),
        )
