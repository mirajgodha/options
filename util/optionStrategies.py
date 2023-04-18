from stopit import threading_timeoutable as timeoutable

from dao.Option import Option, OptionType, TranxType
from util.OptionUtil import generate_strategy


class OptionStrategies:

    @timeoutable()
    def long_iron_butterfly(symbol, option_chain_json, strike_diff: int = 1):
        """
        Sell the PE and CE at ATM
        Buy PE and CE at one strike below and above
        :param option_chain_json:
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
    def short_iron_butterfly(symbol, option_chain_json, strike_diff: int = 1):
        """
        Buy the PE and CE at ATM
        Sell PE and CE at one strike below and above
        :param option_chain_json:
        :param strike_diff: The default strike difference is 1, but we can pass it as int.
                            If strike diff is 2 then the PUT and CALL which will be buyed will be one strike above the ATM.
        :return: df
        """

        strategy = [Option(option_type=OptionType.CALL, tranx_type=TranxType.BUY, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.BUY, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=-1 * strike_diff, lots=1)]

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


    @timeoutable()
    def short_put_butterfly(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the short put butterfly
        Buy 2 put at ATM
        Sell one upper and lower put
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.PUT, tranx_type=TranxType.BUY, strike=0 * strike_diff, lots=2),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=-1 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)


    @timeoutable()
    def short_call_condor(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the Long call condor
        Buy 1 call at ATM
        Buy 1 upper call
        Sell 1 2nd upper call
        Sell 1 lower call
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.CALL, tranx_type=TranxType.BUY, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.BUY, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=2 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=-1 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)

    @timeoutable()
    def long_call_condor(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the Long call condor
        Buy 1 call at below ATM
        Sell 1 ATM call
        Buy 1 2nd upper call
        Sell 1 above ATM call
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.BUY, strike=2 * strike_diff, lots=1),
                    Option(option_type=OptionType.CALL, tranx_type=TranxType.BUY, strike=-1 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)

    @timeoutable()
    def short_put_condor(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the Short put condor
        Buy 1 put at ATM
        Buy 1 upper put
        Sell 1 2nd upper put
        Sell 1 lower put
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.PUT, tranx_type=TranxType.BUY, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.BUY, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=2 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=-1 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)

    @timeoutable()
    def long_put_condor(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the Short put condor
        Buy 1 put blow ATM
        Sell 1 put at ATM
        Sell 1 PUT above ATM
        Sell 1 put 2nd above ATM
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.BUY, strike=2 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.BUY, strike=-1 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)

    @timeoutable()
    def short_straddle(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the Long call condor
        Sell 1 call at ATM
        Sell 1 put at ATM
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=0 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=0 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)

    @timeoutable()
    def short_strangle(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the Long call condor
        Sell 1 call at above ATM
        Sell 1 put at below ATM
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=1 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=-1 * strike_diff, lots=1)]

        return generate_strategy(strategy, symbol, option_chain_json)

    @timeoutable()
    def short_guts(symbol, option_chain_json, strike_diff=1):
        """
        Calculates the Long call condor
        Sell 1 call at below ATM
        Sell 1 put at above ATM
        :param symbol:
        :param option_chain_json:
        :param strike_diff:
        :return:
        """

        strategy = [Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=-1 * strike_diff, lots=1),
                    Option(option_type=OptionType.PUT, tranx_type=TranxType.SELL, strike=1 * strike_diff, lots=1)]
        return generate_strategy(strategy, symbol, option_chain_json)