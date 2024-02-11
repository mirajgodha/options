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
old_days = 2
price_diff_perc = 0
expiry_year = 2023
expiry_month = 4
expiry_day = 27
number_of_records = 200

# Variables defined
today = date.today() - datetime.timedelta(days=old_days)
year = today.year
month = today.month
day = today.day
options_pe_df = pd.DataFrame()
options_ce_df = pd.DataFrame()
stock_price = pd.DataFrame()
error_count = 0


def get_option(stock, type):
    global options_pe_df
    global options_ce_df
    global error_count
    strike_price = get_itm_strike_price(stock, get_rounded_stock_price(stock, type), type)
    expiry_date = datetime.datetime(expiry_year, expiry_month, expiry_day)
    stock_opt = get_history(symbol=stock["Symbol"],
                            start=date(year, month, day),
                            end=date(year, month, day),
                            option_type=type,
                            strike_price=strike_price,
                            expiry_date=expiry_date)
    if len(stock_opt) != 0:
        stock_opt['lot_size'] = stock['Lot_Size']
        stock_opt['Premium'] = stock['Lot_Size'] * stock_opt['Close']
        stock_opt['% Premium'] = stock_opt['Close'] / stock_opt['Underlying']
        if type == 'PE':
            stock_opt['% Diff in price'] = (stock_opt['Underlying'] - stock_opt['Strike Price']) / stock_opt[
                'Underlying']
        elif type == 'CE':
            stock_opt['% Diff in price'] = (stock_opt['Strike Price'] - stock_opt['Underlying']) / stock_opt[
                'Underlying']
        stock_opt['% Cushion'] = stock_opt['% Diff in price'] + stock_opt['% Premium']

        print(tabulate(stock_opt, headers='keys'))
        # stock_opt.plot(y=["Close"], kind="bar", figsize=(9, 8))
        if type == 'PE':
            options_pe_df = pd.concat([options_pe_df, stock_opt], ignore_index=True)
        elif type == 'CE':
            options_ce_df = pd.concat([options_ce_df, stock_opt], ignore_index=True)
    else:
        print("No data found for the given date: ", date(year, month, day), "for type: ", type,
              " for the stock: ", stock["Symbol"],
              " at price: ", strike_price, " at expiry date: ", expiry_date)
        error_count = error_count + 1
    if error_count > 10:
        print("Errors:", error_count)


# --------------
# get last close price of stock
# --------------
def get_stock_price(stock):
    global stock_price
    last_price = get_history(symbol=stock["Symbol"],
                             start=date(year, month, day),
                             end=date(year, month, day))
    # print("------stock price-----")
    print(tabulate(last_price, headers='keys'))
    stock_price = pd.concat([stock_price, last_price], ignore_index=True)
    if len(last_price) == 0:
        stock["Last_Close"] = 0
    else:
        stock["Last_Close"] = last_price.iloc[0]["Prev Close"]


# ------------------------
# get the stock price rounded to the nearest
# options tick price
# ------------------------
def get_rounded_stock_price(stock, type):
    if stock["Last_Close"] == 0:
        get_stock_price(stock)
    if type == "PE":
        rounded_pc = round(stock["Last_Close"] * (1 - price_diff_perc / 100))
    elif type == "CE":
        rounded_pc = round(stock["Last_Close"] * (1 + price_diff_perc / 100))
    if stock["Tick_Size"] >= 10000:
        rounded_pc = math.floor(rounded_pc / 10000) * 10000
    elif stock["Tick_Size"] >= 1000:
        rounded_pc = math.floor(rounded_pc / 1000) * 1000
    elif stock["Tick_Size"] >= 100:
        rounded_pc = math.floor(rounded_pc / 100) * 100
    elif stock["Tick_Size"] >= 10:
        rounded_pc = math.floor(rounded_pc / 10) * 10
    elif stock["Tick_Size"] > 1:
        rounded_pc = rounded_pc

    print("Prev close price: ", stock["Last_Close"], " Rounded: ", rounded_pc)
    return rounded_pc


# -----------------------
# gets in the money strike price for the stock
# which is nearest to the current price
# -----------------------
def get_itm_strike_price(stock, prev_close, type):
    price = prev_close
    strike_price = stock["Strike_Price"]
    print("tick:", stock["Tick_Size"])
    if stock["Tick_Size"] == 0 or math.isnan(stock["Tick_Size"]):
        return
    tick_size = stock["Tick_Size"]
    print("Predicted tick size: ", stock["Tick_Size"])
    # defining symbols used in equations
    # or unknown variables
    x = symbols('x')

    # defining equations
    if price > strike_price:
        eq1 = Eq((strike_price + x * tick_size), price)
    else:
        eq1 = Eq((strike_price - x * tick_size), price)

    # solving the equation
    v = solve(eq1, x)
    print("Values of x is in equation: ", v, " Rounded: ", Rational.round(v[0]))
    if price > strike_price:
        itm_strike_price = float(strike_price + Rational.round(v[0]) * tick_size)
    else:
        itm_strike_price = float(strike_price - Rational.round(v[0]) * tick_size)

    while type == "PE" and itm_strike_price >= price:
        itm_strike_price = itm_strike_price - stock["Tick_Size"]

    while type == "CE" and itm_strike_price <= price:
        itm_strike_price = itm_strike_price + stock["Tick_Size"]

    print("Final In the money strike price for ", stock["Symbol"], " is: ", itm_strike_price)
    return itm_strike_price


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    stocks = pd.read_excel("./data/options_details.xlsx", converters={'Name': str.strip,
                                                                      'Symbol': str.strip})
    # stocks = stocks.dropna()
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
