from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from auth import enforce_session_timeout, get_auth_status, initialize_auth_state, is_locked, login, logout, touch_activity
from engine import BotService, BotSettings
from engine.data import get_price_data
from engine.journal import read_trades
from engine.smc import detect_fvg, detect_order_blocks

st.set_page_config(page_title="MT5 SMC Dashboard", layout="wide")


def _get_service() -> BotService:
    if "bot_service" not in st.session_state:
        st.session_state["bot_service"] = BotService()
    return st.session_state["bot_service"]


def _render_login() -> None:
    st.markdown(
        """
        <style>
            .login-wrapper {display:flex; justify-content:center; margin-top:10vh;}
            .login-card {width:420px; padding:2rem; border-radius:16px; border:1px solid #2a2a2a; background:#101622; box-shadow:0 12px 24px rgba(0,0,0,0.35);}
            .login-title {text-align:center; color:#fff; margin-bottom:1rem; font-size:1.5rem; font-weight:700;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    locked, remaining = is_locked()
    status = get_auth_status()

    st.markdown('<div class="login-wrapper"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Secure MT5 Dashboard Login</div>', unsafe_allow_html=True)

    if st.session_state.get("session_expired"):
        st.warning("Session expired. Please login again.")
        st.session_state["session_expired"] = False

    if locked:
        st.error(f"Login locked. Try again in {remaining} seconds.")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    if st.button("Login", use_container_width=True, disabled=locked):
        if login(password):
            st.success("Login successful")
            st.rerun()
        else:
            locked_after, rem = is_locked()
            if locked_after:
                st.error(f"Too many failed attempts. Locked for {rem} seconds.")
            else:
                attempts_left = max(0, 5 - int(st.session_state.get("failed_attempts", 0)))
                st.error(f"Invalid password. Attempts left: {attempts_left}")

    st.caption(f"Failed attempts: {status.failed_attempts}/5")
    st.markdown("</div></div>", unsafe_allow_html=True)


def _render_sidebar(settings: BotSettings) -> BotSettings:
    st.sidebar.header("Controls")
    if st.sidebar.button("Logout", use_container_width=True):
        logout()
        st.rerun()

    settings.risk_percent = st.sidebar.slider("Risk %", 0.1, 5.0, settings.risk_percent, 0.1)
    settings.confirmations_required = st.sidebar.slider("Confirmations required", 1, 10, settings.confirmations_required)
    settings.confidence_threshold = st.sidebar.slider("Confidence threshold", 0.1, 1.0, settings.confidence_threshold, 0.05)
    settings.dry_run = st.sidebar.toggle("DRY_RUN", value=settings.dry_run)
    settings.no_trade_mode = st.sidebar.toggle("NO_TRADE_MODE", value=settings.no_trade_mode)
    settings.max_spread_points = st.sidebar.number_input("Max spread points", value=settings.max_spread_points, min_value=1)
    settings.cooldown_minutes = st.sidebar.number_input("Cooldown minutes", value=settings.cooldown_minutes, min_value=0)

    st.sidebar.subheader("Session filters (UTC+3)")
    settings.session_london = st.sidebar.checkbox("London", value=settings.session_london)
    settings.session_ny = st.sidebar.checkbox("New York", value=settings.session_ny)

    st.sidebar.subheader("Modules")
    for k, enabled in settings.enabled_modules.items():
        settings.enabled_modules[k] = st.sidebar.checkbox(k.replace("_", " ").title(), value=enabled)

    touch_activity()
    return settings


def _price_chart(symbol: str, timeframe: str) -> None:
    df = get_price_data(symbol, timeframe, 120)
    fvgs = detect_fvg(df)
    obs = detect_order_blocks(df)

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["time"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price",
            )
        ]
    )

    for item in fvgs[-3:]:
        fig.add_hrect(y0=item["low"], y1=item["high"], line_width=0, fillcolor="green" if "bullish" in item["type"] else "red", opacity=0.15)
    for item in obs[-3:]:
        fig.add_hrect(y0=item["low"], y1=item["high"], line_width=1, line_color="blue", fillcolor="blue", opacity=0.08)

    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    initialize_auth_state()
    expired = enforce_session_timeout()

    if expired or not st.session_state.get("authenticated", False):
        _render_login()
        return

    touch_activity()
    bot = _get_service()
    settings = st.session_state.get("settings", BotSettings())
    settings = _render_sidebar(settings)
    st.session_state["settings"] = settings

    st.title("MT5 + SMC Trading Dashboard")
    c1, c2, c3 = st.columns(3)
    c1.metric("Bot status", "Running" if bot.state.running else "Stopped")
    c2.metric("Symbol", settings.symbol)
    c3.metric("Mode", "DRY_RUN" if settings.dry_run else "LIVE")

    a, b = st.columns(2)
    if a.button("Start Bot", use_container_width=True):
        bot.start()
        touch_activity()
    if b.button("Stop Bot", use_container_width=True):
        bot.stop()
        touch_activity()

    if st.button("Scan Market Now", use_container_width=True):
        signal = bot.process_tick(settings)
        if signal:
            st.success(f"Signal: {signal.side.upper()} ({signal.confidence:.2f})")
        else:
            st.info("No qualified signal")
        touch_activity()

    st.subheader("Live Signals")
    st.dataframe(bot.get_live_signals(), use_container_width=True)

    st.subheader("Open Positions")
    open_positions = bot.get_open_positions()
    st.dataframe(open_positions if not open_positions.empty else pd.DataFrame(columns=["ticket", "symbol", "side", "volume", "entry", "sl", "tp", "open_time"]), use_container_width=True)

    st.subheader("Trade History")
    st.dataframe(read_trades(), use_container_width=True)

    st.subheader("Logs (last 200 lines)")
    st.code(bot.logger.read_last_lines(200) or "No logs yet", language="text")

    st.subheader("Price Chart with OB/FVG Overlays")
    _price_chart(settings.symbol, settings.timeframe)


if __name__ == "__main__":
    main()
