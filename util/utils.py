import inspect
import logging
from datetime import datetime, date

from dao.Option import Option, OptionType, TranxType
import pandas as pd
import numpy as np
from util import optionStrategies


def get_nth_option(options, condition, n=1):
    """
    Returns the first or nth matching option from the given options list.
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
    # Requested option does not exists, return a dummy value.
    return Option(option_type=OptionType.CALL, tranx_type=TranxType.SELL, expiry_date="", strike=0)


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


def clear_df(df, sort_by=['MaxLoss', 'PremiumCredit'], sort_order=[False, False]):
    """
    Clears the df by removing all the columns which just contains the value 0 in all rows.
    Also removes the columns which do not contain any value or empty string or NAN
    :param df:
    :return:
    """
    # Remove columns which do not contain any value for this strategy
    df = df.drop(df.columns[(df == 0).all() | (df.isna().all())], axis=1)

    # filter for rows where all columns containing 'price' keyword and have values greater than 0
    df = df.loc[~df.filter(like='price').eq(0).any(axis=1)]

    try:
        df_sorted = df.sort_values(by=sort_by, ascending=sort_order)
    except:
        df_sorted = df

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


def get_list_option_strategies():
    """
    Retruns all the option strategies defined.

    Returns:

    """
    # Get all function names of MyClass
    function_names = [func for func in dir(optionStrategies.OptionStrategies) if
                      callable(getattr(optionStrategies.OptionStrategies, func)) and not func.startswith("__")]

    # Print the function names
    for name in function_names:
        print(name)


def get_days_to_expiry(expiry_date):
    """
    Returns the number of days left to expiry
    Args:
        expiry_date:

    Returns:

    """
    # Calculate the difference between the dates
    delta = datetime.strptime(expiry_date, "%d-%b-%Y").date() - date.today()

    # Extract the number of days between the dates
    return delta.days
