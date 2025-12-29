# Installation & Troubleshooting Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Common Issues & Solutions](#common-issues--solutions)
6. [Performance Optimization](#performance-optimization)
7. [Docker Setup (Optional)](#docker-setup-optional)

---

## System Requirements

### Minimum Requirements
- **OS:** Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python:** 3.7 or higher
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 2GB for application + database
- **Internet:** Required for NSE data fetching

### Optional Requirements
- **Java:** For Metabase dashboards (Java 11+)
- **PostgreSQL/MySQL:** For large-scale analysis (SQLite works for small portfolios)

### Supported Brokers
- ICICI Direct (implemented)
- Others can be added by extending broker base class

---

## Step-by-Step Installation

### On Windows

#### Step 1: Install Python
```bash
# Download Python 3.9+ from https://www.python.org/downloads/
# Run installer
# ✓ CHECK "Add Python to PATH"
# ✓ CHECK "Install pip"

# Verify installation
python --version
pip --version
```

#### Step 2: Clone Repository
```bash
# Open Command Prompt or PowerShell

# Navigate to desired folder
cd C:\Users\YourName\Documents

# Clone repository
git clone https://github.com/mirajgodha/options.git
cd options
```

#### Step 3: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your command prompt
```

#### Step 4: Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 5: Configure Application
```bash
# Edit configuration file
# Open: helper/constants.py in text editor

# Set these values:
TEST_RUN = False  # or True if outside market hours
ICICI_USERNAME = 'your_username'
ICICI_PASSWORD = 'your_password'
```

#### Step 6: Test Installation
```bash
# Run test
python -c "import pandas; import numpy; print('✓ Dependencies OK')"

# Test NSE connection
python -m data.nse_fetcher
```

---

### On macOS

#### Step 1: Install Python (Using Homebrew)
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.9

# Verify
python3 --version
pip3 --version
```

#### Step 2: Clone & Setup
```bash
# Navigate to desired directory
cd ~/Documents

# Clone repository
git clone https://github.com/mirajgodha/options.git
cd options

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### Step 4: Configure
```bash
# Edit configuration
nano helper/constants.py

# Or use your preferred editor
vim helper/constants.py
```

#### Step 5: Install Java (for Metabase)
```bash
# Install Java
brew install openjdk@11

# Verify
java -version
```

---

### On Linux (Ubuntu/Debian)

#### Step 1: Install Python & Dependencies
```bash
# Update package manager
sudo apt update
sudo apt upgrade

# Install Python and pip
sudo apt install python3.9 python3.9-venv python3-pip git

# Verify
python3 --version
pip3 --version
```

#### Step 2: Clone & Setup
```bash
# Navigate to desired directory
cd ~/workspace

# Clone repository
git clone https://github.com/mirajgodha/options.git
cd options

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install system dependencies (if needed)
sudo apt install build-essential libxml2-dev libxslt1-dev

# Install Python requirements
pip install -r requirements.txt
```

#### Step 4: Install Java (for Metabase)
```bash
# Install Java
sudo apt install openjdk-11-jdk

# Verify
java -version
```

---

## Configuration

### 1. Main Configuration File

**File:** `helper/constants.py`

```python
# ===== MARKET SETTINGS =====
TEST_RUN = False                    # True for testing outside market hours
MARKET_OPEN_HOUR = 9               # 9 AM IST
MARKET_CLOSE_HOUR = 15             # 3 PM IST
MARKET_DAYS = [0, 1, 2, 3, 4]     # Mon=0, Fri=4

# ===== DATABASE =====
DB_TYPE = 'sqlite'                 # Options: sqlite, postgresql, mysql
DB_CONNECTION_STRING = 'sqlite:///options_data.db'
DB_ECHO = False                    # Set True for debugging

# PostgreSQL example:
# DB_CONNECTION_STRING = 'postgresql://user:password@localhost:5432/options'

# MySQL example:
# DB_CONNECTION_STRING = 'mysql+pymysql://user:password@localhost:3306/options'

# ===== BROKER INTEGRATION =====
ENABLE_BROKER_SYNC = True
BROKER_SYNC_INTERVAL = 60          # seconds

ICICI_DIRECT_ENABLED = True
ICICI_USERNAME = 'your_userid'
ICICI_PASSWORD = 'your_password'

# ===== STRIKE CONFIGURATION =====
STRIKE_DIFFERENCE_STRANGLE = 100
STRIKE_DIFFERENCE_STRADDLE = 50
STRIKE_DIFFERENCE_GUTS = 200

# ===== SCANNING FILTERS =====
MAX_LOSS_THRESHOLD = 1000          # ₹
PROFIT_PROBABILITY_THRESHOLD = 0.60
MIN_PREMIUM_CREDIT = 500           # ₹

# ===== OUTPUT SETTINGS =====
WRITE_TO_EXCEL = True
WRITE_TO_SQL = True
EXCEL_OUTPUT_PATH = './output/'
INCLUDE_CHARTS_IN_EXCEL = True

# ===== OPTIONS PRICING =====
RISK_FREE_RATE = 0.065             # 6.5% annually
DIVIDEND_YIELD = 0.02              # 2% dividend yield
VOLATILITY_SOURCE = 'nse'          # nse or computed
VOLATILITY_LOOKBACK_DAYS = 30

# ===== ALERTS =====
MARGIN_WARNING_THRESHOLD = 0.80    # 80% usage
BAN_LIST_CHECK_INTERVAL = 300      # 5 minutes
PNL_ALERT_ENABLED = True
```

### 2. Broker Credentials (Secure)

**File:** `config/broker_credentials.json`

```json
{
  "icici_direct": {
    "username": "your_userid",
    "password": "your_password"
  },
  "other_broker": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret"
  }
}
```

**Security Note:** Never commit this file to git!

```bash
# Add to .gitignore
echo "config/broker_credentials.json" >> .gitignore
```

### 3. Database Setup

#### SQLite (Default - No Setup Needed)
```python
# Automatically created on first run
# File: options_data.db (in project root)
```

#### PostgreSQL
```bash
# Install PostgreSQL
# On Ubuntu: sudo apt install postgresql postgresql-contrib
# On macOS: brew install postgresql
# On Windows: Download from https://www.postgresql.org/download/windows/

# Create database
sudo -u postgres psql
CREATE DATABASE options_trading;
\q

# Update constants.py
DB_CONNECTION_STRING = 'postgresql://postgres:password@localhost:5432/options_trading'
```

#### MySQL
```bash
# Install MySQL
# On Ubuntu: sudo apt install mysql-server
# On macOS: brew install mysql
# On Windows: Download from https://www.mysql.com/downloads/

# Create database
mysql -u root -p
CREATE DATABASE options_trading;
EXIT;

# Update constants.py
DB_CONNECTION_STRING = 'mysql+pymysql://root:password@localhost:3306/options_trading'
```

---

## Verification

### Test 1: Python & Dependencies
```bash
# Activate virtual environment
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

# Test imports
python -c "
import pandas as pd
import numpy as np
import openpyxl
from sqlalchemy import create_engine
print('✓ All dependencies installed correctly')
"
```

### Test 2: NSE Data Fetching
```python
# Create test_installation.py
from data.nse_fetcher import NSEDataFetcher

try:
    fetcher = NSEDataFetcher()
    chain = fetcher.fetch_option_chain('RELIANCE', '2025-01-30')
    print(f"✓ NSE Connection OK - Spot: ₹{chain.spot_price}")
except Exception as e:
    print(f"✗ NSE Connection Failed: {e}")
```

### Test 3: Strategy Calculator
```python
from data.nse_fetcher import NSEDataFetcher
from strategy.calculator import StrategyCalculator

# Fetch data
fetcher = NSEDataFetcher()
chain = fetcher.fetch_option_chain('RELIANCE', '2025-01-30')

# Calculate strategy
calc = StrategyCalculator('RELIANCE', chain, 'SHORT_STRANGLE')
strategy = calc.calculate(short_put_strike=2700, short_call_strike=3100)

print(f"✓ Strategy Calculator OK")
print(f"  Max Profit: ₹{strategy.max_profit}")
print(f"  Max Loss: ₹{strategy.max_loss}")
```

### Test 4: Database Connection
```python
from helper.constants import DB_CONNECTION_STRING
from sqlalchemy import create_engine

try:
    engine = create_engine(DB_CONNECTION_STRING)
    with engine.connect() as conn:
        print("✓ Database Connection OK")
except Exception as e:
    print(f"✗ Database Connection Failed: {e}")
```

### Test 5: Broker Connection (Optional)
```python
from brokers.icici_direct import ICICIDirectConnector

try:
    connector = ICICIDirectConnector(
        username='your_username',
        password='your_password'
    )
    connector.authenticate()
    positions = connector.get_positions()
    print(f"✓ Broker Connection OK - {len(positions)} positions")
except Exception as e:
    print(f"✗ Broker Connection Failed: {e}")
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'pandas'"

**Cause:** Dependencies not installed correctly

**Solution:**
```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstall requirements
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

### Issue 2: "No module named 'data.nse_fetcher'"

**Cause:** Project root not in Python path

**Solution:**
```bash
# Run from project root directory
cd options

# Verify structure
ls  # Should show: strategy/ data/ brokers/ helper/ main.py etc.

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Mac/Linux

# Or run with python module
python -m strategy.calculator
```

---

### Issue 3: "NSE data not fetching - ConnectionError"

**Cause:** Internet connectivity or NSE website change

**Solution:**
```python
# Test internet connection
import requests
try:
    response = requests.get('https://www.nseindia.com', timeout=5)
    print(f"✓ NSE website accessible: {response.status_code}")
except Exception as e:
    print(f"✗ Cannot reach NSE: {e}")

# Test with headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
response = requests.get('https://www.nseindia.com', headers=headers)
print(f"Response: {response.status_code}")
```

---

### Issue 4: "TEST_RUN must be True outside market hours"

**Cause:** Running during non-market hours without TEST_RUN flag

**Solution:**
```python
# In helper/constants.py
TEST_RUN = True  # Set to True outside 9 AM - 3:30 PM IST
```

---

### Issue 5: "ICICI Direct authentication failed"

**Cause:** Invalid credentials or API not enabled

**Solution:**
```bash
# Verify credentials
# 1. Check username spelling
# 2. Ensure 2FA is disabled for API access
# 3. Contact ICICI Direct support

# Test with simple request
from brokers.icici_direct import ICICIDirectConnector

connector = ICICIDirectConnector(
    username='your_username',
    password='your_password'
)

# Add timeout and detailed error
try:
    connector.authenticate()
    print("✓ Authenticated")
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"  Check: username, password, 2FA status")
```

---

### Issue 6: "Database locked - sqlite3.OperationalError"

**Cause:** Multiple processes accessing SQLite simultaneously

**Solution:**
```python
# Use WAL mode (Write-Ahead Logging)
import sqlite3

conn = sqlite3.connect('options_data.db')
conn.execute('PRAGMA journal_mode=WAL')
conn.close()

# Or use PostgreSQL for concurrent access
# Update constants.py to use PostgreSQL
```

---

### Issue 7: "Greeks calculation returning NaN"

**Cause:** Invalid inputs to Black-Scholes model

**Solution:**
```python
# Validate inputs
assert stock_price > 0, "Stock price must be positive"
assert strike > 0, "Strike must be positive"
assert time_to_expiry > 0, "Time to expiry must be positive"
assert volatility > 0, "Volatility must be positive"

# Example of correcting
time_to_expiry = max(1/365, days_to_expiry / 365)  # At least 1 day
volatility = max(0.01, implied_volatility)         # At least 1%
```

---

### Issue 8: "Metabase not starting - "Cannot find java""

**Cause:** Java not installed or not in PATH

**Solution:**
```bash
# Install Java
# Ubuntu: sudo apt install openjdk-11-jdk
# macOS: brew install openjdk@11
# Windows: Download from https://adoptium.net/

# Verify
java -version

# Set JAVA_HOME (if needed)
# Windows: set JAVA_HOME=C:\Program Files\Java\jdk-11
# Mac/Linux: export JAVA_HOME=/usr/libexec/java_home -v 11

# Start Metabase
cd metabase/
java -jar metabase.jar
```

---

### Issue 9: "Excel export file locked"

**Cause:** File already open in Excel

**Solution:**
```bash
# Close file in Excel
# Then run export again

# Or use different filename
scanner.export_to_excel(
    results,
    'strategies_new.xlsx'  # Different name
)
```

---

### Issue 10: "Very slow performance - database slow"

**Cause:** Large amount of data in SQLite

**Solution:**
```python
# 1. Add database indexes
CREATE INDEX idx_symbol ON strategies(symbol);
CREATE INDEX idx_date ON strategies(created_at);

# 2. Archive old data
DELETE FROM strategies WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

# 3. Switch to PostgreSQL
# More efficient for large datasets
DB_CONNECTION_STRING = 'postgresql://user:pwd@localhost/options'
```

---

## Performance Optimization

### 1. Database Optimization

```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///options_data.db',
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

### 2. Batch Operations

```python
# Instead of individual inserts
for result in results:
    scanner.export_single(result)  # Slow

# Use batch insert
scanner.export_to_database(results)  # Fast
```

### 3. Multiprocessing for Scanning

```python
from concurrent.futures import ProcessPoolExecutor
from data.nse_fetcher import NSEDataFetcher

def scan_stock(symbol):
    fetcher = NSEDataFetcher()
    chain = fetcher.fetch_option_chain(symbol, expiry)
    # Calculate strategies
    return results

symbols = fetcher.get_all_nse_fno_symbols()

with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(scan_stock, symbols))
```

### 4. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def fetch_option_chain_cached(symbol, expiry):
    fetcher = NSEDataFetcher()
    return fetcher.fetch_option_chain(symbol, expiry)
```

---

## Docker Setup (Optional)

### Install Docker

```bash
# Windows/macOS: Download Docker Desktop from https://www.docker.com/products/docker-desktop
# Linux: sudo apt install docker.io
```

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 3000 5000 8080

# Run application
CMD ["python", "main.py"]
```

### Build & Run

```bash
# Build
docker build -t options-trader .

# Run
docker run -it -v $(pwd)/output:/app/output options-trader

# With Metabase
docker run -it -p 3000:3000 options-trader
```

---

## Updating & Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Backup database
cp options_data.db options_data.db.backup
```

### Database Maintenance

```python
# Clean old data
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('options_data.db')
cursor = conn.cursor()

# Delete data older than 90 days
cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()
cursor.execute('DELETE FROM strategies WHERE created_at < ?', (cutoff_date,))
conn.commit()
conn.close()
```

### Troubleshooting Checklist

- [ ] Python version 3.7+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip list`)
- [ ] Configuration file updated
- [ ] NSE connectivity verified
- [ ] Database connection working
- [ ] Broker credentials configured (if using)
- [ ] First run completed without errors

For additional support, check GitHub Issues or create a new issue with:
- Python version
- Operating system
- Error message (full traceback)
- Steps to reproduce
- Expected vs actual behavior
