import datetime
from helper.logger import logger
import sys
import traceback

import numpy as np
import pandas as pd

import constants.constants_local as c
from dao.Option import Expiry
import sql.sqlite as sqlt
from util.nsepythonUtil import get_fno_stocks, get_optionchain, get_expiry_date
from util.optionStrategies import OptionStrategies
from util.utils import clear_df, concat_df, merge_dataframes
from helper.colours import Colors
from stopit import threading_timeoutable as timeoutable

excel_columns = ['Stock', 'PremiumCreditTotal', 'MaxProfit', 'MaxLoss', 'LTP',
                 'CE_sell_price', 'CE_sell_strike',
                 'PE_sell_price', 'PE_sell_strike',
                 'CE_buy_price', 'CE_buy_strike',
                 'PE_buy_price', 'PE_buy_strike',
                 'CE_sell_price_1', 'CE_sell_strike_1',
                 'PE_sell_price_1', 'PE_sell_strike_1',
                 'CE_buy_price_1', 'CE_buy_strike_1',
                 'PE_buy_price_1', 'PE_buy_strike_1',
                 'CE_sell_price_2', 'CE_sell_strike_2',
                 'PE_sell_price_2', 'PE_sell_strike_2',
                 'CE_buy_price_2', 'CE_buy_strike_2',
                 'PE_buy_price_2', 'PE_buy_strike_2',
                 '% Premium', 'Premium Credit',
                 'IV',
                 'delta', 'theta',
                 'total_delta', 'total_theta',
                 'lot_size', 'pl_on_strikes', 'Strikes']

# DF's for different option strategies
long_call_condor_df = pd.DataFrame(columns=excel_columns)
long_iron_butterfly_df = pd.DataFrame(columns=excel_columns)
long_put_condor_df = pd.DataFrame(columns=excel_columns)
short_call_butterfly_df = pd.DataFrame(columns=excel_columns)
short_call_condor_df = pd.DataFrame(columns=excel_columns)
short_guts_df = pd.DataFrame(columns=excel_columns)
short_iron_butterfly_df = pd.DataFrame(columns=excel_columns)
short_put_butterfly_df = pd.DataFrame(columns=excel_columns)
short_put_condor_df = pd.DataFrame(columns=excel_columns)
short_straddle_df = pd.DataFrame(columns=excel_columns)
short_strangle_df = pd.DataFrame(columns=excel_columns)
concatenate_df = pd.DataFrame(columns=excel_columns)
naked_call_df = pd.DataFrame(columns=excel_columns)
naked_put_df = pd.DataFrame(columns=excel_columns)


def write_data():
    """
    Writes the dfs to excel sheet
    :return:
    """
    global long_call_condor_df
    global long_iron_butterfly_df
    global long_put_condor_df
    global short_call_butterfly_df
    global short_call_condor_df
    global short_guts_df
    global short_iron_butterfly_df
    global short_put_butterfly_df
    global short_put_condor_df
    global short_straddle_df
    global short_strangle_df
    global naked_call_df
    global naked_put_df
    global concatenate_df

    long_call_condor_df = clear_df(long_call_condor_df)
    long_iron_butterfly_df = clear_df(long_iron_butterfly_df)
    long_put_condor_df = clear_df(long_put_condor_df)
    short_call_butterfly_df = clear_df(short_call_butterfly_df)
    short_call_condor_df = clear_df(short_call_condor_df, sort_by=['MaxProfit', 'MaxLoss'], sort_order=[False, True])
    short_guts_df = clear_df(short_guts_df, sort_by=['PremiumCredit', 'MaxLoss'], sort_order=[False, True])
    short_iron_butterfly_df = clear_df(short_iron_butterfly_df)
    short_put_butterfly_df = clear_df(short_put_butterfly_df)
    short_put_condor_df = clear_df(short_put_condor_df)
    short_straddle_df = clear_df(short_straddle_df, sort_by=['% Premium', 'PremiumCredit'], sort_order=[False, False])
    short_strangle_df = clear_df(short_strangle_df, sort_by=['PremiumCredit', 'IV'], sort_order=[False, False])

    concatenate_df = merge_dataframes(long_call_condor_df, long_iron_butterfly_df, long_put_condor_df,
                                      short_call_butterfly_df, short_call_condor_df, short_guts_df,
                                      short_iron_butterfly_df, short_put_butterfly_df,
                                      short_put_condor_df)
    concatenate_df = clear_df(concatenate_df, sort_by=['MaxLoss', 'MaxProfit'], sort_order=[False, False])

    if c.OPTIONS_STRATEGIES_WRITE_TO_FILE:
        with pd.ExcelWriter(c.OPTIONS_STRATEGIES_EXEL_FILE) as writer:
            short_straddle_df.to_excel(writer, sheet_name="short_straddle_df")
            short_strangle_df.to_excel(writer, sheet_name="short_strangle_df")
            concatenate_df.to_excel(writer, sheet_name="All_Strategies_Profitable")
            short_guts_df.to_excel(writer, sheet_name="short_guts_df")
            long_call_condor_df.to_excel(writer, sheet_name="long_call_condor_df")
            long_put_condor_df.to_excel(writer, sheet_name="long_put_condor_df")
            short_call_condor_df.to_excel(writer, sheet_name="short_call_condor_df")
            short_put_condor_df.to_excel(writer, sheet_name="short_put_condor_df")
            long_iron_butterfly_df.to_excel(writer, sheet_name="long_iron_butterfly_df")
            short_iron_butterfly_df.to_excel(writer, sheet_name="short_iron_butterfly_df")
            short_call_butterfly_df.to_excel(writer, sheet_name="short_call_butterfly_df")
            short_put_butterfly_df.to_excel(writer, sheet_name="short_put_butterfly_df")
            naked_call_df.to_excel(writer, sheet_name="naked_call_df")
            naked_put_df.to_excel(writer, sheet_name="naked_put_df")

        logger.debug("Excel file created successfully")
    if c.OPTIONS_STRATEGIES_WRITE_TO_DB:
        conn_inner = sqlt.get_conn()
        try:

            # drop columns which create issues while inserting the data to db and of not much use.
            short_straddle_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            short_straddle_df.to_sql('os_short_straddle', conn_inner, if_exists='replace', index=False)
            logger.debug("os_short_straddle table created successfully")

            short_strangle_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            short_strangle_df.to_sql('os_short_strangle', conn_inner, if_exists='replace', index=False)
            logger.debug("os_short_strangle table created successfully")

            naked_call_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            from tabulate import  tabulate
            logger.debug(tabulate(naked_call_df, headers='keys', tablefmt='psql'))
            naked_call_df.to_sql(name="os_naked_call", con=conn_inner, if_exists='replace', index=False)
            logger.debug("naked_call_df table created successfully")

            naked_put_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            naked_put_df.to_sql(name="os_naked_put", con=conn_inner, if_exists='replace', index=False)
            logger.debug("naked_put_df table created successfully")

            short_guts_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            short_guts_df.to_sql(name="os_short_guts", con=conn_inner, if_exists='replace', index=False)
            logger.debug("short_guts_df table created successfully")

            long_call_condor_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            long_call_condor_df.to_sql(name="os_long_call_condor", con=conn_inner, if_exists='replace', index=False)
            logger.debug("long_call_condor_df table created successfully")

            long_put_condor_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            long_put_condor_df.to_sql(name="os_long_put_condor", con=conn_inner, if_exists='replace', index=False)
            logger.debug("long_put_condor_df table created successfully")

            short_call_condor_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            short_call_condor_df.to_sql(name="os_short_call_condor", con=conn_inner, if_exists='replace', index=False)
            logger.debug("short_call_condor_df table created successfully")

            short_put_condor_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            short_put_condor_df.to_sql(name="os_short_put_condor", con=conn_inner, if_exists='replace', index=False)
            logger.debug("short_put_condor_df table created successfully")

            long_iron_butterfly_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            long_iron_butterfly_df.to_sql(name="os_long_iron_butterfly", con=conn_inner, if_exists='replace',
                                          index=False)
            logger.debug("long_iron_butterfly_df table created successfully")

            short_iron_butterfly_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            short_iron_butterfly_df.to_sql(name="os_short_iron_butterfly", con=conn_inner, if_exists='replace',
                                           index=False)
            logger.debug("short_iron_butterfly_df table created successfully")

            short_call_butterfly_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            short_call_butterfly_df.to_sql(name="os_short_call_butterfly", con=conn_inner, if_exists='replace',
                                           index=False)
            logger.debug("short_call_butterfly_df table created successfully")

            short_put_butterfly_df.drop(columns=['pl_on_strikes', 'Strikes'], inplace=True)
            short_put_butterfly_df.to_sql(name="os_short_put_butterfly", con=conn_inner, if_exists='replace',
                                          index=False)
            logger.debug("short_put_butterfly_df table created successfully")

            if concatenate_df is not None and not concatenate_df.empty and len(concatenate_df) > 0:
                # check if df has columns then only drop them
                if 'pl_on_strikes' in concatenate_df.columns:
                    concatenate_df.drop(columns=['pl_on_strikes'], inplace=True)
                if 'Strikes' in concatenate_df.columns:
                    concatenate_df.drop(columns=['Strikes'], inplace=True)
                concatenate_df.to_sql('os_all_strategies_profitable', conn_inner, if_exists='replace', index=False)
                logger.debug("concatenate_df table created successfully")

        except Exception as e:
            print(f"{Colors.RED}Error inserting data for options strategies {e}{Colors.RESET}")
            traceback.print_exc(file=sys.stdout)
        finally:
            try:
                conn_inner.commit()
            except:
                pass

@timeoutable()
def option_strategies_builder():
    """
    Function to build option strategies
    :return:
    """
    os_last_update_time = sqlt.get_last_updated_time(c.OPTIONS_STRATEGIES_STATUS_TABLE_NAME
                                                     , f"status = '{c.PROCESS_COMPLETED}'")
    if os_last_update_time > (
            datetime.datetime.now() - datetime.timedelta(minutes=c.OPTION_STRATEGIES_DELAY_TIME)):
        # Updated MWPL less than a hour ago, so not updating now.
        logger.debug(f"Option Strategies already updated at {os_last_update_time}, so not updating now.")
        return

    sqlt.insert_os_lastupdated("os_status", c.PROCESS_STARTED)

    # Get the list of Fno stocks
    global long_call_condor_df, long_iron_butterfly_df, long_put_condor_df, short_call_butterfly_df, \
        short_call_condor_df, short_guts_df, short_iron_butterfly_df, short_put_butterfly_df, \
        short_put_condor_df, short_straddle_df, short_strangle_df, naked_call_df, naked_put_df

    if c.OPTIONS_STRATEGIES_TEST_RUN:
        fno_stock_list = get_fno_stocks()[:5]  # For running it for less stocks add [:2], it will run for 2 stocks
    else:
        fno_stock_list = get_fno_stocks()

    expiry_date = get_expiry_date(c.OPTIONS_STRATEGIES_EXPIRY_MONTH)

    logger.info(f"{Colors.GREEN}---Starting Option Trading Strategies----{Colors.RESET}")
    i = 1
    try:
        for symbol in fno_stock_list:
            try:
                logger.debug(f"{i}. {Colors.GREEN}Running for {symbol}{Colors.RESET}")
                option_chain_json = get_optionchain(symbol, timeout=20)
                if option_chain_json is None:
                    raise Exception("Timed Out")
                logger.debug(f"Got option chain for {symbol}")

                i += 1
                logger.debug(option_chain_json)

                # Add the new row to the DataFrame with index=0
                long_call_condor_df = concat_df(long_call_condor_df,
                                                OptionStrategies.long_call_condor(symbol, option_chain_json,
                                                                                  expiry_date,
                                                                                  strike_diff=c.OPTIONS_STRATEGIES_STRIKE_RANGE_PERCENTAGE,
                                                                                  timeout=c.TIMEOUT_SECONDS))
                long_iron_butterfly_df = concat_df(long_iron_butterfly_df,
                                                   OptionStrategies.long_iron_butterfly(symbol, option_chain_json,
                                                                                        expiry_date,
                                                                                        strike_diff=c.OPTIONS_STRATEGIES_STRIKE_RANGE_PERCENTAGE,
                                                                                        timeout=c.TIMEOUT_SECONDS))
                long_put_condor_df = concat_df(long_put_condor_df,
                                               OptionStrategies.long_put_condor(symbol, option_chain_json, expiry_date,
                                                                                timeout=c.TIMEOUT_SECONDS))

                short_call_butterfly_df = concat_df(short_call_butterfly_df,
                                                    OptionStrategies.short_call_butterfly(symbol, option_chain_json,
                                                                                          expiry_date,
                                                                                          timeout=c.TIMEOUT_SECONDS))
                short_call_condor_df = concat_df(short_call_condor_df,
                                                 OptionStrategies.short_call_condor(symbol, option_chain_json,
                                                                                    expiry_date,
                                                                                    timeout=c.TIMEOUT_SECONDS))
                short_guts_df = concat_df(short_guts_df,
                                          OptionStrategies.short_guts(symbol, option_chain_json, expiry_date,
                                                                      timeout=c.TIMEOUT_SECONDS))

                short_iron_butterfly_df = concat_df(short_iron_butterfly_df,
                                                    OptionStrategies.short_iron_butterfly(symbol, option_chain_json,
                                                                                          expiry_date,
                                                                                          timeout=c.TIMEOUT_SECONDS))
                short_put_butterfly_df = concat_df(short_put_butterfly_df,
                                                   OptionStrategies.short_put_butterfly(symbol, option_chain_json,
                                                                                        expiry_date,
                                                                                        timeout=c.TIMEOUT_SECONDS))
                short_put_condor_df = concat_df(short_put_condor_df,
                                                OptionStrategies.short_put_condor(symbol, option_chain_json,
                                                                                  expiry_date,
                                                                                  timeout=c.TIMEOUT_SECONDS))
                short_straddle_df = concat_df(short_straddle_df,
                                              OptionStrategies.short_straddle(symbol, option_chain_json, expiry_date,
                                                                              timeout=c.TIMEOUT_SECONDS))

                short_strangle_df = concat_df(short_strangle_df,
                                              OptionStrategies.short_strangle(symbol, option_chain_json, expiry_date,
                                                                              strike_diff=c.OPTIONS_STRATEGIES_STRIKE_RANGE_PERCENTAGE,
                                                                              timeout=c.TIMEOUT_SECONDS))

                naked_call_df = concat_df(naked_call_df,
                                          OptionStrategies.naked_call(symbol, option_chain_json, expiry_date,
                                                                      strike_diff=c.OPTIONS_STRATEGIES_STRIKE_RANGE_PERCENTAGE,
                                                                      timeout=c.TIMEOUT_SECONDS))

                naked_put_df = concat_df(naked_put_df,
                                         OptionStrategies.naked_put(symbol, option_chain_json, expiry_date,
                                                                    strike_diff=c.OPTIONS_STRATEGIES_STRIKE_RANGE_PERCENTAGE,
                                                                    timeout=c.TIMEOUT_SECONDS))

                # Write all the outputs as exit in between misses all the data
                # write_to_excel()

            except Exception as ex:
                # Many times the nse website response gets stuck an results in whole program halts
                logger.error(f"{Colors.WHITE}Error in processing {symbol} is:  {ex}{Colors.RESET}")
                traceback.print_exc()

    except Exception as ex:
        logger.error(f"{Colors.RED}Error in creating option strategies is:  {ex} {Colors.RESET}")
        sqlt.insert_os_lastupdated("os_status", c.PROCESS_FAILED)

    finally:  # Required as not to miss the data which is already fetched and save it
        # #write the output the final sheet
        write_data()
        sqlt.insert_os_lastupdated("os_status", c.PROCESS_COMPLETED)

# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     option_strategies_builder()
