# Generate ISO8601 Date/DateTime String
import datetime
import pandas as pd

import sql.sqlite
from helper import constants
from helper.colours import Colors
import sql.sqlite as sqlt
from tabulate import tabulate


def is_market_open():
    # Check if the market is open on weekdays
    today = datetime.datetime.now().date()
    if today.weekday() < 5:  # Monday to Friday (0 to 4 are the weekdays)
        current_time = datetime.datetime.now().time()
        market_open_time = datetime.time(9, 15)  # Assuming market opens at 9:15 AM
        market_close_time = datetime.time(15, 30)  # Assuming market closes at 3:30 PM
        return market_open_time <= current_time <= market_close_time
    else:
        return False


def calculate_pnl(response):
    # This method calculates the pnl for all open positions at stock level

    pnl = 0
    df = pd.DataFrame(columns=["stock", "pnl", "expiry_date"])
    if response:
        unique_stock_codes = set(item['stock_code'] for item in response)
        # print(unique_stock_codes)

        for stock in unique_stock_codes:
            pnl = 0
            expiry_date = ''

            for item in response:
                if item['stock_code'] == stock:
                    # print(item)
                    if item['segment'] == 'fno':
                        ltp = float(item['ltp'])
                        cost = float(item['average_price'])
                        qty = int(item['quantity'])
                        expiry_date = item['expiry_date']
                        # print((item['ltp'],item['average_price']))
                        if item['action'] == 'Sell':
                            pnl += round((cost - ltp) * qty, 2)
                        if item['action'] == 'Buy':
                            pnl += round((ltp - cost) * qty, 2)

            # Sample DataFrame
            pnl_data = {
                'stock': stock,
                'pnl': pnl,
                'expiry_date': expiry_date
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
    # Read the file where we can mention the threasholds for profit or loss for each stock

    # Specify the path to your Excel file
    excel_file_path = '../data/profit_loss.xlsx'
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(excel_file_path)

    return df


def get_secreates():
    # Specify the path to your Excel file
    csv_file_path = '../secretes/secretes.csv'
    # Read the Excel file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    return df


# Function to check if profit or loss threshold is reached

def profit_or_loss_threshold_reached(df):
    # Check if the profit or loss threshold is reached for each stock based on the excel def check_pnl_threshold(df):

    # Code to calculate PnL
    print("\nCHECKING P&L Threasholds...")
    print("\n\n#######################################")

    for index, data in df.iterrows():
        if float(data['pnl']) > float(data['profit_target']):
            print(f"{data['stock']}: Profit Target Reached Profit: {data['pnl']}, Target: {data['profit_target']}")
        if float(data['pnl']) < float(data['stop_loss']):
            print(f"{data['stock']}: Stop Loss Reached. Loss:{data['pnl']}, Target: {data['stop_loss']}")

    print("\n\n#######################################")


def contract_value(response, threshold):
    # Code to calculate contract value and if its less than threshold
    # it will make sense to sq of the contract

    # print("\nCHECKING CONTRACT VALUE...")
    df_to_sq_off_contracts = pd.DataFrame(
        columns=["stock", "price_left", "pnl", "strike_price", "expiry_date", "right"])

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
                                  , ignore_index=True)
    print("\n\n#######################################")
    print("Contracts to sq off:")
    print(f'{Colors.GREEN}{df_to_sq_off_contracts}{Colors.WHITE}')
    return df_to_sq_off_contracts


def get_pnl_target(response):
    # Code to calculate PnL

    df_threshold = get_threasholds()

    df_pnl = calculate_pnl(response)
    sql.sqlite.insert_pnl(df_pnl)

    df = pd.merge(df_threshold, df_pnl, on='stock')

    # print("Pnl Targets:")
    # print(df)
    # profit_or_loss_threshold_reached(df)

    # get  the contracts to be sq_offed
    contract_value(response, constants.CONTRACT_MIN_VALUE_TO_BE_SQ_OFFED)

    print("\n\n#######################################")

    return df


def calculate_margin_used(response, api):
    # Calculate Margin Used for all open option positions
    print("\n\n#######################################")

    print("Calculating Margin Used: ")

    if response:
        unique_stock_codes = set(item['stock_code'] for item in response)
        unique_expiry_dates = set(item['expiry_date'] for item in response)

        for expiry_date in unique_expiry_dates:

            for stock in unique_stock_codes:
                if sqlt.get_margins_used_time(stock, expiry_date) > (
                        datetime.datetime.now() - datetime.timedelta(minutes=constants.MARGING_DELAY_TIME)).time():
                    # print(f"Not calculating margin for {stock} as its was calculated less than 10 minutes ago")
                    continue

                # print(f"Calculating margin for {stock}, {expiry_date}")
                df = pd.DataFrame(
                    columns=["strike_price", "quantity", "right", "product", "action", "price", "expiry_date",
                             "stock_code", "cover_order_flow", "fresh_order_type", "cover_limit_rate",
                             "cover_sltp_price", "fresh_limit_rate", "open_quantity"])

                for item in response:
                    if item['stock_code'] == stock and item['expiry_date'] == expiry_date:
                        # print(item)
                        if item['segment'] == 'fno':
                            # Sample DataFrame
                            margin_data = {
                                "strike_price": item['strike_price'],
                                "quantity": item['quantity'],
                                "right": item['right'],
                                "product": item['product_type'],
                                "action": item['action'],
                                "price": item['price'],
                                "expiry_date": item['expiry_date'],
                                "stock_code": item['stock_code'],
                                "cover_order_flow": item['cover_order_flow'],
                                "fresh_order_type": "N",
                                "cover_limit_rate": "0",
                                "cover_sltp_price": "0",
                                "fresh_limit_rate": "0",
                                "open_quantity": "0"
                            }

                            df = pd.concat([df, pd.DataFrame.from_records([margin_data])], ignore_index=True)
                # print(f"Margin Data: {stock} , {expiry_date}")
                # print(df)

                margin_response = api.margin_calculator(df.to_dict(orient='records'), "NFO")
                if margin_response['Status'] == 200:
                    sqlt.insert_margins_used(stock, expiry_date, margin_response['Success'])


def order_list(api, from_date, to_date):
    # Get list of orders and also print them in different colour based on execution status.

    orders = api.get_order_list('NFO', from_date=from_date, to_date=to_date)
    # print(orders)

    print("\n\n##################################")
    # print(orders)
    print("Order Status: ")
    if orders is not None and orders['Success'] is not None:
        for item in orders['Success']:
            if item['status'] == 'Executed':
                print(f"{Colors.BLUE}Executed Order: {item['stock_code']} : {item['action']} :  {item['price']} ")
            if item['status'] == 'Ordered':
                print(
                    f"{Colors.CYAN}Pending Execution: {item['stock_code']} : {item['action']} :  {item['price']} ")

        # insert the order status in to order status table
        sqlt.insert_order_status(orders['Success'])
    else:
        print("No orders found")


