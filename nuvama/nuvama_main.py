# Login: https://nuvamawealth.com/api-connect/login?api_key=1hEqmOmIh5_H2A

import configparser
import traceback
from datetime import datetime

import pandas as pd
from APIConnect.APIConnect import APIConnect
from constants.segment_type import SegmentTypeEnum
import json

import dao.openPositionsDF as openPositionsDF
from dao.orderBookDF import get_nuvama_option_order_book_df
import dao.historicalOrderBookDF as historicalOrderBookDF

# Read the configuration file

# Create a ConfigParser object

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
        json_data = api_connect.GetAllTransactionHistory(segment=SegmentTypeEnum.EQUITY, fromDate='2024-01-15', toDate='2024-02-21')
        print(json_data)
        nuvama_order_history = json.loads(json_data)
        nuvama_order_history = nuvama_order_history['data']['transactionList']
        nuvama_order_history_df = historicalOrderBookDF.get_nuvama_order_history_df(nuvama_order_history)
        # order_book_df = get_order_book()
        # nuvama_order_history_df = pd.concat([order_book_df, nuvama_order_history])
        from tabulate import tabulate
        print("From Nuavam Order History including todays order book")
        print(tabulate(nuvama_order_history_df))
        return nuvama_order_history_df
    except Exception as e:
        traceback.print_exc()
        return None




# Get the portfolio positions


def get_portfolio_positions():
    response = api_connect.NetPosition()
    portfolio_positions = json.loads(response)
    portfolio_positions_df = openPositionsDF.get_nuvama_option_open_positions_df(
        portfolio_positions['eq']['data']['pos'])
    return portfolio_positions_df
