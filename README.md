# Flask Backtester 📈

A comprehensive, local CSV-based options strategy backtesting platform built with Flask. Design, test, and analyze your trading strategies with an intuitive web interface.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### Strategy Builder
- **Multi-leg strategies**: Build complex options strategies with unlimited legs
- **Flexible strike selection**: ATM, ITM, OTM with custom offsets
- **Time-based entries/exits**: Configure entry and exit times
- **Individual leg SL/Target**: Per-leg stoploss and target percentages
- **Combined SL/Target**: Portfolio-level risk management
- **Strategy templates**: Pre-built templates for common strategies

### Data Support
- **Folder-based options data**: Support for expiry-organized data structure
- **Single CSV files**: Traditional CSV format support
- **Real-time validation**: Automatic data validation on upload

### Technical Indicators
- Moving Averages: SMA, EMA, WMA, DEMA, TEMA
- Oscillators: RSI, Stochastic, CCI, Williams %R
- Volatility: ATR, Bollinger Bands, Keltner Channels
- Momentum: MACD, ADX, Momentum, ROC
- Volume: OBV, VWAP

### Analytics Dashboard
- Comprehensive metrics: Sharpe, Sortino, Calmar ratios
- Visual analytics: Equity curve, P&L distribution
- Trade log: Detailed trade-by-trade analysis
- Export functionality: CSV export

## 🚀 Quick Start

```bash
cd backtest_opus
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask run
```

Access at: http://localhost:5000

## 📁 Data Formats

### Spot Data CSV
```csv
datetime,open,high,low,close,volume
2024-01-01 09:15:00,21500.00,21510.50,21495.00,21505.25,150000
```

### Options Data - Folder Structure
```
historical_1_min/
├── 2024-10-03/           # Expiry date
│   ├── 25500.0_CE.csv    # Strike_Type.csv
│   ├── 25500.0_PE.csv
│   └── ...
├── 2024-10-10/
│   └── ...
```

### Options Data - Single CSV
```csv
datetime,symbol,open,high,low,close,volume,oi
2024-01-01 09:15:00,NIFTY24JAN21500CE,150.00,155.50,148.00,153.25,50000,1000000
```

## 📊 Strategy Configuration

```json
{
  "legs": [
    {
      "option_type": "CE",
      "strike_selection": "ATM",
      "strike_offset": 0,
      "action": "SELL",
      "lots": 1,
      "entry_time": "09:20",
      "exit_time": "15:15",
      "stoploss_percent": 30,
      "target_percent": 50
    }
  ],
  "conditions": {
    "combined_sl_percent": 25,
    "combined_target_percent": 40
  }
}
```

## 📈 Performance Metrics

| Metric | Description |
|--------|-------------|
| Net P&L | Total profit/loss after costs |
| Win Rate | Percentage of winning trades |
| Profit Factor | Gross profit / Gross loss |
| Sharpe Ratio | Risk-adjusted return (annualized) |
| Sortino Ratio | Downside risk-adjusted return |
| Max Drawdown | Largest peak-to-trough decline |

## 🔧 Trading Constants

| Constant | NIFTY | BANKNIFTY |
|----------|-------|-----------|
| Lot Size | 25 | 15 |
| Strike Step | 50 | 100 |

Default slippage: 0.05%  
Default brokerage: ₹20 per order

## License

MIT License
