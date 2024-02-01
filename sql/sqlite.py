import sqlite3

# Connect to the SQLite database (creates a new database if it doesn't exist)
conn = sqlite3.connect('stocks.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()


def get_conn():
    global conn, cursor
    if not conn:
        conn = sqlite3.connect('stocks.db')
        cursor = conn.cursor()
    return conn


def get_cursor():
    global conn, cursor
    if not cursor:
        conn = sqlite3.connect('stocks.db')
        cursor = conn.cursor()
    return cursor


def commit():
    conn.commit()


def close():
    cursor.close()
    conn.close()


# Create a table
def create_tables():
    cursor = get_cursor()
    # Create a table (if it doesn't exist)
    cursor.execute('''
        CREATE TABLE if not exists option_pnl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock TEXT NOT NULL,
            expiry TEXT NOT NULL,
            pnl float,
            timestamp dateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(stock, expiry)
        )
    ''')
    conn.commit()

def insert_pnl(df):
    cursor = get_cursor()
    for index, row in df.iterrows():
        stock = row['Stock']
        expiry = row['Expiry']
        pnl = row['PnL']
        cursor.execute("INSERT INTO option_pnl (stock, expiry, pnl) VALUES (?, ?, ?)", (stock, expiry, pnl))
    conn.commit()

def get_pnl(stock, expiry):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM option_pnl WHERE stock = ? AND expiry = ?", (stock, expiry))
    rows = cursor.fetchall()
    return rows


# Close the cursor and the connection
cursor.close()
conn.close()
