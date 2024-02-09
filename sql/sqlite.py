import datetime
import sqlite3
import traceback

import pandas as pd
from helper.colours import Colors

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

    # Create a table ltp (if it doesn't exist)
    cursor_inner.execute('''
                CREATE TABLE if not exists ltp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock TEXT NOT NULL,
                    expiry TEXT NOT NULL,
                    right TEXT NOT NULL,
                    strike_price float,
                    ltp float,
                    ltt dateTime,
                    best_bid_price float,
                    best_bid_quantity int,
                    best_offer_price float,
                    best_offer_quantity int,
                    open float,
                    high float,
                    low float,
                    previous_close float,
                    ltp_percent_change float,
                    upper_circuit float,
                    lower_circuit float,
                    total_quantity_traded int,
                    spot_price float,
                    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
                )
            ''')

    cursor_inner.execute('''
                CREATE TABLE if not exists mwpl(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock TEXT NOT NULL,
                    price float,
                    price_change_percent float,
                    mwpl_prev float,
                    mwpl_current float,
                   timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
                )
                ''')

    cursor_inner.execute('''
                    CREATE TABLE if not exists contracts_to_be_sq_off(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stock TEXT NOT NULL,
                        price_left float,
                        pnl float,
                        strike_price float,
                        expiry_date TEXT NOT NULL,
                        right TEXT NOT NULL,
                       timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
                    )
                    ''')

    # Commit the changes to the database
    conn.commit()


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


def insert_margins_used(stock, expiry, data):
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
        else:
            print("Error inserting data")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def get_last_updated_time_margins_used(stock, expiry):
    cursor_inner = get_cursor()
    cursor_inner.execute("SELECT max(timestamp) FROM margins_used WHERE stock = ? AND expiry = ?",
                         (stock, expiry))
    rows = cursor_inner.fetchall()
    for row in rows:
        if row[0] is None:
            return datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        else:
            # print(datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
            return datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")


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
                                 (item['stock_code'], item['expiry_date'], item['ltp'], item['price'],
                                  item['status'],
                                  datetime.datetime.strptime(item['order_datetime'], "%d-%b-%Y %H:%M:%S"),
                                  item['action'], item['quantity'],
                                  item['right'], item['strike_price'], item['pending_quantity']))
    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: order_status':
            print("Table not found - order_status. Creating table")
        else:
            print(f"Error inserting data into order_status {e}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def insert_ltp(ltp_response):
    # inserts the ltp response into the ltp table
    # print(ltp_response)

    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        for item in ltp_response:
            cursor_inner.execute("INSERT INTO ltp (stock, expiry, right, strike_price, ltp, ltt, best_bid_price, "
                                 "best_bid_quantity, best_offer_price, best_offer_quantity, open, high, low, "
                                 "previous_close, ltp_percent_change, upper_circuit, lower_circuit, "
                                 "total_quantity_traded, spot_price) "
                                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (item['stock_code'], item['expiry_date'], item['right'], item['strike_price'],
                                  item['ltp'], item['ltt'], item['best_bid_price'], item['best_bid_quantity'],
                                  item['best_offer_price'], item['best_offer_quantity'], item['open'], item['high'],
                                  item['low'], item['previous_close'], item['ltp_percent_change'],
                                  item['upper_circuit'], item['lower_circuit'], item['total_quantity_traded'],
                                  item['spot_price']))

    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: order_status':
            print("Table not found - order_status. Creating table")
        else:
            print(f"Error inserting data into order_status {e}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def insert_ltp_df(ltp_df: pd.DataFrame):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    right = ''
    try:
        for index, item in ltp_df.iterrows():
            if item['right'].upper() == 'CE' or item['right'].upper() == 'CALL':
                right = 'C'
            else:
                if item['right'].upper() == 'PE' or item['right'].upper() == 'PUT':
                    right = 'P'

            cursor_inner.execute("INSERT INTO ltp (stock, expiry, right, strike_price, ltp) "
                                 "VALUES (?, ?, ?, ?, ?)",
                                 (item['stock'], item['expiry_date'], right, item['strike_price'],
                                  item['ltp']))

    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: ltp':
            print(f"{Colors.RED} Table not found - order_status. Creating table{Colors.RESET}")
        else:
            print(f"{Colors.RED}Error inserting data into ltp {e}{Colors.RESET}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def get_ltp(stock_code, expiry_date, strike_price, right):
    conn_inner = get_conn()
    cursor_inner = get_cursor()

    # as rights are stored as 'P' and 'C' in this table converting them to appropriate values
    if right.upper() == 'CE' or right.upper() == 'CALL':
        right = 'C'
    else:
        if right.upper() == 'PE' or right.upper() == 'PUT':
            right = 'P'

    try:
        cursor_inner.execute("SELECT ltp FROM ltp  WHERE timestamp = "
                             "(SELECT MAX(timestamp) FROM ltp WHERE "
                             "stock = ? AND expiry = ? AND strike_price = ? AND right = ? ) "
                             "and stock = ? AND expiry = ? AND strike_price = ? AND right = ?",
                             (stock_code, expiry_date, strike_price, right, stock_code, expiry_date, strike_price,
                              right))
        rows = cursor_inner.fetchall()

        # print(f'Got ltp for {stock_code} {expiry_date} {strike_price} {right} : {rows[0][0]]}')
        return rows[0][0]

    except Exception as e:
        print(f"Error getting ltp data from SQL DB for {stock_code} {expiry_date} {strike_price} {right}")
        traceback.print_exc()
        return None


def insert_mwpl(mwpl_list):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        for item in mwpl_list:
            cursor_inner.execute("INSERT INTO mwpl (stock, price, price_change_percent,mwpl_prev, mwpl_current) "
                                 "VALUES (?, ?, ?, ?, ?)",
                                 (item[0], item[1], item[2], item[4], item[3]))
    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: mwpl':
            print("Table not found - mwpl")
        else:
            print(f"Error inserting data into order_status {e}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def get_last_insert_time_mwpl():
    cursor_inner = get_cursor()
    cursor_inner.execute("SELECT max(timestamp) FROM mwpl")
    rows = cursor_inner.fetchall()
    for row in rows:
        if row[0] is None:
            return datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        else:
            # print(datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
            return datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")


def insert_contracts_to_be_sq_off(contracts: pd.DataFrame):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        if len(contracts) > 0:
            # New contracts calculation is done, so delete the old ones.
            cursor_inner.execute("DELETE FROM contracts_to_be_sq_off")

        for index, item in contracts.iterrows():
            cursor_inner.execute("INSERT INTO contracts_to_be_sq_off "
                                 "(stock, price_left, pnl, strike_price, expiry_date, right) "
                                 "VALUES (?, ?, ?, ?, ?, ?)",
                                 (item['stock'], item["price_left"], item["pnl"], item["strike_price"],
                                  item["expiry_date"], item["right"]))
    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: contracts_to_be_sq_off':
            print("Table not found - contracts_to_be_sq_off")
        else:
            print(f"Error inserting data into order_status {e}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


# Create the tables when the module is imported, and if the tables are not created
create_tables()
