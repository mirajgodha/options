# Generate ISO8601 Date/DateTime String
import datetime
import traceback
import pandas as pd

from dao.Option import OptionType, TranxType
from helper.logger import logger

import iciciDirect.icici_direct_main as icici_direct_main
import sql.sqlite
from helper import optionsMWPL, fuzzMatch
import constants.constants_local as c
from datetime import datetime, time, timedelta

from helper.colours import Colors
import sql.sqlite as sqlt
from tabulate import tabulate
from profitnloss import Call, Put, Strategy

from helper.stockCodes import get_nse_stock_code
import nsepython as nse
from util.nsepythonUtil import get_option_price, nse_optionchain_scrapper
from messagning.slack_messaging import send_message


def is_market_open():
    # Check if the market is open on weekdays
    today = datetime.now().date()
    if today.weekday() < 5:  # Monday to Friday (0 to 4 are the weekdays)
        current_time = datetime.now().time()
        market_open_time = time(9, 00)  # Assuming market opens at 9:00 AM
        market_close_time = time(15, 30)  # Assuming market closes at 3:30 PM
        return market_open_time <= current_time <= market_close_time
    else:
        return False


def calculate_pnl(portfolio_positions_df):
    # This method calculates the pnl for all open positions at stock level

    pnl = 0
    df = pd.DataFrame(columns=["stock", "pnl", "expiry_date"])
    if portfolio_positions_df is not None:
        df = portfolio_positions_df.groupby(['stock', 'expiry_date'])['pnl'].sum()
        df = df.reset_index()
        df = df.rename(columns={'pnl': 'pnl'})
        df = df.sort_values(['pnl'])

    else:  # If no positions are open
        pnl = None

    logger.info("Pnl Currently:\n")
    total_pnl = df['pnl'].sum()
    if total_pnl > 0:
        logger.info(f"{Colors.BLUE}Total:: {Colors.GREEN}{total_pnl}{Colors.WHITE}")
    else:
        logger.info(f"{Colors.BLUE}Total:: {Colors.RED}{total_pnl}{Colors.WHITE}")
    logger.info("\n")

    for index, data in df.iterrows():
        if data['pnl'] > 0:
            logger.info(f"{data['stock']}: {Colors.GREEN}{data['pnl']}{Colors.WHITE}")
        if data['pnl'] < 0:
            logger.info(f"{data['stock']}: {Colors.RED}{data['pnl']}{Colors.WHITE}")

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

    for index, data in df.iterrows():
        if float(data['pnl']) > float(data['profit_target']):
            logger.info(
                f"{data['stock']}: Profit Target Reached Profit: {data['pnl']}, Target: {data['profit_target']}")
        if float(data['pnl']) < float(data['stop_loss']):
            logger.info(f"{data['stock']}: Stop Loss Reached. Loss:{data['pnl']}, Target: {data['stop_loss']}")


def contract_value(portfolio_positions_df, threshold):
    # Code to calculate contract value and if it's less than threshold
    # it will make sense to sq of the contract

    logger.debug("CHECKING CONTRACT VALUE...")
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
                          'pnl': round((cost - ltp) * qty * -1, 0),
                          'strike_price': item['strike_price'],
                          'expiry_date': item['expiry_date'],
                          'right': item['right']}])]
                              , ignore_index=True)
    logger.info("\n\n#######################################")
    logger.info("Contracts to sq off:")
    logger.info(f'{Colors.GREEN}{df_to_sq_off_contracts}{Colors.WHITE}')

    sqlt.insert_contracts_to_be_sq_off(df_to_sq_off_contracts)

    return df_to_sq_off_contracts


def get_pnl_target(portfolio_positions_df):
    # Code to calculate PnL

    df_threshold = get_thresholds()

    df_pnl = calculate_pnl(portfolio_positions_df)
    sql.sqlite.insert_pnl(df_pnl)

    df = pd.merge(df_threshold, df_pnl, on='stock')

    logger.debug("Pnl Targets:")
    logger.debug(df)
    # profit_or_loss_threshold_reached(df)

    # get  the contracts to be sq_offed
    contract_value(portfolio_positions_df, c.CONTRACT_MIN_VALUE_TO_BE_SQ_OFFED)

    return df


def calculate_margin_used(open_positions_df, api):
    # Calculate Margin Used for all open option positions

    if open_positions_df is not None and len(open_positions_df) > 0:

        unique_stock_codes = set(open_positions_df['stock'].values.flatten())
        unique_expiry_dates = set(open_positions_df['expiry_date'].values.flatten())

        for expiry_date in unique_expiry_dates:

            for stock in unique_stock_codes:
                if sqlt.get_last_updated_time_margins_used(stock, expiry_date) > (
                        datetime.now() - timedelta(minutes=c.MARGIN_DELAY_TIME)):
                    # print(f"Not calculating margin for {stock} as its was calculated less than 10 minutes ago")
                    continue

                logger.debug(f"Calculating margin for {stock}, {expiry_date}")
                df = pd.DataFrame(
                    columns=["strike_price", "quantity", "right", "product", "action", "price", "expiry_date",
                             "stock_code", "cover_order_flow", "fresh_order_type", "cover_limit_rate",
                             "cover_sltp_price", "fresh_limit_rate", "open_quantity"])

                for index, item in open_positions_df.iterrows():
                    if item['action'] == 'NA':
                        # Pending order, not yet executed.
                        continue

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
                logger.debug(f"Margin Data: {stock} , {expiry_date}")
                logger.debug(tabulate(df, headers='keys', tablefmt='psql'))

                if df.empty or len(df) == 0:  # All positions are sq offed
                    continue

                margin_response = api.margin_calculator(df.to_dict(orient='records'), "NFO")
                logger.debug(f"Margin Response: {margin_response} ")

                if margin_response['Status'] == 200:
                    sqlt.insert_margins_used(stock, expiry_date, margin_response['Success'])
                else:
                    logger.error(
                        f"{Colors.RED}Error calculating margin for {stock} , {expiry_date} - {margin_response}{Colors.RESET}")


def get_and_update_mwpl(portfolio_positions_df):
    '''
    Get the stocks market wide position limit
    In case the mwpl is going above 85%, it will be highlighed on the metabase charts,
    setting to hightlight is there in metabase itself.

    In case if the limit is increased beyound 85% it will send the slack notification too on mwpl channel.
    Parameters
    ----------
    portfolio_positions_df: stokcs for which it has to check the mwpl

    Returns
    -------

    '''

    if sqlt.get_last_updated_time(c.MWLP_TABLE_NAME) > (
            datetime.now() - timedelta(minutes=c.MWPL_DELAY_TIME)):
        # Updated MWPL less than a hour ago, so not updating now.
        return

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
                    logger.debug(
                        f"MWPL: {row['Symbol']} , {row['Price']} , {row['Chg']} , {row['Cur.MWPL']} , {row['Pre.MWPL']} ")
                    break


    for item in mwpl_list:
        # Assuming mwpl_list contains tuples in the format (Symbol, Price, Chg, Cur.MWPL, Pre.MWPL)
        symbol, price, chg, cur_mwpl, pre_mwpl = item

        if float(cur_mwpl.replace("%", "")) > 80:
            logger.debug(f"Symbols where Cur.MWPL is greater than 85 is {symbol} : {cur_mwpl}")
            send_message(f"Stock might go to ban {symbol}, Current: {cur_mwpl}, Prev: {pre_mwpl}, Change: {chg}", c.MWPL_CHANNEL)


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


def get_option_ltp(stock_code, expiry_date, strike_price, right):
    if c.GET_LTP_FROM_ICICI:
        # Get LTP for all open option positions
        # Get LTP from ICICI
        # calling icici multiple times is costly, so this is not used and using nsepy method
        api = icici_direct_main.get_api_session()
        try:
            response = api.get_quotes(stock_code=stock_code, exchange_code='NFO', product_type='options',
                                      expiry_date=expiry_date, strike_price=strike_price, right=right)
            logger.debug(f"LTP: {response}")
            sqlt.insert_option_ltp(response['Success'])
        except Exception as e:
            logger.error(f"{Colors.RED}Exception while getting LTP from ICICI for {stock_code}, {expiry_date}, "
                         f"{strike_price}, {right}: {e} {Colors.RESET}")
            ltp = sqlt.get_ltp_option(stock_code, expiry_date, strike_price, right)
            logger.info(
                "Getting LTP from DB for stock: " + stock_code + ", expiry_date: " + expiry_date + ", strike_price: " +
                strike_price + ", right: " + right + ", returning that.")
            if ltp:
                return ltp
            return 0

        if response['Status'] != 200:
            logger.error(f"{Colors.RED}Error while getting LTP for {stock_code}, {expiry_date}, "
                         f"{strike_price}, {right}: {response} - Status {response['Status']}{Colors.RESET}")
            return 0

        return response['Success'][0]['ltp']
    if c.GET_LTP_FROM_NSE:
        try:
            stock_code_nse = get_nse_stock_code(stock_code)
            if right.upper() == 'CALL':
                option_type = OptionType.CALL
            else:
                option_type = 'PUT'

            option_chain_json = nse_optionchain_scrapper(stock_code_nse)

            ltp, iv = get_option_price(option_chain_json, strike_price, option_type, TranxType.ANY, expiry_date,
                                       need_iv=False)
            if ltp is not None or ltp != 0:
                sqlt.get_conn().execute("INSERT INTO ltp (stock, expiry, right, strike_price, ltp) "
                                        "VALUES (?, ?, ?, ?, ?)",
                                        (stock_code, expiry_date, right, strike_price,
                                         ltp))
            return ltp
        except Exception as e:
            logger.error(f"{Colors.RED}Exception while getting LTP from NSE for {stock_code}, {expiry_date}, "
                         f"{str(strike_price)}, {right}: {e} {Colors.RESET}")
            ltp = sqlt.get_ltp_option(stock_code, expiry_date, strike_price, right)
            logger.debug(
                f"Getting LTP from DB for stock: {stock_code}, expiry_date: {str(expiry_date)}, "
                f"strike_price: {str(strike_price)} ,right: {right} , returning that.")
            if ltp:
                return ltp
            return 0


def order_list(orders_df):
    # Print them in different colour based on execution status.
    logger.debug("Orders: ")
    logger.debug(tabulate(orders_df))
    logger.info(f"{Colors.BOLD}{Colors.CYAN}Order Status: {Colors.RESET}")
    for index, item in orders_df.iterrows():
        if item['order_status'] == c.ORDER_STATUS_COMPLETE:
            logger.info(
                f"{Colors.BLUE}Executed Order: {item['stock']} : {item['action']} : Price: {item['order_price']}  : "
                f"LTP: {item['ltp']} : Qty : {item['quantity']}{Colors.RESET}")
        if item['order_status'] == c.ORDER_STATUS_OPEN:
            logger.info(
                f"{Colors.CYAN}Pending Execution: {item['stock']} : {item['action']} : Price: {item['order_price']} : "
                f"LTP: {item['ltp']}: Qty : {item['quantity']}{Colors.RESET}")

        # insert the order status in to order status table
        sqlt.insert_order_status(orders_df)


def get_and_persist_ltp_stock(portfolio_positions_df):
    if portfolio_positions_df is not None and len(portfolio_positions_df) > 0:
        unique_stock_codes_portfolio = set(portfolio_positions_df['stock'].values.flatten())
    else:
        logger.info(f"{Colors.GREEN}No open portfolio positions found{Colors.RESET}")
        return

    ltp_df = pd.DataFrame(
        columns=["stock", "ltp", 'ltt', 'best_bid_price',
                 'best_bid_quantity', 'best_offer_price', 'best_offer_quantity', 'open',
                 'high', 'low', 'previous_close', 'ltp_percent_change',
                 'upper_circuit', 'lower_circuit', 'total_quantity_traded'])

    try:
        for stock in unique_stock_codes_portfolio:
            logger.debug(f"Getting LTP for {stock}")
            if c.GET_LTP_FROM_ICICI:
                # Not getting from ICICI due to call limit
                api = icici_direct_main.get_api_session()

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

                ltp = api.get_quotes(stock_code=stock, exchange_code='NSE', product_type='cash')
                for item in ltp['Success']:
                    # data for each ltp response so that can crated a consolidated df
                    if ['exchange_code'] == 'BSE':  # No need to store the BSE traded price
                        continue
                    logger.debug(ltp['Success'])
                    ltp_data = {
                        "stock": item['stock_code'],
                        "ltp": float(item['ltp']),
                        'ltt': datetime.strptime(item['ltt'], "%d-%b-%Y %H:%M:%S"),
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

            if c.GET_LTP_FROM_NSE:
                try:
                    nse_stock = get_nse_stock_code(stock)
                    logger.debug(f"Getting ltp for NSE stock: {nse_stock}, Icici stock: {stock} from NSE....")
                    ltp = nse.nsetools_get_quote(nse_stock)

                    if ltp is not None:
                        ltp_data = {
                            "stock": stock,
                            "ltp": ltp['lastPrice'],
                            # 'ltt': datetime.strptime(item['ltt'], "%d-%b-%Y %H:%M:%S"),
                            # 'best_bid_price': float(item['best_bid_price']),
                            # 'best_bid_quantity': int(item['best_bid_quantity']),
                            # 'best_offer_price': float(item['best_offer_price']),
                            # 'best_offer_quantity': int(item['best_offer_quantity']),
                            'open': ltp['open'],
                            'high': ltp['dayHigh'],
                            'low': ltp['dayLow'],
                            'previous_close': ltp['previousClose'],
                            'ltp_percent_change': ltp['pChange'],
                            # 'upper_circuit': ltp['upperCP'],
                            # 'lower_circuit': ltp['lowerCP']
                            'total_quantity_traded': ltp['totalTradedVolume']
                        }
                        ltp_df = pd.concat([ltp_df, pd.DataFrame.from_records([ltp_data])], ignore_index=True)
                except Exception as e:
                    # This will help to persist the ltp which we are able to get from NSE
                    logger.error(f"{Colors.RED}Exception while getting LTP for {stock}: {e}{Colors.RESET}")
                    traceback.print_exc()
    except Exception as e:
        logger.error(f"{Colors.RED}Exception while getting LTP for {stock}: {e}{Colors.RESET}")
        traceback.print_exc()
    finally:
        ltp_df.to_sql(name="ltp_stock", con=sqlt.get_conn(), if_exists='append',
                      index=False)


def get_strategy_breakeven(portfolio_positions_df):
    # Calculate the strategies breakeven points and can also plot them.
    if portfolio_positions_df is not None and len(portfolio_positions_df) > 0:
        unique_stock_codes_portfolio = set(portfolio_positions_df['stock'].values.flatten())
    else:
        logger.info(f"{Colors.GREEN}No open portfolio positions found{Colors.RESET}")
        return

    break_even_df = pd.DataFrame(
        columns=["stock", "lower_side", "higher_side", "lower_break_even_per", "higher_break_even_per",
                 "payoff_at_ltp"])

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

            logger.debug(f"{Colors.PURPLE}Breakeven for {stock}, {s.break_evens()}{Colors.RESET}")
            logger.debug("max loss: %f, max gain: %f" % (s.max_loss(), s.max_gain()))
            logger.debug("strikes and payoffs: " + str(list(zip(s.strikes(), s.payoffs(s.strikes())))))

            break_even_array = s.break_evens()

            lower_side = None
            higher_side = None
            ltp = sqlt.get_ltp_stock(stock)
            lower_break_even_per = 0.0
            higher_break_even_per = 0.0

            if break_even_array:
                if len(break_even_array) == 1:
                    if ltp is not None:
                        if ltp > break_even_array[0]:
                            lower_side = break_even_array[0]
                        else:
                            higher_side = break_even_array[0]
                    else:
                        lower_side = break_even_array[0]
                elif len(break_even_array) > 1:
                    lower_side = break_even_array[0]
                    higher_side = break_even_array[1]

            if ltp is not None and lower_side is not None:
                lower_break_even_per = (ltp - break_even_array[0]) / ltp

            if higher_side is not None and ltp is not None:
                higher_break_even_per = (higher_side - ltp) / ltp

            payoff_at_ltp = s.payoff(ltp)

            break_even_data = {
                "stock": stock,
                "lower_side": lower_side,
                "higher_side": higher_side,
                "lower_break_even_per": lower_break_even_per,
                "higher_break_even_per": higher_break_even_per,
                "payoff_at_ltp": payoff_at_ltp
            }
            break_even_df = pd.concat([break_even_df, pd.DataFrame.from_records([break_even_data])],
                                      ignore_index=True)

            # s.plot()
        logger.debug(tabulate(break_even_df))

    except Exception as e:
        logger.error(f"{Colors.RED}Exception while getting Breakeven for {stock}: {e}{Colors.RESET}")

    finally:
        try:
            conn = sqlt.get_conn()
            break_even_df.to_sql(name="open_positions", con=conn, if_exists='replace',
                                 index=False)
            conn.commit()
        except:
            pass


def persist(df, table_name, if_exists='replace'):
    # if_exists: replace, append
    try:
        conn = sqlt.get_conn()
        df.to_sql(name=table_name, con=conn, if_exists=if_exists,
                                      index=False)
        conn.commit()
    except:
        pass


def get_table_as_df(table_name, where_clause=None):
    conn = sqlt.get_conn()
    sql = f"select * from {table_name}"
    if where_clause is not None:
        sql = f"{sql} where {where_clause}"
    logger.debug(f"Going to execute sql: {sql}")
    df = pd.read_sql(sql, conn)
    return df


def get_closed_pnl(df_order_history):
    logger.debug(tabulate(df_order_history, headers='keys', tablefmt='psql'))

    for index, row in df_order_history.iterrows():
        if row['action'] == 'Sell':
            row['quantity'] = -1 * float(row['quantity'])

    df_order_history['quantity'] = df_order_history['quantity'].astype(float)
    df_order_history['strike_price'] = df_order_history['strike_price'].astype(float)

    # amount paid or received for the given contract
    df_order_history['amount'] = df_order_history['average_price'].astype(float) * \
                                 df_order_history['quantity'].astype(float) * -1 - \
                                 df_order_history['brokerage_amount'].astype(float) - \
                                 df_order_history['total_taxes'].astype(float)

    df_order_history['amount'] = round(df_order_history['amount'], 2)

    # Create a hash map sorted by trade date and keep inserting recorsds into it
    # keys of the hash map will be stock, expiry_date, right, strike_price
    # and for each key, we will have a list of records
    df_order_history['trade_date'] = pd.to_datetime(df_order_history['trade_date'])
    df_order_history = df_order_history.sort_values(by='trade_date', ascending=True)
    open_positions_dict = {}
    stock_pnl_booked_dict = {}

    for index, row in df_order_history.iterrows():
        # if row['stock'] != 'BHAPET' or row['expiry_date'] != '29-FEB-2024':
        #     continue

        # print(f"Data Row --  Right: {row['right']}, "
        #       f"Strike Price: {row['strike_price']}, Quantity: {row['quantity']} , Amount: {row['amount'] } , Action: {row['action']}, Price: {row['average_price']}")

        key = (row['stock'], row['expiry_date'], row['right'], row['strike_price'])

        if key not in open_positions_dict:
            # New contract opened
            open_positions_dict[key] = row
        else:
            current_position = open_positions_dict[key]
            if current_position['quantity'] + row['quantity'] == 0:
                # contract sqred off, add its profit in stock_pnl_dict
                # print(f"Profit realized: {current_position['amount'] + row['amount']}")
                if (row['stock'], row['expiry_date']) in stock_pnl_booked_dict:
                    stock_pnl_booked_dict[(row['stock'], row['expiry_date'])] += current_position['amount'] + row[
                        'amount']
                else:
                    stock_pnl_booked_dict[(row['stock'], row['expiry_date'])] = current_position['amount'] + row[
                        'amount']
                # remove the key from closed_pnl_dict
                del open_positions_dict[key]
            elif (current_position['quantity'] < 0 and row['quantity'] < 0) or \
                    (current_position['quantity'] > 0 and row['quantity'] > 0):
                # Both are long or both are short
                current_position['quantity'] = current_position['quantity'] + row['quantity']
                current_position['amount'] = current_position['amount'] + row['amount']
                open_positions_dict[key] = current_position
            elif (current_position['quantity'] < 0 and row['quantity'] > 0) or \
                    (current_position['quantity'] > 0 and row['quantity'] < 0):
                # partial sqzed off
                left_quantity = current_position['quantity'] + row['quantity']
                current_price = current_position['amount'] / abs(current_position['quantity'])
                row_price = row['amount'] / abs(row['quantity'])
                min_quantity = min(abs(current_position['quantity']), abs(row['quantity']))
                # Need to handle two situations:
                # If current holding quantity is less than the new order,the from short
                # we are moving to long or vice a versa. Else if current quantity is more than
                # new order than there is a partial sq off in the position.
                if min_quantity == abs(current_position['quantity']):
                    pnl_booked = (current_price + row_price) * min_quantity
                    amount_left = row_price * abs(left_quantity)
                else:
                    pnl_booked = (current_price + row_price) * min_quantity
                    amount_left = current_price * abs(left_quantity)

                logger.debug(f"Min quantity: {min_quantity}, Current price: {current_price}, Row price: {row_price}, "
                             f"Pnl booked: {pnl_booked}, Amount left: {amount_left}, Left quantity: {left_quantity}, "
                             f"Current quantity: {current_position['quantity']}, Row quantity: {row['quantity']}")

                # contract partial sqred off, add its profit in stock_pnl_dict
                if (row['stock'], row['expiry_date']) in stock_pnl_booked_dict:
                    stock_pnl_booked_dict[(row['stock'], row['expiry_date'])] += pnl_booked
                else:
                    stock_pnl_booked_dict[(row['stock'], row['expiry_date'])] = pnl_booked
                logger.debug(f"Profit realized: {pnl_booked}")

                # Update the current position
                current_position['quantity'] = left_quantity
                current_position['amount'] = amount_left
                open_positions_dict[key] = current_position

    # print("Final closed pnl dict .........")
    stock_pnl_booked_dict = {key: round(value, 0) for key, value in stock_pnl_booked_dict.items()}

    # print(stock_pnl_booked_dict)
    # Initialize an empty list to store data
    data_list = []

    # Iterate over the dictionary items
    for key, value in stock_pnl_booked_dict.items():
        # Create a dictionary with keys as column names and values as data
        row_data = {'stock': key[0], 'expiry_date': key[1], 'pnl_booked': value}
        # Append the row data to the list
        data_list.append(row_data)

    # Create a DataFrame from the list
    stock_pnl_booked_dict_df = pd.DataFrame(data_list)
    # print(stock_pnl_booked_dict_df)

    stock_pnl_booked_dict_df.to_sql('options_pnl_booked', sqlt.get_conn(), if_exists='replace')
    return stock_pnl_booked_dict_df


def persist_portfolio_positions_df(portfolio_positions_df):
    # duplicate the df to a new df
    portfolio_positions_df_copy = portfolio_positions_df.copy()

    try:

        # Replace column name ltp to option_ltp
        portfolio_positions_df_copy.rename(columns={'ltp': 'option_ltp'}, inplace=True)

        # Rename the column Average price to trade price
        portfolio_positions_df_copy.rename(columns={'average_price': 'order_price'}, inplace=True)

        portfolio_positions_df_copy['stock_ltp'] = 0
        portfolio_positions_df_copy['decay_left'] = 0
        portfolio_positions_df_copy['in_the_money'] = False

        # Update the ltp in the dataframe
        for index, row in portfolio_positions_df_copy.iterrows():
            ltp = sqlt.get_ltp_stock(row['stock'])
            if ltp is None:
                ltp = 0
            logger.debug("Got the ltp of stock {0} as {1}  for index {2}".format(row['stock'], ltp, index))
            # Update the ltp in the dataframe
            portfolio_positions_df_copy.at[index, 'stock_ltp'] = ltp

        logger.debug("Going to print the portfolio positions dataframe")
        logger.debug(tabulate(portfolio_positions_df_copy, headers='keys', tablefmt='psql'))

        # Update the decay left in the dataframe
        for index, row in portfolio_positions_df_copy.iterrows():
            # Figure out the total decay left in the option price.
            if row['right'].upper() == 'CALL':
                if row['strike_price'] >= row['stock_ltp']:
                    portfolio_positions_df_copy.at[index,'decay_left'] = row['option_ltp']
                else:
                    portfolio_positions_df_copy.at[index,'decay_left'] = row['option_ltp'] - (row['stock_ltp'] - row['strike_price'])
                    portfolio_positions_df_copy.at[index,'in_the_money'] = True

            elif row['right'].upper() == 'PUT':
                if row['strike_price'] <= row['stock_ltp']:
                    portfolio_positions_df_copy.at[index,'decay_left'] = row['option_ltp']
                else:
                    portfolio_positions_df_copy.at[index,'decay_left'] = row['option_ltp'] - (row['strike_price'] - row['stock_ltp'])
                    portfolio_positions_df_copy.at[index, 'in_the_money'] = True

        logger.debug("Going to persist the portfolio positions dataframe")
        logger.debug(tabulate(portfolio_positions_df_copy, headers='keys', tablefmt='psql'))

        persist(portfolio_positions_df_copy,c.PROTFOLIO_POSITIONS_TABLE_NAME)
    except Exception as e:
        logger.error(f"Error in persisting portfolio positions dataframe.. {e}")
