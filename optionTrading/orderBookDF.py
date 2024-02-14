from datetime import datetime

import pandas as pd

import iciciDirect.icici_direct_main as icici_direct_main
import nuvama.nuvama_main as nuvama_main
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
        hashmap_orders_ltp[item] = get_option_ltp(icici_direct_main.get_api_session(), item[0], item[1], item[2],
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
            "expiry_date": item['expiry_date'],
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

    # {"eq": {"appID": "d873f9fc27197807714f558ff9306933", "config": {"app": 1, "exp": 1707782415669, "info": 4},
    # "data": {"type": "orderBookResponse", "ord": [{"stkPrc": "", "dur": "DAY", "vlDt": "NA", "rcvTim": "16:34:31",
    # "rcvEpTim": "13/02/2024 16:34:31", "sym": "17400_NSE", "cpName": "Nhpc Ltd", "exit": "false", "syomID": "",
    # "exc": "NSE", "ntQty": "1500", "dpName": "NHPC", "cancel": "false", "sipID": "N", "nstReqID": "1",
    # "ordTyp": "LIMIT", "opTyp": "", "trsTyp": "BUY", "srs": "EQ", "prdCode": "CNC", "prdDp": "CNC", "ogt": "--",
    # "flQty": "0", "trdSym": "NHPLTD", "edit": "false", "asTyp": "EQUITY", "trgPrc": "0.00", "avgPrc": "0.00",
    # "dsQty": "0", "ordID": "240213000147344", "sts": "cancelled", "dpInsTyp": "", "rjRsn": "", "userID":
    # "ROOPALGODHA", "dpExpDt": "", "ltSz": "1", "tkSz": "0.05", "desc": "Buy 1500 Qty @ &#8377 83.00",
    # "prc": "83.00", "exONo": "1200000023265984", "rcvDt": "13/02/2024", "pdQty": "0", "userCmnt": "NA", "rmk": "",
    # "boSeqId": "", "epochTim": "1707822271", "ordTim": "13/02/2024 16:34:31", "trgId": "", "dpVal": "NHPC",
    # "ltp": "85.80", "bsktOrdId": "", "bsktEpch": "", "sipNo": "NA", "chg": "4.80", "chgP": "5.93"}, {"stkPrc":
    # "830", "dur": "DAY", "vlDt": "NA", "rcvTim": "14:07:40", "rcvEpTim": "13/02/2024 14:07:40", "sym": "94706_NFO",
    # "cpName": "Dlf Limited", "exit": "false", "syomID": "", "exc": "NFO", "ntQty": "1650", "dpName": "DLF",
    # "cancel": "false", "sipID": "N", "nstReqID": "2", "ordTyp": "LIMIT", "opTyp": "PE", "trsTyp": "SELL",
    # "srs": "XX", "prdCode": "NRML", "prdDp": "NRML", "ogt": "--", "flQty": "1650", "trdSym": "DLF24FEB830PE",
    # "edit": "false", "asTyp": "OPTSTK", "trgPrc": "0.00", "avgPrc": "23.15", "dsQty": "0",
    # "ordID": "240213000265400", "sts": "complete", "dpInsTyp": "", "rjRsn": "", "userID": "ROOPALGODHA",
    # "dpExpDt": "29 FEB'24", "ltSz": "1650", "tkSz": "0.05", "desc": "1650 Sold @ &#8377 23.15", "prc": "23.10",
    # "exONo": "2200000112127676", "exp": "29Feb2024", "rcvDt": "13/02/2024", "pdQty": "0", "userCmnt": "NA",
    # "rmk": "", "boSeqId": "", "epochTim": "1707813460", "ordTim": "13/02/2024 14:07:40", "trgId": "",
    # "dpVal": "DLF", "ltp": "21.50", "bsktOrdId": "", "bsktEpch": "", "sipNo": "NA", "chg": "-12.85",
    # "chgP": "-37.41"}, {"stkPrc": "7400", "dur": "DAY", "vlDt": "NA", "rcvTim": "11:01:27", "rcvEpTim": "13/02/2024
    # 11:01:27", "sym": "62664_NFO", "cpName": "Oracle Fin Serv Soft Ltd.", "exit": "false", "syomID": "",
    # "exc": "NFO", "ntQty": "200", "dpName": "OFSS", "cancel": "false", "sipID": "N", "nstReqID": "3",
    # "ordTyp": "LIMIT", "opTyp": "PE", "trsTyp": "SELL", "srs": "XX", "prdCode": "NRML", "prdDp": "NRML",
    # "ogt": "--", "flQty": "200", "trdSym": "OFSS24FEB7400PE", "edit": "false", "asTyp": "OPTSTK", "trgPrc": "0.00",
    # "avgPrc": "280.00", "dsQty": "0", "ordID": "240213000143806", "sts": "complete", "dpInsTyp": "", "rjRsn": "",
    # "userID": "USER_ID", "dpExpDt": "29 FEB'24", "ltSz": "200", "tkSz": "0.05", "desc": "200 Sold @ &#8377
    # 280.00", "prc": "280.00", "exONo": "2400000055876947", "exp": "29Feb2024", "rcvDt": "13/02/2024", "pdQty": "0",
    # "userCmnt": "NA", "rmk": "Order placed from Quantsapp", "boSeqId": "", "epochTim": "1707802287",
    # "ordTim": "13/02/2024 11:01:27", "trgId": "", "dpVal": "OFSS", "ltp": "198.00", "bsktOrdId": "", "bsktEpch":
    # "", "sipNo": "NA", "chg": "-255.65", "chgP": "-56.35"}, {"stkPrc": "7600", "dur": "DAY", "vlDt": "NA",
    # "rcvTim": "11:00:45", "rcvEpTim": "13/02/2024 11:00:45", "sym": "62671_NFO", "cpName": "Oracle Fin Serv Soft
    # Ltd.", "exit": "false", "syomID": "", "exc": "NFO", "ntQty": "200", "dpName": "OFSS", "cancel": "false",
    # "sipID": "N", "nstReqID": "1", "ordTyp": "LIMIT", "opTyp": "CE", "trsTyp": "SELL", "srs": "XX", "prdCode":
    # "NRML", "prdDp": "NRML", "ogt": "--", "flQty": "200", "trdSym": "OFSS24FEB7600CE", "edit": "false",
    # "asTyp": "OPTSTK", "trgPrc": "0.00", "avgPrc": "330.00", "dsQty": "0", "ordID": "240213000143803",
    # "sts": "complete", "dpInsTyp": "", "rjRsn": "", "userID": "USER_ID", "dpExpDt": "29 FEB'24", "ltSz": "200",
    # "tkSz": "0.05", "desc": "200 Sold @ &#8377 330.00", "prc": "330.00", "exONo": "2400000055876378",
    # "exp": "29Feb2024", "rcvDt": "13/02/2024", "pdQty": "0", "userCmnt": "NA", "rmk": "Order placed from
    # Quantsapp", "boSeqId": "", "epochTim": "1707802245", "ordTim": "13/02/2024 11:00:45", "trgId": "",
    # "dpVal": "OFSS", "ltp": "380.05", "bsktOrdId": "", "bsktEpch": "", "sipNo": "NA", "chg": "179.90",
    # "chgP": "89.88"}, {"stkPrc": "", "dur": "DAY", "vlDt": "NA", "rcvTim": "10:01:40", "rcvEpTim": "13/02/2024
    # 10:01:40", "sym": "2687_NSE", "cpName": "Polyplex Corporation Ltd", "exit": "false", "syomID": "",
    # "exc": "NSE", "ntQty": "10", "dpName": "POLYPLEX", "cancel": "false", "sipID": "N", "nstReqID": "1",
    # "ordTyp": "LIMIT", "opTyp": "", "trsTyp": "SELL", "srs": "EQ", "prdCode": "CNC", "prdDp": "CNC", "ogt": "--",
    # "flQty": "10", "trdSym": "POLCOR", "edit": "false", "asTyp": "EQUITY", "trgPrc": "0.00", "avgPrc": "941.62",
    # "dsQty": "0", "ordID": "240213000091633", "sts": "complete", "dpInsTyp": "", "rjRsn": "", "userID":
    # "USER_ID", "dpExpDt": "", "ltSz": "1", "tkSz": "0.05", "desc": "10 Sold @ &#8377 941.62", "prc": "940.00",
    # "exONo": "1200000013169645", "rcvDt": "13/02/2024", "pdQty": "0", "userCmnt": "NA", "rmk": "", "boSeqId": "",
    # "epochTim": "1707798700", "ordTim": "13/02/2024 10:01:40", "trgId": "", "dpVal": "POLYPLEX", "ltp": "932.85",
    # "bsktOrdId": "", "bsktEpch": "", "sipNo": "NA", "chg": "-25.30", "chgP": "-2.64"}, {"stkPrc": "", "dur": "DAY",
    # "vlDt": "NA", "rcvTim": "09:26:45", "rcvEpTim": "13/02/2024 09:26:45", "sym": "2963_NSE", "cpName": "Steel
    # Authority Of India", "exit": "false", "syomID": "", "exc": "NSE", "ntQty": "200", "dpName": "SAIL",
    # "cancel": "false", "sipID": "N", "nstReqID": "2", "ordTyp": "LIMIT", "opTyp": "", "trsTyp": "SELL",
    # "srs": "EQ", "prdCode": "CNC", "prdDp": "CNC", "ogt": "--", "flQty": "200", "trdSym": "STEAUT",
    # "edit": "false", "asTyp": "EQUITY", "trgPrc": "0.00", "avgPrc": "118.00", "dsQty": "0",
    # "ordID": "240213000020725", "sts": "complete", "dpInsTyp": "", "rjRsn": "", "userID": "USER_ID",
    # "dpExpDt": "", "ltSz": "1", "tkSz": "0.05", "desc": "200 Sold @ &#8377 118.00", "prc": "118.00",
    # "exONo": "1300000001420939", "rcvDt": "13/02/2024", "pdQty": "0", "userCmnt": "NA", "rmk": "", "boSeqId": "",
    # "epochTim": "1707796605", "ordTim": "13/02/2024 09:26:45", "trgId": "", "dpVal": "SAIL", "ltp": "117.85",
    # "bsktOrdId": "", "bsktEpch": "", "sipNo": "NA", "chg": "-4.90", "chgP": "-3.99"}]}, "msgID":
    # "20c5d7dc-ba9e-417d-bbe2-bbf412633578", "srvTm": 1707833693805}, "comm": ""}

    for item in order_book_response:
        if item['exc'] == 'NFO':
            # Get only option orders, ignore equity orders
            status = item['sts']
            if item['sts'] == "complete":
                status = c.ORDER_STATUS_COMPLETE
            if item['sts'] == "accepted":
                status = c.ORDER_STATUS_OPEN

            right = 'Put' if item['opTyp'] == 'PE' else 'Call'

            expiry_date = item['dpExpDt']  # ge the expiry date in this format - 29 FEB'24
            # converting the expiry date in DD-MMM-YYYY format (29-Feb-2024)
            # expiry_date = datetime.datetime.strptime(expiry_date, '%d %b %y').strftime('%d-%b-%Y')
            # converting the expiry date in DD-MMM-YYYY format (29-Feb-2024)
            expiry_date = expiry_date[0:2] + '-' + expiry_date[3:6] + '-20' + expiry_date[7:9]

            order = {
                "broker": c.NUVAMA_BROKER,
                "stock": get_icici_stock_code(item['dpName']),
                "broker_stock_code": item['dpName'],
                "expiry_date": expiry_date,
                "ltp": float(item['ltp']),
                "order_price": float(item['avgPrc']),
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
