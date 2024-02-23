# Generate ISO8601 Date/DateTime String
import datetime
import pandas as pd

import sql.sqlite
from helper import optionsMWPL, fuzzMatch
from constants import constants_local

from helper.colours import Colors
import sql.sqlite as sqlt
from tabulate import tabulate


def get_secreates():
    # Specify the path to your Excel file
    csv_file_path = '../secretes/secretes.csv'
    # Read the Excel file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    return df


def get_closed_open_pnl(df_order_history):
    for index, row in df_order_history.iterrows():
        if row['action'] == 'Sell':
            df_order_history.at[index, 'quantity'] = -1 * float(row['quantity'])

    df_order_history['quantity'] = df_order_history['quantity'].astype(float)
    df_order_history['strike_price'] = df_order_history['strike_price'].astype(float)
    df_order_history['ltp'] = df_order_history['ltp'].astype(float)

    # amount paid or received for the given contract
    df_order_history['amount'] = df_order_history['average_cost'].astype(float) * \
                                 df_order_history['quantity'].astype(float) * -1 - \
                                 df_order_history['brokerage_amount'].astype(float) - \
                                 df_order_history['total_taxes'].astype(float)
    df_order_history['amount'] = round(df_order_history['amount'], 2)

    # print(tabulate(df_order_history, headers='keys', tablefmt='pretty', showindex=True))

    # Group by specific columns
    grouped_df = df_order_history.groupby(['stock_code', 'expiry_date', 'right', 'strike_price'])

    # Perform aggregation or other operations on the grouped data
    result_df = grouped_df.agg(
        {'quantity': 'sum', 'amount': 'sum', 'ltp': 'mean', 'action': 'count'}).reset_index()

    result_df['Realized'] = 0
    result_df['Unrealized'] = 0

    # current value of the contract
    result_df['current_value'] = result_df['ltp'].astype(float) * result_df['quantity'].astype(float)
    result_df['current_value'] = round(result_df['current_value'], 2)

    for index, row in result_df.iterrows():
        if row['quantity'] < 0:
            result_df.at[index, 'current_value'] = row['current_value'] * -1

    for index, row in result_df.iterrows():
        if row['quantity'] == 0:
            result_df.at[index, 'Realized'] = row['amount']
        else:
            if row['quantity'] > 0:
                # doing plus as amount will be negative here because its a
                # buy order and amount is the amount paid so -ve
                result_df.at[index, 'Unrealized'] = row['current_value'] + row['amount']
            else:
                if row['quantity'] < 0:
                    result_df.at[index, 'Unrealized'] = row['amount'] - row['current_value']

    result_df['amount'] = round(result_df['amount'], 2)
    result_df['current_value'] = round(result_df['current_value'], 2)
    result_df['Realized'] = round(result_df['Realized'], 2)
    result_df['Unrealized'] = round(result_df['Unrealized'], 2)

    # print(tabulate(result_df, headers='keys', tablefmt='pretty', showindex=True))

    result_df = result_df.groupby(by=['stock_code', 'expiry_date'])
    result_df = result_df.agg(
        {'Realized': 'sum', 'Unrealized': 'sum'}).reset_index()

    result_df['Realized'] = round(result_df['Realized'], 0)
    result_df['Unrealized'] = round(result_df['Unrealized'], 0)
    print(tabulate(result_df, headers='keys', tablefmt='pretty', showindex=True))
    # result_df.to_sql('options_closed_open_pnl', sqlt.get_conn(), if_exists='replace')





def update_funds(api):
    if sqlt.get_last_updated_time("funds") > (
            datetime.datetime.now() - datetime.timedelta(minutes=constants_local.FUNDS_DELAY_TIME)):
        return
    funds_response = api.get_funds()
    if funds_response['Status'] != 200:
        print(f"{Colors.RED}Error while getting funds: {funds_response}{Colors.RESET}")
        return

    margin_response = api.get_margin('nfo')
    if margin_response['Status'] != 200:
        print(f"{Colors.RED}Error while getting margin: {margin_response}{Colors.RESET}")
        return

    sqlt.insert_funds(funds_response['Success'], margin_response['Success'])
