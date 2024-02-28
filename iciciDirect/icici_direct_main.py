# Some helpers
# Configure the strategy using API Keys.
# Login : https://api.icicidirect.com/apiuser/home
# and get the api session key

import traceback

import pandas as pd

import iciciDirect.icici_helper as iciciDirectHelper
from datetime import datetime
import configparser
import time
from dao.openPositionsDF import get_icici_option_open_positions_df
from dao.orderBookDF import get_icici_order_book_df
from dao.historicalOrderBookDF import get_icici_order_history_df
from optionTrading.trading_helper import is_market_open,persist,get_table_as_df

from constants import constants_local as constants
from helper.colours import Colors

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

def get_portfolio_positions():
    portfolio_positions_response = api.get_portfolio_positions()
    if portfolio_positions_response['Status'] == 200:
        portfolio_positions_response = portfolio_positions_response['Success']
        portfolio_positions_df = get_icici_option_open_positions_df(portfolio_positions_response)
        # print(portfolio_positions_df)
        return portfolio_positions_df


def get_order_book():
    orders = api.get_order_list('NFO', from_date=today_date, to_date=today_date)
    if orders['Status'] == 200:
        orders = orders['Success']
        # print(orders)
        orders_df = get_icici_order_book_df(orders)
        # print(orders_df)
        return orders_df


def get_historical_order_book(from_date, to_date):
    where_clause = f"last_updated >= '{datetime.today()}'"
    historical_order_book = get_table_as_df(constants.ICICI_HISTORICAL_ORDERS_TABLE_NAME, where_clause)
    if historical_order_book is not None and not historical_order_book.empty:
        return historical_order_book

    # Historical order book did not persisted today in Db, so lets fetch from broker.
    response_historical_order_book = api.get_trade_list(from_date, to_date, exchange_code='NFO')

    if response_historical_order_book['Status'] == 200:
        response_historical_order_book = response_historical_order_book['Success']


        response_historical_order_book_df = get_icici_order_history_df(response_historical_order_book)

        # Persist it for the day as no need to call the api multiple times in the day to get historical orders.
        response_historical_order_book_df['last_updated'] = datetime.now()
        persist(response_historical_order_book_df,constants.ICICI_HISTORICAL_ORDERS_TABLE_NAME)

        return response_historical_order_book_df
    else:
        if response_historical_order_book['Status'] == 500:
            print(f"{Colors.RED}Internal Server Error while getting portfolio position. "
                  f"Status Code: {response_historical_order_book['Status']} received. {Colors.RESET}")
            print(f"Error received from ICICI broker: {response_historical_order_book}")
        else:
            print(f"{Colors.RED}Portfolio position response: {response_historical_order_book}{Colors.RESET}")
        return None


# Main function to be executed in the main thread
def main():
    # Your main code goes here
    try:
        while is_market_open() | constants.TEST_RUN:
            print(f"{Colors.PURPLE}ICICI Direct {datetime.today()}{Colors.WHITE}")
            portfolio_positions_response = api.get_portfolio_positions()
            if portfolio_positions_response['Status'] == 200:
                portfolio_positions_response = portfolio_positions_response['Success']
                # print(response)

            # Call the icici direct functions

            # Calculates the real time PnL for the option open positions in the account
            iciciDirectHelper.get_pnl_target(portfolio_positions_response)

            # Update the LTP for the open positions so that we can plot the LTP chart
            iciciDirectHelper.insert_ltp_for_positions(portfolio_positions_response)

            # Calculate margin used for all open option positions and update in margin table
            iciciDirectHelper.calculate_margin_used(portfolio_positions_response, api)

            # Get the order status real time, also gets and update the ltp for traders and update the ltp in ltp table
            iciciDirectHelper.order_list(api, from_date=today_date, to_date=today_date)

            # Update the Market wide open positions in mwpl table, for the stocks options in the portfolio
            iciciDirectHelper.get_mwpl(portfolio_positions_response=portfolio_positions_response)

            # Update the funds and limits available in a demat account hourly
            iciciDirectHelper.update_funds(api)

            time.sleep(constants.REFRESH_TIME_SECONDS)
    except Exception as e:
        print(f"{Colors.RED}Error in main{Colors.WHITE}")
        traceback.print_exc()
    finally:
        if is_market_open() | constants.TEST_RUN:
            time.sleep(constants.REFRESH_TIME_SECONDS)
            main()
        else:
            if not is_market_open():
                print(f"{Colors.PURPLE}Market Closed{Colors.WHITE}")


# Main function to be executed in the main thread


if __name__ == "__main__":
    # Call the main function to start the program
    print(f"{Colors.PURPLE}Starting ICICI Direct{Colors.WHITE}")
    iciciDirectHelper.order_list(api, from_date=today_date, to_date=today_date)
    # main()
