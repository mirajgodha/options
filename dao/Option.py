from enum import Enum


class OptionType(Enum):
    CALL = 1
    PUT = 2


class TranxType(Enum):
    SELL = 1
    BUY = 2


class Expiry(Enum):
    CURRENT = 0
    NEXT = 1
    NEXT_TO_NEXT = 2


class Option:
    def __init__(self, option_type: OptionType, tranx_type: TranxType, strike: int, expiry_date,
                 strike_price: float = 0, premium: float = 0, lots: int = 1, iv: float = 0):
        """
        inti constractor
        :param option_type:
        :param tranx_type:
        :param strike:
        :param lots:
        :return:
        """
        self.option_type: OptionType = option_type
        self.tranx_type: TranxType = tranx_type
        self.strike: strike = strike
        self.expiry_date = expiry_date
        self.lots: lots = lots
        self.strike_price = strike_price
        self.premium = premium
        self.iv = iv

    def __str__(self):
        return f"Option Type: {self.option_type}, Transaction Type: {self.tranx_type}, " \
               f"Expiry Date: {self.expiry_date}, " \
               f"Strike Price: {self.strike_price}, Premium: {self.premium}, " \
               f"Lots: {self.lots}, " \
               f"IV: {self.iv}"
