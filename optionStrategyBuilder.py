import datetime
import logging
import pandas as pd

from util.nseUtil import get_fno_stocks, nse_optionchain
from util.optionStrategies import OptionStrategies
from util.utils import clear_df, concat_df

excel_columns = ['Stock', 'PremiumCredit', 'MaxProfit', 'MaxLoss',
                 'CE_sell_price', 'CE_sell_strike',
                 'PE_sell_price', 'PE_sell_strike',
                 'CE_buy_price', 'CE_buy_strike',
                 'PE_buy_price', 'PE_buy_strike',
                 'CE_sell_price_1', 'CE_sell_strike_1',
                 'PE_sell_price_1', 'PE_sell_strike_1',
                 'CE_buy_price_1', 'CE_buy_strike_1',
                 'PE_buy_price_1', 'PE_buy_strike_1',
                 'lot_size', 'pl_on_strikes', 'Strikes']


long_iron_butterfly_df = pd.DataFrame(columns=excel_columns)
short_call_butterfly_df = pd.DataFrame(columns=excel_columns)

write_to_file = True


def write_to_excel():
    """
    Writes the dfs to excel sheet
    :return:
    """
    global long_iron_butterfly_df
    global short_call_butterfly_df

    long_iron_butterfly_df = clear_df(long_iron_butterfly_df)
    short_call_butterfly_df = clear_df(short_call_butterfly_df)

    if write_to_file:
        output_file = './data/output/' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xlsx'
        with pd.ExcelWriter(output_file) as writer:
            long_iron_butterfly_df.to_excel(writer, sheet_name="Long Iron Butterfly")
            short_call_butterfly_df.to_excel(writer, sheet_name="Short Call Butterfly")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Get the list of Fno stocks
    fno_stock_list = get_fno_stocks()  # For running it for less stocks add [:2], it will run for 2 stocks
    print("---Starting loop for all fno stocks----")
    i = 1
    try:
        for symbol in fno_stock_list:
            try:
                logging.info(f"{i}. Running for {symbol}")
                option_chain_json = nse_optionchain(symbol, timeout=20)
                if option_chain_json is None:
                    raise Exception("Timed Out")
                logging.info(f"Got option chain for {symbol}")
                i += 1
                logging.debug(option_chain_json)

                # Add the new row to the DataFrame with index=0
                long_iron_butterfly_df = concat_df(long_iron_butterfly_df,
                                                   OptionStrategies.long_iron_butterfly(symbol, option_chain_json, timeout=20))

                short_call_butterfly_df = concat_df(short_call_butterfly_df,
                                                    OptionStrategies.short_call_butterfly(symbol, option_chain_json, timeout=20))

                # Write all the outputs as exit in between misses all the data
                write_to_excel()

            except Exception as ex:
                # Many times the nse website response gets stuck an results in whole program halts
                logging.error(f"Error in processing {symbol} is: ", ex)

    finally:  # Required as not to miss the data which is already fetched and save it
        # #write the output the final sheet
        write_to_excel()
