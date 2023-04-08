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
    return df.drop(df.columns[(df == 0).all()], axis=1)


def concat_df(df, row):
    """
    Concat the given row to Dataframe
    :param df:
    :param row:
    :return:
    """
    df = pd.concat([df, pd.DataFrame.from_records([row])], ignore_index=True)
    return df


def underscore_to_camel_case(s):
    """
    Used to convert the df to readable sheet name for Excel
    :param s:
    :return:
    """
    # Split the string by underscores
    camel_case = ""
    for name, value in inspect.currentframe().f_back.f_locals.items():
        if value is s:
            words = s.split('_')

            # Capitalize the first letter of each word after the first
            # and join them together with spaces
            camel_case = words[0] + ' '.join(w.capitalize() for w in words[1:-1]) + words[-1].capitalize()

    return camel_case
