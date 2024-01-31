#Some helpers
# https://github.com/Idirect-Tech/Breeze-Python-Examples/blob/main/webinar/how_to_use_websockets.py
from breeze_connect import BreezeConnect

import iciciDirect.helpers  as icici_direct_helper
from datetime import datetime

#Configure the strategy using API Keys and set stoploss/takeprofit level.
#Login : https://api.icicidirect.com/apiuser/home
api_key = ""
api_secret = ""
api_session = ''

#Import the library
from breeze_connect import BreezeConnect

#Create API library object
api = BreezeConnect(api_key=api_key)
api.generate_session(api_secret=api_secret,session_token=api_session)

today_date = datetime.today().date().strftime("%Y-%m-%d")

iso_date_string = datetime.strptime("28/02/2021", "%d/%m/%Y").isoformat()[:10] + 'T05:30:00.000Z'
iso_date_time_string = datetime.strptime("28/02/2021 23:59:59", "%d/%m/%Y %H:%M:%S").isoformat()[:19] + '.000Z'

response = api.get_portfolio_positions()
if response['Status'] == 200:
    response = response['Success']
    # print(response)

icici_direct_helper.get_pnl_target(response)

orders = api.get_order_list('NFO',from_date=today_date,to_date=today_date)
print(orders)

for item in orders['Success']:
    if item['status'] == 'Executed':
        print(f"Executed Order: {item['stock_code']} : {item['action']} :  {item['price']} ")
    if item['status'] == 'Ordered':
        print(f"Pending Execution: {item['stock_code']} : {item['action']} :  {item['price']} ")


