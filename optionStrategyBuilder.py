import datetime
import logging
import pandas as pd

from util.nseUtil import get_fno_stocks, nse_optionchain
from util.optionStratagies import long_iron_butterfly

long_iron_butterfly_df = pd.DataFrame(
    columns=['Stock', 'PremiumCredit', 'MaxProfit', 'MaxLoss', 'CE_sell_price', 'CE_sell_strike',
             'PE_sell_price', 'PE_sell_strike', 'CE_buy_price', 'CE_buy_strike',
             'PE_buy_price', 'PE_buy_strike', 'lot_size', 'Strikes'])

write_to_file = True

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Get the list of Fno stocks
    fno_stock_list = get_fno_stocks() # For running it for less stocks add [:2], it will run for 2 stocks
    print("---Starting loop for all fno stocks----")
    print("-##################################################################################-")
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
                # logging.DEBUG(option_chain_json)

                df = long_iron_butterfly(symbol, option_chain_json, timeout=20)
                if df is None:
                    raise Exception("Timed Out")

                print(f"For {df.get('Stock')} total credit is {df.get('PremiumCredit')} ,"
                      f"max_profit is {df.get('MaxProfit')}"
                      f" and max_loss is {df.get('MaxLoss')}")

                # Add the new row to the DataFrame with index=0
                long_iron_butterfly_df = pd.concat([long_iron_butterfly_df, pd.DataFrame.from_records([df])],
                                                   ignore_index=True)

                # Write all the outputs as exit in between misses all the data
                if write_to_file:
                    output_file = './data/output/' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xlsx'
                    with pd.ExcelWriter(output_file) as writer:
                        long_iron_butterfly_df.to_excel(writer, sheet_name='Long Iron Butterfly')

            except Exception as ex:
                # Many times the nse website response gets stuck an results in whole program halts
                logging.error(f"Error in processing {symbol} is: ", ex)

    finally:  # Required as not to miss the data which is already fetched and save it
        # #write the output the final sheet
        if write_to_file:
            output_file = './data/output/' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xlsx'
            with pd.ExcelWriter(output_file) as writer:
                long_iron_butterfly_df.to_excel(writer, sheet_name='Long Iron Butterfly')