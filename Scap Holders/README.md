# Scap Holders — Automated Gold Scalping Bot

Scap Holders is a Python + MetaTrader 5 automated trading variant focused on **XAUUSD/gold scalping experiments**. It combines technical indicators with broker-aware execution and risk controls.

> **⚠️ Important:** This bot can send real orders when `DRY_RUN = False` and an MT5 live account is used. It can cause real financial gains or losses. This is experimental software, not financial advice, and no profitability is guaranteed.

## What it demonstrates

- Python automation connected to MetaTrader 5
- M1 scalping workflow
- EMA/RSI/MACD/ATR-based signals
- Spread and session filtering
- Risk-based position sizing
- Broker minimum-stop-distance validation
- Daily loss circuit breaker
- Nominal USD profit target watcher
- Automated position closing and re-entry through fresh signals
- Live-account confirmation and dry-run mode

## Architecture

```text
Scap Holders/
├── bot.py             # Main loop, signal scanning, profit watcher
├── config.py          # Scalping and risk parameters
├── indicators.py      # Technical indicators
├── strategy.py        # Signal generation
├── risk_manager.py    # Position sizing and risk controls
├── mt5_connector.py   # MT5 connection, execution, and position closing
└── README.md
```

## Scalping design

The preset uses a short timeframe and faster indicator parameters. Because scalping is sensitive to spread, commission, latency, and execution quality, the bot also includes spread and trading-session filters.

## Profit target

When `USE_NOMINAL_PROFIT_TARGET = True`, the bot watches floating profit and requests a position close once `TARGET_PROFIT_USD` is reached.

The configured floating profit is **not the same as guaranteed net profit**. Commission, swap, spread, slippage, and execution conditions can change the final realized result.

## Risk controls

- Risk-per-trade position sizing
- Maximum open positions
- Maximum daily-loss circuit breaker
- Broker stop-distance validation
- Spread filtering
- Trading-session filtering
- Live-account confirmation
- `DRY_RUN` simulation mode

These controls are safeguards, not guarantees against loss.

## Running

```bash
pip install -r requirements.txt
python bot.py
```

Use a demo account first. Scalping strategies should be tested with realistic spreads, commissions, latency, and execution conditions.

## Limitations

The current configuration is an experimental preset rather than a validated production strategy. Performance can differ substantially between brokers, instruments, account types, market regimes, and execution environments.

## Future work

- Reproducible M1 backtesting
- Walk-forward testing
- Automated regression tests
- Execution-latency measurements
- Better monitoring and alerting
- More robust configuration and deployment tooling

## License

Scap Holders is **proprietary — all rights reserved**. The source is published for portfolio, review, and educational reference. Reuse, redistribution, modification, commercial exploitation, or live deployment requires explicit written permission.

See [`LICENSE`](./LICENSE).
