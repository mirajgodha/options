import logging
from stopit import threading_timeoutable as timeoutable

from util.nseUtil import get_atm_strike, get_pe_price, get_ce_price, get_strike_price_list, get_lot_size

@timeoutable()
def long_iron_butterfly(symbol, option_chain_json, strike_diff=1):
    """
    Sell the PE and CE at ATM
    Buy PE and CE at one strike below and above
    :param symbol:
    :param option_chain_json:
    :param strike_diff:
    :return:
    """
    atm_strike = get_atm_strike(option_chain_json)
    logging.info(f"Strike price for {symbol} is {atm_strike}")

    pe_atm_premium = get_pe_price(option_chain_json, atm_strike)
    ce_atm_premium = get_ce_price(option_chain_json, atm_strike)

    logging.info(f"PE sell price {pe_atm_premium} and CE sell price : {ce_atm_premium}")

    # find the index of the item you want to get the value before
    strike_price_list = get_strike_price_list(option_chain_json)
    index_of_item = strike_price_list.index(atm_strike)

    # get the value at the index one less than the index of the specified item
    lower_strike = strike_price_list[index_of_item - strike_diff]
    upper_strike = strike_price_list[index_of_item + strike_diff]

    pe_lower_strike_premium = get_pe_price(option_chain_json, lower_strike)
    ce_upper_strike_premium = get_ce_price(option_chain_json, upper_strike)

    logging.info(f"PE buy price is {pe_lower_strike_premium} at strike {lower_strike}"
                 f" and CE buy price : {ce_upper_strike_premium} at strike {upper_strike}")

    lot_size = get_lot_size(symbol)

    option_list = [("call", "sell", atm_strike, ce_atm_premium, 1),
                   ("put", "sell", atm_strike, pe_atm_premium, 1),
                   ("call", "buy", upper_strike, ce_upper_strike_premium, 1),
                   ("put", "buy", lower_strike, pe_lower_strike_premium, 1)]

    max_profit, max_loss, premium_received = calc_profit_loss(option_list, lot_size, strike_price_list)

    df = {'Stock': symbol, 'PremiumCredit': premium_received, 'MaxProfit': max_profit, 'MaxLoss': max_loss,
          'CE_sell_price': ce_atm_premium, 'CE_sell_strike': atm_strike,
          'PE_sell_price': pe_atm_premium, 'PE_sell_strike': atm_strike,
          'CE_buy_price': ce_upper_strike_premium, 'CE_buy_strike': upper_strike,
          'PE_buy_price': pe_lower_strike_premium, 'PE_buy_strike': lower_strike,
          'lot_size': lot_size, 'Strikes': strike_price_list}
    return df


def option_pl_calculator(option_type, transaction_type, strike_price, premium, lots, expiry_price, lot_size):
    """
    Calculates the profit or loss for a given option at expiry stock price.

    Parameters:
    option_type (str): The type of option, either "call" or "put".
    transaction_type (str): The type of transaction, either "buy" or "sell".
    strike_price (float): The strike price of the option.
    premium (float): The premium paid or received for the option.
    expiry_price (float): The stock price at expiry.

    Returns:
    float: The profit or loss for the option at expiry.
    """

    # Calculate the payoff at expiry
    if option_type == "call":
        payoff = max(expiry_price - strike_price, 0)
    elif option_type == "put":
        payoff = max(strike_price - expiry_price, 0)

    # Calculate the profit or loss based on the transaction type
    if transaction_type == "buy":
        pl = payoff - premium
    elif transaction_type == "sell":
        pl = premium - payoff

    return round(pl * lot_size * lots, 0)


def calc_profit_loss(option_list, lot_size, strike_price_list):
    logging.debug(f"option_list= {option_list}")
    logging.debug(f"lot_size={lot_size}")

    premium_received = 0.0
    for option in option_list:
        option_type, transaction_type, strike_price, premium, lots = option
        # Calculate the profit or loss based on the transaction type
        if transaction_type == "buy":
            premium_received = (premium_received - premium) * lots
        elif transaction_type == "sell":
            premium_received = (premium_received + premium) * lots

    premium_received = round(premium_received * lot_size, 0)
    logging.info(f"Premium received {premium_received}")
    max_profit = max(premium_received, 0)
    max_loss = min(premium_received, 0)

    for expiry_price in strike_price_list:
        pl = 0.0
        for option in option_list:
            option_type, transaction_type, strike_price, premium, lots = option
            pl += option_pl_calculator(option_type, transaction_type, strike_price, premium, lots, expiry_price,
                                       lot_size)
        max_profit = max(pl, max_profit)
        max_loss = min(pl, max_loss)
        logging.info(f"P&L {pl} for expiry_price {expiry_price}")

    return round(max_profit, 0), round(max_loss, 0), premium_received
