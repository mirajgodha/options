# Generate ISO8601 Date/DateTime String
import datetime
import pandas as pd

import iciciDirect.icici_direct_main
import sql.sqlite
from helper import optionsMWPL, fuzzMatch
import constants.constants_local as c

from helper.colours import Colors
import sql.sqlite as sqlt
from tabulate import tabulate
from profitnloss import Call, Put, Strategy


def is_market_open():
    # Check if the market is open on weekdays
    today = datetime.datetime.now().date()
    if today.weekday() < 5:  # Monday to Friday (0 to 4 are the weekdays)
        current_time = datetime.datetime.now().time()
        market_open_time = datetime.time(9, 00)  # Assuming market opens at 9:00 AM
        market_close_time = datetime.time(15, 30)  # Assuming market closes at 3:30 PM
        return market_open_time <= current_time <= market_close_time
    else:
        return False


def calculate_pnl(portfolio_positions_df):
    # This method calculates the pnl for all open positions at stock level

    pnl = 0
    df = pd.DataFrame(columns=["stock", "pnl", "expiry_date"])
    if portfolio_positions_df is not None:
        df = portfolio_positions_df.groupby(['broker', 'stock', 'expiry_date'])['pnl'].sum()
        df = df.reset_index()
        df = df.rename(columns={'pnl': 'pnl'})
        df = df.sort_values(['pnl'])

    else:  # If no positions are open
        pnl = None

    print("Pnl Currently:\n")
    total_pnl = df['pnl'].sum()
    if total_pnl > 0:
        print(f"{Colors.BLUE}Total:: {Colors.GREEN}{total_pnl}{Colors.WHITE}")
    else:
        print(f"{Colors.BLUE}Total:: {Colors.RED}{total_pnl}{Colors.WHITE}")
    print("\n")

    for index, data in df.iterrows():
        if data['pnl'] > 0:
            print(f"{data['stock']}: {Colors.GREEN}{data['pnl']}{Colors.WHITE}")
        if data['pnl'] < 0:
            print(f"{data['stock']}: {Colors.RED}{data['pnl']}{Colors.WHITE}")

    return df


def get_thresholds():
    # Read the file where we can mention the threasholds for profit or loss for each stock

    # Specify the path to your Excel file
    excel_file_path = '../data/profit_loss.xlsx'
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(excel_file_path)

    return df


# Function to check if profit or loss threshold is reached

def profit_or_loss_threshold_reached(df):
    # Check if the profit or loss threshold is reached for each stock based on the excel def check_pnl_threshold(df):

    # Code to calculate PnL
    print("\nCHECKING P&L Thresholds...")
    print("\n\n#######################################")

    for index, data in df.iterrows():
        if float(data['pnl']) > float(data['profit_target']):
            print(f"{data['stock']}: Profit Target Reached Profit: {data['pnl']}, Target: {data['profit_target']}")
        if float(data['pnl']) < float(data['stop_loss']):
            print(f"{data['stock']}: Stop Loss Reached. Loss:{data['pnl']}, Target: {data['stop_loss']}")

    print("\n\n#######################################")


def contract_value(portfolio_positions_df, threshold):
    # Code to calculate contract value and if it's less than threshold
    # it will make sense to sq of the contract

    # print("\nCHECKING CONTRACT VALUE...")
    df_to_sq_off_contracts = pd.DataFrame(
        columns=["stock", "price_left", "pnl", "strike_price", "expiry_date", "right"])

    for index, item in portfolio_positions_df.iterrows():
        ltp = float(item['ltp'])
        cost = float(item['average_price'])
        qty = int(item['quantity'])
        if item['action'] == 'Sell':
            value_left = ltp * qty * -1
            if value_left < threshold:
                df_to_sq_off_contracts = \
                    pd.concat([df_to_sq_off_contracts, pd.DataFrame.from_records(
                        [{'stock': item['stock'],
                          'price_left': value_left,
                          'pnl': round((cost - ltp) * qty, 2),
                          'strike_price': item['strike_price'],
                          'expiry_date': item['expiry_date'],
                          'right': item['right']}])]
                              , ignore_index=True)
    print("\n\n#######################################")
    print("Contracts to sq off:")
    print(f'{Colors.GREEN}{df_to_sq_off_contracts}{Colors.WHITE}')

    sqlt.insert_contracts_to_be_sq_off(df_to_sq_off_contracts)

    return df_to_sq_off_contracts


def get_pnl_target(portfolio_positions_df):
    # Code to calculate PnL

    df_threshold = get_thresholds()

    df_pnl = calculate_pnl(portfolio_positions_df)
    sql.sqlite.insert_pnl(df_pnl)

    df = pd.merge(df_threshold, df_pnl, on='stock')

    # print("Pnl Targets:")
    # print(df)
    # profit_or_loss_threshold_reached(df)

    # get  the contracts to be sq_offed
    contract_value(portfolio_positions_df, c.CONTRACT_MIN_VALUE_TO_BE_SQ_OFFED)

    print("\n\n#######################################")

    return df


def calculate_margin_used(open_positions_df, api):
    # Calculate Margin Used for all open option positions
    print("\n\n#######################################")

    print("Calculating Margin Used: ")

    if open_positions_df is not None and len(open_positions_df) > 0:

        unique_stock_codes = set(open_positions_df['stock'].values.flatten())
        unique_expiry_dates = set(open_positions_df['expiry_date'].values.flatten())

        for expiry_date in unique_expiry_dates:

            for stock in unique_stock_codes:
                if sqlt.get_last_updated_time_margins_used(stock, expiry_date) > (
                        datetime.datetime.now() - datetime.timedelta(minutes=c.MARGIN_DELAY_TIME)):
                    # print(f"Not calculating margin for {stock} as its was calculated less than 10 minutes ago")
                    continue

                # print(f"Calculating margin for {stock}, {expiry_date}")
                df = pd.DataFrame(
                    columns=["strike_price", "quantity", "right", "product", "action", "price", "expiry_date",
                             "stock_code", "cover_order_flow", "fresh_order_type", "cover_limit_rate",
                             "cover_sltp_price", "fresh_limit_rate", "open_quantity"])

                for index, item in open_positions_df.iterrows():
                    if item['stock'] == stock and item['expiry_date'] == expiry_date:
                        # print(item)
                        quantity = int(item['quantity'])

                        # As ICICI supports positive quantity only for all orders types, making the quantity to +Ve
                        if item['action'] == 'Sell':
                            quantity = quantity * -1

                        margin_data = {
                            "strike_price": item['strike_price'],
                            "quantity": quantity,
                            "right": item['right'].lower(),
                            "product": 'options',
                            "action": item['action'].lower(),
                            "price": item['strike_price'],
                            "expiry_date": item['expiry_date'],
                            "stock_code": item['stock']
                            # "cover_order_flow": "N",
                            # "fresh_order_type": "N",
                            # "cover_limit_rate": "0",
                            # "cover_sltp_price": "0",
                            # "fresh_limit_rate": "0",
                            # "open_quantity": "0"
                        }

                        df = pd.concat([df, pd.DataFrame.from_records([margin_data])], ignore_index=True)
                # print(f"Margin Data: {stock} , {expiry_date}")
                print(tabulate(df, headers='keys', tablefmt='psql'))

                margin_response = api.margin_calculator(df.to_dict(orient='records'), "NFO")
                print(f"Margin Response: {margin_response} ")

                if margin_response['Status'] == 200:
                    sqlt.insert_margins_used(stock, expiry_date, margin_response['Success'])
                else:
                    print(
                        f"{Colors.RED}Error calculating margin for {stock} , {expiry_date} - {margin_response}{Colors.RESET}")


def get_mwpl(portfolio_positions_df):
    if sqlt.get_last_updated_time("mwpl") > (
            datetime.datetime.now() - datetime.timedelta(minutes=c.MWPL_DELAY_TIME)):
        # Updated MWPL less than a hour ago, so not updating now.
        return

    print("Getting MWPL")

    mwpl_list = []

    # Get the data of mwpl
    mwpl_df = optionsMWPL.optionsMWPL()
    if portfolio_positions_df is not None and len(portfolio_positions_df) > 0:

        unique_stock_codes_portfolio = set(portfolio_positions_df['stock'].values.flatten())
        unique_stock_codes_mwpl = mwpl_df.drop_duplicates(subset=['Symbol', 'Price', 'Chg', 'Cur.MWPL', 'Pre.MWPL'])[
            'Symbol'].tolist()

        matched_stock_codes = \
            fuzzMatch.get_stock_code_pairs_using_fuzzy_match(unique_stock_codes_portfolio, unique_stock_codes_mwpl)

        similar_code = ''
        for stock in unique_stock_codes_portfolio:
            for x in matched_stock_codes:
                if x[0] == stock:
                    similar_code = x[1]
                    break

            for index, row in mwpl_df.iterrows():
                if row['Symbol'].upper() == similar_code:
                    mwpl_list.append((row['Symbol'], row['Price'], row['Chg'], row['Cur.MWPL'], row['Pre.MWPL']))
                    print(row['Symbol'], row['Price'], row['Chg'], row['Cur.MWPL'], row['Pre.MWPL'])
                    break

    sqlt.insert_mwpl(mwpl_list)


def insert_ltp_for_positions(portfolio_positions_response):
    # Insert the LTP for the open positions so that we can plot the LTP chart
    df = pd.DataFrame(columns=["stock_code", "strike_price", "expiry_date", "right", "ltp"])

    for item in portfolio_positions_response:
        if item['segment'] == 'fno':
            # Sample DataFrame
            ltp_data = {
                'stock': item['stock_code'],
                'pnl': float(item['ltp']),
                'expiry_date': item['expiry_date'],
                'right': item['right'],
                'strike_price': item['strike_price'],
                'ltp': float(item['ltp'])
            }

            df = pd.concat([df, pd.DataFrame.from_records([ltp_data])], ignore_index=True)

    sqlt.insert_ltp_df(df)


def get_option_ltp(api, stock_code, expiry_date, strike_price, right):
    # Get LTP for all open option positions
    try:
        response = api.get_quotes(stock_code=stock_code, exchange_code='NFO', product_type='options',
                                  expiry_date=expiry_date, strike_price=strike_price, right=right)
        # print(f"LTP: {response}")
        sqlt.insert_ltp(response['Success'])
    except Exception as e:
        print(f"{Colors.RED}Exception while getting LTP for {stock_code}, {expiry_date}, "
              f"{strike_price}, {right}: {e} {Colors.RESET}")
        ltp = sqlt.get_ltp_option(stock_code, expiry_date, strike_price, right)
        if ltp:
            return ltp
        return 0

    if response['Status'] != 200:
        print(f"{Colors.RED}Error while getting LTP for {stock_code}, {expiry_date}, "
              f"{strike_price}, {right}: {response}{Colors.RESET}")
        return 0

    return response['Success'][0]['ltp']


def order_list(orders_df):
    # Print them in different colour based on execution status.
    # print(orders)
    print("Order Status: ")
    for index, item in orders_df.iterrows():
        if item['order_status'] == c.ORDER_STATUS_COMPLETE:
            print(f"{Colors.BLUE}Executed Order: {item['stock']} : {item['action']} : Price: {item['order_price']}  : "
                  f"LTP: {item['ltp']} : Qty : {item['quantity']}")
        if item['order_status'] == c.ORDER_STATUS_OPEN:
            print(
                f"{Colors.CYAN}Pending Execution: {item['stock']} : {item['action']} : Price: {item['order_price']} : "
                f"LTP: {item['ltp']}: Qty : {item['quantity']}")

        # insert the order status in to order status table
        sqlt.insert_order_status(orders_df)


def get_ltp_stock(portfolio_positions_df):
    if portfolio_positions_df is not None and len(portfolio_positions_df) > 0:
        unique_stock_codes_portfolio = set(portfolio_positions_df['stock'].values.flatten())
    else:
        print(f"{Colors.GREEN}No open portfolio positions found{Colors.RESET}")
        return

    for stock in unique_stock_codes_portfolio:
        # print(f"Getting LTP for {stock}")
        api = iciciDirect.icici_direct_main.get_api_session()

        # {'Success': [{'exchange_code': 'NSE', 'product_type': '', 'stock_code': 'MOTSUM', 'expiry_date': None,
        # 'right': None, 'strike_price': 0.0, 'ltp': 114.05, 'ltt': '14-Feb-2024 15:29:58', 'best_bid_price': 0.0,
        # 'best_bid_quantity': '0', 'best_offer_price': 0.0, 'best_offer_quantity': '0', 'open': 114.65,
        # 'high': 114.75, 'low': 112.2, 'previous_close': 115.45, 'ltp_percent_change': 1.21264616717194,
        # 'upper_circuit': 126.95, 'lower_circuit': 103.9, 'total_quantity_traded': '15946868', 'spot_price': None},
        # {'exchange_code': 'BSE', 'product_type': '', 'stock_code': 'MOTSUM', 'expiry_date': None, 'right': None,
        # 'strike_price': 0.0, 'ltp': 114.3, 'ltt': '14-Feb-2024 15:30:38', 'best_bid_price': 114.2,
        # 'best_bid_quantity': '100', 'best_offer_price': 114.3, 'best_offer_quantity': '869', 'open': 114.25,
        # 'high': 114.65, 'low': 112.2, 'previous_close': 115.55, 'ltp_percent_change': 1.08178277801817,
        # 'upper_circuit': 127.1, 'lower_circuit': 104.0, 'total_quantity_traded': '1053974', 'spot_price': None}],
        # 'Status': 200, 'Error': None}

        ltp_df = pd.DataFrame(
            columns=["stock", "ltp", 'ltt', 'best_bid_price',
                     'best_bid_quantity', 'best_offer_price', 'best_offer_quantity', 'open',
                     'high', 'low', 'previous_close', 'ltp_percent_change',
                     'upper_circuit', 'lower_circuit', 'total_quantity_traded'])
        try:
            ltp = api.get_quotes(stock_code=stock, exchange_code='NSE', product_type='cash')
            for item in ltp['Success']:
                # data for each ltp response so that can crated a consolidated df
                if ['exchange_code'] == 'BSE':  # No need to store the BSE traded price
                    continue
                # print(ltp['Success'])
                ltp_data = {
                    "stock": item['stock_code'],
                    "ltp": float(item['ltp']),
                    'ltt': datetime.datetime.strptime(item['ltt'], "%d-%b-%Y %H:%M:%S"),
                    'best_bid_price': float(item['best_bid_price']),
                    'best_bid_quantity': int(item['best_bid_quantity']),
                    'best_offer_price': float(item['best_offer_price']),
                    'best_offer_quantity': int(item['best_offer_quantity']),
                    'open': float(item['open']),
                    'high': float(item['high']),
                    'low': float(item['low']),
                    'previous_close': float(item['previous_close']),
                    'ltp_percent_change': float(item['ltp_percent_change']),
                    'upper_circuit': float(item['upper_circuit']),
                    'lower_circuit': float(item['lower_circuit']),
                    'total_quantity_traded': int(item['total_quantity_traded'])
                }
                ltp_df = pd.concat([ltp_df, pd.DataFrame.from_records([ltp_data])], ignore_index=True)

            # convert the in a pandas DataFrame datetime64[ns] to python datetime
            ltp_df['ltt'] = pd.to_datetime(ltp_df['ltt'])
            ltp_df['ltt'] = ltp_df['ltt'].dt.strftime('%Y-%m-%d %H:%M:%S')

        except Exception as e:
            print(f"{Colors.RED}Exception while getting LTP for {stock}: {e}{Colors.RESET}")
        finally:
            ltp_df.to_sql(name="ltp_stock", con=sqlt.get_conn(), if_exists='append',
                          index=False)


def get_strategy_breakeven(portfolio_positions_df):
    # Calculate the strategies breakeven points and can also plot them.
    if portfolio_positions_df is not None and len(portfolio_positions_df) > 0:
        unique_stock_codes_portfolio = set(portfolio_positions_df['stock'].values.flatten())
    else:
        print(f"{Colors.GREEN}No open portfolio positions found{Colors.RESET}")
        return

    break_even_df = pd.DataFrame(
        columns=["stock", "lower_side", "higher_side","lower_break_even_per", "higher_break_even_per" ])

    try:
        for stock in unique_stock_codes_portfolio:
            # Filter 1: Get all the open positions for the stock
            open_positions_df = portfolio_positions_df[portfolio_positions_df['stock'] == stock]
            # For the given open position create strategy object
            s = Strategy()
            for index, item in open_positions_df.iterrows():


                # Create strategy for each right and action type
                if item['right'] == 'Call' and item['action'] == 'Sell':
                    s.sell(Call(item['strike_price'], item['average_price'], item['quantity'] * -1))
                if item['right'] == 'Call' and item['action'] == 'Buy':
                    s.buy(Call(item['strike_price'], item['average_price'], item['quantity']))
                if item['right'] == 'Put' and item['action'] == 'Sell':
                    s.sell(Put(item['strike_price'], item['average_price'], item['quantity'] * -1))
                if item['right'] == 'Put' and item['action'] == 'Buy':
                    s.buy(Put(item['strike_price'], item['average_price'], item['quantity']))
            print(f"{Colors.PURPLE}Breakeven for {stock}, {s.break_evens()}{Colors.RESET}")
            # print("max loss: %f, max gain: %f" % (s.max_loss(), s.max_gain()))
            # print("strikes and payoffs: " + str(list(zip(s.strikes(), s.payoffs(s.strikes())))))
            break_even_array = s.break_evens()
            if break_even_array:

                if len(break_even_array) > 1:
                    higher_side = break_even_array[1]
                else:
                    higher_side = None
                lower_break_even_per = 0
                higher_break_even_per = 0

                ltp = sqlt.get_ltp_stock(stock)

                if ltp is not None:
                    lower_break_even_per = (ltp - break_even_array[0]) / ltp

                if higher_side is not None and ltp is not None:
                    higher_break_even_per = (higher_side - ltp) / ltp

                break_even_data = {
                    "stock": stock,
                    "lower_side": break_even_array[0],
                    "higher_side": higher_side,
                    "lower_break_even_per": lower_break_even_per,
                    "higher_break_even_per": higher_break_even_per
                }
                break_even_df = pd.concat([break_even_df, pd.DataFrame.from_records([break_even_data])],
                                          ignore_index=True)

            # s.plot()
        print(tabulate(break_even_df))

    except Exception as e:
        print(f"{Colors.RED}Exception while getting Breakeven for {stock}: {e}{Colors.RESET}")

    finally:
        try:
            conn = sqlt.get_conn()
            break_even_df.to_sql(name="open_positions", con=conn, if_exists='replace',
                                 index=False)
            conn.commit()
        except:
            pass
