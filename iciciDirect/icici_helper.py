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



def get_closed_open_pnl(api):
    response_portfolio_position = api.get_trade_list(from_date='2024-01-01', to_date='2024-02-04', exchange_code='NFO')
    if response_portfolio_position['Status'] == 200:
        response_portfolio_position = response_portfolio_position['Success']
        print(response_portfolio_position)
        df_portfolio_position = pd.DataFrame(response_portfolio_position)

        for index, row in df_portfolio_position.iterrows():
            if row['action'] == 'Sell':
                df_portfolio_position.at[index, 'quantity'] = -1 * float(row['quantity'])

        df_portfolio_position['quantity'] = df_portfolio_position['quantity'].astype(float)
        df_portfolio_position['strike_price'] = df_portfolio_position['strike_price'].astype(float)
        df_portfolio_position['ltp'] = df_portfolio_position['ltp'].astype(float)

        # amount paid or received for the given contract
        df_portfolio_position['amount'] = df_portfolio_position['average_cost'].astype(float) * \
                                          df_portfolio_position['quantity'].astype(float) * -1 - \
                                          df_portfolio_position['brokerage_amount'].astype(float) - \
                                          df_portfolio_position['total_taxes'].astype(float)
        df_portfolio_position['amount'] = round(df_portfolio_position['amount'], 2)

        print(tabulate(df_portfolio_position, headers='keys', tablefmt='pretty', showindex=True))

        # Group by specific columns
        grouped_df = df_portfolio_position.groupby(['stock_code', 'expiry_date', 'right', 'strike_price'])

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

        print(tabulate(result_df, headers='keys', tablefmt='pretty', showindex=True))

        print("\n\n#######################################")
    else:
        if response_portfolio_position['Status'] == 500:
            print(f"{Colors.RED}Internal Server Error while getting portfolio position. "
                  f"Status Code: {response_portfolio_position['Status']} received. {Colors.RESET}")
        else:
            print(f"{Colors.RED}Error while getting portfolio position: {response_portfolio_position}{Colors.RESET}")





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
