from datetime import datetime, date
from stopit import threading_timeoutable as timeoutable

from nsepython import *
import pandas as pd
from helper.logger import logger

from dao.Option import TranxType, OptionType
from util.optionGreeksUtil import implied_volatility

lot_sizes = pd.DataFrame()
india_vix = 0

def get_quote(symbol):
    """
    Get the quote for the given symbol
    :param symbol:
    :return:
    """
    return nsetools_get_quote(symbol)

# ------------
# Utility methods based on nsepython scraper utility
# ------------

def get_atm_strike(option_chain_json):
    """
    Get at the money strike price from the given stock option chain
    :param option_chain_json:
    :return:
    """
    return get_strike(option_chain_json,0)

def get_strike(option_chain_json,strike_diff_perc=0):
    """
    Get the strike price from the given option chain
    :param option_chain_json:
    :param strike_diff_perc:
    """
    data = option_chain_json['filtered']['data']
    try:
        ltp = data[0]['PE']['underlyingValue']
    except:
        try:
            ltp = data[0]['CE']['underlyingValue']
        except:
            ltp = data[1]['PE']['underlyingValue']

    logger.debug(f"Got ltp: {ltp}")
    ltp = ltp * (1 + strike_diff_perc/100)
    logger.debug(f"Updated ltp with strike_diff_perc: {ltp} , strike_diff_perc: {strike_diff_perc}")
    strike_price_list = [x['strikePrice'] for x in data]
    strike = sorted([[round(abs(ltp - i), 2), i] for i in strike_price_list])[0][1]
    logger.debug(f"Got strike: {strike} in the list: {strike_price_list}")
    return strike

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
def get_optionchain(symbol):
    return nse_optionchain_scrapper(symbol)


def get_ltp(option_chain_json):
    """
    Returns the last traded price of the stock
    Args:
        option_chain_json:

    Returns:

    """
    return option_chain_json["records"]["underlyingValue"]


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
    """
    Returns the expiry date for the given expiry month
    Args:
        wihch_month:

    Returns:

    """
    return expiry_list("RELIANCE", "list")[wihch_month.value]


def get_days_to_expiry(expiry_date):
    """
    Returns the number of days left to expiry
    Args:
        expiry_date:

    Returns:

    """
    # Calculate the difference between the dates
    delta = datetime.datetime.strptime(expiry_date, "%d-%b-%Y").date() - date.today()

    # Extract the number of days between the dates
    return delta.days


def get_india_vix():
    """
    Returns the india vix value
    Returns:

    """
    global india_vix
    if india_vix == 0:
        india_vix = indiavix()
    return india_vix


def get_option_price(option_chain_json, strike_price, option_type, tranx_type, expiry_date,need_iv=True):
    """
    Returns the PE price for the given stirke price
    :param option_chain_json: get it like nse_optionchain_scrapper("DLF")
    :param strike_price: int
    :param tranx_type: TranxType.SELL or TranxType.BUY
    :param option_type: OptionType.PUT or OptionType.CALL
    It is used to get the correct price at which trade can happen, as many times there is a huge
                    difference between bid and ask price. So bid price is take when we want to sell and
                    ask price is considered when we want o buy
    :param expiry_date: 29-Feb-2024
    :return: option price, option iv

    """
    for dictt in option_chain_json['records']['data']:
        try:
            if dictt['strikePrice'] == strike_price and dictt['expiryDate'] == expiry_date:
                if tranx_type == TranxType.SELL:
                    if option_type == OptionType.PUT:
                        option_price = dictt['PE']['bidprice']
                    else:
                        option_price = dictt['CE']['bidprice']
                elif tranx_type == TranxType.BUY:
                    if option_type == OptionType.PUT:
                        option_price = dictt['PE']['askPrice']
                    else:
                        option_price = dictt['CE']['askPrice']
                elif tranx_type == TranxType.ANY:
                    # Get ltp, instead of bid or ask price
                    if option_type == OptionType.PUT:
                        option_price = dictt['PE']['lastPrice']
                    else:
                        option_price = dictt['CE']['lastPrice']

                option_iv = 0
                # Get iv only if needed.
                if need_iv :
                    if option_type == OptionType.PUT:
                        option_iv = dictt['PE']['impliedVolatility']
                    else:
                        option_iv = dictt['CE']['impliedVolatility']

                    if option_iv == 0:
                        option_iv = implied_volatility(option_price, get_ltp(option_chain_json), strike_price,
                                                   get_days_to_expiry(expiry_date), 10, OptionType.PUT, get_india_vix())
                return option_price, option_iv
        except KeyError as ke:
            logger.debug(f"Key error {ke}")
        except Exception as e:
            logger.debug(e)

    logger.debug(f"No instrument found with the given strike {strike_price} , will return price as 0.")
    return 0, 0


def get_black_scholes_dexter(S0, X, t, σ="", r=10, q=0.0, td=365):
    if σ == "": σ = get_india_vix()
    if σ == 0: σ = get_india_vix()
    if t == 0: t = 1  # it gives error on last day of expiry, when t is zero.

    S0, X, σ, r, q, t = float(S0), float(X), float(σ / 100), float(r / 100), float(q / 100), float(t / td)
    # https://unofficed.com/black-scholes-model-options-calculator-google-sheet/

    d1 = (math.log(S0 / X) + (r - q + 0.5 * σ ** 2) * t) / (σ * math.sqrt(t))
    # stackoverflow.com/questions/34258537/python-typeerror-unsupported-operand-types-for-float-and-int

    # stackoverflow.com/questions/809362/how-to-calculate-cumulative-normal-distribution
    Nd1 = (math.exp((-d1 ** 2) / 2)) / math.sqrt(2 * math.pi)
    d2 = d1 - σ * math.sqrt(t)
    Nd2 = norm.cdf(d2)
    call_theta = (-((S0 * σ * math.exp(-q * t)) / (2 * math.sqrt(t)) * (1 / (math.sqrt(2 * math.pi))) * math.exp(
        -(d1 * d1) / 2)) - (r * X * math.exp(-r * t) * norm.cdf(d2)) + (q * math.exp(-q * t) * S0 * norm.cdf(d1))) / td
    put_theta = (-((S0 * σ * math.exp(-q * t)) / (2 * math.sqrt(t)) * (1 / (math.sqrt(2 * math.pi))) * math.exp(
        -(d1 * d1) / 2)) + (r * X * math.exp(-r * t) * norm.cdf(-d2)) - (
                         q * math.exp(-q * t) * S0 * norm.cdf(-d1))) / td
    call_premium = math.exp(-q * t) * S0 * norm.cdf(d1) - X * math.exp(-r * t) * norm.cdf(d1 - σ * math.sqrt(t))
    put_premium = X * math.exp(-r * t) * norm.cdf(-d2) - math.exp(-q * t) * S0 * norm.cdf(-d1)
    call_delta = math.exp(-q * t) * norm.cdf(d1)
    put_delta = math.exp(-q * t) * (norm.cdf(d1) - 1)
    gamma = (math.exp(-r * t) / (S0 * σ * math.sqrt(t))) * (1 / (math.sqrt(2 * math.pi))) * math.exp(-(d1 * d1) / 2)
    vega = ((1 / 100) * S0 * math.exp(-r * t) * math.sqrt(t)) * (
            1 / (math.sqrt(2 * math.pi)) * math.exp(-(d1 * d1) / 2))
    call_rho = (1 / 100) * X * t * math.exp(-r * t) * norm.cdf(d2)
    put_rho = (-1 / 100) * X * t * math.exp(-r * t) * norm.cdf(-d2)

    return call_theta, put_theta, call_premium, put_premium, call_delta, put_delta, gamma, vega, call_rho, put_rho


# print(get_option_price(nse_optionchain_scrapper("DLF"),900,OptionType.PUT,TranxType.BUY,expiry_list("DLF","list")[0]))
# print(expiry_list("DLF","list")[0])
# print(nse_optionchain_scrapper("DLF"))