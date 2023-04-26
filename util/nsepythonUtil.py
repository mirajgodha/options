from stopit import threading_timeoutable as timeoutable

from nsepython import *
import pandas as pd
import logging

from dao.Option import TranxType
from optionStrategyBuilder import expiry_month

logging.basicConfig(level=logging.INFO)

lot_sizes = pd.DataFrame()

# ------------
# Utility methods based on nsepython scraper utility
# ------------

def get_atm_strike(option_chain_json):
    """
    Get at the money strike price from the given stock option chain
    :param option_chain_json:
    :return:
    """
    data = option_chain_json['filtered']['data']
    try:
        ltp = data[0]['PE']['underlyingValue']
    except:
        try:
            ltp = data[0]['CE']['underlyingValue']
        except:
            ltp = data[1]['PE']['underlyingValue']

    strike_price_list = [x['strikePrice'] for x in data]
    atm_strike = sorted([[round(abs(ltp - i), 2), i] for i in strike_price_list])[0][1]
    return atm_strike


def get_pe_price(option_chain_json, strike_price, txType):
    for dictt in option_chain_json['records']['data']:
        if dictt['strikePrice'] == strike_price and dictt['expiryDate'] == expiry_month:
            if txType == TranxType.SELL:
                pe_price = dictt['PE']['bidprice']
            else:
                pe_price = dictt['PE']['askPrice']
            return pe_price
    else:
        print(f"No instrument found with the given strike {strike_price}.")
        return 0


def get_ce_price(option_chain_json, strike_price,txType):
    for dictt in option_chain_json['records']['data']:
        if dictt['strikePrice'] == strike_price and dictt['expiryDate'] == expiry_month:
            if txType == TranxType.SELL:
                ce_price = dictt['CE']['bidprice']
            else :
                ce_price = dictt['CE']['askPrice']
            return ce_price
    else:
        print(f"No instrument found with the given strike {strike_price}.")
        return 0


def get_fno_stocks():
    """
    Get list of FNO stocks
    :return:
    """
    fnoList = fnolist()
    not_containing = "NIFTY"
    result_list = [elem for elem in fnoList if not_containing not in elem]
    return result_list

@timeoutable()
def nse_optionchain(symbol):
    return nse_optionchain_scrapper(symbol)

def get_strike_price_list(option_chain_json):
    """
    Get the list of strike prices of the stock
    :param option_chain_json:
    :return: strike price list sorted
    """
    strike_price_list: list = [x['strikePrice'] for x in option_chain_json['filtered']['data']]
    strike_price_list.sort()
    return strike_price_list


def get_lot_size(symbol):
    """
    Return lot size of given stock
    :param symbol: 
    :return: 
    """
    global lot_sizes
    if lot_sizes.empty:
        lot_sizes = nse_get_fno_lot_sizes(mode="pandas")

    # remove spaces from column names
    lot_sizes = lot_sizes.rename(columns=lambda x: x.replace(' ', ''))
    # remove spaces from values
    lot_sizes = lot_sizes.replace('\s+', '', regex=True)

    lot_size: int = int(lot_sizes[lot_sizes["SYMBOL"] == symbol].iloc[0, 2])

    return lot_size

def get_expiry_date(wihch_month):
    return expiry_list("RELIANCE","list")[wihch_month]