# Options Strategy Builder

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NSE](https://img.shields.io/badge/Exchange-NSE-green.svg)](https://www.nseindia.com/)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

A comprehensive Python platform for NSE options traders to analyze, calculate, and visualize multi-leg options strategies with real-time P&L tracking across multiple brokers (ICICI Direct, Nuvama).

## 🎯 What It Does

- **Strategy Analysis:** Calculates max profit, max loss, and breakeven points for 13 predefined options strategies
- **Greeks Calculation:** Computes Delta, Gamma, Theta, Vega, and IV for portfolio risk analysis
- **Profitability Scanning:** Automatically scans entire NSE F&O universe for profitable opportunities
- **Multi-Broker Integration:** Consolidates positions and P&L across ICICI Direct and Nuvama Wealth
- **Real-time Dashboard:** Visualize strategies and P&L using Metabase (open-source BI tool)
- **Excel Export:** Generates sorted, formatted Excel sheets with all strategy metrics
- **Risk Management:** Monitor margin, set P&L alerts, track order execution across brokers

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

### Monitor Live Positions

```python
from brokers.icici_direct import ICICIDirectConnector
from brokers.nuvama import NuvamaBrokerConnector

# Connect to ICICI Direct
icici = ICICIDirectConnector(username='your_id', password='your_pwd')
icici.authenticate()
icici_positions = icici.get_positions()

# Connect to Nuvama
nuvama = NuvamaBrokerConnector(client_id='your_client_id', password='your_pwd')
nuvama.authenticate()
nuvama_positions = nuvama.get_positions()

# Consolidated view
total_pnl = sum(p['pnl'] for p in (icici_positions + nuvama_positions))
print(f"Total P&L across all brokers: ₹{total_pnl:,.2f}")
```

## 📁 Project Structure

```
options/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── helper/
│   └── constants.py               # Configuration settings
├── strategy/                       # Core calculation engine
│   ├── calculator.py              # Strategy calculator
│   ├── definitions.py             # Strategy definitions
│   └── greeks.py                  # Greeks calculation
├── data/                           # Data fetching
│   ├── nse_fetcher.py             # NSE option chain data
│   └── historical_data.py         # Historical prices
├── brokers/                        # Broker integrations
│   ├── icici_direct.py            # ICICI Direct connector
│   ├── nuvama.py                  # Nuvama Wealth connector
│   └── broker_base.py             # Abstract interface
├── scanner/                        # Scanning engine
│   ├── profitability_scanner.py   # Strategy scanning
│   └── filters.py                 # Filtering logic
├── output/                         # Export functionality
│   ├── excel_writer.py            # Excel export
│   ├── sql_writer.py              # Database export
│   └── metabase_config.py         # Metabase setup
├── dashboard/                      # Metabase configs
├── metabase/                       # Metabase JAR and configs
├── main.py                         # Entry point
└── docs/                           # 📚 Documentation
    ├── START_HERE.md
    ├── QUICK_NUVAMA_SETUP.md
    ├── installation_guide.md
    ├── nuvama_integration_guide.md
    ├── multi_broker_integration_guide.md
    ├── comprehensive_docs_with_screenshots.md
    ├── api_documentation.md
    └── DOCUMENTATION_INDEX.md
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

# Broker Configuration
ENABLE_BROKER_SYNC = True

# ICICI Direct
ICICI_DIRECT_ENABLED = True
ICICI_USERNAME = 'your_username'
ICICI_PASSWORD = 'your_password'

# Nuvama Wealth
NUVAMA_ENABLED = True
NUVAMA_CLIENT_ID = 'your_client_id'      # Get from profile
NUVAMA_PASSWORD = 'your_password'

# Output
WRITE_TO_EXCEL = True
WRITE_TO_SQL = True
EXCEL_OUTPUT_PATH = './output/'
```

## 🔌 Broker Integration

### Supported Brokers

| Broker | Status | API Charges | F&O Support | Documentation |
|--------|--------|-------------|-------------|----------------|
| **ICICI Direct** | ✅ Production Ready | No | Yes | [Setup](./docs/installation_guide.md) |
| **Nuvama Wealth** | ✅ Production Ready | No | Yes | [Guide](./docs/nuvama_integration_guide.md) |
| **Multi-Broker** | ✅ Production Ready | No | Yes | [Guide](./docs/multi_broker_integration_guide.md) |
| **Zerodha** | 📋 Roadmap | No | Yes | - |
| **5Paisa** | 📋 Roadmap | No | Yes | - |

### ICICI Direct

```python
from brokers.icici_direct import ICICIDirectConnector

connector = ICICIDirectConnector(username='your_id', password='your_pwd')
connector.authenticate()

positions = connector.get_positions()       # Current positions
margin = connector.get_margin_used()        # Margin status
orders = connector.get_orders(status='OPEN') # Open orders
mwpl = connector.check_mwpl()               # Ban list alerts
```

### Nuvama Wealth

```python
from brokers.nuvama import NuvamaBrokerConnector

# Get Client ID from https://www.nuvamawealth.com/login → Profile
connector = NuvamaBrokerConnector(client_id='your_client_id', password='your_pwd')
connector.authenticate()

positions = connector.get_positions()        # Current positions
margin = connector.get_margin_used()         # Margin status
orders = connector.get_orders(status='OPEN') # Open orders
mwpl = connector.check_mwpl()                # MWPL status
```

### Consolidated Multi-Broker Dashboard

```python
from brokers.icici_direct import ICICIDirectConnector
from brokers.nuvama import NuvamaBrokerConnector

# Connect to both brokers
icici = ICICIDirectConnector(username='id', password='pwd')
nuvama = NuvamaBrokerConnector(client_id='id', password='pwd')

icici.authenticate()
nuvama.authenticate()

# Consolidated metrics
icici_pnl = sum(p['pnl'] for p in icici.get_positions())
nuvama_pnl = sum(p['pnl'] for p in nuvama.get_positions())

print(f"ICICI Direct: ₹{icici_pnl:,.2f}")
print(f"Nuvama Wealth: ₹{nuvama_pnl:,.2f}")
print(f"Total: ₹{icici_pnl + nuvama_pnl:,.2f}")
```

### Broker Documentation

**Quick Start (10 minutes):**
- [**QUICK_NUVAMA_SETUP.md**](./docs/QUICK_NUVAMA_SETUP.md) - Get started with Nuvama immediately

**Complete Integration Guides (30-40 minutes each):**
- [**Nuvama Integration Guide**](./docs/nuvama_integration_guide.md) - Complete setup, 12+ working examples, troubleshooting, advanced features
- [**Multi-Broker Integration Guide**](./docs/multi_broker_integration_guide.md) - Use ICICI Direct + Nuvama together, consolidated dashboard, real-time monitoring script

**General Setup & Reference:**
- [**Installation Guide**](./docs/installation_guide.md) - All platforms (Windows/Mac/Linux/Docker), 10 troubleshooting solutions
- [**API Reference**](./docs/api_documentation.md) - 50+ working code examples

**Complete Feature Documentation:**
- [**Comprehensive Guide**](./docs/comprehensive_docs_with_screenshots.md) - All features, 13 strategies, 13 integrated screenshots

### Nuvama Wealth - Key Benefits

✅ **No API charges** - Completely free integration  
✅ **₹20/lot options** - Competitive options brokerage  
✅ **Deep OTM trading** - Trade far out-of-money options in NRML mode  
✅ **Discounted exchange charges** - ~₹3,500/Cr vs standard rates  
✅ **Online margin pledge** - Enhance margin instantly  
✅ **SEBI regulated** - Safe and trustworthy broker  

**Quick Links:**
- Account Opening: https://www.nuvamawealth.com/demat-account
- Login Portal: https://www.nuvamawealth.com/login
- API Documentation: https://www.nuvamawealth.com/api-connect/
- Support: 1800-102-3335 | helpdesk@nuvama.com

### Adding New Brokers

To add support for Zerodha, 5Paisa, or other brokers, see [Multi-Broker Guide - Adding New Brokers](./docs/multi_broker_integration_guide.md#adding-new-brokers) section.

Implement the `BrokerInterface` abstract class:
- `authenticate()`
- `get_positions()`
- `get_margin_used()`
- `get_orders()`
- `check_mwpl()`
- `place_order()` (optional)

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
- Multi-broker position tracking

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

## 📝 Greeks Reference

- **Delta:** Directional sensitivity (range: -1 to +1)
- **Gamma:** Rate of delta change (positive for long options)
- **Theta:** Daily time decay (positive for short options)
- **Vega:** Volatility sensitivity (per 1% IV change)
- **IV:** Implied Volatility (market's volatility expectations)

## 📚 Documentation

Complete documentation is available in the `/docs` folder. Start here based on your needs:

### 🚀 New Users (Quick Path: 30 minutes)
1. **[START_HERE.md](./docs/START_HERE.md)** (5 min) - Overview and what to do next
2. **[QUICK_NUVAMA_SETUP.md](./docs/QUICK_NUVAMA_SETUP.md)** (10 min) - Get started with Nuvama in 10 minutes
3. **[Installation Guide](./docs/installation_guide.md)** (15 min) - Complete setup for your platform

### 📖 Learning the Tool (1-2 hours)
- **[Comprehensive Guide](./docs/comprehensive_docs_with_screenshots.md)** - Complete documentation with all 13 strategies, features, and 13 integrated screenshots

### 💻 Developers (1 hour)
- **[API Reference](./docs/api_documentation.md)** - Complete API documentation with 50+ working code examples
- **[Multi-Broker Guide](./docs/multi_broker_integration_guide.md)** - Integration patterns, 9+ examples

### 🔧 Broker Integration (30-40 minutes each)
- **[Nuvama Integration Guide](./docs/nuvama_integration_guide.md)** - Complete Nuvama setup, 12+ examples, advanced features
- **[Multi-Broker Integration Guide](./docs/multi_broker_integration_guide.md)** - Use multiple brokers with unified interface

### 🗺️ Navigation & Reference
- **[Documentation Index](./docs/DOCUMENTATION_INDEX.md)** - Complete index of all documentation files

### 📊 Documentation Quick Reference

| Document | Time | Best For |
|----------|------|----------|
| START_HERE.md | 5 min | Everyone - start here |
| QUICK_NUVAMA_SETUP.md | 10 min | Nuvama quick start |
| Installation Guide | 15 min | New users |
| Comprehensive Guide | 60 min | Learning all features |
| API Reference | 20 min | Developers |
| Nuvama Integration | 30 min | Nuvama users |
| Multi-Broker Guide | 30 min | Multi-broker setup |
| Documentation Index | 10 min | Finding things |

## 🐛 Troubleshooting

**NSE data not fetching?**
- Check internet connectivity
- Verify TEST_RUN flag during market hours
- See [Installation Guide - Common Issues](./docs/installation_guide.md#common-issues--solutions)

**ICICI Direct auth failing?**
- Ensure 2FA is disabled for API access
- Verify username/password in config
- See [Installation Guide - Common Issues](./docs/installation_guide.md#common-issues--solutions)

**Nuvama auth failing?**
- Verify Client ID is correct (6-8 digits from profile)
- Check password
- See [Nuvama Guide - Troubleshooting](./docs/nuvama_integration_guide.md#troubleshooting)

**Metabase not loading?**
- Check if Java is installed: `java -version`
- Verify Metabase is running: `curl http://localhost:3000`

**Greeks returning NaN?**
- Ensure time to expiry > 0
- Verify IV > 0
- See [API Reference - Greeks](./docs/api_documentation.md#greeks-calculator-module)

**Need more help?**
- See **[Installation Guide](./docs/installation_guide.md#common-issues--solutions)** for 10 common issues & solutions
- Check **[Documentation Index](./docs/DOCUMENTATION_INDEX.md)** for complete file navigation

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

- **GitHub Issues:** [GitHub Issues](https://github.com/mirajgodha/options/issues)
- **GitHub Discussions:** [GitHub Discussions](https://github.com/mirajgodha/options/discussions)
- **ICICI Direct Support:** 9650200000
- **Nuvama Support:** 1800-102-3335
- **Documentation:** See `/docs` folder for comprehensive guides

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
