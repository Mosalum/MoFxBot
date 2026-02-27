# MT5 Streamlit SMC Bot

Secure MT5 + Streamlit trading dashboard with SMC/indicator confluence, authentication, risk controls, and journaling.

## Features

- Password-protected Streamlit dashboard.
- SHA256 password verification (default password: `Mosalum123!!!`, stored only as hash).
- Session timeout (20 minutes inactivity), failed-login lockout (5 attempts, 2 minutes).
- Trading engine with:
  - Support/Resistance
  - Breakout + Retest
  - EMA crossover
  - RSI
  - Candlestick patterns
  - BOS / CHoCH
  - FVG
  - Order Block
  - Liquidity sweep
  - RSI divergence
  - Confluence scoring
  - Risk management
  - Broker minimum stop-level enforcement
  - XAUUSD spread/stop constraints
  - Cooldown period
  - DRY_RUN and NO_TRADE_MODE
- Dashboard widgets for live signals, open positions, trade history, logs, and chart overlays.

## Project structure

```text
mt5_streamlit_smc_bot/
  app.py
  auth.py
  engine/
    __init__.py
    config.py
    mt5_utils.py
    data.py
    indicators.py
    patterns.py
    structure.py
    smc.py
    strategy.py
    risk.py
    execute.py
    bot_service.py
    journal.py
    models.py
    logger.py
  storage/
    state.json
    trades.csv
    logs.txt
  requirements.txt
  README.md
```

## Run

```bash
cd mt5_streamlit_smc_bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Security notes

- Password is never stored or logged in plain text.
- Password input is masked.
- Dashboard cannot be accessed when unauthenticated.
- Timeout auto-logout is enforced every rerun.

