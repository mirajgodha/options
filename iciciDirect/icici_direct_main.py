# Some helpers
# Configure the strategy using API Keys.
# Login : https://api.icicidirect.com/apiuser/home
# and get the api session key

import configparser
from datetime import datetime, timedelta

from constants import constants_local as constants
from dao.historicalOrderBookDF import get_icici_order_history_df
from dao.openPositionsDF import get_icici_option_open_positions_df
from dao.orderBookDF import get_icici_order_book_df
from helper.colours import Colors
from helper.logger import logger
from optionTrading.trading_helper import persist, get_table_as_df
import sql.sqlite as sqlt
import constants.constants_local as c
from stopit import threading_timeoutable as timeoutable


# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('../secretes/config.ini')

# Access values using sections and keys
api_key = config['ICICI']['api_key']
api_secret = config['ICICI']['api_secret']
api_session = config['ICICI']['api_session']

# Import the library
from breeze_connect import BreezeConnect

# Create API library object
api = BreezeConnect(api_key=api_key)
api.generate_session(api_secret=api_secret, session_token=api_session)

today_date = datetime.today().date().strftime("%Y-%m-%d")


def get_api_session():
    return api


# Get the portfolio positions
@timeoutable()
def get_portfolio_positions():
    portfolio_positions_response = api.get_portfolio_positions()
    if portfolio_positions_response['Status'] == 200:
        portfolio_positions_response = portfolio_positions_response['Success']
        portfolio_positions_df = get_icici_option_open_positions_df(portfolio_positions_response)
        # print(portfolio_positions_df)
        return portfolio_positions_df

@timeoutable()
def get_order_book():
    orders = api.get_order_list('NFO', from_date=today_date, to_date=today_date)
    if orders['Status'] == 200:
        orders = orders['Success']
        # print(orders)
        orders_df = get_icici_order_book_df(orders)
        # print(orders_df)
        return orders_df

@timeoutable()
def get_historical_order_book(from_date, to_date,exchange_code='NFO'):
    where_clause = f"last_updated >= '{datetime.today() - timedelta(hours=8)}'"
    historical_order_book = get_table_as_df(constants.ICICI_HISTORICAL_ORDERS_TABLE_NAME, where_clause)
    if historical_order_book is not None and not historical_order_book.empty and len(historical_order_book) > 0:
        logger.debug("Historical order book for ICICI Direct found in Db, returning it.")
        return historical_order_book

    # Historical order book did not persisted today in Db, so let's fetch from broker.
    logger.debug("Getting historical order book from ICICI Direct for from_date: "
                f"{from_date} and to_date: {to_date}")
    response_historical_order_book = api.get_trade_list(from_date=from_date, to_date=to_date, exchange_code=exchange_code)
    logger.debug(f"Historical order book response from ICICI Direct: {response_historical_order_book}")

    if response_historical_order_book['Status'] == 200:
        response_historical_order_book = response_historical_order_book['Success']

        response_historical_order_book_df = get_icici_order_history_df(response_historical_order_book)

        # Persist it for the day as no need to call the api multiple times in the day to get historical orders.
        response_historical_order_book_df['last_updated'] = datetime.now()
        persist(response_historical_order_book_df,constants.ICICI_HISTORICAL_ORDERS_TABLE_NAME)

        return response_historical_order_book_df
    else:
        if response_historical_order_book['Status'] == 500:
            logger.error(f"{Colors.RED}Internal Server Error while getting portfolio position. "
                  f"Status Code: {response_historical_order_book['Status']} received. {Colors.RESET}")
            logger.error(f"Error received from ICICI broker: {response_historical_order_book}")
        else:
            logger.error(f"{Colors.RED}Portfolio position response: {response_historical_order_book}{Colors.RESET}")
        return None


@timeoutable()
def update_funds():
    if sqlt.get_last_updated_time("icici_funds") < (
            datetime.now() - timedelta(minutes=c.FUNDS_DELAY_TIME)):
        funds_response = api.get_funds()
        if funds_response['Status'] != 200:
            logger.error(f"{Colors.RED}Error while getting funds: {funds_response}{Colors.RESET}")
            return

        margin_response = api.get_margin('nfo')
        if margin_response['Status'] != 200:
            logger.error(f"{Colors.RED}Error while getting margin: {margin_response}{Colors.RESET}")
            return

        if funds_response is not None and margin_response is not None:
            funds_response = funds_response['Success']
            margin_response = margin_response['Success']
            sqlt.insert_icici_funds(funds_response, margin_response)
