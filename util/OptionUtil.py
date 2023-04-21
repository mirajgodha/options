import logging

from dao.Option import Option, OptionType, TranxType
from util.nsepythonUtil import get_strike_price_list, get_atm_strike, get_pe_price, get_ce_price, get_lot_size
from util.profitLossCalculator import calc_profit_loss
from util.utils import get_nth_option, reduce_pl_strike_list


def generate_strategy(strategy: [Option], symbol, option_chain_json):
    """
    Generates the option strategy for the given strategy list and its returns its corresponding df
    :param strategy: List of options trades which need to be executed for given option strategy
    :param symbol: Stock name
    :param option_chain_json: price data from NSE
    :return: df which contains data which can be printed in Excel
    """
    # find the index of the item you want to get the value before
    strike_price_list = get_strike_price_list(option_chain_json)

    atm_strike = get_atm_strike(option_chain_json)
    logging.info(f"Strike price for {symbol} is {atm_strike}")

    index_of_item = strike_price_list.index(atm_strike)

    for option in strategy:
        option.strike_price = strike_price_list[index_of_item + option.strike]
        if option.option_type == OptionType.PUT:
            option.premium = get_pe_price(option_chain_json, option.strike_price, option.tranx_type)
        else:
            option.premium = get_ce_price(option_chain_json, option.strike_price, option.tranx_type)

    lot_size = get_lot_size(symbol)

    max_profit, max_loss, premium_received, pl_on_strikes = calc_profit_loss(strategy, lot_size, strike_price_list)

    # Create a DF so that it can be printed into Excel.
    df = {'Stock': symbol, 'PremiumCredit': premium_received, 'MaxProfit': max_profit, 'MaxLoss': max_loss,
          'CE_sell_price': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.SELL).premium,
          'CE_sell_strike': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.SELL).strike_price,
          'PE_sell_price': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.SELL).premium,
          'PE_sell_strike': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.SELL).strike_price,
          'CE_buy_price': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.BUY).premium,
          'CE_buy_strike': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.BUY).strike_price,
          'PE_buy_price': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.BUY).premium,
          'PE_buy_strike': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.BUY).strike_price,
          'CE_sell_price_1': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.SELL, n=2).premium,
          'CE_sell_strike_1': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.SELL, n=2).strike_price,
          'PE_sell_price_1': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.SELL, n=2).premium,
          'PE_sell_strike_1': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.SELL, n=2).strike_price,
          'CE_buy_price_1': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.BUY, n=2).premium,
          'CE_buy_strike_1': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.BUY, n=2).strike_price,
          'PE_buy_price_1': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.BUY, n=2).premium,
          'PE_buy_strike_1': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.BUY, n=2).strike_price,
          'CE_sell_price_2': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.SELL, n=3).premium,
          'CE_sell_strike_2': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.SELL, n=3).strike_price,
          'PE_sell_price_2': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.SELL, n=3).premium,
          'PE_sell_strike_2': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.SELL, n=3).strike_price,
          'CE_buy_price_2': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.BUY, n=3).premium,
          'CE_buy_strike_2': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.CALL and x.tranx_type == TranxType.BUY, n=3).strike_price,
          'PE_buy_price_2': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.BUY, n=3).premium,
          'PE_buy_strike_2': get_nth_option(strategy, condition=lambda
              x: x.option_type == OptionType.PUT and x.tranx_type == TranxType.BUY, n=3).strike_price,
          'lot_size': lot_size,
          'pl_on_strikes': reduce_pl_strike_list(pl_on_strikes),
          'Strikes': strike_price_list}

    return df
