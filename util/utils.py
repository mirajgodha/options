import inspect
import logging

from dao.Option import Option, OptionType, TranxType
import pandas as pd


def get_nth_option(options, condition, n=1):
    """
    Rertusn the first or nth matching option from the given options list.
    :param options:
    :param condition:
    :param n:
    :return:
    """
    count = 0
    for option in options:
        if condition(option):
            count += 1
            if count == n:
                return option
    return Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, strike=0)


def reduce_pl_strike_list(data):
    result = []
    current_pl = None
    range_start = None

    for pl, strike in data:
        if pl != current_pl:
            # Finish previous range, start a new one
            if current_pl is not None:
                result.append((current_pl, range_start, strike))
            current_pl = pl
            range_start = strike
        else:
            # Continue current range
            pass

    # Add last range
    if current_pl is not None:
        result.append((current_pl, range_start, strike))
    return result


def clear_df(df):
    """
    Clears the df by removing all the columns which just contains the value 0 in all rows.
    :param df:
    :return:
    """
    df = df.drop(df.columns[(df == 0).all()], axis=1)
    df_sorted = df.sort_values(by=['MaxLoss', 'MaxProfit'], ascending=[False, False])
    return df_sorted


def concat_df(df, row):
    """
    Concat the given row to Dataframe
    :param df:
    :param row:
    :return:
    """
    df = pd.concat([df, pd.DataFrame.from_records([row])], ignore_index=True)
    return df
