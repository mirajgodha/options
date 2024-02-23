import pandas as pd
from helper.stockCodes import get_icici_stock_code
import constants.constants_local as c
from datetime import datetime


# ---------------------------------------------------------------------------------------------------------------------
# Open Positions - Option Trading DataFrames
# ---------------------------------------------------------------------------------------------------------------

# Columns for the positions dataframe
# stock - the stock code, using a unified stock code across all borkers as ICICI direct stock code.
# broker_stock_code - broker specific stock code
# average_price - is the price of buy or sell for the contract.
# quantity - is the number of contracts bought or sold. if Sell, then qty will be stored as -ve, else +ve
# strike_price - is the price at which the option contract is exercised.
# expiry_date - is the date on which the option contract expires. DD-MMM-YYYY format (29-Feb-2024)
# right - is the type of option contract (Call or Put).
# action - is the type of action taken (Buy or Sell).
# Columns for the order history dataframe
option_historical_order_book_columns = ["broker", "stock", "broker_stock_code",
                                        "average_price", "quantity", "strike_price",
                                        "expiry_date", "right", "action",
                                        'brokerage_amount','total_taxes','trade_date']


# ---------------------------------------------------------------------------------------------------------------


def get_icici_order_history_df(historical_order_book):
    # Convert the portfolio positions response from icici to standard df used in the project.

    df = pd.DataFrame(columns=option_historical_order_book_columns)

    for item in historical_order_book:
        # print(item)
        if item['exchange_code'] == 'NFO':
            # print(item) Sample ICICI DataFrame [{'book_type': 'Trade-Book', 'trade_date': '21-Feb-2024',
            # 'stock_code': 'AURPHA', 'action': 'Buy', 'quantity': '1100', 'average_cost': '1.4', 'brokerage_amount':
            # '0', 'product_type': 'Options', 'exchange_code': 'NFO', 'order_id': '202402214100003250', 'segment':
            # None, 'settlement_code': None, 'dp_id': None, 'client_id': None, 'ltp': '1.5', 'eatm_withheld_amount':
            # None, 'cash_withheld_amount': None, 'total_taxes': '0', 'order_type': None, 'expiry_date':
            # '29-Feb-2024', 'right': 'Put', 'strike_price': '950'}, {'book_type': 'Trade-Book', 'trade_date':
            # '19-Feb-2024', 'stock_code': 'NATMIN', 'action': 'Sell', 'quantity': '4500', 'average_cost': '5.1',
            # 'brokerage_amount': '10', 'product_type': 'Options', 'exchange_code': 'NFO', 'order_id':
            # '202402194100013745', 'segment': None, 'settlement_code': None, 'dp_id': None, 'client_id': None,
            # 'ltp': '10.7', 'eatm_withheld_amount': None, 'cash_withheld_amount': None, 'total_taxes': '29.73',
            # 'order_type': None, 'expiry_date': '29-Feb-2024', 'right': 'Put', 'strike_price': '245'}, {'book_type':
            # 'Trade-Book', 'trade_date': '19-Feb-2024', 'stock_code': 'RELIND', 'action': 'Sell', 'quantity': '250',
            # 'average_cost': '24.05', 'brokerage_amount': '10', 'product_type': 'Options', 'exchange_code': 'NFO',
            # 'order_id': '202402194100006239', 'segment': None, 'settlement_code': None, 'dp_id': None, 'client_id':
            # None, 'ltp': '35.15', 'eatm_withheld_amount': None, 'cash_withheld_amount': None, 'total_taxes':
            # '9.15', 'order_type': None, 'expiry_date': '29-Feb-2024', 'right': 'Call', 'strike_price': '2980'}]

            qty = int(item['quantity'])
            if item['action'] == 'Sell':
                qty = qty * -1  # When sell lets keep the quantity in -ve
            pnl_data = {
                "broker": c.ICICI_DIRECT_BROKER,
                "stock": item['stock_code'],
                "broker_stock_code": item['stock_code'],
                "average_price": float(item['average_cost']),
                "quantity": qty,
                "strike_price": float(item['strike_price']),
                "expiry_date": item['expiry_date'].upper(),
                "right": item['right'],
                "action": item['action'],
                "brokerage_amount": float(item['brokerage_amount']),
                "total_taxes" : float(item['total_taxes']),
                "trade_date": datetime.strptime(item['trade_date'], '%d-%b-%Y')
            }

            df = pd.concat([df, pd.DataFrame.from_records([pnl_data])], ignore_index=True)

    # print(df)
    return df


def get_nuvama_order_history_df(historical_order_book):
    # Convert the portfolio positions response from nuvama to standard df used in the project.

    df = pd.DataFrame(columns=option_historical_order_book_columns)
    for item in historical_order_book:
        # print(item)
        if '-OPT-' in item['security'] :
            # Sample DataFrame {"status": true, "data": {"totalRecords": 78, "transactionList": [{"accountCode":
            # "60278133", "security": "DLF-OPT-29Feb2024-PE-900-NSE", "transactionDate": "21-Feb-24", "txnType":
            # "NSE", "action": "Sell", "exchangeName": "NSE", "quantity": 1650.0, "transactionPrice": 21.65,
            # "brokerage": 10.0007, "stampDutyCharges": 0.0, "sebiTax": 0.04, "transactionCharge": 17.86, "other": 0,
            # "accountID": 48567889, "tranId": 426543177, "editFlag": 0, "filterFlags": {"editable": false},
            # "priceEditable": false, "splitAllowed": false, "scripIdentifier": 48567889, "cumulativeQuantity":
            # -1650.0, "netCharges": 55.3, "assetType": null, "isin": null, "stax_GST": 5.02, "stt": 22.38,
            # "tstax": 0.0}, {"accountCode": "60278133", "security": "DLF-OPT-29Feb2024-PE-890-NSE",
            # "transactionDate": "21-Feb-24", "txnType": "NSE", "action": "Sell", "exchangeName": "NSE", "quantity":
            # 1650.0, "transactionPrice": 20.5, "brokerage": 10.0007, "stampDutyCharges": 0.0, "sebiTax": 0.03,
            # "transactionCharge": 16.91, "other": 0, "accountID": 48581482, "tranId": 426543176, "editFlag": 0,
            # "filterFlags": {"editable": false}, "priceEditable": false, "splitAllowed": false, "scripIdentifier":
            # 48581482, "cumulativeQuantity": -1650.0, "netCharges": 52.92, "assetType": null, "isin": null,
            # "stax_GST": 4.84, "stt": 21.14, "tstax": 0.0}, {"accountCode": "60278133", "security":
            # "HAVELLS-OPT-25Jan2024-CE-1500-NSE", "transactionDate": "15-Jan-24", "txnType": "NSE",
            # "action": "Sell", "exchangeName": "NSE", "quantity": 500.0, "transactionPrice": 11.6, "brokerage":
            # 10.0, "stampDutyCharges": 0.0, "sebiTax": 0.01, "transactionCharge": 2.9, "other": 0, "accountID":
            # 47691953, "tranId": 422706228, "editFlag": 0, "filterFlags": {"editable": false}, "priceEditable":
            # false, "splitAllowed": false, "scripIdentifier": 47691953, "cumulativeQuantity": -500.0, "netCharges":
            # 18.86, "assetType": null, "isin": null, "stax_GST": 2.32, "stt": 3.63, "tstax": 0.0}]}}

            trdSym = item['security'] #DLF-OPT-29Feb2024-PE-900-NSE
            stock = trdSym.split('-')[0]

            right = 'Put' if trdSym.split('-')[3] == 'PE' else 'Call'
            action = 'Sell' if item['action'].upper() == 'SELL' else 'Buy'
            average_price = float(item['transactionPrice'])

            expiry_date = trdSym.split('-')[2] # get the expiry date in this format - 29Feb2024
            # Parse the date string
            date_obj = datetime.strptime(expiry_date, "%d%b%Y")
            # Format the date object to the desired format
            expiry_date = date_obj.strftime("%d-%b-%Y")

            quantity = int(item['quantity'])
            if action == 'Sell':
                quantity = quantity * -1

            strike_price = float(trdSym.split('-')[4])
            # print(strike_price)

            pnl_data = {
                "broker": c.NUVAMA_BROKER,
                "stock": get_icici_stock_code(stock),
                "broker_stock_code": stock,
                "average_price": average_price,
                "quantity": quantity,
                "strike_price": strike_price,
                "expiry_date": expiry_date.upper(),
                "right": right,
                "action": action,
                "brokerage_amount": float(item['brokerage']),
                "total_taxes": float(item['netCharges']),
                "trade_date" : datetime.strptime(item['transactionDate'], '%d-%b-%y')
            }

            df = pd.concat([df, pd.DataFrame.from_records([pnl_data])], ignore_index=True)

    # print(df)
    return df