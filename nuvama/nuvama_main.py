# Login: https://nuvamawealth.com/api-connect/login?api_key=1hEqmOmIh5_H2A

import configparser
import traceback
from datetime import datetime, timedelta

from dao import portfolioHoldingsDF
from helper.logger import logger
from helper.colours import Colors

import pandas as pd
from APIConnect.APIConnect import APIConnect
from constants.segment_type import SegmentTypeEnum
import json

import dao.openPositionsDF as openPositionsDF
from dao.orderBookDF import get_nuvama_option_order_book_df
import dao.historicalOrderBookDF as historicalOrderBookDF

from optionTrading.trading_helper import persist, get_table_as_df
import constants.constants_local as constants
import sql.sqlite as sqlt
import constants.constants_local as c
from stopit import threading_timeoutable as timeoutable


# Read the configuration file

# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('../secretes/config.ini')

# Access values using sections and keys
api_key = config['NUVAMA']['api_key']
api_secret = config['NUVAMA']['api_secret']
api_session = config['NUVAMA']['api_session']

today_date = datetime.today().date().strftime("%m/%d/%Y")

api_connect = APIConnect(api_key, api_secret, api_session, True, "../nuvama/settings.ini")


def get_api_connect():
    return api_connect


# Get the order book

def get_order_book():
    response = api_connect.OrderBook()
    try:
        order_book = json.loads(response)
        order_book_df = get_nuvama_option_order_book_df(order_book['eq']['data']['ord'])
        return order_book_df
    except Exception as e:
        print(e)
        return None


def get_historical_order_book(from_date, to_date):
    try:
        where_clause = f"last_updated >= '{datetime.today() - timedelta(hours=8)}'"
        historical_order_book = get_table_as_df(constants.NUVAMA_HISTORICAL_ORDERS_TABLE_NAME, where_clause)
        if historical_order_book is not None and len(historical_order_book) > 0:
            logger.debug("Getting historical order book from database for Nuvama so using it")
            return historical_order_book

        logger.debug("Getting historical order book from nuvama as no historical order book found in the database")

        json_data = api_connect.GetAllTransactionHistory(segment=SegmentTypeEnum.EQUITY, fromDate=from_date,
                                                         toDate=to_date)
        # print(json_data)
        nuvama_order_history = json.loads(json_data)
        nuvama_order_history = nuvama_order_history['data']['transactionList']
        nuvama_order_history_df = historicalOrderBookDF.get_nuvama_order_history_df(nuvama_order_history)
        # order_book_df = get_order_book()
        # nuvama_order_history_df = pd.concat([order_book_df, nuvama_order_history])
        # from tabulate import tabulate
        # print("From Nuavam Order History including todays order book")
        # print(tabulate(nuvama_order_history_df))

        # Persist it for the day as no need to call the api multiple times in the day to get historical orders.
        nuvama_order_history_df['last_updated'] = datetime.now()
        persist(nuvama_order_history_df, constants.NUVAMA_HISTORICAL_ORDERS_TABLE_NAME)
        return nuvama_order_history_df
    except Exception as e:
        traceback.print_exc()
        return None


# Get the portfolio positions


def get_portfolio_positions():
    try:
        response = api_connect.NetPosition()
        logger.debug("Nuavala Portfolio Positions Response: " + response)
        portfolio_positions = json.loads(response)
        portfolio_positions_df = openPositionsDF.get_nuvama_option_open_positions_df(
            portfolio_positions['eq']['data']['pos'])
        return portfolio_positions_df
    except Exception as e:
        logger.error(f"{Colors.RED}Nuvama login error, please check the api key and secret{Colors.RESET}")
        logger.error(f"{Colors.RED}{e}{Colors.RESET}")
        return None


def update_funds():
    try:
        # Update Nuvama funds
        if sqlt.get_last_updated_time("nuvama_funds") < (
                datetime.now() - timedelta(minutes=c.FUNDS_DELAY_TIME)):
            response = api_connect.Limits()
            logger.debug("Funds Response: " + response)
            funds = json.loads(response)

            if funds is not None:
                funds = funds['eq']['data']
                sqlt.nuvama_funds(funds)
    except Exception as e:
        print(e)

@timeoutable()
def get_portfolio_holdings():
    if sqlt.get_last_updated_time(c.NUVAMA_PORTFOLIO_HONDINGS_VIEW_NAME) < (
            datetime.now() - timedelta(minutes=c.PORTFOLIO_DELAY_TIME)):
        try:
            response = api_connect.Holdings()
            logger.debug("Nuavala Portfolio Holdings Response: " + response)
            portfolio_holdings = json.loads(response)
            portfolio_holdings = portfolio_holdings['eq']['data']['rmsHdg']
            portfolio_holdings_df = portfolioHoldingsDF.get_nuvama_portfolio_holdings_df(portfolio_holdings)
            return portfolio_holdings_df
        except Exception as e:
            logger.error(e)
            return None
    else:
        return None
