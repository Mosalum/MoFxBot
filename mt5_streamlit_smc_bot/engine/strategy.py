from __future__ import annotations

from datetime import datetime

import pandas as pd

from .indicators import ema, rsi, support_resistance
from .models import BotSettings, Signal
from .patterns import detect_pattern
from .smc import detect_fvg, detect_liquidity_sweep, detect_order_blocks, detect_rsi_divergence
from .structure import breakout_retest, detect_bos_choch


def _in_session(now_utc: datetime, london: bool, ny: bool) -> bool:
    h = (now_utc.hour + 3) % 24  # UTC+3
    london_ok = london and 10 <= h <= 18
    ny_ok = ny and 15 <= h <= 23
    return london_ok or ny_ok


def build_signal(df: pd.DataFrame, settings: BotSettings) -> Signal | None:
    if not _in_session(datetime.utcnow(), settings.session_london, settings.session_ny):
        return None

    df = df.copy()
    df["ema_fast"] = ema(df["close"], 21)
    df["ema_slow"] = ema(df["close"], 50)
    df["rsi"] = rsi(df["close"], 14)

    sup, res = support_resistance(df)
    pattern = detect_pattern(df)
    structure = detect_bos_choch(df)
    fvgs = detect_fvg(df)
    obs = detect_order_blocks(df)
    sweep = detect_liquidity_sweep(df)
    div = detect_rsi_divergence(df)

    latest = df.iloc[-1]
    score: dict[str, float] = {}

    if settings.enabled_modules.get("ema", True):
        score["ema"] = 1.0 if latest["ema_fast"] > latest["ema_slow"] else -1.0
    if settings.enabled_modules.get("rsi", True):
        score["rsi"] = 1.0 if latest["rsi"] < 35 else (-1.0 if latest["rsi"] > 65 else 0)
    if settings.enabled_modules.get("support_resistance", True):
        score["support_resistance"] = 1.0 if latest["close"] <= sup + 0.5 else (-1.0 if latest["close"] >= res - 0.5 else 0)
    if settings.enabled_modules.get("breakout_retest", True):
        score["breakout_retest"] = 1.0 if breakout_retest(df, res, "buy") else (-1.0 if breakout_retest(df, sup, "sell") else 0)
    if settings.enabled_modules.get("candlestick", True):
        score["candlestick"] = 1.0 if pattern == "bullish_engulfing" else (-1.0 if pattern == "bearish_engulfing" else 0)
    if settings.enabled_modules.get("bos_choch", True):
        score["bos_choch"] = 1.0 if structure == "bos_bull" else (-1.0 if structure == "bos_bear" else 0)
    if settings.enabled_modules.get("fvg", True):
        score["fvg"] = 1.0 if any(g["type"] == "bullish_fvg" for g in fvgs) else (-1.0 if any(g["type"] == "bearish_fvg" for g in fvgs) else 0)
    if settings.enabled_modules.get("order_block", True):
        score["order_block"] = 1.0 if any(o["type"] == "bullish_ob" for o in obs) else (-1.0 if any(o["type"] == "bearish_ob" for o in obs) else 0)
    if settings.enabled_modules.get("liquidity_sweep", True):
        score["liquidity_sweep"] = 1.0 if sweep == "buy_side_sweep" else (-1.0 if sweep == "sell_side_sweep" else 0)
    if settings.enabled_modules.get("rsi_divergence", True):
        score["rsi_divergence"] = 1.0 if div == "bullish_divergence" else (-1.0 if div == "bearish_divergence" else 0)

    active_votes = [v for v in score.values() if v != 0]
    if len(active_votes) < settings.confirmations_required:
        return None

    total = sum(score.values())
    confidence = (abs(total) / max(len(score), 1))
    if confidence < settings.confidence_threshold:
        return None

    side = "buy" if total > 0 else "sell"
    entry = float(latest["close"])
    stop_distance = 4.0
    sl = entry - stop_distance if side == "buy" else entry + stop_distance
    tp = entry + (stop_distance * 2) if side == "buy" else entry - (stop_distance * 2)
    return Signal(
        symbol=settings.symbol,
        timeframe=settings.timeframe,
        side=side,
        confidence=round(confidence, 2),
        reason=f"confluence={score}",
        score=score,
        entry=entry,
        sl=sl,
        tp=tp,
    )
