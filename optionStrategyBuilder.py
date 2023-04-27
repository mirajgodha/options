import datetime
import logging
import pandas as pd

from dao.Option import Expiry
from util.nsepythonUtil import get_fno_stocks, get_optionchain, get_expiry_date
from util.optionStrategies import OptionStrategies
from util.utils import clear_df, concat_df

# Expiry month for which we want to run the utility
expiry_month = Expiry.NEXT
test_run = False
write_to_file = True

excel_columns = ['Stock', 'PremiumCredit', 'MaxProfit', 'MaxLoss', 'LTP',
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


def write_to_excel():
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

    long_call_condor_df = clear_df(long_call_condor_df)
    long_iron_butterfly_df = clear_df(long_iron_butterfly_df)
    long_put_condor_df = clear_df(long_put_condor_df)
    short_call_butterfly_df = clear_df(short_call_butterfly_df)
    short_call_condor_df = clear_df(short_call_condor_df)
    short_guts_df = clear_df(short_guts_df)
    short_iron_butterfly_df = clear_df(short_iron_butterfly_df)
    short_put_butterfly_df = clear_df(short_put_butterfly_df)
    short_put_condor_df = clear_df(short_put_condor_df)
    short_straddle_df = clear_df(short_straddle_df, sort_by=['MaxProfit', 'PremiumCredit'], sort_order=[False, False])
    short_strangle_df = clear_df(short_strangle_df, sort_by=['MaxProfit', 'PremiumCredit'], sort_order=[False, False])

    if write_to_file:
        output_file = './data/output/' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xlsx'
        with pd.ExcelWriter(output_file) as writer:
            long_call_condor_df.to_excel(writer, sheet_name="long_call_condor_df")
            long_iron_butterfly_df.to_excel(writer, sheet_name="long_iron_butterfly_df")
            long_put_condor_df.to_excel(writer, sheet_name="long_put_condor_df")
            short_call_butterfly_df.to_excel(writer, sheet_name="short_call_butterfly_df")
            short_call_condor_df.to_excel(writer, sheet_name="short_call_condor_df")
            short_guts_df.to_excel(writer, sheet_name="short_guts_df")
            short_iron_butterfly_df.to_excel(writer, sheet_name="short_iron_butterfly_df")
            short_put_butterfly_df.to_excel(writer, sheet_name="short_put_butterfly_df")
            short_put_condor_df.to_excel(writer, sheet_name="short_put_condor_df")
            short_straddle_df.to_excel(writer, sheet_name="short_straddle_df")
            short_strangle_df.to_excel(writer, sheet_name="short_strangle_df")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Get the list of Fno stocks
    if test_run:
        fno_stock_list = get_fno_stocks()[:5]  # For running it for less stocks add [:2], it will run for 2 stocks
    else:
        fno_stock_list = get_fno_stocks()

    expiry_date = get_expiry_date(expiry_month)

    print("---Starting loop for all fno stocks----")
    i = 1
    try:
        for symbol in fno_stock_list:
            try:
                logging.info(f"{i}. Running for {symbol}")
                option_chain_json = get_optionchain(symbol, timeout=20)
                if option_chain_json is None:
                    raise Exception("Timed Out")
                logging.debug(f"Got option chain for {symbol}")

                i += 1
                logging.debug(option_chain_json)

                # Add the new row to the DataFrame with index=0
                long_call_condor_df = concat_df(long_call_condor_df,
                                                OptionStrategies.long_call_condor(symbol, option_chain_json,
                                                                                  expiry_date,
                                                                                  strike_diff=2,
                                                                                  timeout=20))
                long_iron_butterfly_df = concat_df(long_iron_butterfly_df,
                                                   OptionStrategies.long_iron_butterfly(symbol, option_chain_json,
                                                                                        expiry_date,
                                                                                        strike_diff=2,
                                                                                        timeout=20))
                long_put_condor_df = concat_df(long_put_condor_df,
                                               OptionStrategies.long_put_condor(symbol, option_chain_json, expiry_date,
                                                                                timeout=20))

                short_call_butterfly_df = concat_df(short_call_butterfly_df,
                                                    OptionStrategies.short_call_butterfly(symbol, option_chain_json,
                                                                                          expiry_date,
                                                                                          timeout=20))
                short_call_condor_df = concat_df(short_call_condor_df,
                                                 OptionStrategies.short_call_condor(symbol, option_chain_json,
                                                                                    expiry_date,
                                                                                    timeout=20))
                short_guts_df = concat_df(short_guts_df,
                                          OptionStrategies.short_guts(symbol, option_chain_json, expiry_date,
                                                                      timeout=20))

                short_iron_butterfly_df = concat_df(short_iron_butterfly_df,
                                                    OptionStrategies.short_iron_butterfly(symbol, option_chain_json,
                                                                                          expiry_date,
                                                                                          timeout=20))
                short_put_butterfly_df = concat_df(short_put_butterfly_df,
                                                   OptionStrategies.short_put_butterfly(symbol, option_chain_json,
                                                                                        expiry_date,
                                                                                        timeout=20))
                short_put_condor_df = concat_df(short_put_condor_df,
                                                OptionStrategies.short_put_condor(symbol, option_chain_json,
                                                                                  expiry_date,
                                                                                  timeout=20))
                short_straddle_df = concat_df(short_straddle_df,
                                              OptionStrategies.short_straddle(symbol, option_chain_json, expiry_date,
                                                                              timeout=20))

                short_strangle_df = concat_df(short_strangle_df,
                                              OptionStrategies.short_strangle(symbol, option_chain_json, expiry_date,
                                                                              strike_diff=4,
                                                                              timeout=20))

                # Write all the outputs as exit in between misses all the data
                # write_to_excel()

            except Exception as ex:
                # Many times the nse website response gets stuck an results in whole program halts
                logging.error(f"Error in processing {symbol} is: ", ex)

    finally:  # Required as not to miss the data which is already fetched and save it
        # #write the output the final sheet
        write_to_excel()
