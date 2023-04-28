from stopit import threading_timeoutable as timeoutable

from nsepython import *
import pandas as pd
import logging

from dao.Option import TranxType

logging.basicConfig(level=logging.INFO)

lot_sizes = pd.DataFrame()
india_vix = 0


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


def get_pe_price(option_chain_json, strike_price, txType, expiry_date):
    for dictt in option_chain_json['records']['data']:
        if dictt['strikePrice'] == strike_price and dictt['expiryDate'] == expiry_date:
            if txType == TranxType.SELL:
                pe_price = dictt['PE']['bidprice']
            else:
                pe_price = dictt['PE']['askPrice']
            pe_iv = dictt['PE']['impliedVolatility']
            return pe_price, pe_iv
    else:
        print(f"No instrument found with the given strike {strike_price}.")
        return 0, 0


def get_ce_price(option_chain_json, strike_price, txType, expiry_date):
    for dictt in option_chain_json['records']['data']:
        if dictt['strikePrice'] == strike_price and dictt['expiryDate'] == expiry_date:
            if txType == TranxType.SELL:
                ce_price = dictt['CE']['bidprice']
            else:
                ce_price = dictt['CE']['askPrice']
            ce_iv = dictt['CE']['impliedVolatility']
            return ce_price, ce_iv
    else:
        print(f"No instrument found with the given strike {strike_price}.")
        return 0, 0


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


def get_india_vix():
    """
    Returns the india vix value
    Returns:

    """
    global india_vix
    if india_vix == 0:
        india_vix = indiavix()
    return india_vix


def get_black_scholes_dexter(S0, X, t, σ="", r=10, q=0.0, td=365):
    if σ == "": σ = get_india_vix()
    if σ == 0: σ = get_india_vix()
    if t == 0: t = 1 #it gives error on last day of expiry, when t is zero.

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
