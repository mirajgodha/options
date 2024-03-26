import pandas as pd
import constants.constants_local as c
from datetime import datetime

from helper.stockCodes import get_icici_stock_code

# ---------------------------------------------------------------------------------------------------------------------
# Portfolio Holdings DF
# ---------------------------------------------------------------------------------------------------------------

# Columns for the positions dataframe
# stock - the stock code, using a unified stock code across all borkers as ICICI direct stock code.
# broker_stock_code - broker specific stock code
# average_price - is the price of buy for the stock
# quantity - is the number of stocks hold

# Columns for the order history dataframe
portfolio_holdings_columns = ["broker", "stock", "broker_stock_code",
                                        "average_price", "quantity", "ltp", "change_percentage",
                                        "timestamp"]


# ---------------------------------------------------------------------------------------------------------------


def get_icici_portfolio_holding_df(portfolio_holdings):
    # Convert the portfolio positions response from icici to standard df used in the project.

    df = pd.DataFrame(columns=portfolio_holdings_columns)

    for item in portfolio_holdings:
        # [{'stock_code': 'SANEN', 'exchange_code': 'NSE', 'quantity': '150', 'average_price': '953.27',
        # 'booked_profit_loss': '0', 'current_market_price': '957.25', 'change_percentage': '-0.25528811086798',
        # 'answer_flag': 'N', 'product_type': None, 'expiry_date': None, 'strike_price': None, 'right': None,
        # 'category_index_per_stock': None, 'action': None, 'realized_profit': None, 'unrealized_profit': None,
        # 'open_position_value': None, 'portfolio_charges': None}, {'stock_code': 'HDFBAN', 'exchange_code': 'NSE',
        # 'quantity': '70', 'average_price': '1581.59', 'booked_profit_loss': '0', 'current_market_price': '1459.55',
        # 'change_percentage': '2.22370079843115', 'answer_flag': 'N', 'product_type': None, 'expiry_date': None,
        # 'strike_price': None, 'right': None, 'category_index_per_stock': None, 'action': None, 'realized_profit':
        # None, 'unrealized_profit': None, 'open_position_value': None, 'portfolio_charges': None}]

        portfolio_data = {
            "broker": c.ICICI_DIRECT_BROKER,
            "stock": item['stock_code'],
            "broker_stock_code": item['stock_code'],
            "average_price": float(item['average_price']),
            "quantity": int(item['quantity']),
            "ltp": float(item['current_market_price']),
            "change_percentage": float(item['change_percentage']),
        }

        df = pd.concat([df, pd.DataFrame.from_records([portfolio_data])], ignore_index=True)
    df['timestamp'] = datetime.now()
    return df


def get_nuvama_portfolio_holdings_df(portfolio_holdings):
    # Convert the portfolio holdings response from nuvama to standard df used in the project.

    df = pd.DataFrame(columns=portfolio_holdings_columns)
    for item in portfolio_holdings:

        # [{'asTyp': 'EQUITY', 'chgP': '0.77', 'cncRmsHdg': {'td': 'true', 'hdgVl': '438722.40', 'clUQty': '0',
        # 'hdgUQty': '0', 'usdQty': '0', 't1HQty': '0', 'clQty': '272', 'qty': '272', 'pdQty': '272',
        # 'pdCnt': '272.0', 'totQty': '272'}, 'cpName': ' Infosys  Limited ', 'dpName': 'INFY', 'exc': 'NSE',
        # 'hairCut': '25.00', 'isin': 'INE009A01021', 'ltSz': '1', 'ltp': '1612.95', 'sym': '1594_NSE',
        # 'tkSz': '0.05', 'totalQty': '272', 'totalVal': '438722.40', 'trdSym': 'INFLTD'}, {'asTyp': 'EQUITY',
        # 'chgP': '-0.49', 'cncRmsHdg': {'td': 'true', 'hdgVl': '114151.20', 'clUQty': '0', 'hdgUQty': '0',
        # 'usdQty': '0', 't1HQty': '0', 'clQty': '48', 'qty': '48', 'pdQty': '48', 'pdCnt': '48.0', 'totQty': '48'},
        # 'cpName': ' Hindustan  Unilever  Ltd. ', 'dpName': 'HINDUNILVR', 'exc': 'NSE', 'hairCut': '25.00',
        # 'isin': 'INE030A01027', 'ltSz': '1', 'ltp': '2378.15', 'sym': '1394_NSE', 'tkSz': '0.05', 'totalQty': '48',
        # 'totalVal': '114151.20', 'trdSym': 'HINUNI'}]

        portfolio_data = {
            "broker": c.NUVAMA_BROKER,
            "stock": get_icici_stock_code(item['dpName']),
            "broker_stock_code": item['dpName'],
            "average_price": float(get_average_price(item['dpName'])),
            "quantity": int(item['totalQty']),
            "ltp": float(item['ltp']),
            "change_percentage": float(item['chgP']),
        }

        df = pd.concat([df, pd.DataFrame.from_records([portfolio_data])], ignore_index=True)

    df['timestamp'] = datetime.now()
    return df

def get_average_price(stock):
    # create a map of stock name and price and return the price of given stock.
    stock_buy_price_map = {
        "AARTISURF": 856.77,
        "ADANIPORTS": 1351.42,
        "BEL": 215.27,
        "CARYSIL": 632.77,
        "DEEPAKNTR": 2015.27,
        "DIVISLAB": 3844.47,
        "DLF": 633.53,
        "HDFCBANK": 1617.42,
        "HINDUNILVR": 2560.17,
        "ICICIBANK": 881.47,
        "INFY": 1407.98,
        "ITC": 268.72,
        "J&KBANK": 129.96,
        "JIOFIN": 118.06,
        "JUBLFOOD": 640.94,
        "POLYPLEX": 1709.85,
        "RELIANCE": 2399.72,
        "SRF": 2383.93,
        "TATAMOTORS": 716.77,
        "TCS": 3319.67,
        "TIMKEN": 3248.07,
        "VEDL": 290.49,
        "ZOMATO": 134.17,
        "BHINVIT-IV": 100
    }
    return stock_buy_price_map[stock]




