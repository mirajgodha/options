# Options Strategy Builder - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation & Setup](#installation--setup)
4. [Quick Start](#quick-start)
5. [Core Architecture](#core-architecture)
6. [Strategy Reference](#strategy-reference)
7. [Configuration Guide](#configuration-guide)
8. [API & Output Formats](#api--output-formats)
9. [Broker Integration](#broker-integration)
10. [Dashboard & Visualization](#dashboard--visualization)
11. [Advanced Usage](#advanced-usage)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)

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

### Target Users
- Active options traders managing positions across multiple brokers
- Quantitative traders building systematic strategies
- Risk managers monitoring portfolio exposure
- Options educators and learners

### Technology Stack
- **Language:** Python 3.7+
- **Data Processing:** Pandas, NumPy
- **Options Pricing:** Black-Scholes Model implementation
- **Visualization:** Metabase (open-source BI platform)
- **Database:** SQL-based (supports SQLite, PostgreSQL, MySQL)
- **Broker Integration:** ICICI Direct API, extensible for other brokers
- **Excel Export:** openpyxl, xlrd

---

## Features

### Strategy Analysis Engine

The tool supports 13 predefined options strategies with full P&L analysis:

| Strategy | Type | Risk | Reward | Use Case |
|----------|------|------|--------|----------|
| **Long Call Condor** | Debit | Limited | Limited | Neutral outlook, low volatility |
| **Long Iron Butterfly** | Neutral | Limited | Limited | Range-bound market |
| **Long Put Condor** | Debit | Limited | Limited | Bearish, low vol |
| **Short Call Butterfly** | Credit | Limited | Limited | Sideways market |
| **Short Call Condor** | Credit | Limited | Limited | Bullish, high vol |
| **Short Guts** | Credit | Unlimited | Limited | High volatility environment |
| **Short Iron Butterfly** | Credit | Limited | Limited | Tight range expected |
| **Short Put Butterfly** | Credit | Limited | Limited | Support holding |
| **Short Put Condor** | Credit | Limited | Limited | Bullish, narrow range |
| **Short Straddle** | Credit | Unlimited | Limited | Neutral, low vol |
| **Short Strangle** | Credit | Unlimited | Limited | Neutral, out-of-money |
| **Naked Call** | Credit | Unlimited | Limited | Bearish view |
| **Naked Put** | Credit | Unlimited | Limited | Bullish view |

### Greeks Calculation
Comprehensive options Greeks are calculated for each strategy:
- **Delta:** Directional sensitivity to stock price changes
- **Gamma:** Rate of change of delta
- **Theta:** Time decay benefit
- **Vega:** Volatility sensitivity
- **Implied Volatility (IV):** Market's volatility expectations

### Multi-Broker Position Aggregation
- **Unified Dashboard:** View consolidated positions across multiple brokers
- **Real-time P&L:** Mark-to-market calculations
- **Margin Tracking:** Monitor margin utilization across strategies
- **Order Management:** Track pending and executed orders
- **Ban List Monitoring:** MWPL (Market Wide Position Limits) alerts

### Automated Profitability Scanning
- **"All Strategies Profitable" Mode:** Scan entire NSE F&O universe
- **Customizable Filters:** Configure strike differences and profit thresholds
- **Excel Export:** Sorted results by profitability
- **Database Storage:** Store results for historical analysis

### Advanced Dashboarding
- **Metabase Integration:** Professional visualization platform
- **Multiple View Types:** Charts, tables, KPIs, time-series
- **Custom Alerts:** Set profit/loss triggers
- **Historical Analysis:** Track strategy performance over time
- **Multi-broker Reporting:** Consolidated financial metrics

---

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Java (for Metabase)
- SQL Database (SQLite, PostgreSQL, or MySQL)

### Step 1: Clone Repository
```bash
git clone https://github.com/mirajgodha/options.git
cd options
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Required Packages:**
```
pandas>=1.3.0
numpy>=1.21.0
openpyxl>=3.6.0
requests>=2.26.0
beautifulsoup4>=4.9.3
lxml>=4.6.3
sqlalchemy>=1.4.0
py_vollib>=0.1.0  # For Greeks calculation
scipy>=1.7.0
matplotlib>=3.4.0
```

### Step 3: Configure Constants
Edit `helper/constants.py` to set:
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

### Step 4: Database Setup
For SQLite (default):
```python
# Automatically created on first run
pass
```

For PostgreSQL:
```bash
createdb options_trading
psql options_trading < schema.sql
```

### Step 5: Broker Credentials (Optional)
Create a `config/broker_credentials.json`:
```json
{
  "icici_direct": {
    "username": "your_icicidirect_username",
    "password": "your_password"
  }
}
```

---

## Quick Start

### Basic Strategy Analysis

**Scenario:** Analyze Short Strangle on RELIANCE with max loss threshold of ₹2000

```python
from strategy.calculator import StrategyCalculator
from data.nse_fetcher import NSEDataFetcher

# Step 1: Fetch option chain data
fetcher = NSEDataFetcher()
option_chain = fetcher.fetch_option_chain('RELIANCE', expiry_date='2025-01-30')

# Step 2: Initialize calculator
calc = StrategyCalculator(
    stock_symbol='RELIANCE',
    option_chain=option_chain,
    strategy_type='SHORT_STRANGLE'
)

# Step 3: Calculate strategy metrics
strategy = calc.calculate(
    short_put_strike=2700,
    short_call_strike=3100,
    quantity=1
)

# Step 4: View results
print(f"Premium Credit: ₹{strategy.premium_credit}")
print(f"Max Profit: ₹{strategy.max_profit}")
print(f"Max Loss: ₹{strategy.max_loss}")
print(f"Breakeven Points: {strategy.breakeven_points}")
print(f"Delta: {strategy.greeks['delta']}")
print(f"Theta (Daily): ₹{strategy.greeks['theta']}")
```

### Scan All Stocks for Profitable Strategies

```python
from scanner.profitability_scanner import ProfitabilityScanner

scanner = ProfitabilityScanner(
    max_loss_threshold=2000,
    profit_probability_threshold=0.60
)

results = scanner.scan_all_strategies(
    strategies=['SHORT_STRANGLE', 'SHORT_STRADDLE', 'NAKED_PUT'],
    strike_difference=100
)

scanner.export_to_excel(results, 'profitable_strategies.xlsx')
scanner.export_to_database(results)
```

### Set Up Broker Integration

```python
from brokers.icici_direct_connector import ICICIDirectConnector

connector = ICICIDirectConnector(
    username='your_username',
    password='your_password'
)

# Get current positions
positions = connector.get_positions()
margin_used = connector.get_margin_used()
orders = connector.get_orders()

print(f"Total Margin Used: ₹{margin_used['total']}")
for pos in positions:
    print(f"{pos['stock']} - P&L: ₹{pos['pnl']}")
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

### Data Flow Diagram

```
NSE Option Chain Data
        ↓
Strategy Calculator (Black-Scholes)
        ↓
Greeks Calculation
        ↓
├─→ Excel Export
├─→ Database Storage
└─→ Metabase Dashboard

Broker Positions (ICICI Direct)
        ↓
Position Aggregator
        ↓
├─→ Consolidated P&L Dashboard
├─→ Margin Tracker
├─→ Order Monitor
└─→ Risk Alerts
```

### Key Modules

#### `strategy/calculator.py`
**Purpose:** Core engine for strategy P&L calculation

**Key Classes:**
```python
class StrategyCalculator:
    def __init__(self, stock_symbol, option_chain, strategy_type)
    def calculate(self, **kwargs) -> Strategy
    
class Strategy:
    premium_credit: float
    premium_debit: float
    max_profit: float
    max_loss: float
    breakeven_points: List[float]
    greeks: Dict[str, float]
    pl_on_strikes: List[Tuple[float, float, float]]
```

#### `data/nse_fetcher.py`
**Purpose:** Fetch live option chain data from NSE

**Key Methods:**
```python
class NSEDataFetcher:
    def fetch_option_chain(self, symbol, expiry_date) -> OptionChain
    def fetch_strike_data(self, symbol) -> List[Strike]
    def fetch_implied_volatility(self, symbol) -> Dict
```

#### `brokers/icici_direct.py`
**Purpose:** ICICI Direct integration for position tracking

**Key Methods:**
```python
class ICICIDirectConnector:
    def get_positions(self) -> List[Position]
    def get_margin_used(self) -> Dict[str, float]
    def get_orders(self) -> List[Order]
    def place_order(self, order) -> OrderResponse
    def cancel_order(self, order_id) -> bool
```

---

## Strategy Reference

### Long Call Condor

**Definition:** Buy lower strike call, sell two middle strikes, buy higher strike call

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

**Investor View:**
- Neutral on direction
- Bearish on volatility

**Risk:** Limited (net premium paid)  
**Reward:** Limited (difference between strikes - net premium paid)

**Profit Zone:** Between the two sold strikes at expiration

**When to Use:**
- Expecting consolidation in a narrow range
- Want to reduce cost of long call spread
- Higher probability of profit than butterfly

---

### Short Strangle

**Definition:** Sell out-of-the-money put, sell out-of-the-money call

**Setup:**
```python
strategy = calc.calculate(
    strategy_type='SHORT_STRANGLE',
    short_put_strike=2650,
    short_call_strike=3050,
    quantity=1
)
```

**Investor View:**
- Neutral on direction
- Bearish on volatility

**Risk:** Unlimited  
**Reward:** Limited (net premium received)

**Profit Zone:** Between the two short strikes at expiration

**When to Use:**
- Expecting low volatility
- Wider profit range than short straddle
- Good for theta decay capture

**Greeks Insights:**
```python
greeks = strategy.greeks
print(f"Theta Decay: ₹{greeks['theta']} per day")  # Positive (beneficial)
print(f"Vega Exposure: {greeks['vega']}")           # Negative (benefits from IV drop)
```

---

### Short Straddle

**Definition:** Sell at-the-money put, sell at-the-money call

**Setup:**
```python
strategy = calc.calculate(
    strategy_type='SHORT_STRADDLE',
    strike=2850,
    quantity=1
)
```

**Investor View:**
- Directionally neutral
- Strongly bearish on volatility

**Risk:** Unlimited  
**Reward:** Limited (premium received)

**Profit Zone:** Between breakeven points (strike ± premium)

**When to Use:**
- Expecting very low volatility
- After earnings announcement (IV crush)
- Narrowest profit range, highest theta

---

### Naked Put

**Definition:** Sell out-of-the-money put option

**Setup:**
```python
strategy = calc.calculate(
    strategy_type='NAKED_PUT',
    short_put_strike=2650,
    quantity=1
)
```

**Investor View:**
- Bullish outlook
- Willing to buy stock at strike

**Risk:** Strike price minus premium  
**Reward:** Limited (premium received)

**When to Use:**
- Bullish on stock, want to own it
- Collect premium if stock stays above strike
- Capital-efficient alternative to covered call

**Capital Requirements:**
```python
# Typically 20x the premium collected
margin_required = strategy.max_loss * 0.2
```

---

## Configuration Guide

### `helper/constants.py` - Detailed Settings

```python
# ===== MARKET SETTINGS =====
TEST_RUN = False                    # Run outside market hours
MARKET_OPEN_HOUR = 9               # Market open time (IST)
MARKET_CLOSE_HOUR = 15             # Market close time (IST)
MARKET_DAYS = [0,1,2,3,4]         # Monday=0, Friday=4

# ===== STRIKE CONFIGURATION =====
# For SHORT_STRANGLE, NAKED_PUT, NAKED_CALL, SHORT_GUTS
STRIKE_DIFFERENCE_STRANGLE = 100    # Strike spacing
STRIKE_DIFFERENCE_STRADDLE = 50
STRIKE_DIFFERENCE_GUTS = 200

# ===== PROFITABILITY SCANNING =====
MAX_LOSS_THRESHOLD = 1000          # Max acceptable loss (₹)
PROFIT_PROBABILITY_THRESHOLD = 0.60 # Min probability of profit
MIN_PREMIUM_CREDIT = 500            # Minimum premium for credit strategies

# ===== DATABASE =====
DB_TYPE = 'sqlite'                  # sqlite / postgresql / mysql
DB_CONNECTION_STRING = 'sqlite:///options_data.db'
DB_ECHO = False                    # SQL query logging

# ===== BROKER INTEGRATION =====
ENABLE_BROKER_SYNC = True
BROKER_SYNC_INTERVAL = 60           # Seconds
ICICI_DIRECT_ENABLED = True

# ===== VISUALIZATION =====
WRITE_TO_EXCEL = True
WRITE_TO_SQL = True
EXCEL_OUTPUT_PATH = './output/'
EXCEL_INCLUDE_PL_CHART = True

# ===== OPTIONS PRICING =====
RISK_FREE_RATE = 0.065             # Annual risk-free rate
DIVIDEND_YIELD = 0.02              # Expected dividend yield
VOLATILITY_SOURCE = 'nse'          # nse / computed
VOLATILITY_LOOKBACK_DAYS = 30      # For historical volatility

# ===== ALERTS =====
MARGIN_WARNING_THRESHOLD = 0.80    # Alert at 80% margin usage
BAN_LIST_CHECK_INTERVAL = 300      # Check every 5 minutes
PNL_ALERT_ENABLED = True
```

### Profile-Based Configuration

Create environment-specific configs:

**config/prod.py**
```python
DB_CONNECTION_STRING = 'postgresql://user:pass@localhost/options_prod'
WRITE_TO_SQL = True
ENABLE_BROKER_SYNC = True
```

**config/dev.py**
```python
TEST_RUN = True
DB_CONNECTION_STRING = 'sqlite:///options_dev.db'
WRITE_TO_SQL = False
```

Load configuration:
```python
import os
env = os.getenv('ENVIRONMENT', 'dev')
if env == 'prod':
    from config.prod import *
else:
    from config.dev import *
```

---

## API & Output Formats

### Output Format: Strategy Results

**Excel Export Structure:**

Each strategy generates a separate Excel sheet with columns:

| Column | Type | Description |
|--------|------|-------------|
| Stock | String | NSE symbol |
| Premium Credit/Debit | Float | Total premium |
| Max Profit | Float | Absolute max profit (₹) |
| Max Loss | Float | Absolute max loss (₹) |
| ROI | Float | Return on margin |
| PE_sell_price | Float | Put option sell price |
| PE_sell_strike | Float | Put strike price |
| PE_buy_price | Float | Put buy price (if applicable) |
| PE_buy_strike | Float | Put buy strike |
| CE_sell_price | Float | Call sell price |
| CE_sell_strike | Float | Call strike price |
| CE_buy_price | Float | Call buy price |
| CE_buy_strike | Float | Call buy strike |
| lot_size | Integer | Contract multiplier |
| IV | Float | Implied Volatility |
| Theta (Total) | Float | Daily theta decay (₹) |
| Delta (Total) | Float | Direction sensitivity |
| Gamma | Float | Delta acceleration |
| Vega | Float | Volatility sensitivity |
| pl_on_strikes | List | P&L at different prices |
| Strikes | List | All available strikes |

**Example P&L Range:**
```
pl_on_strikes = [
    (-430.0, 1120, 1420),   # Loss 430 between 1120-1420
    (2320.0, 1420, 1440),   # Profit 2320 between 1420-1440
    (-430.0, 1440, 1800)    # Loss 430 between 1440-1800
]
```

### Database Schema

**strategies table:**
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
    breakeven_points JSON,
    greeks JSON,  -- {delta, gamma, theta, vega, iv}
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**positions table:**
```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER,
    broker VARCHAR(50),
    quantity INTEGER,
    entry_price FLOAT,
    current_price FLOAT,
    pnl FLOAT,
    pnl_percent FLOAT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);
```

### API Response Format (JSON)

**Strategy Calculation Response:**
```json
{
  "strategy_type": "SHORT_STRANGLE",
  "symbol": "RELIANCE",
  "expiry_date": "2025-01-30",
  "premium_credit": 850.0,
  "max_profit": 850.0,
  "max_loss": 2150.0,
  "roi": 39.5,
  "breakeven_points": [2650, 3050],
  "greeks": {
    "delta": -0.15,
    "gamma": 0.002,
    "theta": 45.3,
    "vega": -120.5,
    "iv": 18.5
  },
  "legs": [
    {
      "type": "put",
      "strike": 2650,
      "price": 50.0,
      "quantity": -1
    },
    {
      "type": "call",
      "strike": 3050,
      "price": 40.0,
      "quantity": -1
    }
  ]
}
```

---

## Broker Integration

### ICICI Direct Integration

**Setup:**
```python
from brokers.icici_direct import ICICIDirectConnector

connector = ICICIDirectConnector(
    username='your_username',
    password='your_password'
)
```

**Available Methods:**

1. **Get Positions**
```python
positions = connector.get_positions()
# Returns: [
#   {
#     'stock': 'RELIANCE',
#     'quantity': 10,
#     'entry_price': 2850,
#     'current_price': 2900,
#     'pnl': 500,
#     'multiplier': 100
#   }
# ]
```

2. **Get Margin Information**
```python
margin = connector.get_margin_used()
# Returns: {
#   'total': 500000,
#   'used': 400000,
#   'available': 100000,
#   'pct_used': 80.0
# }
```

3. **Get Orders**
```python
orders = connector.get_orders(status='pending')
# Returns: [
#   {
#     'order_id': '12345',
#     'symbol': 'RELIANCE',
#     'quantity': 1,
#     'price': 2850,
#     'status': 'pending',
#     'timestamp': '2025-01-15 10:30:00'
#   }
# ]
```

4. **Monitor MWPL (Market Wide Position Limits)**
```python
mwpl = connector.check_mwpl()
# Returns warnings for stocks approaching ban limit
```

### Adding New Broker Integration

Extend `brokers/broker_base.py`:

```python
class BrokerBase(ABC):
    @abstractmethod
    def authenticate(self): pass
    
    @abstractmethod
    def get_positions(self): pass
    
    @abstractmethod
    def get_margin_used(self): pass
    
    @abstractmethod
    def get_orders(self): pass

# Implement for your broker
class YourBrokerConnector(BrokerBase):
    def authenticate(self):
        # Your auth logic
        pass
    
    def get_positions(self):
        # Fetch positions
        pass
```

---

## Dashboard & Visualization

### Metabase Setup

**Step 1: Download Metabase**
```bash
cd metabase/
wget https://downloads.metabase.com/v0.46.6/metabase.jar
```

**Step 2: Start Metabase**
```bash
cd metabase/
java -jar metabase.jar
```

**Step 3: Access Dashboard**
Visit `http://localhost:3000` in your browser

**Step 4: Configure Database**
- Click gear icon → Admin → Databases
- Add your database connection
- Sync tables

**Step 5: Import Dashboards**
```bash
# Dashboards are pre-configured in metabase/
# They auto-sync with your database
```

### Available Dashboards

#### 1. **Consolidated P&L Dashboard**
- Total profit/loss across all brokers
- Strategy-wise breakdown
- Time-series P&L chart
- Daily/weekly/monthly views

#### 2. **Stock Strategy Dashboard**
- Individual stock strategy performance
- P&L by strategy type
- Greeks visualization
- Risk metrics

#### 3. **Margin & Risk Dashboard**
- Real-time margin utilization
- Margin by strategy
- Ban list warnings
- Risk alerts

#### 4. **Order Tracking Dashboard**
- Pending orders
- Executed orders
- Order P&L analysis
- Fill price analysis

#### 5. **Greeks Heatmap**
- Delta exposure across strikes
- Gamma concentration areas
- Theta decay visualization
- Vega risk zones

### Custom Queries

Create custom Metabase questions:

**Example: Top 5 Most Profitable Strategies**
```sql
SELECT 
    symbol,
    strategy_type,
    SUM(pnl) as total_pnl,
    COUNT(*) as num_trades,
    AVG(pnl) as avg_pnl
FROM positions
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY symbol, strategy_type
ORDER BY total_pnl DESC
LIMIT 5;
```

---

## Advanced Usage

### Batch Strategy Scanning

Scan entire NSE F&O universe for opportunities:

```python
from scanner.profitability_scanner import ProfitabilityScanner
from scanner.filters import FilterConfig

# Configure filters
filters = FilterConfig(
    max_loss_threshold=1000,
    min_profit_threshold=500,
    profit_probability=0.65,
    liquidity_filter='HIGH',  # HIGH/MEDIUM/LOW
    iv_percentile_range=(30, 70)  # Exclude extremes
)

# Initialize scanner
scanner = ProfitabilityScanner(filters=filters)

# Scan multiple strategies
results = scanner.scan_multiple(
    strategies=['SHORT_STRANGLE', 'NAKED_PUT', 'SHORT_STRADDLE'],
    strike_differences={
        'SHORT_STRANGLE': 150,
        'NAKED_PUT': 100
    }
)

# Export results
scanner.export_to_excel(
    results,
    'strategies_scan.xlsx',
    sort_by='max_profit'
)

scanner.export_to_database(results)
```

### Real-time Position Monitoring

Monitor positions and trigger exits based on P&L:

```python
from monitoring.position_monitor import PositionMonitor
from monitoring.triggers import ProfitTrigger, LossTrigger

monitor = PositionMonitor()

# Add profit trigger
profit_trigger = ProfitTrigger(
    strategy_id=123,
    profit_target=5000,
    action='SELL_AT_MARKET'
)

# Add loss trigger
loss_trigger = LossTrigger(
    strategy_id=123,
    loss_limit=2000,
    action='SELL_AT_MARKET'
)

monitor.add_trigger(profit_trigger)
monitor.add_trigger(loss_trigger)

# Start monitoring
monitor.start()
```

### Greeks-Based Risk Management

Rebalance positions based on Greeks:

```python
from risk_management.greeks_rebalancer import GreeksRebalancer

rebalancer = GreeksRebalancer(portfolio=positions)

# Target Greeks
target_delta = -0.2  # Bearish tilt
target_vega = 0      # Neutral vega

# Get rebalancing suggestions
suggestions = rebalancer.suggest_rebalance(
    target_delta=target_delta,
    target_vega=target_vega
)

for suggestion in suggestions:
    print(f"Adjust {suggestion['symbol']}: {suggestion['action']}")
```

### Backtesting Strategy Performance

Historical analysis of strategy returns:

```python
from backtesting.strategy_backtest import StrategyBacktester

backtest = StrategyBacktester(
    strategy_type='SHORT_STRANGLE',
    symbol='RELIANCE',
    start_date='2024-01-01',
    end_date='2024-12-31'
)

results = backtest.run(
    strike_difference=100,
    profit_target=0.30,  # 30% of premium
    loss_limit=0.70      # 70% of premium
)

print(f"Win Rate: {results['win_rate']:.2%}")
print(f"Avg Profit: ₹{results['avg_profit']}")
print(f"Max Loss: ₹{results['max_loss']}")
print(f"Profit Factor: {results['profit_factor']:.2f}")
```

---

## Troubleshooting

### Common Issues

**Issue 1: "TEST_RUN must be True outside market hours"**

**Solution:**
```python
# helper/constants.py
TEST_RUN = True  # Set to True when market is closed
```

**Issue 2: Option chain data not fetching**

**Solution:**
```python
# Check NSE connectivity
from data.nse_fetcher import NSEDataFetcher

fetcher = NSEDataFetcher()
try:
    chain = fetcher.fetch_option_chain('RELIANCE', '2025-01-30')
    print("✓ NSE connection successful")
except Exception as e:
    print(f"✗ NSE connection failed: {e}")
```

**Issue 3: ICICI Direct authentication failing**

**Solution:**
```python
from brokers.icici_direct import ICICIDirectConnector

try:
    connector = ICICIDirectConnector(
        username='your_username',
        password='your_password'
    )
    connector.authenticate()
    print("✓ Authentication successful")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
    # Check username/password
    # Ensure 2FA is disabled for API access
```

**Issue 4: Metabase dashboard not loading**

**Solution:**
```bash
# Check if Java is installed
java -version

# Check if Metabase is running
curl http://localhost:3000

# Check database connection
# Go to http://localhost:3000 > Admin > Databases
# Verify connection settings
```

**Issue 5: Greeks calculation returning NaN**

**Solution:**
```python
# Ensure time to expiration is > 0
# IV should be > 0
# Stock price and strike should be positive

from strategy.greeks import GreeksCalculator

calc = GreeksCalculator()
greeks = calc.calculate(
    stock_price=2850,
    strike=2850,
    time_to_expiry=10/365,  # 10 days
    volatility=0.20,        # 20% IV
    risk_free_rate=0.065,
    option_type='put'
)
```

### Debug Logging

Enable detailed logging:

```python
import logging

# Set logging level
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug("Detailed debug messages")
logger.info("Info messages")
logger.warning("Warning messages")
logger.error("Error messages")
```

### Performance Optimization

For large-scale scanning:

```python
# Use multiprocessing
from concurrent.futures import ProcessPoolExecutor

def scan_stock(symbol):
    # Scan logic
    pass

symbols = get_all_nse_fno_stocks()

with ProcessPoolExecutor(max_workers=8) as executor:
    results = executor.map(scan_stock, symbols)
```

---

## Contributing

### Code Style

Follow PEP 8:
```bash
pip install flake8
flake8 options/ --max-line-length=100
```

### Testing

Run unit tests:
```bash
pip install pytest
pytest tests/ -v
```

### Submitting Pull Requests

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Reporting Issues

Include:
- Python version
- Environment (Windows/Mac/Linux)
- Error message and traceback
- Steps to reproduce
- Expected behavior vs actual behavior

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Disclaimer

This tool is provided for educational and research purposes. Trading options involves substantial risk. Always:
- Understand the strategies before trading
- Use proper risk management
- Start with paper trading
- Consult financial advisors
- Paper trade before live trading

## Support & Community

- **GitHub Issues:** For bug reports and feature requests
- **Discussions:** For Q&A and general discussions
- **Wiki:** For additional guides and tutorials

---

## Changelog

### Version 1.0.0 (Sep 2024)
- Initial release with 13 predefined strategies
- NSE integration for option chain data
- ICICI Direct broker integration
- Metabase dashboard support
- Greeks calculation
- Profitability scanning

### Future Features (Roadmap)
- [ ] Additional broker integrations (Zerodha, 5Paisa)
- [ ] Machine learning for strategy recommendations
- [ ] Options spreads optimizer
- [ ] Real-time alerts via SMS/Email
- [ ] Mobile app for position monitoring
- [ ] Advanced risk analytics
- [ ] Portfolio optimization module

---

## FAQ

**Q: Can I use this for live trading?**  
A: Yes, but start with paper trading first and thoroughly backtest your strategies.

**Q: Does it support international markets?**  
A: Currently supports NSE (India). Future versions will support other exchanges.

**Q: How often is pricing data updated?**  
A: During market hours, it updates in real-time. Outside market hours, historical data is used.

**Q: Can I add custom strategies?**  
A: Yes, extend `strategy/definitions.py` with your custom strategy logic.

**Q: Is this free?**  
A: Yes, this is open-source and free to use.

---

**For detailed implementation examples and video tutorials, visit the GitHub repository.**
