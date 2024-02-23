from datetime import datetime

import pandas as pd

from helper.colours import Colors
from optionTrading.trading_helper import get_option_ltp
import constants.constants_local as c
from helper.stockCodes import get_icici_stock_code

# Columns for the order book dataframe
# broker - the broker code, using a unified stock code across all borkers as ICICI direct stock code.
# stock - the stock code, using a unified stock code across all borkers as ICICI direct stock code.
# broker_stock_code - is the stock code used by the broker.
# expiry_date - is the date on which the option contract expires. DD-MMM-YYYY format (29-Feb-2024)
# ltp - is the last traded price of the option contract.
# order_price - is the price at which the order was placed.
# order_status - is the status of the order (Open, Filled, Cancelled, etc.).
# order_time - is the time at which the order was placed.
# action - is the type of action taken (Buy or Sell).
# quantity - is the number of contracts bought or sold.
# right - is the type of option contract (Call or Put).
# strike_price - is the price at which the option contract is exercised.
# pending_quantity - is the number of contracts that have not yet been filled.
order_book_columns = ["broker", "stock", "broker_stock_code", "expiry_date", "ltp", "order_price", "order_status",
                      "order_time", "action", "quantity", "right", "strike_price", "pending_quantity"]


def get_icici_order_book_df(order_book_response):
    df = pd.DataFrame(columns=order_book_columns)

    if order_book_response is None:
        return df

    # {'Success': [{'order_id': '202402134100008043', 'exchange_order_id': '2100000032054472',
    # 'exchange_code': 'NFO', 'stock_code': 'PERSYS', 'product_type': 'Options', 'action': 'Sell', 'order_type':
    # 'Limit', 'stoploss': '0', 'quantity': '100', 'price': '89.5', 'validity': 'Day', 'disclosed_quantity': '0',
    # 'expiry_date': '29-Feb-2024', 'right': 'Put', 'strike_price': 8200.0, 'average_price': '89.5',
    # 'cancelled_quantity': '0', 'pending_quantity': '0', 'status': 'Executed', 'user_remark': None,
    # 'order_datetime': '13-Feb-2024 10:16:03', 'parent_order_id': '', 'modification_number': None,
    # 'exchange_acknowledgement_date': None, 'SLTP_price': None, 'exchange_acknowledge_number': None,
    # 'initial_limit': None, 'intial_sltp': None, 'LTP': None, 'limit_offset': None, 'mbc_flag': None,
    # 'cutoff_price': None, 'validity_date': None}, {'order_id': '202402134100008034', 'exchange_order_id':
    # '2100000031956785', 'exchange_code': 'NFO', 'stock_code': 'PERSYS', 'product_type': 'Options', 'action': 'Buy',
    # 'order_type': 'Limit', 'stoploss': '0', 'quantity': '200', 'price': '58.25', 'validity': 'Day',
    # 'disclosed_quantity': '0', 'expiry_date': '29-Feb-2024', 'right': 'Put', 'strike_price': 8000.0,
    # 'average_price': '58.25', 'cancelled_quantity': '0', 'pending_quantity': '0', 'status': 'Executed',
    # 'user_remark': None, 'order_datetime': '13-Feb-2024 10:17:14', 'parent_order_id': '', 'modification_number':
    # None, 'exchange_acknowledgement_date': None, 'SLTP_price': None, 'exchange_acknowledge_number': None,
    # 'initial_limit': None, 'intial_sltp': None, 'LTP': None, 'limit_offset': None, 'mbc_flag': None,
    # 'cutoff_price': None, 'validity_date': None}, {'order_id': '202402134100005794', 'exchange_order_id':
    # '2000000021135407', 'exchange_code': 'NFO', 'stock_code': 'BHAPET', 'product_type': 'Options',
    # 'action': 'Sell', 'order_type': 'Limit', 'stoploss': '0', 'quantity': '1800', 'price': '14', 'validity': 'Day',
    # 'disclosed_quantity': '0', 'expiry_date': '29-Feb-2024', 'right': 'Call', 'strike_price': 600.0,
    # 'average_price': '14', 'cancelled_quantity': '0', 'pending_quantity': '0', 'status': 'Executed', 'user_remark':
    # None, 'order_datetime': '13-Feb-2024 09:54:10', 'parent_order_id': '', 'modification_number': None,
    # 'exchange_acknowledgement_date': None, 'SLTP_price': None, 'exchange_acknowledge_number': None,
    # 'initial_limit': None, 'intial_sltp': None, 'LTP': None, 'limit_offset': None, 'mbc_flag': None,
    # 'cutoff_price': None, 'validity_date': None}, {'order_id': '202402134100005348', 'exchange_order_id':
    # '2000000018684538', 'exchange_code': 'NFO', 'stock_code': 'BHAPET', 'product_type': 'Options',
    # 'action': 'Sell', 'order_type': 'Limit', 'stoploss': '0', 'quantity': '1800', 'price': '25', 'validity': 'Day',
    # 'disclosed_quantity': '0', 'expiry_date': '29-Feb-2024', 'right': 'Call', 'strike_price': 610.0,
    # 'average_price': '0', 'cancelled_quantity': '0', 'pending_quantity': '1800', 'status': 'Expired',
    # 'user_remark': None, 'order_datetime': '13-Feb-2024 10:05:53', 'parent_order_id': '', 'modification_number':
    # None, 'exchange_acknowledgement_date': None, 'SLTP_price': None, 'exchange_acknowledge_number': None,
    # 'initial_limit': None, 'intial_sltp': None, 'LTP': None, 'limit_offset': None, 'mbc_flag': None,
    # 'cutoff_price': None, 'validity_date': None}, {'order_id': '202402134100005326', 'exchange_order_id':
    # '2000000018557011', 'exchange_code': 'NFO', 'stock_code': 'BHAPET', 'product_type': 'Options', 'action': 'Buy',
    # 'order_type': 'Limit', 'stoploss': '0', 'quantity': '1800', 'price': '3.5', 'validity': 'Day',
    # 'disclosed_quantity': '0', 'expiry_date': '29-Feb-2024', 'right': 'Call', 'strike_price': 650.0,
    # 'average_price': '3.5', 'cancelled_quantity': '0', 'pending_quantity': '0', 'status': 'Executed',
    # 'user_remark': None, 'order_datetime': '13-Feb-2024 09:49:05', 'parent_order_id': '', 'modification_number':
    # None, 'exchange_acknowledgement_date': None, 'SLTP_price': None, 'exchange_acknowledge_number': None,
    # 'initial_limit': None, 'intial_sltp': None, 'LTP': None, 'limit_offset': None, 'mbc_flag': None,
    # 'cutoff_price': None, 'validity_date': None}], 'Status': 200, 'Error': None}

    # Specify the columns for which you want to create a set
    selected_columns = ['stock_code', 'expiry_date', 'strike_price', 'right']

    # Create a set for the specified columns
    unique_combinations_set = {tuple(item_dict[column] for column in selected_columns) for item_dict in
                               order_book_response}

    # create a hash map which will contain the ltp for
    # each unique combination of stock_code, expiry_date, strike_price, right
    hashmap_orders_ltp = {combination: 0 for combination in unique_combinations_set}

    for item in unique_combinations_set:
        hashmap_orders_ltp[item] = get_option_ltp(item[0], item[1], item[2],
                                                  item[3])

    # Update ltp in orders as icici do not provide ltp in order list
    for item in order_book_response:
        item['ltp'] = hashmap_orders_ltp[tuple(item[column] for column in selected_columns)]

    for item in order_book_response:
        status = item['status']
        if item['status'] == "Executed":
            status = c.ORDER_STATUS_COMPLETE
        if item['status'] == "Ordered":
            status = c.ORDER_STATUS_OPEN

        order = {
            "broker": c.ICICI_DIRECT_BROKER,
            "stock": item['stock_code'],
            "broker_stock_code": item['stock_code'],
            "expiry_date": item['expiry_date'].upper(),
            "ltp": float(item['ltp']),
            "order_price": float(item['price']),
            "order_status": status,
            "order_time": datetime.strptime(item['order_datetime'], "%d-%b-%Y %H:%M:%S"),
            "action": item['action'],
            "quantity": int(item['quantity']),
            "right": item['right'],
            "strike_price": float(item['strike_price']),
            "pending_quantity": int(item['pending_quantity'])
        }

        df = pd.concat([df, pd.DataFrame.from_records([order])], ignore_index=True)

    return df


def get_nuvama_option_order_book_df(order_book_response):
    df = pd.DataFrame(columns=order_book_columns)

    if order_book_response is None:
        return df

    # {'eq': {'appID': 'd873f9fc27197807714f558ff9306933', 'config': {'app': 1, 'exp': 1708473617109, 'info': 4},
    # 'data': {'type': 'orderBookResponse', 'ord': [{'stkPrc': '850', 'dur': 'DAY', 'vlDt': 'NA', 'rcvTim':
    # '10:06:58', 'rcvEpTim': '21/02/2024 10:06:58', 'sym': '43600_NFO', 'cpName': 'Dlf Limited', 'exit': 'false',
    # 'syomID': '', 'exc': 'NFO', 'ntQty': '1650', 'dpName': 'DLF', 'cancel': 'true', 'sipID': 'N', 'nstReqID': '2',
    # 'ordTyp': 'LIMIT', 'opTyp': 'PE', 'trsTyp': 'BUY', 'srs': 'XX', 'prdCode': 'NRML', 'prdDp': 'NRML',
    # 'ogt': '--', 'flQty': '0', 'trdSym': 'DLF24FEB850PE', 'edit': 'true', 'asTyp': 'OPTSTK', 'trgPrc': '0.00',
    # 'avgPrc': '0.00', 'dsQty': '0', 'ordID': '240221000091759', 'sts': 'open', 'dpInsTyp': '', 'rjRsn': '',
    # 'userID': 'ROOPALGODHA', 'dpExpDt': "29 FEB'24", 'ltSz': '1650', 'tkSz': '0.05', 'desc': 'Buy 1650 Qty @ &#8377
    # 3.00', 'prc': '3.00', 'exONo': '2200000019627418', 'exp': '29Feb2024', 'rcvDt': '21/02/2024', 'pdQty': '1650',
    # 'userCmnt': 'NA', 'rmk': 'Order placed from Quantsapp', 'boSeqId': '', 'epochTim': '1708490218',
    # 'ordTim': '21/02/2024 10:06:58', 'trgId': '', 'dpVal': 'DLF', 'ltp': '5.00', 'bsktOrdId': '', 'bsktEpch': '',
    # 'sipNo': 'NA', 'chg': '-4.55', 'chgP': '-47.64'}, {'stkPrc': '860', 'dur': 'DAY', 'vlDt': 'NA',
    # 'rcvTim': '10:06:47', 'rcvEpTim': '21/02/2024 10:06:47', 'sym': '43611_NFO', 'cpName': 'Dlf Limited',
    # 'exit': 'false', 'syomID': '', 'exc': 'NFO', 'ntQty': '3300', 'dpName': 'DLF', 'cancel': 'true', 'sipID': 'N',
    # 'nstReqID': '1', 'ordTyp': 'LIMIT', 'opTyp': 'PE', 'trsTyp': 'BUY', 'srs': 'XX', 'prdCode': 'NRML',
    # 'prdDp': 'NRML', 'ogt': '--', 'flQty': '0', 'trdSym': 'DLF24FEB860PE', 'edit': 'true', 'asTyp': 'OPTSTK',
    # 'trgPrc': '0.00', 'avgPrc': '0.00', 'dsQty': '0', 'ordID': '240221000095620', 'sts': 'open', 'dpInsTyp': '',
    # 'rjRsn': '', 'userID': 'ROOPALGODHA', 'dpExpDt': "29 FEB'24", 'ltSz': '1650', 'tkSz': '0.05', 'desc': 'Buy 3300
    # Qty @ &#8377 6.00', 'prc': '6.00', 'exONo': '2200000021259712', 'exp': '29Feb2024', 'rcvDt': '21/02/2024',
    # 'pdQty': '3300', 'userCmnt': 'NA', 'rmk': 'Order placed from Quantsapp', 'boSeqId': '', 'epochTim':
    # '1708490207', 'ordTim': '21/02/2024 10:06:47', 'trgId': '', 'dpVal': 'DLF', 'ltp': '7.30', 'bsktOrdId': '',
    # 'bsktEpch': '', 'sipNo': 'NA', 'chg': '-6.65', 'chgP': '-47.67'}, {'stkPrc': '890', 'dur': 'DAY', 'vlDt': 'NA',
    # 'rcvTim': '10:02:58', 'rcvEpTim': '21/02/2024 10:02:58', 'sym': '52576_NFO', 'cpName': 'Dlf Limited',
    # 'exit': 'false', 'syomID': '', 'exc': 'NFO', 'ntQty': '1650', 'dpName': 'DLF', 'cancel': 'false', 'sipID': 'N',
    # 'nstReqID': '1', 'ordTyp': 'LIMIT', 'opTyp': 'PE', 'trsTyp': 'SELL', 'srs': 'XX', 'prdCode': 'NRML',
    # 'prdDp': 'NRML', 'ogt': '--', 'flQty': '1650', 'trdSym': 'DLF24FEB890PE', 'edit': 'false', 'asTyp': 'OPTSTK',
    # 'trgPrc': '0.00', 'avgPrc': '20.50', 'dsQty': '0', 'ordID': '240221000090375', 'sts': 'complete', 'dpInsTyp':
    # '', 'rjRsn': 'order is not open', 'userID': 'ROOPALGODHA', 'dpExpDt': "29 FEB'24", 'ltSz': '1650',
    # 'tkSz': '0.05', 'desc': '1650 Sold @ &#8377 20.50', 'prc': '20.50', 'exONo': '2200000019188471',
    # 'exp': '29Feb2024', 'rcvDt': '21/02/2024', 'pdQty': '0', 'userCmnt': 'NA', 'rmk': 'Order placed from
    # Quantsapp', 'boSeqId': '', 'epochTim': '1708489978', 'ordTim': '21/02/2024 10:02:58', 'trgId': '',
    # 'dpVal': 'DLF', 'cta': '', 'ltp': '19.75', 'bsktOrdId': '', 'bsktEpch': '', 'sipNo': 'NA', 'chg': '-16.40',
    # 'chgP': '-45.37'}, {'stkPrc': '870', 'dur': 'DAY', 'vlDt': 'NA', 'rcvTim': '09:31:42', 'rcvEpTim': '21/02/2024
    # 09:31:42', 'sym': '51365_NFO', 'cpName': 'Dlf Limited', 'exit': 'false', 'syomID': '', 'exc': 'NFO',
    # 'ntQty': '1650', 'dpName': 'DLF', 'cancel': 'false', 'sipID': 'N', 'nstReqID': '1', 'ordTyp': 'LIMIT',
    # 'opTyp': 'PE', 'trsTyp': 'SELL', 'srs': 'XX', 'prdCode': 'NRML', 'prdDp': 'NRML', 'ogt': '--', 'flQty': '1650',
    # 'trdSym': 'DLF24FEB870PE', 'edit': 'false', 'asTyp': 'OPTSTK', 'trgPrc': '0.00', 'avgPrc': '16.00',
    # 'dsQty': '0', 'ordID': '240221000040812', 'sts': 'complete', 'dpInsTyp': '', 'rjRsn': '', 'userID':
    # 'ROOPALGODHA', 'dpExpDt': "29 FEB'24", 'ltSz': '1650', 'tkSz': '0.05', 'desc': '1650 Sold @ &#8377 16.00',
    # 'prc': '16.00', 'exONo': '2200000004543401', 'exp': '29Feb2024', 'rcvDt': '21/02/2024', 'pdQty': '0',
    # 'userCmnt': 'NA', 'rmk': 'Order placed from Quantsapp', 'boSeqId': '', 'epochTim': '1708488102',
    # 'ordTim': '21/02/2024 09:31:42', 'trgId': '', 'dpVal': 'DLF', 'ltp': '10.40', 'bsktOrdId': '', 'bsktEpch': '',
    # 'sipNo': 'NA', 'chg': '-9.20', 'chgP': '-46.94'}]}, 'msgID': 'fe3a264a-e260-487b-a45f-fa740c7f8a20',
    # 'srvTm': 1708490534274}, 'comm': ''}

    for item in order_book_response:
        if item['exc'] == 'NFO':
            # Get only option orders, ignore equity orders
            status = item['sts']
            if item['sts'] == "complete":
                status = c.ORDER_STATUS_COMPLETE
            if item['sts'] == "accepted" or item['sts'] == "open":
                status = c.ORDER_STATUS_OPEN

            right = 'Put' if item['opTyp'] == 'PE' else 'Call'

            expiry_date = item['dpExpDt']  # ge the expiry date in this format - 29 FEB'24
            # converting the expiry date in DD-MMM-YYYY format (29-Feb-2024)
            # expiry_date = datetime.datetime.strptime(expiry_date, '%d %b %y').strftime('%d-%b-%Y')
            # converting the expiry date in DD-MMM-YYYY format (29-Feb-2024)
            expiry_date = expiry_date[0:2] + '-' + expiry_date[3:6] + '-20' + expiry_date[7:9]

            if float(item['avgPrc']) != 0:
                order_price = float(item['avgPrc'])
            else:
                order_price = float(item['prc'])

            order = {
                "broker": c.NUVAMA_BROKER,
                "stock": get_icici_stock_code(item['dpName']),
                "broker_stock_code": item['dpName'],
                "expiry_date": expiry_date.upper(),
                "ltp": float(item['ltp']),
                "order_price": order_price,
                "order_status": status,
                "order_time": datetime.strptime(item['rcvEpTim'], "%d/%m/%Y %H:%M:%S"),
                "action": item['trsTyp'],
                "quantity": int(item['ntQty']),
                "right": right,
                "strike_price": float(item['stkPrc']),
                "pending_quantity": int(item['pdQty'])
            }

            df = pd.concat([df, pd.DataFrame.from_records([order])], ignore_index=True)

    return df
