import pandas as pd
from helper.stockCodes import get_icici_stock_code
import constants.constants_local as c

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
# ltp - is the last traded price of the option contract.
# pnl - is the profit or loss made on the option contract.
# action - is the type of action taken (Buy or Sell).
# Columns for the positions dataframe
option_open_positions_columns = ["broker", "stock", "broker_stock_code", "ltp", "average_price", "quantity", "strike_price",
                                 "expiry_date", "right", "pnl", "action"]


# ---------------------------------------------------------------------------------------------------------------


def get_icici_option_open_positions_df(portfolio_positions_response):
    # Convert the portfolio positions response from icici to standard df used in the project.

    df = pd.DataFrame(columns=option_open_positions_columns)

    for item in portfolio_positions_response:
        # print(item)
        if item['segment'] == 'fno':
            # print(item)
            # Sample ICICI DataFrame
            # {'segment': 'fno', 'product_type': 'Options', 'exchange_code': 'NFO',
            # 'stock_code': 'TATPOW', 'expiry_date': '29-Feb-2024', 'strike_price': '370',
            # 'right': 'Put', 'action': 'Sell', 'quantity': '3375', 'average_price': '8.2',
            # 'settlement_id': None, 'margin_amount': None, 'ltp': '16.75', 'price': '0.04',
            # 'stock_index_indicator': 'Stock', 'cover_quantity': '0', 'stoploss_trigger': '0',
            # 'stoploss': None, 'take_profit': None, 'available_margin': None, 'squareoff_mode': None,
            # 'mtf_sell_quantity': None, 'mtf_net_amount_payable': None, 'mtf_expiry_date': None,
            # 'order_id': '', 'cover_order_flow': None, 'cover_order_executed_quantity': None,
            # 'pledge_status': None, 'pnl': None, 'underlying': 'TATPOW', 'order_segment_code': None}
            ltp = float(item['ltp'])
            cost = float(item['average_price'])
            qty = int(item['quantity'])
            # As ICICI do not send the pnl calculated, calculating it for the contract
            pnl = 0
            if item['action'] == 'Sell':
                pnl = round((cost - ltp) * qty, 2)
            if item['action'] == 'Buy':
                pnl = round((ltp - cost) * qty, 2)
            if item['action'] == 'Sell':
                qty = qty * -1  # When sell lets keep the quantity in -ve
            pnl_data = {
                "broker": c.ICICI_DIRECT_BROKER,
                "stock": item['stock_code'],
                "broker_stock_code": item['stock_code'],
                "ltp": float(item['ltp']),
                "average_price": float(item['average_price']),
                "quantity": qty,
                "strike_price": float(item['strike_price']),
                "expiry_date": item['expiry_date'].upper(),
                "right": item['right'],
                "pnl": pnl,
                "action": item['action']
            }

            df = pd.concat([df, pd.DataFrame.from_records([pnl_data])], ignore_index=True)

    # print(df)
    return df


def get_nuvama_option_open_positions_df(portfolio_positions_response):
    # Convert the portfolio positions response from nuvama to standard df used in the project.

    df = pd.DataFrame(columns=option_open_positions_columns)

    for item in portfolio_positions_response:
        # print(item)
        if item['exc'] == 'NFO':
            # print(item)
            # Sample DataFrame
            # {'asTyp': 'OPTSTK', 'dpInsTyp': '', 'dpName': 'AARTIIND', 'exc': 'NFO',
            # 'ltSz': '1000', 'ltp': '21.85', 'sym': '73200_NFO', 'tkSz': '0.05',
            # 'trdSym': 'AARTIIND24FEB665PE', 'dpExpDt': "29 FEB'24", 'opTyp': 'PE',
            # 'stkPrc': '665', 'GD': '1', 'GN': '1', 'PD': '1', 'PN': '1', 'avgByPrc': '0.00',
            # 'avgSlPrc': '19.00', 'byAmt': '0.00', 'byQty': '0', 'cpName': 'Aarti Industries Ltd',
            # 'mtm': '-2850.00', 'mul': '1', 'ntAmt': '19000.00', 'ntPL': '-2850.0', 'ntQty': '-1000',
            # 'nwsFlg': '0', 'prc': '19.00', 'prdCode': 'NRML', 'rchFlg': '0', 'rlzPL': '0.00',
            # 'slAmt': '19000.00', 'slQty': '1000', 'sqOff': 'true', 'trsTyp': 'S',
            # 'uniqKey': 'AARTIIND24FEB665PE', 'urlzPL': '-2850.00', 'cfAvgSlPrc': '19.00',
            # 'cfAvgByPrc': '0.00', 'cfSlQty': '0', 'cfByQty': '0', 'cfSlAmt': '0.00',
            # 'cfByAmt': '0.00', 'ntSlQty': '1000', 'ntByQty': '0', 'ntSlAmt': '19,000.00',
            # 'ntByAmt': '0.00', 'brkEvnPrc': '19.00', 'prdDp': 'NRML'}
            right = 'Put' if item['opTyp'] == 'PE' else 'Call'
            action = 'Sell' if item['trsTyp'] == 'S' else 'Buy'
            if action == 'Buy':
                average_price = float(item['avgByPrc'])
            else:
                average_price = float(item['avgSlPrc'])

            expiry_date = item['dpExpDt']  # ge the expiry date in this format - 29 FEB'24
            # converting the expiry date in DD-MMM-YYYY format (29-Feb-2024)
            # expiry_date = datetime.datetime.strptime(expiry_date, '%d %b %y').strftime('%d-%b-%Y')
            # converting the expiry date in DD-MMM-YYYY format (29-Feb-2024)
            expiry_date = expiry_date[0:2] + '-' + expiry_date[3:6] + '-20' + expiry_date[7:9]

            pnl_data = {
                "broker": c.NUVAMA_BROKER,
                "stock": get_icici_stock_code(item['dpName']),
                "broker_stock_code": item['dpName'],
                "ltp": float(item['ltp']),
                "average_price": average_price,
                "quantity": int(item['ntQty']),
                "strike_price": float(item['stkPrc']),
                "expiry_date": expiry_date,
                "right": right,
                "pnl": round(float(item['ntPL']),0),
                "action": action
            }

            df = pd.concat([df, pd.DataFrame.from_records([pnl_data])], ignore_index=True)

    # print(df)
    return df