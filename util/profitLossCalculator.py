from helper.logger import logger
from typing import List

from util.nsepythonUtil import get_black_scholes_dexter, get_days_to_expiry
from util.optionStrategies import Option, OptionType, TranxType


def option_pl_calculator(option: Option, expiry_price, lot_size):
    """
    Calculates the profit or loss for a given option at expiry stock price.

    Parameters:
    optiton (Option): Options details
    expiry_price (float): The stock price at expiry.

    Returns:
    float: The profit or loss for the option at expiry.
    """

    # Calculate the payoff at expiry
    if option.option_type == OptionType.CALL:
        payoff = max(expiry_price - option.strike_price, 0)
    elif option.option_type == OptionType.PUT:
        payoff = max(option.strike_price - expiry_price, 0)

    # Calculate the profit or loss based on the transaction type
    if option.tranx_type == TranxType.BUY:
        pl = payoff - option.premium
    elif option.tranx_type == TranxType.SELL:
        pl = option.premium - payoff

    return round(pl * lot_size * option.lots, 0)


def calc_profit_loss(option_list: List[Option], lot_size, strike_price_list):
    """
    Calcualates the total profit and loss for the given option list
    :param option_list: option_type, transaction_type, strike_price, premium, lots
    :param lot_size:
    :param strike_price_list:
    :return:
    """
    logger.debug(f"option_list= {option_list}")
    logger.debug(f"lot_size={lot_size}")

    premium_received = 0.0
    for option in option_list:
        # Calculate the profit or loss based on the transaction type
        if option.tranx_type == TranxType.BUY:
            premium_received = (premium_received - option.premium) * option.lots
        elif option.tranx_type == TranxType.SELL:
            premium_received = (premium_received + option.premium) * option.lots

    premium_received = round(premium_received * lot_size, 0)
    logger.debug(f"Premium received {premium_received}")
    max_profit = max(premium_received, 0)
    max_loss = min(premium_received, 0)
    pl_on_strikes = []

    for expiry_price in strike_price_list:
        pl = 0.0
        for option in option_list:
            pl += option_pl_calculator(option, expiry_price, lot_size)

        max_profit = max(pl, max_profit)
        max_loss = min(pl, max_loss)
        pl_on_strikes.append((round(pl / 10, 0) * 10, expiry_price))

        logger.debug(f"P&L {pl} for expiry_price {expiry_price}")

    return round(max_profit / 10, 0) * 10, round(max_loss / 10, 0) * 10, premium_received, pl_on_strikes


def calc_greeks(option_list: List[Option], lot_size, ltp):
    """
    Calcualtes the greeks for the given option strategy
    Args:
        option_list:
        lot_size:

    Returns:

    """
    delta, theta, total_delta, total_theta = 0.0, 0.0, 0.0, 0.0
    for option in option_list:
        # Calculate the greeks based on the transaction type
        logger.debug("Calculating greeks for option: " )
        logger.debug(f"Option: {option} and ltp: {ltp}")

        call_theta, put_theta, call_premium, put_premium, call_delta, put_delta, gamma, vega, call_rho, put_rho = \
            get_black_scholes_dexter(
                ltp, option.strike_price, get_days_to_expiry(option.expiry_date),
                option.iv, r=10, q=0.0, td=365)

        logger.debug(f"For option: {option}")
        logger.debug(f"Greeks are Call Theta: {call_theta:.3f}, Put Theta: {put_theta:.3f}, Call Premium: "
                     f"{call_premium:.3f}, Put Premium: {put_premium:.3f}, Call Delta: {call_delta:.3f}, "
                     f"Put Delta: {put_delta:.3f}, Gamma: {gamma:.3f}, Vega: {vega:.3f}, "
                     f"Call Rho: {call_rho:.3f}, Put Rho: {put_rho:.3f}")

        if option.option_type == OptionType.PUT:
            if option.tranx_type == TranxType.SELL:
                theta += -1 * put_theta
                delta += -1 * put_delta
            else:
                theta += put_theta
                delta += put_delta
        if option.option_type == OptionType.CALL:
            if option.tranx_type == TranxType.SELL:
                theta += -1 * call_theta
                delta += -1 * call_delta
            else:
                theta += call_theta
                delta += call_delta

    return delta, theta, round(delta * lot_size,0), round(theta * lot_size,0)


def get_iv(option_list: List[Option]):
    """
    Returns the avg iv of all option trades
    Rounded to nearest integer
    Args:
        option_list:

    Returns:

    """
    sum_iv = 0
    total = 0
    for option in option_list:
        sum_iv += option.iv
        if option.iv != 0:
            total += 1
    if total == 0:
        total = 1
    return round(sum_iv / total,0)
