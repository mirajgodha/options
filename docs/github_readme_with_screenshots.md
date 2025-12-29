# Options Strategy Builder

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NSE](https://img.shields.io/badge/Exchange-NSE-green.svg)](https://www.nseindia.com/)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

A comprehensive Python platform for NSE options traders to analyze, calculate, and visualize multi-leg options strategies with real-time P&L tracking across multiple brokers.

## 🎯 What It Does

- **Strategy Analysis:** Calculates max profit, max loss, and breakeven points for 13 predefined options strategies
- **Greeks Calculation:** Computes Delta, Gamma, Theta, Vega, and IV for portfolio risk analysis
- **Profitability Scanning:** Automatically scans entire NSE F&O universe for profitable opportunities
- **Multi-Broker Integration:** Consolidates positions and P&L across ICICI Direct and other brokers
- **Real-time Dashboard:** Visualize strategies and P&L using Metabase (open-source BI tool)
- **Excel Export:** Generates sorted, formatted Excel sheets with all strategy metrics
- **Risk Management:** Monitor margin, set P&L alerts, track order execution

## 📊 Supported Strategies

| Strategy | Type | Risk | Reward | Best For |
|----------|------|------|--------|----------|
| Long Call Condor | Debit | Limited | Limited | Neutral, low vol |
| Long Iron Butterfly | Debit | Limited | Limited | Range-bound |
| Long Put Condor | Debit | Limited | Limited | Bearish, low vol |
| Short Call Butterfly | Credit | Limited | Limited | Sideways |
| Short Call Condor | Credit | Limited | Limited | Bullish, high vol |
| Short Guts | Credit | Unlimited | Limited | High volatility |
| Short Iron Butterfly | Credit | Limited | Limited | Tight range |
| Short Put Butterfly | Credit | Limited | Limited | Support holding |
| Short Put Condor | Credit | Limited | Limited | Bullish, narrow |
| Short Straddle | Credit | Unlimited | Limited | Neutral, low vol |
| Short Strangle | Credit | Unlimited | Limited | Neutral, wide |
| Naked Call | Credit | Unlimited | Limited | Bearish |
| Naked Put | Credit | Unlimited | Limited | Bullish |

## 📈 Visual Dashboards & Output

### Excel Strategy Analysis
All strategies are exported to Excel with complete P&L analysis:

![Excel Output Format](https://user-images.githubusercontent.com/3658490/232991057-11ee44a8-c231-4aea-b196-762cc7f62960.png)

### Metabase Dashboards

**Consolidated P&L Dashboard** - Total profit/loss across all brokers:

![Consolidated P&L](https://github.com/mirajgodha/options/assets/3658490/b30698a0-654a-4f8f-b369-89c0d84da46e)

**Strategy Performance Dashboard** - Individual stock strategy analysis:

![Strategy P&L](https://github.com/mirajgodha/options/assets/3658490/d1c2d70c-0a88-42db-a0d6-89635d24490b)

### Position Management & Risk Tracking

**Stock Strategy P&L Charts:**

![Stock Strategy Charts](https://github.com/mirajgodha/options/assets/3658490/dae464e0-c903-4721-9725-e80827281e67)

**Time-Series P&L Analysis:**

![TimeSeries Analysis](https://github.com/mirajgodha/options/assets/3658490/0f9c76e0-eca1-4466-83f3-0fa18c56afae)

**MWPL (Ban List) Monitoring:**

![MWPL Dashboard](https://github.com/mirajgodha/options/assets/3658490/32953db0-0350-4b91-83d0-dbd290d9b13e)

**Option Price Charts:**

![Option Price Charts](https://github.com/mirajgodha/options/assets/3658490/32813d73-abdc-4687-a7de-09ee03bb481c)

**Margin Tracking Dashboard:**

![Margin Usage](https://github.com/mirajgodha/options/assets/3658490/f4c42c0b-f820-4fba-afa7-5acc5fa6c431)

**Orders Management Dashboard:**

![Orders Dashboard](https://github.com/mirajgodha/options/assets/3658490/a7b344fa-189a-4737-a699-a675fc4446c3)

**Multi-Strategy Analysis:**

![Multi-Strategy Dashboard](https://github.com/mirajgodha/options/assets/3658490/5b7f4eb6-d764-4bc8-86e8-026625bd54cc)

**Profitable Strategies Scan Results:**

![All Profitable Strategies](https://github.com/mirajgodha/options/assets/3658490/4fc94f21-285a-4db8-9878-b6c0837d0124)

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip / conda
- Optional: Java (for Metabase dashboards)

### Installation

```bash
# Clone the repository
git clone https://github.com/mirajgodha/options.git
cd options

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure settings
# Edit helper/constants.py with your preferences

# Run analysis
python main.py
```

### Basic Usage

```python
from strategy.calculator import StrategyCalculator
from data.nse_fetcher import NSEDataFetcher

# Fetch option chain data
fetcher = NSEDataFetcher()
option_chain = fetcher.fetch_option_chain('RELIANCE', expiry_date='2025-01-30')

# Calculate SHORT_STRANGLE strategy
calc = StrategyCalculator('RELIANCE', option_chain, 'SHORT_STRANGLE')
strategy = calc.calculate(short_put_strike=2700, short_call_strike=3100, quantity=1)

# View results
print(f"Max Profit: ₹{strategy.max_profit}")
print(f"Max Loss: ₹{strategy.max_loss}")
print(f"Theta (Daily Decay): ₹{strategy.greeks['theta']}")
print(f"Breakeven: {strategy.breakeven_points}")
```

### Scan All Stocks for Opportunities

```python
from scanner.profitability_scanner import ProfitabilityScanner

scanner = ProfitabilityScanner(
    max_loss_threshold=2000,
    profit_probability_threshold=0.60
)

results = scanner.scan_all_strategies(
    strategies=['SHORT_STRANGLE', 'SHORT_STRADDLE'],
    strike_difference=100
)

scanner.export_to_excel(results, 'profitable_strategies.xlsx')
scanner.export_to_database(results)
```

### Monitor Live Positions (ICICI Direct)

```python
from brokers.icici_direct import ICICIDirectConnector

connector = ICICIDirectConnector(username='your_id', password='your_pwd')
positions = connector.get_positions()
margin = connector.get_margin_used()

print(f"Total Margin Used: ₹{margin['used']}")
for pos in positions:
    print(f"{pos['stock']} - P&L: ₹{pos['pnl']}")
```

## 📁 Project Structure

```
options/
├── strategy/                 # Core calculation engine
│   ├── calculator.py        # Strategy calculator
│   ├── definitions.py       # Strategy definitions
│   └── greeks.py           # Greeks calculation
├── data/                     # Data fetching
│   ├── nse_fetcher.py      # NSE option chain
│   └── historical_data.py  # Historical prices
├── brokers/                  # Broker integrations
│   ├── icici_direct.py     # ICICI Direct connector
│   └── broker_base.py      # Abstract interface
├── scanner/                  # Scanning engine
│   ├── profitability_scanner.py
│   └── filters.py
├── output/                   # Export functionality
│   ├── excel_writer.py
│   ├── sql_writer.py
│   └── metabase_config.py
├── dashboard/               # Metabase configs
├── helper/                  # Utilities
│   └── constants.py        # Configuration
├── main.py                 # Entry point
└── requirements.txt        # Dependencies
```

## ⚙️ Configuration

Edit `helper/constants.py`:

```python
# Market settings
TEST_RUN = False                    # Test outside market hours
MARKET_OPEN_HOUR = 9
MARKET_CLOSE_HOUR = 15

# Strategy configuration
STRIKE_DIFFERENCE = 100             # For strangle/straddle
MAX_LOSS_THRESHOLD = 1000          # Scanning filter

# Database
DB_TYPE = 'sqlite'
DB_CONNECTION_STRING = 'sqlite:///options_data.db'

# Broker
ICICI_DIRECT_ENABLED = True
ICICI_USERNAME = 'your_username'
ICICI_PASSWORD = 'your_password'

# Output
WRITE_TO_EXCEL = True
WRITE_TO_SQL = True
EXCEL_OUTPUT_PATH = './output/'
```

## 📈 Visualization with Metabase

```bash
# Download Metabase
cd metabase/
wget https://downloads.metabase.com/v0.46.6/metabase.jar

# Start Metabase
java -jar metabase.jar

# Access at http://localhost:3000
```

**Available Dashboards:**
- Consolidated P&L across all brokers
- Strategy-wise P&L breakdown
- Real-time margin tracking
- Order execution analysis
- Greeks heatmaps
- MWPL monitoring

## 📊 Excel Output Format

Each strategy generates a separate tab with:
- Symbol, premium, max profit/loss
- Breakeven points
- Greeks (Delta, Gamma, Theta, Vega, IV)
- P&L at different price levels
- Available strike prices

**Example Output:**
```
RELIANCE | Premium: ₹850 | Max Profit: ₹850 | Max Loss: ₹2150
Theta: ₹45.3/day | Delta: -0.15 | IV: 18.5%
Breakeven: 2650, 3050
```

## 🔧 Advanced Features

### Batch Scanning
```python
# Scan multiple strategies across all NSE F&O stocks
scanner.scan_multiple(
    strategies=['SHORT_STRANGLE', 'NAKED_PUT', 'SHORT_STRADDLE'],
    strike_differences={'SHORT_STRANGLE': 150, 'NAKED_PUT': 100}
)
```

### Position Monitoring
```python
# Real-time P&L alerts
monitor = PositionMonitor()
monitor.add_profit_trigger(strategy_id=123, profit_target=5000)
monitor.add_loss_trigger(strategy_id=123, loss_limit=2000)
monitor.start()
```

### Greeks Rebalancing
```python
# Rebalance portfolio to target Greeks
rebalancer.suggest_rebalance(
    target_delta=-0.2,
    target_vega=0
)
```

### Backtesting
```python
# Historical analysis of strategy returns
backtest = StrategyBacktester('SHORT_STRANGLE', 'RELIANCE', 
    start_date='2024-01-01', end_date='2024-12-31')
results = backtest.run(strike_difference=100, profit_target=0.30)
print(f"Win Rate: {results['win_rate']:.2%}")
```

## 🔌 Broker Integration

### ICICI Direct
```python
connector = ICICIDirectConnector(username='id', password='pwd')
connector.get_positions()      # Current positions
connector.get_margin_used()    # Margin utilization
connector.get_orders()         # Order status
connector.check_mwpl()         # Ban list alerts
```

### Adding New Brokers
Extend `brokers/broker_base.py` and implement:
- `authenticate()`
- `get_positions()`
- `get_margin_used()`
- `get_orders()`

## 📝 Greeks Reference

- **Delta:** Directional sensitivity (range: -1 to +1)
- **Gamma:** Rate of delta change (positive for long options)
- **Theta:** Daily time decay (positive for short options)
- **Vega:** Volatility sensitivity (per 1% IV change)
- **IV:** Implied Volatility (market's volatility expectations)

## 🐛 Troubleshooting

**NSE data not fetching?**
- Check internet connectivity
- Verify TEST_RUN flag during market hours

**ICICI Direct auth failing?**
- Ensure 2FA is disabled for API access
- Verify username/password in config

**Metabase not loading?**
- Check if Java is installed: `java -version`
- Verify Metabase is running: `curl http://localhost:3000`
- Check database connection settings

**Greeks returning NaN?**
- Ensure time to expiry > 0
- Verify IV > 0
- Check stock price and strike are positive

## 📚 Documentation

- **[Comprehensive Guide](./docs/comprehensive_guide.md)** - Detailed documentation
- **[API Reference](./docs/api_reference.md)** - Function signatures and examples
- **[Installation Guide](./docs/installation.md)** - Platform-specific setup
- **[Strategy Details](./docs/strategies.md)** - In-depth strategy explanations

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Style
```bash
pip install flake8
flake8 options/ --max-line-length=100
```

### Testing
```bash
pip install pytest
pytest tests/ -v
```

## 📋 Requirements

```
pandas>=1.3.0
numpy>=1.21.0
openpyxl>=3.6.0
requests>=2.26.0
beautifulsoup4>=4.9.3
lxml>=4.6.3
sqlalchemy>=1.4.0
py_vollib>=0.1.0
scipy>=1.7.0
matplotlib>=3.4.0
```

## 🔒 Disclaimer

**This tool is for educational and research purposes.** Options trading involves substantial risk of loss. Always:

- ✓ Understand strategies before trading
- ✓ Use proper risk management
- ✓ Paper trade before live trading
- ✓ Consult financial advisors
- ✓ Start with small positions

**Past performance does not guarantee future results.**

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙋 Support

- **Issues:** [GitHub Issues](https://github.com/mirajgodha/options/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mirajgodha/options/discussions)

## 🎯 Roadmap

- [ ] Additional broker integrations (Zerodha, 5Paisa, ICICI Securities)
- [ ] ML-based strategy recommendations
- [ ] Options spreads optimizer
- [ ] Real-time SMS/Email alerts
- [ ] Mobile app for monitoring
- [ ] Portfolio optimization module
- [ ] Advanced Greeks visualizations
- [ ] Options chain screener

## 👏 Acknowledgments

Built by options traders, for options traders. Inspired by professional tools like SensiBull and QuantsApp, but open-source and free.

## 📞 Connect

- GitHub: [@mirajgodha](https://github.com/mirajgodha)
- Contributions welcome!

---

**⭐ If you find this useful, please star the repository!**

---

**Last Updated:** Jan 2025  
**Version:** 1.0.0  
**Python:** 3.7+
