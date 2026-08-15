# Cyruss — Automated Trading System

Cyruss is a Python-based automated trading system built for **MetaTrader 5 (MT5)**. The current preset is designed for short-term/scalping experiments and includes technical-signal generation, broker-aware execution, position sizing, and defensive risk controls.

> **⚠️ Important:** Cyruss can send real orders when configured with `DRY_RUN = False` and connected to a live MT5 account. It can therefore cause real financial gains or losses. This project is experimental software, not financial advice, and does not guarantee profit.

## What it demonstrates

- Modular Python application architecture
- MetaTrader 5 integration and market-data handling
- Rule-based signal generation using **EMA, RSI, MACD, and ATR**
- Position sizing based on account risk
- Stop-loss validation against broker constraints
- Spread filtering and trading-session filtering
- Daily loss circuit breaker
- Live-account confirmation before trading
- Nominal USD profit watcher with automated position closing
- Defensive handling of broker/external-system failures

## Architecture

```text
Cyruss/
├── bot.py             # Main execution loop and trade orchestration
├── config.py          # Strategy, risk, and execution parameters
├── indicators.py      # EMA, RSI, MACD, ATR calculations
├── strategy.py        # BUY / SELL / HOLD signal logic
├── risk_manager.py    # Position sizing, SL/TP, daily loss controls
├── mt5_connector.py   # MT5 connection, market data, order execution
└── README.md
```

## Strategy

The default signal logic combines:

- **EMA crossover** for directional/trend information
- **RSI** as a momentum/extreme-condition filter
- **MACD histogram** as momentum confirmation
- **ATR** for stop-loss distance and risk calculations

Signals are evaluated from closed candles to reduce decisions based on an unfinished candle.

## Risk controls

Cyruss is intentionally designed to fail conservatively where practical. Important controls include:

- Risk-per-trade position sizing
- Maximum open-position limits
- Maximum daily-loss circuit breaker
- Broker minimum-stop-distance validation
- Spread filtering
- Live-account confirmation
- `DRY_RUN` mode for simulation

These controls **reduce specific operational risks; they do not make trading safe or profitable**.

## Profit-target mechanism

The current preset can use a nominal USD target instead of a broker-side price-based TP. A watcher monitors open positions and requests a close when the configured floating profit target is reached.

This does **not** guarantee a net profit: spread, commission, swap, slippage, latency, and execution conditions can change the final result.

## Configuration

Credentials are loaded from environment variables rather than hard-coded in source files. Do not commit real MT5 credentials.

Key settings include:

| Setting | Purpose |
|---|---|
| `SYMBOLS` | Instruments monitored by the bot |
| `TIMEFRAME` | Market-data timeframe |
| `RISK_PERCENT_PER_TRADE` | Risk allocation used for position sizing |
| `MAX_DAILY_LOSS_PERCENT` | Daily loss circuit breaker |
| `MAX_SPREAD_POINTS` | Maximum accepted spread |
| `DRY_RUN` | Simulation mode when `True` |
| `USE_NOMINAL_PROFIT_TARGET` | Enables the nominal profit watcher |
| `TARGET_PROFIT_USD` | Floating-profit threshold used by the watcher |

## Running

```bash
pip install -r requirements.txt
python bot.py
```

Use a **demo account first** and validate the strategy, execution behavior, and risk controls before considering any live deployment.

## Limitations

This project has not been presented as a guaranteed profitable system. Performance can vary substantially by instrument, broker, spread, market regime, execution latency, and parameter choices. The current strategy should be treated as an engineering and research experiment rather than a production trading product.

## Future work

- Historical backtesting and reproducible performance reports
- Automated unit/integration tests
- Better structured logging and monitoring
- More robust configuration management
- Native MQL5 execution for latency-sensitive experiments
- Paper-trading and walk-forward validation

## License

Cyruss is **proprietary — all rights reserved**. Viewing the source on GitHub is permitted for portfolio, review, and educational reference purposes. Reuse, redistribution, modification, commercial exploitation, or live deployment requires explicit written permission.

See [`LICENSE`](./LICENSE).
