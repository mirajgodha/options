# API & Code Examples Documentation

## Complete API Reference

### Strategy Calculator Module

#### Class: `StrategyCalculator`

Main class for calculating P&L and Greeks for options strategies.

**Constructor:**
```python
from strategy.calculator import StrategyCalculator

calc = StrategyCalculator(
    stock_symbol: str,           # NSE stock symbol (e.g., 'RELIANCE')
    option_chain: OptionChain,   # Option chain data object
    strategy_type: str           # Strategy type (see list below)
)
```

**Strategy Types:**
- `'LONG_CALL_CONDOR'`
- `'LONG_IRON_BUTTERFLY'`
- `'LONG_PUT_CONDOR'`
- `'SHORT_CALL_BUTTERFLY'`
- `'SHORT_CALL_CONDOR'`
- `'SHORT_GUTS'`
- `'SHORT_IRON_BUTTERFLY'`
- `'SHORT_PUT_BUTTERFLY'`
- `'SHORT_PUT_CONDOR'`
- `'SHORT_STRADDLE'`
- `'SHORT_STRANGLE'`
- `'NAKED_CALL'`
- `'NAKED_PUT'`

**Methods:**

##### `calculate(**kwargs) -> Strategy`

Calculates the strategy metrics.

**Parameters (vary by strategy type):**

```python
# For SHORT_STRANGLE
strategy = calc.calculate(
    short_put_strike: float,       # Strike to sell put at
    short_call_strike: float,      # Strike to sell call at
    quantity: int = 1              # Lot multiplier
)

# For SHORT_STRADDLE
strategy = calc.calculate(
    strike: float,                 # ATM strike
    quantity: int = 1
)

# For LONG_CALL_CONDOR
strategy = calc.calculate(
    buy_low_call_strike: float,
    sell_mid_low_call_strike: float,
    sell_mid_high_call_strike: float,
    buy_high_call_strike: float,
    quantity: int = 1
)

# For NAKED_CALL / NAKED_PUT
strategy = calc.calculate(
    strike: float,                 # Strike to sell
    quantity: int = 1
)
```

**Returns:**

```python
class Strategy:
    symbol: str                           # Stock symbol
    strategy_type: str                    # Strategy name
    premium_credit: float                 # Premium received (credit strategies)
    premium_debit: float                  # Premium paid (debit strategies)
    max_profit: float                     # Maximum possible profit (₹)
    max_loss: float                       # Maximum possible loss (₹)
    roi: float                            # Return on margin (%)
    breakeven_points: List[float]         # Break-even stock prices
    
    legs: List[StrategyLeg]              # Option legs
    greeks: Dict[str, float]             # Greeks dictionary
    pl_on_strikes: List[Tuple]           # P&L at different prices
    strikes: List[float]                 # All available strikes
    
    def get_pnl_at_price(price: float) -> float
    def get_greek(greek_name: str) -> float
```

**Greek Values:**
```python
strategy.greeks = {
    'delta': -0.25,              # Directional sensitivity
    'gamma': 0.002,              # Delta acceleration
    'theta': 45.50,              # Daily time decay (₹)
    'vega': -120.75,             # Volatility sensitivity
    'iv': 18.5,                  # Implied volatility (%)
    'total_theta': 45.50,        # Total theta for lot size
    'total_delta': -0.25         # Total delta for lot size
}
```

**Example Usage:**
```python
from data.nse_fetcher import NSEDataFetcher
from strategy.calculator import StrategyCalculator

# Fetch data
fetcher = NSEDataFetcher()
chain = fetcher.fetch_option_chain('RELIANCE', '2025-01-30')

# Calculate strategy
calc = StrategyCalculator('RELIANCE', chain, 'SHORT_STRANGLE')
strategy = calc.calculate(
    short_put_strike=2700,
    short_call_strike=3100,
    quantity=1
)

# Access results
print(f"Max Profit: ₹{strategy.max_profit}")
print(f"Max Loss: ₹{strategy.max_loss}")
print(f"Break-evens: {strategy.breakeven_points}")
print(f"Daily Theta: ₹{strategy.greeks['theta']:.2f}")

# Get P&L at specific price
pnl_at_2800 = strategy.get_pnl_at_price(2800)
print(f"P&L at ₹2800: ₹{pnl_at_2800}")
```

---

### Data Fetching Module

#### Class: `NSEDataFetcher`

Fetches real-time and historical option chain data from NSE.

```python
from data.nse_fetcher import NSEDataFetcher

fetcher = NSEDataFetcher()
```

**Methods:**

##### `fetch_option_chain(symbol: str, expiry_date: str) -> OptionChain`

Fetches complete option chain for a stock on a specific expiry.

**Parameters:**
- `symbol` (str): NSE symbol (e.g., 'RELIANCE', 'BANKNIFTY')
- `expiry_date` (str): Date in format 'YYYY-MM-DD'

**Returns:**
```python
class OptionChain:
    symbol: str
    spot_price: float
    expiry_date: str
    expirations: List[str]              # All available expirations
    
    calls: Dict[float, Option]          # Strike -> Call option
    puts: Dict[float, Option]           # Strike -> Put option
    
    def get_call(strike: float) -> Option
    def get_put(strike: float) -> Option
    def get_all_strikes() -> List[float]

class Option:
    strike: float
    bid_price: float
    ask_price: float
    last_price: float
    open_interest: int
    volume: int
    implied_volatility: float           # As percentage (e.g., 18.5 for 18.5%)
    greeks: Dict[str, float]
    
    @property
    def mid_price() -> float            # (bid + ask) / 2
```

**Example:**
```python
# Fetch option chain
chain = fetcher.fetch_option_chain('RELIANCE', '2025-01-30')

# Access spot price
print(f"Spot: ₹{chain.spot_price}")

# Get all strikes
strikes = chain.get_all_strikes()
print(f"Strikes available: {strikes}")

# Get specific option
call = chain.get_call(2850)
put = chain.get_put(2800)

print(f"2850 Call IV: {call.implied_volatility}%")
print(f"2800 Put Price: ₹{put.mid_price}")
```

##### `fetch_implied_volatility(symbol: str, span: str = '30d') -> Dict`

Fetches historical IV data.

**Parameters:**
- `symbol` (str): Stock symbol
- `span` (str): '7d', '30d', '90d', '1y'

**Returns:**
```python
{
    'current_iv': 18.5,
    'iv_low': 16.2,
    'iv_high': 22.1,
    'iv_average': 19.3,
    'iv_percentile': 65
}
```

**Example:**
```python
iv_data = fetcher.fetch_implied_volatility('RELIANCE', '30d')
print(f"Current IV: {iv_data['current_iv']}%")
print(f"IV Percentile (30d): {iv_data['iv_percentile']}th")
```

---

### Broker Integration Module

#### Class: `ICICIDirectConnector`

Connects to ICICI Direct trading platform.

```python
from brokers.icici_direct import ICICIDirectConnector

connector = ICICIDirectConnector(
    username='your_username',
    password='your_password'
)
```

**Methods:**

##### `get_positions() -> List[Position]`

Returns current open positions.

**Returns:**
```python
class Position:
    symbol: str
    quantity: int                       # Positive for long, negative for short
    entry_price: float
    current_price: float
    pnl: float                         # Absolute P&L
    pnl_percent: float                 # P&L percentage
    multiplier: int                    # Contract size
    instrument_type: str               # 'call' or 'put'
    strike: float
    expiry_date: str
    
    @property
    def is_profitable() -> bool
```

**Example:**
```python
positions = connector.get_positions()

for pos in positions:
    print(f"{pos.symbol} {pos.strike} {pos.instrument_type}")
    print(f"  Qty: {pos.quantity}")
    print(f"  P&L: ₹{pos.pnl} ({pos.pnl_percent:.2%})")
    
    # Filter profitable positions
    if pos.is_profitable:
        print(f"  ✓ Profitable")
```

##### `get_margin_used() -> MarginInfo`

Returns margin usage details.

**Returns:**
```python
class MarginInfo:
    total_margin: float                # Total available margin
    used_margin: float                 # Margin currently used
    available_margin: float            # Remaining margin
    pct_used: float                    # Used as percentage
    
    @property
    def is_low_margin() -> bool        # True if > 80% used
```

**Example:**
```python
margin = connector.get_margin_used()

print(f"Total Margin: ₹{margin.total_margin:,.0f}")
print(f"Used: ₹{margin.used_margin:,.0f} ({margin.pct_used:.1f}%)")
print(f"Available: ₹{margin.available_margin:,.0f}")

if margin.is_low_margin:
    print("⚠️ WARNING: Margin usage is high!")
```

##### `get_orders(status: str = 'all') -> List[Order]`

Returns order history.

**Parameters:**
- `status` (str): 'pending', 'executed', 'cancelled', 'rejected', 'all'

**Returns:**
```python
class Order:
    order_id: str
    symbol: str
    instrument_type: str               # 'call' or 'put'
    strike: float
    expiry_date: str
    side: str                          # 'BUY' or 'SELL'
    quantity: int
    order_price: float                 # Price ordered at
    fill_price: float                  # Actual fill price
    status: str                        # Current status
    filled_quantity: int
    pending_quantity: int
    timestamp: datetime
    
    @property
    def is_filled() -> bool
    @property
    def fill_slippage() -> float       # Actual vs ordered price
```

**Example:**
```python
# Get pending orders
pending = connector.get_orders('pending')

for order in pending:
    print(f"Order {order.order_id}: {order.symbol} {order.strike} {order.side}")
    print(f"  Pending: {order.pending_quantity} @ ₹{order.order_price}")
    print(f"  Current LTP: ₹{order.current_ltp}")

# Get executed orders from today
executed = connector.get_orders('executed')
print(f"Total executed today: {len(executed)}")
print(f"Avg fill slippage: {executed.avg_slippage:.2f} paise")
```

##### `check_mwpl() -> List[BanListWarning]`

Checks Market Wide Position Limits (ban list status).

**Returns:**
```python
class BanListWarning:
    symbol: str
    position: int                      # Current position
    limit: int                         # MWPL limit
    pct_limit: float                   # % of limit
    status: str                        # 'SAFE', 'CAUTION', 'ALERT'
    can_enter_new_positions: bool
```

**Example:**
```python
warnings = connector.check_mwpl()

for warn in warnings:
    if warn.status != 'SAFE':
        print(f"⚠️ {warn.symbol}: {warn.pct_limit:.1f}% of MWPL")
        if not warn.can_enter_new_positions:
            print(f"   Cannot open new positions!")
```

---

### Profitability Scanner Module

#### Class: `ProfitabilityScanner`

Scans entire NSE universe for profitable strategy opportunities.

```python
from scanner.profitability_scanner import ProfitabilityScanner
from scanner.filters import FilterConfig

# Configure filters
filters = FilterConfig(
    max_loss_threshold=1000,           # Max loss tolerance (₹)
    min_profit_threshold=500,          # Min profit required (₹)
    profit_probability=0.65,           # Min probability of profit
    liquidity_filter='HIGH',           # HIGH / MEDIUM / LOW
    iv_percentile_range=(30, 70)      # Exclude IV extremes
)

scanner = ProfitabilityScanner(filters=filters)
```

**Methods:**

##### `scan_all_strategies(strategies: List[str], strike_differences: Dict = None) -> ScanResults`

Scans all NSE F&O stocks for specified strategies.

**Parameters:**
- `strategies` (List[str]): List of strategy types to scan
- `strike_differences` (Dict): Optional strike spacing per strategy

**Returns:**
```python
class ScanResults:
    total_stocks_scanned: int
    total_opportunities: int
    results: List[ScanResult]          # Sorted by profitability
    
    def filter_by_max_loss(max_loss: float) -> ScanResults
    def filter_by_probability(min_prob: float) -> ScanResults
    def get_top_n(n: int) -> List[ScanResult]

class ScanResult:
    symbol: str
    strategy_type: str
    short_strike_1: float
    short_strike_2: float             # Optional
    buy_strike: float                 # Optional
    premium_credit: float
    max_profit: float
    max_loss: float
    probability_of_profit: float      # Percentage
    expected_value: float             # EV of the trade
    roi: float                        # Return on margin
    liquidity_score: float            # 0-100
```

**Example:**
```python
# Scan for SHORT_STRANGLE opportunities
results = scanner.scan_all_strategies(
    strategies=['SHORT_STRANGLE'],
    strike_differences={'SHORT_STRANGLE': 100}
)

print(f"Opportunities found: {results.total_opportunities}")

# Get top 10 by expected value
top_10 = results.get_top_n(10)

for i, result in enumerate(top_10, 1):
    print(f"{i}. {result.symbol}")
    print(f"   Premium: ₹{result.premium_credit}")
    print(f"   Max Loss: ₹{result.max_loss}")
    print(f"   PoP: {result.probability_of_profit:.1%}")
    print(f"   EV: ₹{result.expected_value:.0f}")
```

##### `export_to_excel(results: ScanResults, filename: str, sort_by: str = 'max_profit')`

Exports scan results to formatted Excel file.

**Parameters:**
- `results` (ScanResults): Scan results
- `filename` (str): Output filename
- `sort_by` (str): 'max_profit', 'probability', 'roi', 'liquidity'

**Example:**
```python
scanner.export_to_excel(
    results,
    'nse_opportunities_2025_01_15.xlsx',
    sort_by='expected_value'
)
```

##### `export_to_database(results: ScanResults)`

Stores scan results in database for historical analysis.

**Example:**
```python
scanner.export_to_database(results)

# Later, retrieve historical scans
historical = scanner.get_historical_scans(
    start_date='2025-01-01',
    end_date='2025-01-15'
)
```

---

### Greeks Calculator Module

#### Class: `GreeksCalculator`

Calculates individual option Greeks using Black-Scholes model.

```python
from strategy.greeks import GreeksCalculator

calc = GreeksCalculator()
```

**Methods:**

##### `calculate(stock_price: float, strike: float, time_to_expiry: float, volatility: float, option_type: str) -> Dict[str, float]`

Calculates all Greeks for a single option.

**Parameters:**
- `stock_price` (float): Current stock price
- `strike` (float): Strike price
- `time_to_expiry` (float): Time in years (e.g., 10/365 for 10 days)
- `volatility` (float): Implied volatility (e.g., 0.20 for 20%)
- `option_type` (str): 'call' or 'put'

**Returns:**
```python
{
    'delta': -0.35,              # Change per ₹1 move
    'gamma': 0.0025,             # Delta acceleration per ₹1
    'theta': -2.50,              # Daily decay (₹/day)
    'vega': 85.50,               # Change per 1% IV
    'rho': 12.30,                # Change per 1% rate
    'iv': 18.5                   # Implied volatility
}
```

**Example:**
```python
greeks = calc.calculate(
    stock_price=2850,
    strike=2850,
    time_to_expiry=10/365,    # 10 days
    volatility=0.185,         # 18.5%
    option_type='put'
)

print(f"Delta: {greeks['delta']:.4f}")     # -0.5 for ATM put
print(f"Theta: ₹{greeks['theta']:.2f}")    # Daily decay
print(f"Vega: ₹{greeks['vega']:.2f}")      # Per 1% IV move
```

---

## Complete Code Examples

### Example 1: Analyze Single Strategy

```python
from data.nse_fetcher import NSEDataFetcher
from strategy.calculator import StrategyCalculator
import json

# Step 1: Fetch data
fetcher = NSEDataFetcher()
chain = fetcher.fetch_option_chain('BANKNIFTY', '2025-01-30')

print(f"Spot Price: ₹{chain.spot_price}")

# Step 2: Calculate SHORT_STRANGLE
calc = StrategyCalculator('BANKNIFTY', chain, 'SHORT_STRANGLE')
strategy = calc.calculate(
    short_put_strike=44000,
    short_call_strike=45500,
    quantity=1
)

# Step 3: Display Results
print("\n=== STRATEGY ANALYSIS ===")
print(f"Premium Credit: ₹{strategy.premium_credit:.0f}")
print(f"Max Profit: ₹{strategy.max_profit:.0f}")
print(f"Max Loss: ₹{strategy.max_loss:.0f}")
print(f"ROI: {strategy.roi:.1f}%")
print(f"Breakevens: {strategy.breakeven_points}")

print("\n=== GREEKS ===")
print(f"Delta: {strategy.greeks['delta']:.4f}")
print(f"Gamma: {strategy.greeks['gamma']:.6f}")
print(f"Theta: ₹{strategy.greeks['theta']:.2f} / day")
print(f"Vega: ₹{strategy.greeks['vega']:.2f} / 1% IV")
print(f"IV: {strategy.greeks['iv']:.2f}%")

print("\n=== P&L AT DIFFERENT PRICES ===")
test_prices = [44000, 44500, 45000, 45500, 46000]
for price in test_prices:
    pnl = strategy.get_pnl_at_price(price)
    print(f"At ₹{price:,}: {pnl:+.0f}")

# Step 4: Export to Excel
from output.excel_writer import ExcelWriter
writer = ExcelWriter()
writer.write_strategy(strategy, 'single_strategy.xlsx')
```

### Example 2: Scan & Filter Strategies

```python
from scanner.profitability_scanner import ProfitabilityScanner
from scanner.filters import FilterConfig

# Configure filters
filters = FilterConfig(
    max_loss_threshold=5000,
    min_profit_threshold=2000,
    profit_probability=0.70,
    iv_percentile_range=(40, 80)
)

# Initialize scanner
scanner = ProfitabilityScanner(filters=filters)

print("Scanning NSE universe for SHORT_STRANGLE opportunities...")
results = scanner.scan_all_strategies(
    strategies=['SHORT_STRANGLE'],
    strike_differences={'SHORT_STRANGLE': 200}
)

print(f"\nTotal scanned: {results.total_stocks_scanned}")
print(f"Opportunities found: {results.total_opportunities}")

# Get top opportunities
print("\n=== TOP 5 OPPORTUNITIES ===")
top_5 = results.get_top_n(5)

for i, result in enumerate(top_5, 1):
    print(f"\n{i}. {result.symbol}")
    print(f"   Premium: ₹{result.premium_credit:.0f}")
    print(f"   Max Loss: ₹{result.max_loss:.0f}")
    print(f"   PoP: {result.probability_of_profit:.1%}")
    print(f"   ROI: {result.roi:.1f}%")
    print(f"   Liquidity: {result.liquidity_score:.0f}/100")

# Export to Excel
scanner.export_to_excel(results, 'opportunities.xlsx', sort_by='roi')
print("\n✓ Results exported to opportunities.xlsx")

# Save to database for tracking
scanner.export_to_database(results)
print("✓ Results saved to database")
```

### Example 3: Monitor Live Positions

```python
from brokers.icici_direct import ICICIDirectConnector
from datetime import datetime
import time

connector = ICICIDirectConnector(
    username='your_id',
    password='your_password'
)

print("=== LIVE POSITION MONITOR ===\n")

while True:
    # Get current positions
    positions = connector.get_positions()
    margin = connector.get_margin_used()
    
    # Display summary
    total_pnl = sum(pos.pnl for pos in positions)
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}]")
    print(f"Total P&L: ₹{total_pnl:+.0f}")
    print(f"Margin Used: {margin.pct_used:.1f}% (₹{margin.used_margin:,.0f})")
    
    # Display positions
    print("\nPositions:")
    for pos in positions:
        symbol = pos.symbol
        qty = f"{pos.quantity:+d}" if pos.quantity > 0 else f"{pos.quantity:d}"
        pnl_color = "+" if pos.pnl > 0 else "-"
        
        print(f"  {symbol:12} {qty:+4}  "
              f"P&L: ₹{pnl_color}{abs(pos.pnl):.0f}  "
              f"({pos.pnl_percent:+.2%})")
    
    # Alert if margin is low
    if margin.pct_used > 90:
        print("\n⚠️ WARNING: Margin usage > 90%")
    
    # Check MWPL
    mwpl_warnings = connector.check_mwpl()
    if mwpl_warnings:
        print("\n⚠️ MWPL Alerts:")
        for warn in mwpl_warnings:
            if warn.status != 'SAFE':
                print(f"   {warn.symbol}: {warn.pct_limit:.1f}% of limit")
    
    # Sleep before next update
    time.sleep(60)  # Update every minute
```

### Example 4: Multi-Broker Consolidation

```python
from brokers.icici_direct import ICICIDirectConnector

# Connect to broker
connector = ICICIDirectConnector(
    username='your_id',
    password='your_password'
)

# Get all data
positions = connector.get_positions()
margin = connector.get_margin_used()
pending_orders = connector.get_orders('pending')
executed_orders = connector.get_orders('executed')

# Consolidate P&L by strategy
strategy_pnl = {}
for pos in positions:
    symbol = pos.symbol
    strike = pos.strike
    expiry = pos.expiry_date
    
    key = f"{symbol} {strike} {pos.instrument_type} ({expiry})"
    
    if key not in strategy_pnl:
        strategy_pnl[key] = {'pnl': 0, 'qty': 0, 'positions': []}
    
    strategy_pnl[key]['pnl'] += pos.pnl
    strategy_pnl[key]['qty'] += pos.quantity
    strategy_pnl[key]['positions'].append(pos)

# Display consolidated report
print("=== CONSOLIDATED PORTFOLIO ===\n")
print(f"Total P&L: ₹{sum(p['pnl'] for p in strategy_pnl.values()):+.0f}")
print(f"Margin Used: {margin.pct_used:.1f}%")
print(f"Open Positions: {len(positions)}")
print(f"Pending Orders: {len(pending_orders)}")

print("\n=== BY STRATEGY ===")
for strategy, data in sorted(
    strategy_pnl.items(),
    key=lambda x: x[1]['pnl'],
    reverse=True
):
    print(f"{strategy}: ₹{data['pnl']:+.0f}")
```

### Example 5: Greeks-Based Risk Analysis

```python
from strategy.calculator import StrategyCalculator
from data.nse_fetcher import NSEDataFetcher

# Fetch option chain
fetcher = NSEDataFetcher()
chain = fetcher.fetch_option_chain('TCS', '2025-01-30')

# Analyze multiple strategies
strategies = [
    ('SHORT_STRANGLE', {'short_put_strike': 3800, 'short_call_strike': 4200}),
    ('SHORT_STRADDLE', {'strike': 4000}),
    ('LONG_CALL_CONDOR', {
        'buy_low_call_strike': 3900,
        'sell_mid_low_call_strike': 3950,
        'sell_mid_high_call_strike': 4050,
        'buy_high_call_strike': 4100
    })
]

print("=== GREEKS COMPARISON ===\n")
print(f"{'Strategy':<20} {'Delta':<10} {'Theta':<10} {'Vega':<10} {'Gamma':<10}")
print("-" * 50)

for strategy_type, params in strategies:
    calc = StrategyCalculator('TCS', chain, strategy_type)
    strategy = calc.calculate(**params)
    
    print(f"{strategy_type:<20} "
          f"{strategy.greeks['delta']:>+8.3f} "
          f"{strategy.greeks['theta']:>+8.2f} "
          f"{strategy.greeks['vega']:>+8.2f} "
          f"{strategy.greeks['gamma']:>+8.4f}")

# Risk analysis
print("\n=== RISK EXPOSURE ===")
print("\nDelta Exposure (Directional Risk):")
for strategy_type, params in strategies:
    calc = StrategyCalculator('TCS', chain, strategy_type)
    strategy = calc.calculate(**params)
    delta = strategy.greeks['delta']
    
    if abs(delta) < 0.2:
        risk = "Very Low - Nearly delta-neutral"
    elif abs(delta) < 0.5:
        risk = "Low - Minor directional exposure"
    else:
        risk = "High - Strong directional bias"
    
    print(f"{strategy_type}: {risk}")
```

---

## Advanced Scenarios

### Building a Position Management Dashboard

```python
from brokers.icici_direct import ICICIDirectConnector
from monitoring.position_monitor import PositionMonitor
import pandas as pd

# Connect and get data
connector = ICICIDirectConnector(username='id', password='pwd')
positions = connector.get_positions()
margin = connector.get_margin_used()

# Convert to DataFrame for analysis
df = pd.DataFrame([
    {
        'Symbol': p.symbol,
        'Strike': p.strike,
        'Type': p.instrument_type,
        'Qty': p.quantity,
        'Entry': p.entry_price,
        'Current': p.current_price,
        'P&L': p.pnl,
        'P&L%': p.pnl_percent,
        'Expiry': p.expiry_date
    }
    for p in positions
])

# Analysis
print("Position Summary:")
print(f"Total P&L: ₹{df['P&L'].sum():+.0f}")
print(f"Win Rate: {(df['P&L'] > 0).sum() / len(df):.1%}")

# Winners
winners = df[df['P&L'] > 0].sort_values('P&L', ascending=False)
print(f"\nTop Winners:")
for _, row in winners.head(3).iterrows():
    print(f"  {row['Symbol']} {row['Strike']} {row['Type']}: ₹{row['P&L']:+.0f}")

# Losers
losers = df[df['P&L'] < 0].sort_values('P&L')
print(f"\nBiggest Losers:")
for _, row in losers.head(3).iterrows():
    print(f"  {row['Symbol']} {row['Strike']} {row['Type']}: ₹{row['P&L']:+.0f}")
```

This comprehensive API documentation provides everything needed to use the Options Strategy Builder effectively.
