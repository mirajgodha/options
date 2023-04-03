from nsepy import get_quote, get_history
from datetime import date, datetime, timedelta
from stopit import threading_timeoutable as timeoutable

from nsepy import get_expiry_date
from nsepython import *
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

lot_sizes = pd.DataFrame()


def find_atm_price(tick_start_price, tick_size, stock_price):
    """
    Get at the money price for the stock option, using nsepy
    :param tick_start_price:
    :param tick_size:
    :param stock_price:
    :return:
    """
    tick_count = int(round((stock_price - tick_start_price) / tick_size))
    nearest_tick_price = tick_start_price + tick_count * tick_size
    return nearest_tick_price


def find_atm_ce_price(tick_start_price, tick_size, stock_price):
    """
    Get at the money price for call
    :param tick_start_price:
    :param tick_size:
    :param stock_price:
    :return:
    """
    tick_count = int(round((stock_price - tick_start_price) / tick_size))
    if tick_start_price > stock_price:
        tick_count += 1
    if tick_count >= 0:
        tick_count += 1
    nearest_tick_price = tick_start_price + tick_count * tick_size
    return nearest_tick_price


def find_atm_pe_price(tick_start_price, tick_size, stock_price):
    """
    Get at the money price for put
    :param tick_start_price:
    :param tick_size:
    :param stock_price:
    :return:
    """
    tick_count = int(round((stock_price - tick_start_price) / tick_size))
    if tick_start_price > stock_price:
        tick_count += 1
    if tick_count <= 0:
        tick_count -= 1
    nearest_tick_price = tick_start_price + tick_count * tick_size
    return nearest_tick_price


def get_stock_price(stock, start_date, end_date):
    """
    get last close price of stock
    :param stock:
    :param start_date:
    :param end_date:
    :return:
    """
    global stock_price
    last_price = get_history(symbol=stock["Symbol"],
                             start=start_date, end=end_date)
    if len(last_price) == 0:
        stock["Last_Close"] = 0
    else:
        stock["Last_Close"] = last_price.iloc[0]["Prev Close"]


def get_stock_expiry_date():
    today = datetime.now().date()
    expiry_date = get_expiry_date(year=today.year, month=today.month, stock=True, index=False)

    if today > list(expiry_date)[0]:
        next_month = today.replace(day=28) + timedelta(days=4)
        expiry_date = get_expiry_date(year=next_month.year, month=next_month.month, stock=True, index=False)

    return list(expiry_date)[0]


def get_last_working_day(old_days=0):
    """
    Returns last nse working day
    :param old_days:
    :return:
    """
    # Get today's date
    today = datetime.today().date() - timedelta(days=old_days)

    # Get the historical data for NIFTY 50 for the last 7 days
    historical_data = get_history(symbol="SBIN", start=today - timedelta(days=7), end=today)

    # Find the last working day
    if not historical_data.empty:
        return historical_data.index[-1]
    else:
        return today


# ------------
# Based on nsepython scraper utility
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

    print(ltp)
    strike_price_list = [x['strikePrice'] for x in data]
    atm_strike = sorted([[round(abs(ltp - i), 2), i] for i in strike_price_list])[0][1]
    return atm_strike


def get_pe_price(option_chain_json, strike_price):
    for dictt in option_chain_json['filtered']['data']:
        if dictt['strikePrice'] == strike_price:
            pe_price = dictt['PE']['askPrice']
            return pe_price
    else:
        print(f"No instrument found with the given strike {strike_price}.")
        return 0


def get_ce_price(option_chain_json, strike_price):
    for dictt in option_chain_json['filtered']['data']:
        if dictt['strikePrice'] == strike_price:
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
