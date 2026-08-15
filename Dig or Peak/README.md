# Dig or Peak — Automated Forex Trading Bot

Dig or Peak is a Python + MetaTrader 5 automated trading experiment that reads market data, generates rule-based signals, calculates position size, and can submit BUY/SELL orders with Stop Loss and Take Profit.

> **⚠️ Important:** This bot can send real orders when `DRY_RUN = False` and an MT5 live account is used. Trading can produce substantial losses. This project is experimental software, not financial advice, and does not guarantee profit.

## What it demonstrates

- Python modular architecture
- MetaTrader 5 integration
- EMA/RSI/MACD/ATR-based signal processing
- Risk-based position sizing
- ATR-based Stop Loss and Take Profit
- Maximum-open-position control
- Daily loss circuit breaker
- Broker-aware order filling
- Live-account confirmation and simulation mode

## Architecture

```text
Dig or Peak/
├── bot.py             # Main trading loop
├── config.py          # Strategy, risk, and execution settings
├── indicators.py      # Technical indicators
├── strategy.py        # Signal generation
├── risk_manager.py    # Position sizing and risk controls
├── mt5_connector.py   # MT5 connection and order execution
├── requirements.txt
└── README.md
```

## Default strategy

The default strategy uses an **EMA crossover** to identify direction, **RSI** as a filter, and **MACD histogram** as momentum confirmation. ATR is used for Stop Loss / Take Profit distance and position sizing.

## Risk management

The bot includes:

- Risk-per-trade sizing
- Maximum concurrent positions
- Daily-loss circuit breaker
- Broker volume constraints
- Stop Loss / Take Profit calculation
- Live-account confirmation
- `DRY_RUN` simulation mode

These are engineering safeguards, not guarantees against financial loss.

## Configuration

Credentials are loaded from environment variables. Never commit real MT5 passwords or account credentials.

Important settings include `SYMBOLS`, `TIMEFRAME`, `RISK_PERCENT_PER_TRADE`, `MAX_DAILY_LOSS_PERCENT`, and `DRY_RUN`.

## Running

```bash
pip install -r requirements.txt
python bot.py
```

Start with a demo account and validate behavior across different market conditions before considering live use.

## Limitations

The strategy is rule-based and does not guarantee profitability. Results can change with market conditions, spreads, commissions, execution quality, leverage, broker specifications, and parameter selection.

## Future work

- Historical backtesting
- Automated tests
- Better monitoring and logging
- Walk-forward validation
- More robust broker/execution handling

## License

Dig or Peak is **proprietary — all rights reserved**. The source is published for portfolio, review, and educational reference. Reuse, redistribution, modification, commercial exploitation, or live deployment requires explicit written permission.

See [`LICENSE`](./LICENSE).
