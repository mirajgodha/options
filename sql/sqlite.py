import datetime
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
    if not cursor or not conn or not cursor.connection:
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
    # Create a table option_pnl (if it doesn't exist)
    cursor_inner.execute('''
        CREATE TABLE if not exists option_pnl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock TEXT NOT NULL,
            expiry TEXT NOT NULL,
            pnl float,
            timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
        )
    ''')
    # Create a table margins_used (if it doesn't exist)
    cursor_inner.execute('''
            CREATE TABLE if not exists margins_used (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock TEXT NOT NULL,
                expiry TEXT NOT NULL,
                non_span_margin_required float,
                order_value float,
                order_margin float,
                trade_margin float,
                block_trade_margin float,
                span_margin_required float,
                timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
            )
        ''')

    # Create a table order_status (if it doesn't exist)
    cursor_inner.execute('''
                CREATE TABLE if not exists order_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock TEXT NOT NULL,
                    expiry TEXT NOT NULL,
                    ltp float,
                    order_price float,
                    order_status TEXT NOT NULL,
                    order_time dateTime NOT NULL,
                    action TEXT NOT NULL,
                    quantity int,
                    right TEXT NOT NULL,
                    strike_price float,
                    pending_quantity int,
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
        except:
            pass


# Query the database


def get_pnl(stock, expiry):
    cursor_inner = get_cursor()
    cursor_inner.execute("SELECT * FROM option_pnl WHERE stock = ? AND expiry = ?", (stock, expiry))
    rows = cursor_inner.fetchall()
    cursor_inner.close()
    return rows


def insert_margins_used(stock, expiry,data):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        cursor_inner.execute("INSERT INTO margins_used "
                             "(stock, expiry, non_span_margin_required, order_value, order_margin, "
                             "trade_margin, block_trade_margin, span_margin_required) "
                             "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (stock, expiry, data["non_span_margin_required"],
                                                                 data["order_value"], data["order_margin"],
                                                                 data["trade_margin"], data["block_trade_margin"],
                                                                 data["span_margin_required"]))

    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: option_pnl':
            print("Table not found - margins_used. Creating table")
            create_tables()
            insert_margins_used(stock, expiry, data)
        else:
            print("Error inserting data")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def get_margins_used_time(stock, expiry):
    cursor_inner = get_cursor()
    cursor_inner.execute("SELECT max(timestamp) FROM margins_used WHERE stock = ? AND expiry = ?",
                         (stock, expiry))
    rows = cursor_inner.fetchall()
    for row in rows:
        if row[0] is None:
            return datetime.datetime.utcfromtimestamp(0).time()
        else:
            # print(row[0])
            return datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").time()

def insert_order_status(orders):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        if len(orders) > 0:
            # New orders to insert so truncate the table
            cursor_inner.execute("DELETE FROM order_status")
        for item in orders:
            cursor_inner.execute("INSERT INTO order_status "
                                 "(stock, expiry, ltp, order_price, order_status, order_time, action, quantity, "
                                 "right, strike_price, pending_quantity) "
                                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (item['stock_code'], item['expiry_date'], item['SLTP_price'], item['price'],
                                  item['status'], item['order_datetime'], item['action'], item['quantity'],
                                  item['right'], item['strike_price'], item['pending_quantity']))
    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: order_status':
            print("Table not found - order_status. Creating table")
            create_tables()
            insert_order_status(orders)
        else:
            print("Error inserting data into order_status")
    finally:
        try:
            conn_inner.commit()
        except:
            pass