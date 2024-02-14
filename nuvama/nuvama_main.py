# Login: https://nuvamawealth.com/api-connect/login?api_key=1hEqmOmIh5_H2A

import configparser
from datetime import datetime
from APIConnect.APIConnect import APIConnect
import json

import optionTrading.openPositionsDF as openPositionsDF
import optionTrading.orderBookDF as orderBookDF

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


def get_order_book():
    response = api_connect.OrderBook()
    try:
        order_book = json.loads(response)
        order_book_df = orderBookDF.get_nuvama_option_order_book_df(order_book['eq']['data']['ord'])
        return order_book_df
    except Exception as e:
        print(e)
        return None



def get_portfolio_positions():
    response = api_connect.NetPosition()
    portfolio_positions = json.loads(response)
    portfolio_positions_df = openPositionsDF.get_nuvama_option_open_positions_df(
        portfolio_positions['eq']['data']['pos'])
    return portfolio_positions_df
