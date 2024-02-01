# Generate ISO8601 Date/DateTime String
import datetime
import pandas as pd

from helper.colours import Colors
from tabulate import tabulate


def is_market_open():
    current_time = datetime.datetime.now().time()
    market_open_time = datetime.time(9, 15)  # Assuming market opens at 9:15 AM
    market_close_time = datetime.time(15, 30)  # Assuming market closes at 3:30 PM
    return market_open_time <= current_time <= market_close_time


def calculate_pnl(response):
    pnl = 0
    df = pd.DataFrame(columns=["stock", "pnl"])
    if response:
        unique_stock_codes = set(item['stock_code'] for item in response)
        #print(unique_stock_codes)

        for stock in unique_stock_codes:
            pnl = 0
            for item in response:
                if item['stock_code'] == stock:
                    # print(item)
                    if item['segment'] == 'fno':
                        ltp = float(item['ltp'])
                        cost = float(item['average_price'])
                        qty = int(item['quantity'])
                        # print((item['ltp'],item['average_price']))
                        if item['action'] == 'Sell':
                            pnl += round((cost - ltp) * qty, 2)
                        if item['action'] == 'Buy':
                            pnl += round((ltp - cost) * qty, 2)

            # Sample DataFrame
            pnl_data = {
                'stock': stock,
                'pnl': pnl
            }

            df = pd.concat([df, pd.DataFrame.from_records([pnl_data])], ignore_index=True)
            df = df.sort_values(['pnl'])

    else:  # If no positions are open
        pnl = None

    print("Pnl Currently:\n")
    total_pnl = df['pnl'].sum()
    if total_pnl > 0:
        print(f"{Colors.BLUE}Total:: {Colors.GREEN}{total_pnl}{Colors.WHITE}")
    else:
        print(f"{Colors.BLUE}Total:: {Colors.RED}{total_pnl}{Colors.WHITE}")
    print("\n")

    for index, data in df.iterrows():
        if data['pnl'] > 0:
            print(f"{data['stock']}: {Colors.GREEN}{data['pnl']}{Colors.WHITE}")
        if data['pnl'] < 0:
            print(f"{data['stock']}: {Colors.RED}{data['pnl']}{Colors.WHITE}")

    return df


def get_threasholds():
    # Specify the path to your Excel file
    excel_file_path = '../data/profit_loss.xlsx'
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(excel_file_path)

    return df

def get_secreates():
    # Specify the path to your Excel file
    csv_file_path = '../secreates/secreates.csv'
    # Read the Excel file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    return df



# Function to check if profit or loss threshold is reached

def profit_or_loss_threshold_reached(df):
    # Code to calculate PnL
    print("\nCHECKING P&L Threasholds...")
    print("\n\n#######################################")

    for index, data in df.iterrows():
        if float(data['pnl']) > float(data['profit_target']) :
            print(f"{data['stock']}: Profit Target Reached Profit: {data['pnl']}, Target: {data['profit_target']}")
        if float(data['pnl']) < float(data['stop_loss']):
            print(f"{data['stock']}: Stop Loss Reached. Loss:{data['pnl']}, Target: {data['stop_loss']}")

    print("\n\n#######################################")


def contract_value(response, threshold):
    # Code to calculate contract value and if its less than threshold
    # it will make sense to sq of the contract

    # print("\nCHECKING CONTRACT VALUE...")
    df_to_sq_off_contracts = pd.DataFrame(columns=["stock", "price_left", "pnl","strike_price", "expiry_date", "right" ])

    for item in response:
        if item['segment'] == 'fno':
            ltp = float(item['ltp'])
            cost = float(item['average_price'])
            qty = int(item['quantity'])
            if item['action'] == 'Sell':
                value_left = ltp * qty
                if value_left < threshold:
                    df_to_sq_off_contracts = \
                        pd.concat([df_to_sq_off_contracts, pd.DataFrame.from_records(
                            [{'stock': item['stock_code'],
                              'price_left': value_left,
                              'pnl': round((cost - ltp) * qty, 2),
                              'strike_price': item['strike_price'],
                              'expiry_date': item['expiry_date'],
                              'right': item['right']}])]
                                  ,ignore_index=True)
    print("\n\n#######################################")
    print("Contracts to sq off:")
    print(f'{Colors.GREEN}{df_to_sq_off_contracts}{Colors.WHITE}')
    return df_to_sq_off_contracts


def get_pnl_target(response):
    # Code to calculate PnL

    df_threshold = get_threasholds()
    df_pnl = calculate_pnl(response)
    df = pd.merge(df_threshold, df_pnl, on='stock')

    # print("Pnl Targets:")
    # print(df)
    # profit_or_loss_threshold_reached(df)

    #get  the contracts to be sq_offed
    contract_value(response, 2000)


    print("\n\n#######################################")

    return df