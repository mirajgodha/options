import logging
from typing import List

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
    logging.debug(f"option_list= {option_list}")
    logging.debug(f"lot_size={lot_size}")

    premium_received = 0.0
    for option in option_list:
        # Calculate the profit or loss based on the transaction type
        if option.tranx_type == TranxType.BUY:
            premium_received = (premium_received - option.premium) * option.lots
        elif option.tranx_type == TranxType.SELL:
            premium_received = (premium_received + option.premium) * option.lots

    premium_received = round(premium_received * lot_size, 0)
    logging.info(f"Premium received {premium_received}")
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

        logging.debug(f"P&L {pl} for expiry_price {expiry_price}")

    return round(max_profit / 10, 0) * 10, round(max_loss / 10, 0) * 10, premium_received, pl_on_strikes
