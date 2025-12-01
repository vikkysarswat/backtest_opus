# Flask Backtester 📈

A comprehensive, local CSV-based options strategy backtesting platform built with Flask. Design, test, and analyze your trading strategies with an intuitive web interface.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

## Features

- **Multi-leg Strategy Builder**: Build complex options strategies with unlimited legs
- **Folder-based Options Data**: Support for expiry-date organized data structure
- **18+ Technical Indicators**: SMA, EMA, RSI, MACD, ATR, Bollinger Bands, etc.
- **Comprehensive Analytics**: Sharpe, Sortino, Calmar ratios, drawdown analysis
- **Interactive Charts**: Equity curve, P&L distribution, daily breakdown
- **Dark/Light Theme**: Modern UI with Bootstrap 5

## Quick Start

```bash
cd backtest_opus
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask run
```

## Data Structure

### Spot Data (CSV)
```csv
datetime,open,high,low,close,volume
2024-01-01 09:15:00,21500.00,21510.50,21495.00,21505.25,150000
```

### Options Data (Folder Structure)
```
historical_1_min/
├── 2024-10-03/
│   ├── 25500.0_CE.csv
│   ├── 25500.0_PE.csv
│   └── ...
├── 2024-10-10/
│   └── ...
```

## License

MIT License
