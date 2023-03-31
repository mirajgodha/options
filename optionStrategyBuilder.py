# Get all stocks options prices to the nearest strikes
import datetime
import sys

from nsepy import get_history
from datetime import date
import matplotlib.pyplot as plt
from nsepy.derivatives import get_expiry_date
import math
from IPython.display import display
import pandas as pd
from tabulate import tabulate
from sympy import symbols, Eq, solve, Integer, Rational
import pandas as pd
import xlsxwriter

##Input params
write_to_file = True
number_of_records = 2 # for debug purpose make it 1 or 2


options_pe_df = pd.DataFrame()
options_ce_df = pd.DataFrame()
stock_price = pd.DataFrame()
error_count = 0

stock_opt = get_history(symbol=stock["Symbol"],
                        start=date(year, month, day),
                        end=date(year, month, day),
                        option_type=type,
                        strike_price=strike_price,
                        expiry_date=expiry_date)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    stocks = pd.read_excel("./data/options_details.xlsx", converters={'Name': str.strip,
                                                                      'Symbol': str.strip})
    print(stocks.columns)
    print("---Starting loop for each stock defined in input file----")
    for index, row in stocks.iterrows():
        if index < number_of_records:
            print("-##################################################################################-")
            print(index," ---###############################  ",row["Symbol"], "  #########################################-")
            print("-##################################################################################-")
            print("---Getting data for", row["Symbol"], ", Strike Price any one: ", row["Strike_Price"],
                  " , Tick Size: ", row["Tick_Size"], "-")
            try:
                get_option(row, "PE")
                get_option(row, "CE")
            except Exception as e:
                print("Issue in getting option details for : ", row["Symbol"], e)
            stocks.iloc[index] = row
    #         print("### final options PE")
    #         print(tabulate(options_pe_df, headers='keys'))
    #         print("### final options CE")
    #         print(tabulate(options_ce_df, headers='keys'))
    #         print("### final stock prices")
    #         print(tabulate(stock_price, headers='keys'))
    call_put_df = options_pe_df
    call_put_df = call_put_df.set_index('Symbol').join(options_ce_df.set_index('Symbol'), lsuffix='_put',
                                                       rsuffix='_call')
    call_put_df['Total Premium'] = call_put_df['Premium_put'] + call_put_df['Premium_call']
    call_put_df['% Total Premium'] = call_put_df['% Premium_put'] + call_put_df['% Premium_call']
    call_put_df['% Total Diff in price'] = call_put_df['% Diff in price_put'] + call_put_df['% Diff in price_call']
    call_put_df['% Total Cushion'] = call_put_df['% Cushion_put'] + call_put_df['% Cushion_call']

    # Reorder columns for ease of reading
    call_put_df = call_put_df[['Total Premium',
                               '% Total Premium', '% Total Diff in price', '% Total Cushion',
                               'Strike Price_put', 'Strike Price_call', 'Underlying_put',
                               'Premium_put', '% Premium_put', '% Diff in price_put',
                               '% Cushion_put', 'Premium_call', '% Premium_call',
                               '% Diff in price_call', '% Cushion_call',
                               'Expiry_put', 'Open_put',
                               'High_put', 'Low_put', 'Close_put', 'Last_put', 'Settle Price_put',
                               'Number of Contracts_put', 'Turnover_put', 'Premium Turnover_put',
                               'Open Interest_put', 'Change in OI_put',
                               'lot_size_put',
                               'Open_call', 'High_call', 'Low_call', 'Close_call', 'Last_call', 'Settle Price_call',
                               'Number of Contracts_call', 'Turnover_call',
                               'Premium Turnover_call', 'Open Interest_call', 'Change in OI_call',
                               'Underlying_call']]

    # #write the output the final sheet
    if write_to_file:
        output_file = './data/output/' + str(year) + "-" + str(month) + "-" + str(day) + '.xlsx'
        with pd.ExcelWriter(output_file) as writer:
            options_pe_df.to_excel(writer, sheet_name='PE prices')
            options_ce_df.to_excel(writer, sheet_name='CE prices')
            stocks.to_excel(writer, sheet_name='Stock Data')
            stock_price.to_excel(writer, sheet_name='Stock Price')
            call_put_df.to_excel(writer, sheet_name='Call Put Prices')
        # workbook = xlsxwriter.Workbook(output_file)
        # workbook.add_vba_project('./vba/excelHighlighter.bin')
