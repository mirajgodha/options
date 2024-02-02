import sqlite3

db_name = '../sql/stocks.db'

# Create a connection object
# Connect to the SQLite database (creates a new database if it doesn't exist)
conn = sqlite3.connect(db_name)

# Create a cursor object to interact with the database
cursor = conn.cursor()


def get_conn():
    global conn, cursor
    if not conn or not cursor:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
    return conn


def get_cursor():
    global conn, cursor
    if not cursor:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
    return cursor


def commit():
    conn.commit()


def close():
    cursor.close()
    conn.close()


# Create a table
def create_tables():
    cursor_inner = get_cursor()
    # Create a table (if it doesn't exist)
    cursor_inner.execute('''
        CREATE TABLE if not exists option_pnl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock TEXT NOT NULL,
            expiry TEXT NOT NULL,
            pnl float,
            timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
        )
    ''')
    conn.commit()
    cursor_inner.close()


# Insert a row of data


def insert_pnl(df):
    conn_inner = get_conn()
    cursor_inner = get_cursor()

    try:
        for index, row in df.iterrows():
            stock = row['stock']
            expiry = row['expiry_date']
            pnl = row['pnl']
            cursor_inner.execute("INSERT INTO option_pnl (stock, expiry, pnl) VALUES (?, ?, ?)", (stock, expiry, pnl))
    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: option_pnl':
            print("Table not found - option_pnl. Creating table")
            create_tables()
            insert_pnl(df)
        else:
            print("Error inserting data")
    finally:
        try:
            conn_inner.commit()
            # cursor_inner.close()
            # conn_inner.close()
        except:
            pass


# Query the database




def get_pnl(stock, expiry):
    cursor_inner = get_cursor()
    cursor_inner.execute("SELECT * FROM option_pnl WHERE stock = ? AND expiry = ?", (stock, expiry))
    rows = cursor_inner.fetchall()
    cursor_inner.close()
    return rows


# # Close the cursor and the connection
# cursor.close()
# conn.close()
