from stopit import threading_timeoutable as timeoutable

from dao.Option import Option, OptionType, TranxType
from util.OptionUtil import generate_strategy


class OptionStrategies:

    @timeoutable()
    def long_iron_butterfly(symbol, option_chain_json, strike_diff: int = 1):
        """
        Sell the PE and CE at ATM
        Buy PE and CE at one strike below and above
        :param strike_diff: The default strike difference is 1, but we can pass it as int.
                            If strike diff is 2 then the PUT and CALL which will be buyed will be one strike above the ATM.
        :return: df
        """

        strategy = [Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.BUY, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.BUY, strike=-1 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)

    @timeoutable()
    def short_call_butterfly(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the short call butterfly
        Buy 2 call at ATM
        Sell one upper and lower call
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.CALL, tranx_type=TranxType.BUY, strike=0 * strike_diff, lots=2),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=-1 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)

    # def long_call_condor(symbol, option_chain_json, strike_diff=1):
    #     """
    #     Calculates the Long call condor
    #     Buy 1 call at ATM
    #     Buy 1 upper call
    #     Sell 1 2nd upper call
    #     Sell 1 lower call
    #     :param symbol:
    #     :param option_chain_json:
    #     :param strike_diff:
    #     :return:
    #     """
    #     atm_strike = get_atm_strike(option_chain_json)
    #     logging.info(f"Strike price for {symbol} is {atm_strike}")
    #
    #     ce_atm_premium = get_ce_price(option_chain_json, atm_strike)
    #
    #     logging.info(f"CE buy price : {ce_atm_premium}")
    #
    #     # find the index of the item you want to get the value before
    #     strike_price_list = get_strike_price_list(option_chain_json)
    #     index_of_item = strike_price_list.index(atm_strike)
    #
    #     # get the value at the index one less than the index of the specified item
    #     lower_strike = strike_price_list[index_of_item - strike_diff]
    #     upper_strike = strike_price_list[index_of_item + strike_diff]
    #     upper_2_strike = strike_price_list[index_of_item + strike_diff * 2]
    #
    #     pe_lower_strike_premium = get_pe_price(option_chain_json, lower_strike)
    #     ce_upper_strike_premium = get_ce_price(option_chain_json, upper_strike)
    #
    #     logging.info(f"PE buy price is {pe_lower_strike_premium} at strike {lower_strike}"
    #                  f" and CE buy price : {ce_upper_strike_premium} at strike {upper_strike}")
    #
    #     lot_size = get_lot_size(symbol)
    #
    #     option_list = [("call", "sell", atm_strike, ce_atm_premium, 1),
    #                    ("put", "sell", atm_strike, pe_atm_premium, 1),
    #                    ("call", "buy", upper_strike, ce_upper_strike_premium, 1),
    #                    ("put", "buy", lower_strike, pe_lower_strike_premium, 1)]
    #
    #     max_profit, max_loss, premium_received = calc_profit_loss(option_list, lot_size, strike_price_list)
    #
    #     df = {'Stock': symbol, 'PremiumCredit': premium_received, 'MaxProfit': max_profit, 'MaxLoss': max_loss,
    #           'CE_sell_price': ce_atm_premium, 'CE_sell_strike': atm_strike,
    #           'PE_sell_price': pe_atm_premium, 'PE_sell_strike': atm_strike,
    #           'CE_buy_price': ce_upper_strike_premium, 'CE_buy_strike': upper_strike,
    #           'PE_buy_price': pe_lower_strike_premium, 'PE_buy_strike': lower_strike,
    #           'lot_size': lot_size, 'Strikes': strike_price_list}
    #     return df


