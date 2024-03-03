import configparser

from breeze_connect import BreezeConnect


# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('../secretes/config.ini')

# Access values using sections and keys
api_key = config['ICICI']['api_key']
api_secret = config['ICICI']['api_secret']
api_session = config['ICICI']['api_session']
# Initialize SDK


# Import Libraries

from datetime import datetime
import pandas as pd

# Setup my API keys
api = BreezeConnect(api_key=api_key)
api.generate_session(api_secret=api_secret, session_token=api_session)


# *********************************************************************************************************************************************************************

# Callback to receive ticks.
# Event based function

def on_ticks(ticks):
    print(ticks)


# *********************************************************************************************************************************************************************


# Main Function
if __name__ == "__main__":
    print("Starting Execution \n")

    # Switch on Websockets
    api.ws_connect()
    api.on_ticks = on_ticks

    api.subscribe_feeds(exchange_code="NFO",
                        stock_code='NIFTY',
                        product_type="options",
                        expiry_date='27-Apr-2023',
                        strike_price='17500',
                        right='call', interval="1minute")