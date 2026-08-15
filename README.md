# Home Project

A collection of personal software projects, experiments, and learning work built while developing my programming and problem-solving skills.

This repository is part of my personal portfolio and documents how I learn by building real projects rather than only following tutorials.

## Featured Project: Cyruss

**Cyruss** is a Python-based automated trading system designed to connect with **MetaTrader 5 (MT5)** and execute a rule-based trading strategy.

The project was built as a practical exercise in software architecture, financial-market programming, automation, risk management, and defensive programming.

> **Important:** Cyruss is an educational/personal software project, not financial advice. Automated trading involves substantial risk. The project does not guarantee profitability and should not be used with real funds without extensive testing and validation.

### What Cyruss demonstrates

- Designing a modular Python application
- Connecting Python applications to MetaTrader 5
- Separating trading strategy, indicators, execution, and risk management
- Calculating position size based on risk and broker constraints
- Handling failures from external systems safely
- Working with market data and technical indicators
- Building software that prioritizes safe failure modes

### Architecture

```text
Cyruss/
├── bot.py             # Main bot workflow and execution loop
├── config.py          # Configuration and strategy parameters
├── indicators.py      # Technical indicator calculations
├── strategy.py        # Trading signal and strategy logic
├── risk_manager.py    # Position sizing and risk controls
├── mt5_connector.py   # MetaTrader 5 connection and order handling
└── README.md          # Cyruss documentation
```

The code is intentionally separated into modules so that individual components can be tested, improved, and maintained without putting the entire application in one file.

### Strategy & risk management

Cyruss uses technical-analysis components such as **EMA, RSI, and MACD** to generate rule-based signals. Risk management is handled separately from the strategy so that trade sizing and broker constraints can be controlled independently.

The bot also accounts for practical broker requirements such as minimum/maximum volume and volume-step precision.

### Reliability improvements

During code review, several failure cases were identified and hardened:

- Safely abort when an MT5 price tick cannot be retrieved.
- Treat a failed MT5 position query as a fail-safe condition instead of assuming there are no open positions.
- Respect broker volume steps such as `0.001` when calculating order size.
- Reject invalid broker volume metadata before attempting position sizing.

These changes are important because failures in an automated trading system should generally result in **no new trade**, rather than silently making assumptions about the account state.

## Other Projects

This repository also contains smaller projects and experiments that represent different stages of my learning journey:

| Project | Description |
| --- | --- |
| **Cyruss** | Python + MetaTrader 5 automated trading system |
| **Porto** | Personal portfolio website built with HTML/CSS |
| **HTML & CSS** | Front-end learning experiments and small web projects |
| **Dig or Peak** | Personal project / experiment |
| **Scap Holders** | Personal project / experiment |
| **File Pengganti** | Supporting project files and experiments |

## Technologies

- **Python** — application logic, automation, trading system
- **MetaTrader 5** — market data and trade execution interface
- **HTML5** — web structure
- **CSS3** — web styling
- **JavaScript** — front-end interactivity
- **Git & GitHub** — version control and project management

## What I Am Learning

Through these projects, I am developing practical experience in:

- Programming fundamentals and software structure
- Python application development
- Web development
- API and external-system integration
- Debugging and defensive programming
- Risk-aware software design
- Git workflows and version control
- Turning ideas into working software

## Development Philosophy

I use this repository as a record of my progression as a developer. Some projects are experiments and may be unfinished; that is intentional. The goal is to learn by building, identify problems, improve the implementation, and document what I learn along the way.

Rather than presenting every project as production-ready software, I want this repository to show the **process of learning, engineering decisions, debugging, and continuous improvement** behind my work.

## Future Improvements

Planned improvements include:

- Add automated tests for core Cyruss components
- Improve logging and monitoring
- Add backtesting capabilities
- Improve configuration management
- Add CI checks for Python code quality
- Refactor older experiments into cleaner standalone repositories
- Improve documentation and project demonstrations

## License

This repository is licensed under the MIT License. See [`LICENSE`](./LICENSE) for details.

## About Me

I am a student developer from Indonesia who enjoys learning through hands-on projects, especially in **Python, web development, automation, and software engineering**.

This repository is a work in progress, and I use it to document my journey from learning programming fundamentals to building increasingly complex projects.
