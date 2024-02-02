#Login: https://nuvamawealth.com/api-connect/login?api_key=1hEqmOmIh5_H2A

import configparser
from datetime import datetime
from APIConnect.APIConnect import APIConnect
import json


# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('../secreates/config.ini')

# Access values using sections and keys
api_key = config['NUVAMA']['api_key']
api_secret = config['NUVAMA']['api_secret']
api_session = config['NUVAMA']['api_session']

today_date = datetime.today().date().strftime("%m/%d/%Y")


api_connect = APIConnect(api_key, api_secret, api_session, True, "settings.ini")
response = api_connect.OrderHistory('01/15/2024', '01/31/2024')

print(response)

json_data = json.loads(response)
for order in json_data['eq']['data']['hstOrdBk']:
    print(order)