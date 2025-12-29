# Multi-Broker Integration Guide (ICICI Direct + Nuvama)

## Overview

The Options Strategy Builder supports multiple brokers, enabling you to:

- Consolidate positions across different brokers
- Track unified P&L dashboard
- Monitor margin across accounts
- Automate strategy execution on any broker
- Compare broker-specific pricing

---

## Supported Brokers

| Broker | Status | Setup Complexity | API Charges | F&O Support |
|--------|--------|-----------------|-------------|------------|
| **ICICI Direct** | ✅ Production Ready | Medium | No | Yes |
| **Nuvama Wealth** | ✅ Production Ready | Medium | No | Yes |
| **Zerodha** | 📋 Roadmap | Easy | No | Yes |
| **5Paisa** | 📋 Roadmap | Medium | No | Yes |

---

## Quick Comparison: ICICI Direct vs Nuvama

| Feature | ICICI Direct | Nuvama Wealth |
|---------|--------------|---------------|
| **Options Brokerage** | ₹20/lot | ₹20/lot |
| **API Charges** | No | No |
| **Deep OTM Trading** | Standard | Yes (NRML) |
| **Exchange Charges** | Standard | Discounted (~₹3500/Cr) |
| **Margin Pledge** | Manual | Online |
| **Minimum Account** | ₹0 | ₹0 |
| **Setup Complexity** | Medium | Medium |

---

## Setup Instructions

### 1. ICICI Direct Setup

#### Get Your Credentials

1. Log in to ICICI Direct portal
2. Note your **User ID**
3. Keep your **Password** secure
4. Optional: Enable 2FA

#### Configure in Application

Edit `helper/constants.py`:

```python
# ===== ICICI DIRECT CONFIGURATION =====
ICICI_DIRECT_ENABLED = True
ICICI_USERNAME = 'your_icici_user_id'
ICICI_PASSWORD = 'your_icici_password'
ICICI_PIN = 'your_pin'              # Optional: for 2FA
```

### 2. Nuvama Wealth Setup

#### Get Your Credentials

1. Log in to https://www.nuvamawealth.com/login
2. Go to **Profile** section
3. Note your **Client ID** (6-8 digits)
4. Keep your **Password** secure

#### Configure in Application

Edit `helper/constants.py`:

```python
# ===== NUVAMA WEALTH CONFIGURATION =====
NUVAMA_ENABLED = True
NUVAMA_CLIENT_ID = 'your_client_id'
NUVAMA_PASSWORD = 'your_password'
NUVAMA_TOTP_ENABLED = False            # Set True if 2FA enabled
NUVAMA_TOTP_SECRET = 'your_totp_secret' # If 2FA enabled
```

### 3. Secure Credentials Storage

Create `config/broker_credentials.json`:

```json
{
  "icici_direct": {
    "username": "your_icici_user_id",
    "password": "your_icici_password",
    "pin": "your_pin"
  },
  "nuvama": {
    "client_id": "your_nuvama_client_id",
    "password": "your_nuvama_password",
    "totp_secret": "your_totp_secret"
  }
}
```

⚠️ **CRITICAL:** Add to `.gitignore`:

```bash
echo "config/broker_credentials.json" >> .gitignore
```

---

## Usage: Unified Broker Interface

### Initialize All Brokers

```python
from brokers.icici_direct import ICICIDirectConnector
from brokers.nuvama import NuvamaBrokerConnector

# Initialize ICICI
icici = ICICIDirectConnector(username='id', password='pwd')
icici.authenticate()

# Initialize Nuvama
nuvama = NuvamaBrokerConnector(client_id='client_id', password='pwd')
nuvama.authenticate()

print("✓ Connected to both brokers")
```

### Consolidated Positions Dashboard

```python
def get_consolidated_view(icici_connector, nuvama_connector):
    """Get unified position view across all brokers"""
    
    # Fetch from both brokers
    icici_pos = icici_connector.get_positions()
    nuvama_pos = nuvama_connector.get_positions()
    
    # Combine
    all_positions = []
    for pos in icici_pos:
        pos['broker'] = 'ICICI Direct'
        all_positions.append(pos)
    
    for pos in nuvama_pos:
        pos['broker'] = 'Nuvama'
        all_positions.append(pos)
    
    # Calculate totals
    total_pnl = sum(p['pnl'] for p in all_positions)
    total_margin = sum(p.get('margin', 0) for p in all_positions)
    
    # By broker breakdown
    print("=" * 70)
    print("CONSOLIDATED POSITIONS ACROSS BROKERS")
    print("=" * 70)
    
    for broker_name in ['ICICI Direct', 'Nuvama']:
        broker_positions = [p for p in all_positions if p['broker'] == broker_name]
        broker_pnl = sum(p['pnl'] for p in broker_positions)
        broker_margin = sum(p.get('margin', 0) for p in broker_positions)
        
        print(f"\n{broker_name}:")
        print(f"  Positions: {len(broker_positions)}")
        print(f"  Total P&L: ₹{broker_pnl:.2f}")
        print(f"  Margin Used: ₹{broker_margin:.2f}")
        
        for pos in broker_positions[:3]:  # Show top 3
            print(f"    {pos['symbol']}: ₹{pos['pnl']:.2f}")
    
    # Grand totals
    print(f"\n{'='*70}")
    print(f"GRAND TOTAL")
    print(f"{'='*70}")
    print(f"Total Positions: {len(all_positions)}")
    print(f"Total P&L: ₹{total_pnl:.2f}")
    print(f"Total Margin: ₹{total_margin:.2f}")
    
    return all_positions

# Run
positions = get_consolidated_view(icici, nuvama)
```

### Unified Margin Tracking

```python
def track_unified_margin(icici_connector, nuvama_connector):
    """Track margin across all brokers"""
    
    icici_margin = icici_connector.get_margin_used()
    nuvama_margin = nuvama_connector.get_margin_used()
    
    print("\nMARGIN UTILIZATION")
    print("=" * 50)
    
    # ICICI
    print("\nICICI Direct:")
    print(f"  Used: ₹{icici_margin['used']:.2f}")
    print(f"  Available: ₹{icici_margin['available']:.2f}")
    print(f"  Utilization: {icici_margin['utilization_percent']:.1f}%")
    
    # Nuvama
    print("\nNuvama Wealth:")
    print(f"  Used: ₹{nuvama_margin['used']:.2f}")
    print(f"  Available: ₹{nuvama_margin['available']:.2f}")
    print(f"  Utilization: {nuvama_margin['utilization_percent']:.1f}%")
    
    # Total
    total_used = icici_margin['used'] + nuvama_margin['used']
    total_available = icici_margin['available'] + nuvama_margin['available']
    total_util = (total_used / (total_used + total_available) * 100) if (total_used + total_available) > 0 else 0
    
    print(f"\nCombined:")
    print(f"  Used: ₹{total_used:.2f}")
    print(f"  Available: ₹{total_available:.2f}")
    print(f"  Utilization: {total_util:.1f}%")
    
    # Warnings
    if icici_margin['utilization_percent'] > 80:
        print("\n⚠️  ICICI margin > 80%")
    if nuvama_margin['utilization_percent'] > 80:
        print("⚠️  Nuvama margin > 80%")

# Monitor
track_unified_margin(icici, nuvama)
```

### Multi-Broker Order Management

```python
def get_all_open_orders(icici_connector, nuvama_connector):
    """Get all open orders across brokers"""
    
    icici_orders = icici_connector.get_orders(status='OPEN')
    nuvama_orders = nuvama_connector.get_orders(status='OPEN')
    
    print("\n" + "=" * 80)
    print("OPEN ORDERS ACROSS ALL BROKERS")
    print("=" * 80)
    
    # ICICI Orders
    print(f"\nICICI Direct ({len(icici_orders)} orders):")
    for order in icici_orders:
        print(f"  {order['symbol']} | {order['order_type']} | "
              f"{order['quantity']} @ ₹{order['price']} | "
              f"ID: {order['order_id']}")
    
    # Nuvama Orders
    print(f"\nNuvama Wealth ({len(nuvama_orders)} orders):")
    for order in nuvama_orders:
        print(f"  {order['symbol']} | {order['order_type']} | "
              f"{order['quantity']} @ ₹{order['price']} | "
              f"ID: {order['order_id']}")
    
    print(f"\nTotal Open Orders: {len(icici_orders) + len(nuvama_orders)}")

# Get all orders
get_all_open_orders(icici, nuvama)
```

### Strategy Monitoring Across Brokers

```python
def monitor_strategies(icici_connector, nuvama_connector, symbols):
    """Monitor specific strategies across brokers"""
    
    print("\nSTRATEGY MONITORING ACROSS BROKERS")
    print("=" * 70)
    
    for symbol in symbols:
        icici_pos = [p for p in icici_connector.get_positions() 
                     if symbol in p['symbol']]
        nuvama_pos = [p for p in nuvama_connector.get_positions() 
                      if symbol in p['symbol']]
        
        icici_pnl = sum(p['pnl'] for p in icici_pos)
        nuvama_pnl = sum(p['pnl'] for p in nuvama_pos)
        total_pnl = icici_pnl + nuvama_pnl
        
        print(f"\n{symbol}:")
        if icici_pos:
            print(f"  ICICI: ₹{icici_pnl:.2f} ({len(icici_pos)} positions)")
        if nuvama_pos:
            print(f"  Nuvama: ₹{nuvama_pnl:.2f} ({len(nuvama_pos)} positions)")
        print(f"  Total: ₹{total_pnl:.2f}")

# Monitor strategies
monitor_strategies(icici, nuvama, ['RELIANCE', 'INFY', 'TCS'])
```

---

## Real-time Monitoring Script

```python
import time
from datetime import datetime

def monitor_all_brokers(icici, nuvama, interval_seconds=60):
    """
    Real-time monitoring of all brokers
    Press Ctrl+C to stop
    """
    
    print("Starting multi-broker monitoring...")
    print(f"Update interval: {interval_seconds} seconds\n")
    
    try:
        while True:
            # Get data from both brokers
            icici_pos = icici.get_positions()
            nuvama_pos = nuvama.get_positions()
            
            icici_margin = icici.get_margin_used()
            nuvama_margin = nuvama.get_margin_used()
            
            # Combined metrics
            all_positions = icici_pos + nuvama_pos
            total_pnl = sum(p['pnl'] for p in all_positions)
            total_margin_used = icici_margin['used'] + nuvama_margin['used']
            
            # Display
            print(f"\n{'='*70}")
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*70}")
            
            # Summary
            print(f"\n📊 SUMMARY:")
            print(f"  Total Positions: {len(all_positions)}")
            print(f"  Total P&L: ₹{total_pnl:,.2f}")
            print(f"  Margin Used: ₹{total_margin_used:,.2f}")
            
            # By Broker
            print(f"\n🏢 BY BROKER:")
            print(f"  ICICI: {len(icici_pos)} positions | "
                  f"P&L: ₹{sum(p['pnl'] for p in icici_pos):,.2f} | "
                  f"Margin: ₹{icici_margin['used']:,.2f}")
            print(f"  Nuvama: {len(nuvama_pos)} positions | "
                  f"P&L: ₹{sum(p['pnl'] for p in nuvama_pos):,.2f} | "
                  f"Margin: ₹{nuvama_margin['used']:,.2f}")
            
            # Alerts
            if total_pnl < -10000:
                print(f"\n🚨 ALERT: Large loss! P&L: ₹{total_pnl:,.2f}")
            if total_margin_used / (total_margin_used + icici_margin['available'] + nuvama_margin['available']) > 0.9:
                print(f"\n⚠️  ALERT: Margin utilization > 90%")
            
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

# Run monitoring
# monitor_all_brokers(icici, nuvama, interval_seconds=60)
```

---

## Integration with Metabase

Export consolidated data to database for Metabase visualization:

```python
from output.sql_writer import SQLWriter

def export_multi_broker_data(icici, nuvama, db_writer):
    """Export data from all brokers to database"""
    
    # Get data
    icici_pos = icici.get_positions()
    nuvama_pos = nuvama.get_positions()
    
    # Write ICICI positions
    for pos in icici_pos:
        db_writer.write_position({
            'broker': 'ICICI_DIRECT',
            'symbol': pos['symbol'],
            'quantity': pos['quantity'],
            'pnl': pos['pnl'],
            'margin': pos['margin'],
            'timestamp': datetime.now()
        })
    
    # Write Nuvama positions
    for pos in nuvama_pos:
        db_writer.write_position({
            'broker': 'NUVAMA',
            'symbol': pos['symbol'],
            'quantity': pos['quantity'],
            'pnl': pos['pnl'],
            'margin': pos['margin'],
            'timestamp': datetime.now()
        })
    
    print("✓ Data exported to database")

# Export
# db_writer = SQLWriter()
# export_multi_broker_data(icici, nuvama, db_writer)
```

---

## Troubleshooting

### Both Brokers Connected?

```python
def verify_broker_connections(icici, nuvama):
    """Verify both brokers are connected"""
    
    try:
        icici_pos = icici.get_positions()
        print("✓ ICICI Direct: Connected")
    except Exception as e:
        print(f"✗ ICICI Direct: {e}")
    
    try:
        nuvama_pos = nuvama.get_positions()
        print("✓ Nuvama Wealth: Connected")
    except Exception as e:
        print(f"✗ Nuvama Wealth: {e}")

verify_broker_connections(icici, nuvama)
```

### Handle Connection Failures

```python
def safe_get_all_positions(icici, nuvama):
    """Get positions with error handling"""
    
    positions = []
    
    try:
        icici_pos = icici.get_positions()
        for p in icici_pos:
            p['broker'] = 'ICICI'
            positions.append(p)
    except Exception as e:
        print(f"⚠️  ICICI error: {e}")
    
    try:
        nuvama_pos = nuvama.get_positions()
        for p in nuvama_pos:
            p['broker'] = 'Nuvama'
            positions.append(p)
    except Exception as e:
        print(f"⚠️  Nuvama error: {e}")
    
    return positions

positions = safe_get_all_positions(icici, nuvama)
```

---

## Adding New Brokers

To add a new broker (e.g., Zerodha):

1. Create `brokers/zerodha.py`
2. Implement the interface:

```python
from brokers.broker_base import BrokerInterface

class ZerodhaConnector(BrokerInterface):
    def authenticate(self):
        """Implement Zerodha authentication"""
        pass
    
    def get_positions(self):
        """Return list of positions"""
        pass
    
    def get_margin_used(self):
        """Return margin info"""
        pass
    
    def get_orders(self, status='OPEN'):
        """Return orders"""
        pass
    
    def check_mwpl(self):
        """Check MWPL status"""
        pass
```

3. Update configuration in `constants.py`
4. Use same unified interface!

---

## Performance Best Practices

1. **Cache Data:** Store results for 5-10 seconds
2. **Async Updates:** Run broker sync in background thread
3. **Batch Calls:** Get all data at once, not individually
4. **Error Handling:** Implement retry logic for failed calls
5. **Database Sync:** Write to DB asynchronously

---

## Support

- **ICICI Direct:** Call 9650200000
- **Nuvama Wealth:** Call 1800-102-3335
- **Application Issues:** Check logs in `logs/` directory

---

**Last Updated:** January 2025  
**Version:** 1.0.0
