from __future__ import annotations


def position_size(balance: float, risk_percent: float, stop_points: float, point_value: float = 1.0) -> float:
    if stop_points <= 0:
        return 0.01
    risk_amount = balance * (risk_percent / 100)
    lots = risk_amount / (stop_points * point_value)
    return round(max(lots, 0.01), 2)


def enforce_min_stop(stop_points: float, broker_min_points: int, xauusd_min_points: int, symbol: str) -> float:
    baseline = max(stop_points, broker_min_points)
    if symbol.upper() == "XAUUSD":
        baseline = max(baseline, xauusd_min_points)
    return float(baseline)
