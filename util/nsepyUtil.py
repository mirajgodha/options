from nsepy import get_quote, get_history
from datetime import date, datetime, timedelta

from nsepy import get_expiry_date

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

lot_sizes = pd.DataFrame()
#----------------------
# This class contains utility method based on nsepy package
#------------------

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
