#Some helpers
# https://github.com/Idirect-Tech/Breeze-Python-Examples/blob/main/webinar/how_to_use_websockets.py
from breeze_connect import BreezeConnect

import iciciDirect.helpers  as icici_direct_helper
from datetime import datetime
import configparser
import time


# Set the desired wait time in seconds
wait_time = 30
test_run = False

from helper.colours import Colors

#Configure the strategy using API Keys and set stoploss/takeprofit level.
#Login : https://api.icicidirect.com/apiuser/home

# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('../secreates/config.ini')

# Access values using sections and keys
api_key = config['ICICI']['api_key']
api_secret = config['ICICI']['api_secret']
api_session = config['ICICI']['api_session']


#Import the library
from breeze_connect import BreezeConnect

#Create API library object
api = BreezeConnect(api_key=api_key)
api.generate_session(api_secret=api_secret,session_token=api_session)

today_date = datetime.today().date().strftime("%Y-%m-%d")

iso_date_string = datetime.strptime("28/02/2021", "%d/%m/%Y").isoformat()[:10] + 'T05:30:00.000Z'
iso_date_time_string = datetime.strptime("28/02/2021 23:59:59", "%d/%m/%Y %H:%M:%S").isoformat()[:19] + '.000Z'

while icici_direct_helper.is_market_open() | test_run:
    print(f"{Colors.PURPLE}ICICI Direct {datetime.today()}{Colors.WHITE}")
    response = api.get_portfolio_positions()
    if response['Status'] == 200:
        response = response['Success']
        # print(response)

    icici_direct_helper.get_pnl_target(response)

    orders = api.get_order_list('NFO',from_date=today_date,to_date=today_date)
    #print(orders)

    print("\n\n##################################")
    # print(orders)
    print("Order Status: ")
    if orders is not None and orders['Success'] is not None:
        for item in orders['Success']:
            if item['status'] == 'Executed':
                print(f"{Colors.BLUE}Executed Order: {item['stock_code']} : {item['action']} :  {item['price']} ")
            if item['status'] == 'Ordered':
                print(f"{Colors.CYAN}Pending Execution: {item['stock_code']} : {item['action']} :  {item['price']} ")
    else:
        print("No orders found")

    time.sleep(wait_time)