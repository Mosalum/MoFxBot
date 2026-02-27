from __future__ import annotations

from typing import Any


try:
    import MetaTrader5 as mt5
except ImportError:  # optional in local environment
    mt5 = None


def initialize_mt5() -> bool:
    if mt5 is None:
        return False
    return mt5.initialize()


def shutdown_mt5() -> None:
    if mt5 is not None:
        mt5.shutdown()


def symbol_info_tick(symbol: str) -> dict[str, Any]:
    if mt5 is None:
        return {"bid": 2300.0, "ask": 2300.3}
    tick = mt5.symbol_info_tick(symbol)
    return {"bid": tick.bid, "ask": tick.ask} if tick else {"bid": 0.0, "ask": 0.0}


def get_spread_points(symbol: str) -> float:
    tick = symbol_info_tick(symbol)
    return max((tick["ask"] - tick["bid"]) * 100, 0)


def broker_min_stop_points(symbol: str) -> int:
    if mt5 is None:
        return 150
    info = mt5.symbol_info(symbol)
    if not info:
        return 150
    return int(info.trade_stops_level or 150)
