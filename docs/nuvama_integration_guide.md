# Nuvama Wealth Integration Guide

## Overview

Nuvama Wealth is a SEBI-registered broker offering competitive pricing and comprehensive API support. This integration enables you to:

- Monitor live positions across Nuvama accounts
- Track margin utilization in real-time
- Manage orders (open, executed, pending)
- Monitor Market Wide Position Limits (MWPL)
- Consolidate P&L across multiple brokers
- Automate strategy execution

## Nuvama Broker Details

### Account Requirements

- **Account Type:** Nuvama Demat + Trading Account
- **F&O Activation:** Must be enabled on your account
- **API Access:** Available with no additional fees
- **Support:** 1800-102-3335 | helpdesk@nuvama.com

### Nuvama Pricing

| Segment | Charges |
|---------|---------|
| Equity Delivery | 0.30% per order |
| Equity Intraday | 0.03% per order |
| Equity Futures | ₹20 per order |
| **Options** | **₹20 per lot** |
| Currency Futures | ₹20 per lot |
| Currency Options | ₹20 per lot |

### Key Benefits

✅ No API charges  
✅ Can trade deep ITM and far OTM options in NRML  
✅ Discounted NSE exchange charges (~₹3500/Cr)  
✅ Online security pledge for margin enhancement  
✅ Web terminal: https://www.nuvamawealth.com/login  
✅ API Connect: https://www.nuvamawealth.com/api-connect/

---

## Setup & Configuration

### Step 1: Get Your Nuvama Client ID

1. Log in to your Nuvama account at https://www.nuvamawealth.com/login
2. Go to **Profile** section
3. Find your **Client ID** (format: typically 6-8 digits)
4. Keep this ID handy for configuration

### Step 2: Configure Nuvama in Your Application

Edit `helper/constants.py`:

```python
# ===== BROKER INTEGRATION =====
ENABLE_BROKER_SYNC = True
BROKER_SYNC_INTERVAL = 60              # seconds

# NUVAMA WEALTH
NUVAMA_ENABLED = True
NUVAMA_CLIENT_ID = 'your_client_id'     # Your 6-8 digit client ID
NUVAMA_PASSWORD = 'your_password'       # Nuvama login password (if using auto-login)
NUVAMA_TOTP_ENABLED = True             # Set False if 2FA disabled
```

### Step 3: Store Credentials Securely

Create `config/nuvama_credentials.json`:

```json
{
  "nuvama": {
    "client_id": "your_client_id",
    "password": "your_password",
    "totp_secret": "your_totp_secret_key"
  }
}
```

**⚠️ Security:** Never commit this file to git!

```bash
# Add to .gitignore
echo "config/nuvama_credentials.json" >> .gitignore
```

---

## Usage Examples

### Basic Connection

```python
from brokers.nuvama import NuvamaBrokerConnector

# Initialize connector
connector = NuvamaBrokerConnector(
    client_id='YOUR_CLIENT_ID',
    password='YOUR_PASSWORD'
)

# Authenticate with Nuvama
try:
    connector.authenticate()
    print("✓ Connected to Nuvama successfully")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
```

### Get Current Positions

```python
# Fetch all current positions
positions = connector.get_positions()

# Print summary
print(f"Total Positions: {len(positions)}")
print(f"Total P&L: ₹{sum(p['pnl'] for p in positions)}")

# Detail for each position
for pos in positions:
    print(f"\nSymbol: {pos['symbol']}")
    print(f"  Quantity: {pos['quantity']}")
    print(f"  Avg Price: ₹{pos['avg_price']}")
    print(f"  LTP: ₹{pos['ltp']}")
    print(f"  P&L: ₹{pos['pnl']} ({pos['pnl_percent']:.2f}%)")
    print(f"  Margin: ₹{pos['margin']}")
```

### Monitor Margin

```python
# Get current margin status
margin = connector.get_margin_used()

print(f"Margin Used: ₹{margin['used']:.2f}")
print(f"Margin Available: ₹{margin['available']:.2f}")
print(f"Total Margin: ₹{margin['total']:.2f}")
print(f"Utilization: {margin['utilization_percent']:.2f}%")

# Set up margin alert
if margin['utilization_percent'] > 80:
    print("⚠️  WARNING: Margin utilization exceeds 80%")
    print("Consider exiting some positions")
```

### Track Orders

```python
# Get all open orders
open_orders = connector.get_orders(status='OPEN')

print(f"Open Orders: {len(open_orders)}")
for order in open_orders:
    print(f"\nOrder ID: {order['order_id']}")
    print(f"  Symbol: {order['symbol']}")
    print(f"  Type: {order['order_type']}")
    print(f"  Quantity: {order['quantity']}")
    print(f"  Price: ₹{order['price']}")
    print(f"  Status: {order['status']}")

# Get executed orders (last 10)
executed_orders = connector.get_orders(status='EXECUTED', limit=10)

print(f"\n\nLast {len(executed_orders)} Executed Orders:")
for order in executed_orders:
    print(f"{order['symbol']} - {order['quantity']} @ ₹{order['execution_price']}")
```

### Check MWPL Status

```python
# Check Market Wide Position Limit
mwpl_data = connector.check_mwpl()

print("MWPL Status:")
for symbol in mwpl_data['symbols']:
    data = mwpl_data['symbols'][symbol]
    print(f"\n{symbol}:")
    print(f"  OI Limit: {data['oi_limit']}")
    print(f"  Current OI: {data['current_oi']}")
    print(f"  Utilization: {data['utilization_percent']:.2f}%")
    print(f"  Status: {data['status']}")
    
    if data['status'] == 'CAUTION':
        print(f"  ⚠️  MWPL at caution level - approaching limit")
    elif data['status'] == 'HALT':
        print(f"  🛑 MWPL HALTED - no new entry allowed")
```

### Real-time Position Monitor

```python
import time
from datetime import datetime

# Monitor positions every 30 seconds
def monitor_positions(connector, duration_minutes=60):
    """Monitor positions in real-time"""
    
    start_time = time.time()
    duration_seconds = duration_minutes * 60
    
    while (time.time() - start_time) < duration_seconds:
        positions = connector.get_positions()
        margin = connector.get_margin_used()
        mwpl = connector.check_mwpl()
        
        # Display current status
        print(f"\n{'='*60}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # P&L Summary
        total_pnl = sum(p['pnl'] for p in positions)
        print(f"\n📊 P&L Summary:")
        print(f"  Total P&L: ₹{total_pnl:.2f}")
        print(f"  Positions: {len(positions)}")
        
        # Margin Status
        print(f"\n💰 Margin Status:")
        print(f"  Used: ₹{margin['used']:.2f} ({margin['utilization_percent']:.1f}%)")
        print(f"  Available: ₹{margin['available']:.2f}")
        
        # Top positions
        print(f"\n📈 Top Performers:")
        sorted_positions = sorted(positions, key=lambda x: x['pnl'], reverse=True)
        for pos in sorted_positions[:3]:
            print(f"  {pos['symbol']}: ₹{pos['pnl']:.2f}")
        
        # MWPL warnings
        print(f"\n⚠️  MWPL Alerts:")
        has_warning = False
        for symbol, data in mwpl['symbols'].items():
            if data['utilization_percent'] > 75:
                print(f"  {symbol}: {data['utilization_percent']:.1f}% utilized")
                has_warning = True
        if not has_warning:
            print(f"  All symbols within safe limits")
        
        # Wait before next update
        time.sleep(30)

# Run monitoring
# monitor_positions(connector, duration_minutes=60)
```

### Consolidated Multi-Broker Dashboard

```python
from brokers.icici_direct import ICICIDirectConnector
from brokers.nuvama import NuvamaBrokerConnector

# Connect to both brokers
icici = ICICIDirectConnector(username='icici_id', password='icici_pwd')
nuvama = NuvamaBrokerConnector(client_id='nuvama_id', password='nuvama_pwd')

icici.authenticate()
nuvama.authenticate()

# Get positions from both
icici_positions = icici.get_positions()
nuvama_positions = nuvama.get_positions()

# Consolidated view
all_positions = []
for pos in icici_positions:
    pos['broker'] = 'ICICI'
    all_positions.append(pos)
for pos in nuvama_positions:
    pos['broker'] = 'Nuvama'
    all_positions.append(pos)

# Consolidated P&L
total_pnl = sum(p['pnl'] for p in all_positions)
print(f"Consolidated P&L across all brokers: ₹{total_pnl}")

# By broker breakdown
for broker_name in ['ICICI', 'Nuvama']:
    broker_pnl = sum(p['pnl'] for p in all_positions if p['broker'] == broker_name)
    broker_positions = len([p for p in all_positions if p['broker'] == broker_name])
    print(f"{broker_name}: ₹{broker_pnl} ({broker_positions} positions)")
```

---

## Integration with Strategy Calculator

### Monitor Strategy P&L Across Brokers

```python
from strategy.calculator import StrategyCalculator
from brokers.nuvama import NuvamaBrokerConnector
from data.nse_fetcher import NSEDataFetcher

# Setup
nuvama = NuvamaBrokerConnector(client_id='YOUR_ID')
nuvama.authenticate()

fetcher = NSEDataFetcher()

# Function to get strategy P&L from Nuvama positions
def get_strategy_pnl(nuvama_connector, symbol, strategy_type):
    """
    Calculate P&L for a specific strategy across Nuvama positions
    """
    positions = nuvama_connector.get_positions()
    
    # Filter positions for the symbol
    symbol_positions = [p for p in positions if symbol in p['symbol']]
    
    if not symbol_positions:
        print(f"No positions found for {symbol}")
        return None
    
    # Calculate strategy-level P&L
    strategy_pnl = {
        'symbol': symbol,
        'strategy': strategy_type,
        'total_pnl': sum(p['pnl'] for p in symbol_positions),
        'positions': len(symbol_positions),
        'margin_used': sum(p['margin'] for p in symbol_positions),
    }
    
    return strategy_pnl

# Get P&L for specific strategies
short_strangle_pnl = get_strategy_pnl(nuvama, 'RELIANCE', 'SHORT_STRANGLE')
if short_strangle_pnl:
    print(f"SHORT_STRANGLE on {short_strangle_pnl['symbol']}: ₹{short_strangle_pnl['total_pnl']}")
```

---

## Troubleshooting

### Issue 1: "Authentication Failed"

**Causes:**
- Invalid Client ID
- Incorrect password
- 2FA enabled without TOTP

**Solution:**
```python
# Verify credentials
print("Checking credentials...")
print(f"Client ID: {connector.client_id}")

# Disable 2FA if not set up
NUVAMA_TOTP_ENABLED = False  # In constants.py

# Try manual authentication
connector.authenticate(force_manual=True)
```

### Issue 2: "MWPL Check Failed"

**Causes:**
- MWPL temporarily unavailable
- Network connectivity issue
- Nuvama API down

**Solution:**
```python
import time

def safe_mwpl_check(connector, max_retries=3):
    """Check MWPL with retry logic"""
    for attempt in range(max_retries):
        try:
            return connector.check_mwpl()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait 5 seconds before retry
    return None
```

### Issue 3: "Orders Not Updating"

**Causes:**
- Cache not refreshed
- Market hours check

**Solution:**
```python
# Force refresh orders
orders = connector.get_orders(status='OPEN', force_refresh=True)

# Check if market is open
from helper.constants import MARKET_OPEN_HOUR, MARKET_CLOSE_HOUR, TEST_RUN
from datetime import datetime

current_hour = datetime.now().hour

if not TEST_RUN:
    if current_hour < MARKET_OPEN_HOUR or current_hour >= MARKET_CLOSE_HOUR:
        print("⚠️  Market is closed. Orders may not update in real-time.")
```

### Issue 4: "Margin Calculation Incorrect"

**Solution:**
```python
# Get detailed margin breakdown
margin_detail = connector.get_margin_detail()

print("Margin Breakdown:")
print(f"  Cash Available: ₹{margin_detail['cash']}")
print(f"  Pledged Margin: ₹{margin_detail['pledged_margin']}")
print(f"  F&O Margin: ₹{margin_detail['fo_margin']}")
print(f"  Total Margin: ₹{margin_detail['total']}")
```

---

## Advanced Features

### Auto-Sync Positions to Database

```python
from brokers.nuvama import NuvamaBrokerConnector
from output.sql_writer import SQLWriter
import time

def sync_nuvama_positions(connector, db_writer, interval_seconds=300):
    """Continuously sync Nuvama positions to database"""
    
    while True:
        try:
            # Fetch positions
            positions = connector.get_positions()
            margin = connector.get_margin_used()
            
            # Write to database
            for pos in positions:
                db_writer.write_position({
                    'broker': 'NUVAMA',
                    'symbol': pos['symbol'],
                    'quantity': pos['quantity'],
                    'avg_price': pos['avg_price'],
                    'ltp': pos['ltp'],
                    'pnl': pos['pnl'],
                    'margin': pos['margin'],
                    'timestamp': datetime.now()
                })
            
            # Write margin status
            db_writer.write_margin({
                'broker': 'NUVAMA',
                'used': margin['used'],
                'available': margin['available'],
                'utilization': margin['utilization_percent'],
                'timestamp': datetime.now()
            })
            
            print(f"Synced {len(positions)} positions at {datetime.now()}")
            
        except Exception as e:
            print(f"Sync error: {e}")
        
        # Wait before next sync
        time.sleep(interval_seconds)

# Start syncing
# sync_nuvama_positions(nuvama, db_writer)
```

### P&L Alerts

```python
def setup_pnl_alerts(connector, loss_limit=-5000, profit_target=10000):
    """Set up alerts for P&L targets"""
    
    while True:
        positions = connector.get_positions()
        total_pnl = sum(p['pnl'] for p in positions)
        
        if total_pnl <= loss_limit:
            print(f"🚨 ALERT: P&L hit loss limit! Current: ₹{total_pnl}")
            # Send email/SMS alert
            # send_alert(f"Loss limit reached: ₹{total_pnl}")
            
        elif total_pnl >= profit_target:
            print(f"✅ ALERT: Profit target reached! Current: ₹{total_pnl}")
            # send_alert(f"Profit target reached: ₹{total_pnl}")
        
        time.sleep(30)  # Check every 30 seconds
```

---

## Performance Tips

1. **Reduce API Calls:** Cache position data for 5-10 seconds
2. **Batch Operations:** Get all data at once rather than individual calls
3. **Use MWPL Cache:** Update MWPL every 5 minutes instead of on every request
4. **Async Monitoring:** Run monitoring in background threads
5. **Database Syncing:** Write to database asynchronously to avoid blocking

---

## Support & Resources

- **Nuvama Support:** 1800-102-3335
- **Email:** helpdesk@nuvama.com
- **API Documentation:** https://www.nuvamawealth.com/api-connect/
- **Trading Terminal:** https://www.nuvamawealth.com/login
- **Account Opening:** https://www.nuvamawealth.com/demat-account

---

**Last Updated:** January 2025  
**Version:** 1.0.0
