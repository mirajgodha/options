# Options Strategy Builder - Complete Documentation with Screenshots

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Strategy Output & Visualization](#strategy-output--visualization)
4. [Installation & Setup](#installation--setup)
5. [Core Architecture](#core-architecture)
6. [Strategy Reference](#strategy-reference)
7. [Configuration Guide](#configuration-guide)
8. [API & Output Formats](#api--output-formats)
9. [Broker Integration](#broker-integration)
10. [Dashboard & Visualization](#dashboard--visualization)
11. [Advanced Usage](#advanced-usage)
12. [Troubleshooting](#troubleshooting)

---

## Overview

**Options Strategy Builder** is a comprehensive Python-based platform designed for retail and professional options traders on the National Stock Exchange (NSE) of India. The tool automates the analysis, calculation, and visualization of multi-leg options strategies across all NSE derivatives-traded stocks.

### What Problem Does It Solve?

Options trading involves complex calculations across multiple strike prices, expiration dates, and strategy types. Traditional broker platforms lack:
- Real-time P&L tracking across multiple brokers
- Automated strategy profitability scanning
- Greeks calculation and sensitivity analysis
- Consolidated position management
- Risk visualization and margin tracking

This tool addresses all these challenges by providing a unified platform for strategy analysis, execution planning, and portfolio management.

---

## Features

### 13 Predefined Options Strategies

The tool supports 13 fully-implemented options strategies:

1. **Long Call Condor** - Neutral, limited risk/reward
2. **Long Iron Butterfly** - Range-bound, limited risk/reward
3. **Long Put Condor** - Bearish, limited risk/reward
4. **Short Call Butterfly** - Sideways, limited risk/reward
5. **Short Call Condor** - Bullish with high volatility
6. **Short Guts** - High volatility, unlimited risk
7. **Short Iron Butterfly** - Tight range, limited risk/reward
8. **Short Put Butterfly** - Support holding, limited risk/reward
9. **Short Put Condor** - Bullish narrow range
10. **Short Straddle** - Neutral low volatility
11. **Short Strangle** - Neutral wide range
12. **Naked Call** - Bearish view
13. **Naked Put** - Bullish view

### Excel Export with Strategy Analysis

When **Write to Excel** is enabled, the tool creates an Excel file with:
- **Separate tab for each strategy** - Organized by strategy type
- **Sorted format** - By profitability metrics
- **All NSE F&O stocks** - Complete universe analysis

**Sample Excel Output:**

![Sample Excel Output Format](https://user-images.githubusercontent.com/3658490/232991057-11ee44a8-c231-4aea-b196-762cc7f62960.png)

**Excel Columns Explanation:**
- **Stock** - NSE symbol of stock
- **PremiumCredit** - Premium credited for this strategy
- **MaxProfit** - Maximum possible profit (₹)
- **MaxLoss** - Maximum possible loss (₹)
- **PE_sell_price** - Put option sell price
- **PE_sell_strike** - Strike at which put is sold
- **PE_buy_price** - Put option buy price
- **PE_buy_strike** - Strike price of put buy
- **CE_sell_price** - Call option sell price
- **CE_sell_strike** - Strike at which call is sold
- **CE_buy_price** - Call option buy price
- **CE_buy_strike** - Strike price of call buy
- **lot_size** - Option lot size (contract multiplier)
- **pl_on_strikes** - P&L at different price ranges
  - Example: `[(-430.0, 1120, 1420), (2320.0, 1420, 1440), (-430.0, 1440, 1800)]`
  - Interpretation: Loss of ₹430 if stock closes 1120-1420, Profit of ₹2320 if 1420-1440, Loss of ₹430 if 1440-1800
- **Strikes** - All available strikes for the underlying
- **Greeks** - Delta, Gamma, Theta, Vega, IV for the complete strategy

### Greeks Calculation for Strategy Analysis

All Greeks are calculated for the complete multi-leg strategy:

- **IV** - Implied Volatility for the whole strategy
- **Theta** - Daily time decay (₹/day)
- **Total Theta** - Total theta decay for entire lot
- **Delta** - Directional sensitivity to price moves
- **Total Delta** - Total delta across all legs
- **Gamma** - Rate of change of delta
- **Vega** - Sensitivity to volatility changes (per 1% IV move)

### Automated Profitability Scanning

**"All Strategies Profitable" Mode** - Special feature that:
- Scans entire NSE F&O universe
- Tests all 13 strategies on all stocks
- Filters by configurable thresholds:
  - Maximum acceptable loss
  - Minimum profit probability
  - Minimum premium credit
- Returns sorted, actionable opportunities

**All Profitable Strategies Dashboard View:**

![All Profitable Strategies Scan](https://github.com/mirajgodha/options/assets/3658490/4fc94f21-285a-4db8-9878-b6c0837d0124)

---

## Strategy Output & Visualization

### Multi-Broker Consolidation Features

#### Consolidated P&L Dashboard

View total profit/loss across all brokers in a single unified dashboard:

![Consolidated P&L Overview](https://github.com/mirajgodha/options/assets/3658490/b30698a0-654a-4f8f-b369-89c0d84da46e)

#### Strategy-Wise P&L Charts

Individual stock strategy performance with visual breakdown:

![Strategy P&L Breakdown](https://github.com/mirajgodha/options/assets/3658490/d1c2d70c-0a88-42db-a0d6-89635d24490b)

### Position Management Dashboards

#### Stock Strategy Performance

View P&L and loss/profit bar graphs across different stock strategies:

![Stock Strategy Charts](https://github.com/mirajgodha/options/assets/3658490/dae464e0-c903-4721-9725-e80827281e67)

#### Time-Series P&L Analysis

Track PnL trends across each stock strategy over time:

![TimeSeries P&L Chart](https://github.com/mirajgodha/options/assets/3658490/0f9c76e0-eca1-4466-83f3-0fa18c56afae)

### Real-Time Market Position Tracking

#### MWPL (Market Wide Position Limits) Dashboard

Monitor ban list status and upcoming restrictions:
- Shows MWPL for each stock
- Highlights stocks approaching ban limits
- Warns about possible restrictions on new entries

![MWPL Dashboard](https://github.com/mirajgodha/options/assets/3658490/32953db0-0350-4b91-83d0-dbd290d9b13e)

#### Option Price Charts

Historical price charts for specific strikes in your open positions:

![Option Price Charts](https://github.com/mirajgodha/options/assets/3658490/32813d73-abdc-4687-a7de-09ee03bb481c)

### Margin & Risk Tracking

#### Margin Utilization Dashboard

Real-time tracking of margin used and available:
- Total margin used across all strategies
- Margin breakdown by stock
- Margin by strategy type
- Visual percentage indicators

![Margin Usage Dashboard](https://github.com/mirajgodha/options/assets/3658490/f4c42c0b-f820-4fba-afa7-5acc5fa6c431)

### Order Management & Tracking

#### Orders Dashboard

Real-time order tracking with LTP (Last Traded Price):
- **Open Orders List** - All pending orders with LTP
- **Executed Orders** - Historical list with fill prices
- **Mark-to-Market Analysis** - Current P&L on each order
- **Fill Decision Quality** - How good was your order execution?

![Orders Dashboard](https://github.com/mirajgodha/options/assets/3658490/a7b344fa-189a-4737-a699-a675fc4446c3)

### Metabase Dashboards

#### Complete P&L Dashboard

Consolidated total loss and profit across all option strategies across all brokers:

![Metabase P&L Dashboard](https://github.com/mirajgodha/options/assets/3658490/3580e74e-ac6f-4dc4-bc17-5d26daa6b1f4)

#### Multi-Strategy Analysis Dashboard

Charts of profit and loss for each stock option strategy - A unique feature unavailable in SensiBull or QuantsApp:

![Multi-Strategy Dashboard](https://github.com/mirajgodha/options/assets/3658490/5b7f4eb6-d764-4bc8-86e8-026625bd54cc)

---

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Java (for Metabase dashboards)
- SQL Database (SQLite, PostgreSQL, or MySQL)

### Quick Installation

```bash
# Clone repository
git clone https://github.com/mirajgodha/options.git
cd options

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure settings
# Edit helper/constants.py with your preferences
```

### Configure for Your Use Case

Edit `helper/constants.py`:

```python
# Market settings
TEST_RUN = False  # Set to True for testing outside market hours
MARKET_OPEN_HOUR = 9
MARKET_CLOSE_HOUR = 15

# Strike configuration
STRIKE_DIFFERENCE = 100  # For strangle/straddle strategies
MAX_LOSS_THRESHOLD = 1000  # For profitable strategy scanning

# Database
DB_TYPE = 'sqlite'  # or 'postgresql', 'mysql'
DB_CONNECTION_STRING = 'sqlite:///options_data.db'

# Broker configuration
ENABLE_ICICI_DIRECT = True
ICICI_USERNAME = 'your_username'
ICICI_PASSWORD = 'your_password'

# Output settings
WRITE_TO_EXCEL = True
WRITE_TO_SQL = True
EXCEL_OUTPUT_PATH = './output/'
```

---

## Core Architecture

### Project Structure

```
options/
├── strategy/
│   ├── calculator.py          # Core strategy calculation engine
│   ├── definitions.py         # Strategy definitions and parameters
│   └── greeks.py              # Options Greeks calculation
├── data/
│   ├── nse_fetcher.py        # NSE option chain data fetching
│   ├── historical_data.py    # Historical price and IV data
│   └── data_models.py        # Data structures
├── brokers/
│   ├── icici_direct.py       # ICICI Direct broker integration
│   └── broker_base.py        # Abstract broker interface
├── scanner/
│   ├── profitability_scanner.py  # Strategy scanning engine
│   └── filters.py             # Filtering and sorting logic
├── output/
│   ├── excel_writer.py       # Excel export functionality
│   ├── sql_writer.py         # Database persistence
│   └── metabase_config.py    # Metabase dashboard setup
├── dashboard/
│   ├── metabase/             # Metabase configuration files
│   └── config.json           # Dashboard definitions
├── helper/
│   ├── constants.py          # Global configuration
│   └── utilities.py          # Helper functions
├── main.py                   # Entry point
└── requirements.txt          # Python dependencies
```

### Data Flow

```
NSE Option Chain Data
        ↓
Strategy Calculator (Black-Scholes)
        ↓
Greeks Calculation
        ↓
├─→ Excel Export (sorted by profitability)
├─→ Database Storage (SQLite/PostgreSQL/MySQL)
└─→ Metabase Dashboard (visualization)

ICICI Direct Positions
        ↓
Position Aggregator
        ↓
├─→ Consolidated P&L Dashboard
├─→ Margin Tracker
├─→ Order Monitor
└─→ Risk Alerts
```

---

## Strategy Reference

### Long Call Condor

**Investor View:** Neutral on direction and bearish on volatility

**Setup:**
```python
strategy = calc.calculate(
    strategy_type='LONG_CALL_CONDOR',
    buy_low_call_strike=2800,
    sell_mid_low_call_strike=2850,
    sell_mid_high_call_strike=2900,
    buy_high_call_strike=2950,
    quantity=1
)
```

**Risk:** Limited  
**Reward:** Limited

**Profit Zone:** Between the two sold strikes at expiration

**Payoff Diagram:**

![Long Call Condor Payoff](https://user-images.githubusercontent.com/3658490/233072905-24081545-ffcf-4577-9dd9-02ebd5194ced.png)

**When to Use:**
- Expecting consolidation in a narrow range
- Want to reduce cost of long call spread
- Higher probability of profit than butterfly

---

### Short Strangle

**Investor View:** Neutral on direction, bearish on volatility

**Setup:**
```python
strategy = calc.calculate(
    strategy_type='SHORT_STRANGLE',
    short_put_strike=2650,
    short_call_strike=3050,
    quantity=1
)
```

**Risk:** Unlimited  
**Reward:** Limited (net premium received)

**When to Use:**
- Expecting low volatility
- Wider profit range than short straddle
- Good for theta decay capture

**Greeks Analysis:**
```python
greeks = strategy.greeks
print(f"Theta Decay: ₹{greeks['theta']} per day")  # Positive
print(f"Vega Exposure: {greeks['vega']}")          # Negative (benefits from IV drop)
```

---

### Short Straddle

**Investor View:** Directionally neutral, strongly bearish on volatility

**Setup:**
```python
strategy = calc.calculate(
    strategy_type='SHORT_STRADDLE',
    strike=2850,
    quantity=1
)
```

**Risk:** Unlimited  
**Reward:** Limited (premium received)

**When to Use:**
- Expecting very low volatility
- After earnings announcement (IV crush)
- Narrowest profit range, highest theta

---

### Naked Put

**Investor View:** Bullish outlook, willing to buy stock at strike

**Setup:**
```python
strategy = calc.calculate(
    strategy_type='NAKED_PUT',
    short_put_strike=2650,
    quantity=1
)
```

**Risk:** Strike price minus premium  
**Reward:** Limited (premium received)

**Capital Requirements:**
```python
# Typically 20x the premium collected
margin_required = strategy.max_loss * 0.2
```

---

## Configuration Guide

### Main Configuration File

**File:** `helper/constants.py`

Complete list of configurable options:

```python
# MARKET SETTINGS
TEST_RUN = False                    # Run outside market hours
MARKET_OPEN_HOUR = 9               # Market open (IST)
MARKET_CLOSE_HOUR = 15             # Market close (IST)
MARKET_DAYS = [0,1,2,3,4]         # Mon=0, Fri=4

# STRIKE CONFIGURATION
STRIKE_DIFFERENCE_STRANGLE = 100
STRIKE_DIFFERENCE_STRADDLE = 50
STRIKE_DIFFERENCE_GUTS = 200

# PROFITABILITY SCANNING
MAX_LOSS_THRESHOLD = 1000          # ₹
PROFIT_PROBABILITY_THRESHOLD = 0.60
MIN_PREMIUM_CREDIT = 500

# DATABASE
DB_TYPE = 'sqlite'                 # sqlite / postgresql / mysql
DB_CONNECTION_STRING = 'sqlite:///options_data.db'

# BROKER INTEGRATION
ENABLE_BROKER_SYNC = True
BROKER_SYNC_INTERVAL = 60          # seconds
ICICI_DIRECT_ENABLED = True

# VISUALIZATION
WRITE_TO_EXCEL = True
WRITE_TO_SQL = True
EXCEL_OUTPUT_PATH = './output/'

# OPTIONS PRICING
RISK_FREE_RATE = 0.065             # 6.5% annually
DIVIDEND_YIELD = 0.02              # 2% dividend yield
VOLATILITY_LOOKBACK_DAYS = 30

# ALERTS
MARGIN_WARNING_THRESHOLD = 0.80    # 80% usage
BAN_LIST_CHECK_INTERVAL = 300      # 5 minutes
```

---

## API & Output Formats

### Excel Output Structure

Each strategy generates a separate Excel sheet with complete P&L analysis:

| Column | Type | Description |
|--------|------|-------------|
| Stock | String | NSE symbol |
| Premium Credit/Debit | Float | Total premium (₹) |
| Max Profit | Float | Absolute max profit |
| Max Loss | Float | Absolute max loss |
| ROI | Float | Return on margin (%) |
| PE_sell_price | Float | Put option sell price |
| CE_sell_price | Float | Call option sell price |
| lot_size | Integer | Contract multiplier |
| IV | Float | Implied Volatility (%) |
| Theta (Total) | Float | Daily theta decay (₹) |
| Delta (Total) | Float | Direction sensitivity |
| Gamma | Float | Delta acceleration |
| Vega | Float | Volatility sensitivity |

### Database Schema

Strategies are stored in SQL database for historical analysis:

```sql
CREATE TABLE strategies (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR(20),
    strategy_type VARCHAR(50),
    expiry_date DATE,
    premium_credit FLOAT,
    premium_debit FLOAT,
    max_profit FLOAT,
    max_loss FLOAT,
    greeks JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Broker Integration

### ICICI Direct Integration

The tool integrates with ICICI Direct to:
- Get current open positions
- Monitor margin usage in real-time
- Track order list (pending and executed)
- Monitor MWPL (Market Wide Position Limits)

**How to Run:**
```bash
# Run ICICI Direct position sync
python brokers/icici_direct_main.py
```

**Data Retrieved:**
- Current positions with P&L
- Margin used and available
- List of executed orders with fill prices
- List of pending orders with current LTP

---

## Dashboard & Visualization

### Metabase Setup

**Download and Start:**
```bash
# Download Metabase
cd metabase/
wget https://www.metabase.com/start/oss/jar

# Install Java (if not installed)
# Ubuntu: sudo apt install openjdk-11-jdk
# macOS: brew install openjdk@11

# Start Metabase
java -jar metabase.jar
```

**Access Dashboard:**
Visit `http://localhost:3000/dashboard/1-pnl?tab=1-tab-1` in your browser

**Available Dashboards:**
1. **Consolidated P&L** - Total profit/loss across all brokers
2. **Strategy Performance** - Individual strategy P&L analysis
3. **Margin Tracking** - Real-time margin utilization
4. **Order Analysis** - Execution quality and fill analysis
5. **Risk Metrics** - Greeks exposure and risk analysis

---

## Advanced Usage

### Batch Strategy Scanning

```python
from scanner.profitability_scanner import ProfitabilityScanner

scanner = ProfitabilityScanner(
    max_loss_threshold=1000,
    profit_probability=0.65
)

results = scanner.scan_all_strategies(
    strategies=['SHORT_STRANGLE', 'NAKED_PUT'],
    strike_differences={'SHORT_STRANGLE': 150}
)

# Export results
scanner.export_to_excel(results, 'opportunities.xlsx')
scanner.export_to_database(results)
```

### Real-Time Position Monitoring

```python
from brokers.icici_direct import ICICIDirectConnector

connector = ICICIDirectConnector(username='id', password='pwd')

# Get positions
positions = connector.get_positions()
margin = connector.get_margin_used()

# Monitor MWPL
mwpl = connector.check_mwpl()
```

### Backtesting Strategies

```python
from backtesting.strategy_backtest import StrategyBacktester

backtest = StrategyBacktester(
    strategy_type='SHORT_STRANGLE',
    symbol='RELIANCE',
    start_date='2024-01-01',
    end_date='2024-12-31'
)

results = backtest.run(strike_difference=100)
print(f"Win Rate: {results['win_rate']:.2%}")
```

---

## Troubleshooting

### Common Issues

**NSE Data Not Fetching**
- Check internet connectivity
- Verify TEST_RUN flag during market hours
- Check for NSE website changes

**Broker Connection Failing**
- Verify username and password
- Ensure 2FA is disabled for API access
- Contact ICICI Direct support

**Metabase Not Starting**
- Verify Java is installed: `java -version`
- Check if port 3000 is available
- Ensure Metabase jar is in correct directory

**Database Locked Error**
- Close any other connections to the database
- For SQLite, enable WAL mode
- Consider using PostgreSQL for concurrent access

---

## Next Steps

1. **Clone & Install** - Follow installation steps above
2. **Configure** - Set up `helper/constants.py`
3. **Run First Scan** - Execute profitability scanner
4. **View Results** - Check Excel export
5. **Set Up Metabase** - Optional but recommended
6. **Monitor Positions** - Use ICICI Direct integration
7. **Optimize** - Use strategies that match your view

---

## Support & Community

- **GitHub Issues:** For bug reports and feature requests
- **Discussions:** For Q&A and general discussions
- **Documentation:** For detailed guides and tutorials

**Disclaimer:** Trading options involves substantial risk. Always use proper risk management, paper trade first, and consult financial advisors.
