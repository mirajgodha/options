import datetime
import sqlite3
import traceback

import pandas as pd
from helper.colours import Colors
import constants.constants_local as constants
from helper.logger import logger

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
    conn_inner = get_conn()

    sql_file = '../sql/schema.sql'

    # Read the SQL file and split statements by semicolon
    with open(sql_file, 'r') as file:
        sql_statements = file.read().split(';')

    # Execute each SQL statement one by one
    for sql_statement in sql_statements:
        try:
            cursor_inner.execute(sql_statement)
            conn_inner.commit()
            logger.debug("Successfully executed:", sql_statement.strip())
        except sqlite3.Error as e:
            logger.error("Error executing statement:", sql_statement.strip())
            logger.error("Error:", e)
        finally:
            conn_inner.commit()



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


def insert_order_status(orders_df):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        if len(orders_df) > 0:
            # New orders to insert so truncate the table
            cursor_inner.execute("DELETE FROM order_status")

        # convert the in a pandas DataFrame datetime64[ns] to python datetime
        orders_df['order_time'] = pd.to_datetime(orders_df['order_time'])
        orders_df['order_time'] = orders_df['order_time'].dt.strftime('%Y-%m-%d %H:%M:%S')

        for index, item in orders_df.iterrows():
            cursor_inner.execute("INSERT INTO order_status "
                                 "(broker, stock, expiry, ltp, order_price, order_status, order_time, action, quantity,"
                                 "right, strike_price, pending_quantity) "
                                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (item['broker'], item['stock'], item['expiry_date'], item['ltp'], item['order_price'],
                                  item['order_status'],
                                  item['order_time'],
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


def insert_option_ltp(ltp_response):
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


def get_ltp_option(stock_code, expiry_date, strike_price, right):
    conn_inner = get_conn()
    cursor_inner = get_cursor()

    # as rights are stored as 'P' and 'C' in this table converting them to appropriate values
    if right.upper() == 'CE' or right.upper() == 'CALL':
        right = 'C'
    else:
        if right.upper() == 'PE' or right.upper() == 'PUT':
            right = 'P'

    try:
        cursor_inner.execute("SELECT ltp FROM ltp  WHERE id = "
                             "(SELECT MAX(id) FROM ltp WHERE "
                             "stock = ? AND upper(expiry) = ? AND strike_price = ? AND right = ? ) "
                             "and stock = ? AND upper(expiry) = ? AND strike_price = ? AND right = ?",
                             (stock_code, expiry_date.upper(), strike_price, right, stock_code, expiry_date.upper(),
                              strike_price,
                              right))
        rows = cursor_inner.fetchall()

        # print(f'Got ltp for {stock_code} {expiry_date} {strike_price} {right} : {rows[0][0]]}')
        return rows[0][0]

    except IndexError as e:
        print(f"LTP does not exist in DB for {stock_code} {expiry_date} {strike_price} {right}")
        return None
    except Exception as e:
        print(f"Error getting ltp data from SQL DB for {stock_code} {expiry_date} {strike_price} {right}")
        traceback.print_exc()
        return None


def get_ltp_stock(stock):
    conn_inner = get_conn()
    cursor_inner = get_cursor()

    try:
        cursor_inner.execute("SELECT ltp FROM ltp_stock  WHERE id = "
                             "(SELECT MAX(id) FROM ltp_stock WHERE "
                             "stock = ? ) "
                             "and stock = ? ",
                             (stock, stock))
        rows = cursor_inner.fetchall()
        return rows[0][0]

    except Exception as e:
        print(f"{Colors.RED}Error getting ltp_stock data from SQL DB for {stock}{Colors.RESET}")
        # traceback.print_exc()
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


def insert_contracts_to_be_sq_off(contracts: pd.DataFrame):
    conn_inner = get_conn()
    try:
        contracts.to_sql('contracts_to_be_sq_off', get_conn(), if_exists='replace', index=False)
    except Exception as e:
        print(f"Error inserting data into contracts_to_be_sq_off {e}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def insert_icici_funds(funds_response, margin_response):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        cursor_inner.execute("INSERT INTO icici_funds "
                             "(total_bank_balance,allocated_equity, "
                             "allocated_fno, block_by_trade_equity, "
                             "block_by_trade_fno, block_by_trade_balance,"
                             "unallocated_balance,limit_used,limit_available,"
                             "limit_total) "
                             "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (funds_response['total_bank_balance'], funds_response['allocated_equity'],
                              funds_response['allocated_fno'], funds_response['block_by_trade_equity'],
                              funds_response['block_by_trade_fno'], funds_response['block_by_trade_balance'],
                              funds_response['unallocated_balance'], margin_response['limit_list'][0]['amount'],
                              margin_response['cash_limit'],
                              (float(margin_response['limit_list'][0]['amount']) * -1) + float(
                                  margin_response['cash_limit'])
                              ))
    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: icici_funds':
            logger.error("Table not found - icici_funds")
        else:
            logger.error(f"Error inserting data into icici_funds table {e}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def nuvama_funds(nuvama_funds):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        cursor_inner.execute("INSERT INTO nuvama_funds "
                             "(adhoc_margin,day_open_balance,funds_added,margin_available,"
                             "stock_collateral_value,"
                             "blocked_released_for_delivery,funds_withdrawn,"
                             "margin_utilized,premium_paid_received,"
                             "realized_pnl,unrealized_mark_to_market,"
                             "mtom_margin,nvl,nvl_percent, dpcharges, dpdues, fnopenality, ist) "
                             "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (nuvama_funds['mrgAvl']['adMrg'], nuvama_funds['mrgAvl']['dayOpenBal'],
                              nuvama_funds['mrgAvl']['fndAdd'], nuvama_funds['mrgAvl']['mrgAvl'],
                              nuvama_funds['mrgAvl']['stkColVal'],
                              nuvama_funds['mrgUtd']['blkRelDlvry'], nuvama_funds['mrgUtd']['fndWthdrwn'],
                              nuvama_funds['mrgUtd']['mrgUtd'], nuvama_funds['mrgUtd']['prmPdRcd'],
                              nuvama_funds['mrgUtd']['rlPnl'], nuvama_funds['mrgUtd']['unRlMtm'],
                              nuvama_funds['mtmMg'], nuvama_funds['nvl'], nuvama_funds['nvlPer'],
                              nuvama_funds.get('unPstdChrgs', {}).get('ntUnPstdChrg', {}).get('dpcharges', 0),
                              nuvama_funds.get('unPstdChrgs', {}).get('ntUnPstdChrg', {}).get('dpdues', 0),
                              nuvama_funds.get('unPstdChrgs', {}).get('ntUnPstdChrg', {}).get('fnopenality', 0),
                              nuvama_funds.get('unPstdChrgs', {}).get('ntUnPstdChrg', {}).get('ist', 0)
                              ))
    except sqlite3.OperationalError as e:
        if e.args[0] == 'no such table: nuvama_funds':
            logger.error("Table not found - nuvama_funds")
        else:
            logger.error(f"Error inserting data into nuvama_funds table {e}")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error inserting data into nuvama_funds table {e}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass


def get_last_updated_time(table_name, where_clause=None):
    cursor_inner = get_cursor()
    sql = f"SELECT max(timestamp) FROM {table_name}"
    if where_clause is not None:
        sql += f" WHERE {where_clause}"
    cursor_inner.execute(sql)
    rows = cursor_inner.fetchall()
    for row in rows:
        if row[0] is None:
            return datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        else:
            try:
                last_updated = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                last_updated = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")

            return last_updated


# Create the tables when the module is imported, and if the tables are not created
create_tables()


def insert_os_lastupdated(table_name, status):
    conn_inner = get_conn()
    cursor_inner = get_cursor()
    try:
        cursor_inner.execute(f"INSERT INTO {table_name} (status) VALUES (?)", (status,))
    except sqlite3.OperationalError as e:
        if e.args[0] == f'no such table: {table_name}':
            print(f"{Colors.RED}Table not found - {table_name}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Error inserting data into {table_name} {e}{Colors.RESET}")
    finally:
        try:
            conn_inner.commit()
        except:
            pass
