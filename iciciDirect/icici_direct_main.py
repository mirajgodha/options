# Some helpers
# https://github.com/Idirect-Tech/Breeze-Python-Examples/blob/main/webinar/how_to_use_websockets.py
import hashlib

from breeze_connect import BreezeConnect

import iciciDirect.helpers as iciciDirectHelper
from datetime import datetime
import configparser
import time
import pandas as pd

from helper import constants
from helper.colours import Colors

# Configure the strategy using API Keys and set stoploss/takeprofit level.
# Login : https://api.icicidirect.com/apiuser/home

# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('../secreates/config.ini')

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


# Main function to be executed in the main thread
def main():
    # Your main code goes here
    while iciciDirectHelper.is_market_open() | constants.TEST_RUN:
        print(f"{Colors.PURPLE}ICICI Direct {datetime.today()}{Colors.WHITE}")
        response = api.get_portfolio_positions()
        if response['Status'] == 200:
            response = response['Success']
            # print(response)

        # Call the icici direct functions
        iciciDirectHelper.get_pnl_target(response)
        iciciDirectHelper.calculate_margin_used(response, api)
        iciciDirectHelper.order_list(api, from_date=today_date, to_date=today_date)

        time.sleep(constants.REFRESH_TIME_SECONDS)


if __name__ == "__main__":
    main()
