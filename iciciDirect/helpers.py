# Generate ISO8601 Date/DateTime String
import datetime
import pandas as pd

import sql.sqlite
from helper import constants, optionsMWPL, fuzzMatch

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


def calculate_pnl(portfolio_positions_response):
    # This method calculates the pnl for all open positions at stock level

    pnl = 0
    df = pd.DataFrame(columns=["stock", "pnl", "expiry_date"])
    if portfolio_positions_response:
        unique_stock_codes = set(item['stock_code'] for item in portfolio_positions_response)
        # print(unique_stock_codes)

        for stock in unique_stock_codes:
            pnl = 0
            expiry_date = ''

            for item in portfolio_positions_response:
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

    sqlt.insert_contracts_to_be_sq_off(df_to_sq_off_contracts)

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
                if sqlt.get_last_updated_time_margins_used(stock, expiry_date) > (
                        datetime.datetime.now() - datetime.timedelta(minutes=constants.MARGING_DELAY_TIME)):
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


def get_option_ltp(api, stock_code, expiry_date, strike_price, right):
    # Get LTP for all open option positions
    try:
        response = api.get_quotes(stock_code=stock_code, exchange_code='NFO', product_type='options',
                                  expiry_date=expiry_date, strike_price=strike_price, right=right)
        # print(f"LTP: {response}")
        sqlt.insert_ltp(response['Success'])
    except Exception as e:
        print(f"{Colors.RED}Exception while getting LTP for {stock_code}, {expiry_date}, "
              f"{strike_price}, {right}: {e} {Colors.RESET}")
        ltp = sqlt.get_ltp(stock_code, expiry_date, strike_price, right)
        if ltp:
            return ltp
        return 0

    if response['Status'] != 200:
        print(f"{Colors.RED}Error while getting LTP for {stock_code}, {expiry_date}, "
              f"{strike_price}, {right}: {response}{Colors.RESET}")
        return 0

    return response['Success'][0]['ltp']


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

        # Specify the columns for which you want to create a set
        selected_columns = ['stock_code', 'expiry_date', 'strike_price', 'right']

        # Create a set for the specified columns
        unique_combinations_set = {tuple(item_dict[column] for column in selected_columns) for item_dict in
                                   orders['Success']}

        # create a hash map which will contain the ltp for
        # each unique combination of stock_code, expiry_date, strike_price, right
        hashmap_orders_ltp = {combination: 0 for combination in unique_combinations_set}

        for item in unique_combinations_set:
            hashmap_orders_ltp[item] = get_option_ltp(api, item[0], item[1], item[2], item[3])

        # Update ltp in orders as icici do not provide ltp in order list
        for item in orders['Success']:
            item['ltp'] = hashmap_orders_ltp[tuple(item[column] for column in selected_columns)]

        # print(orders['Success'])
        # insert the order status in to order status table
        sqlt.insert_order_status(orders['Success'])
    else:
        print("No orders found")


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


def get_mwpl(portfolio_positions_response):
    if sqlt.get_last_updated_time("mwpl") > (
            datetime.datetime.now() - datetime.timedelta(minutes=constants.MWPL_DELAY_TIME)):
        # Updated MWPL less than a hour ago, so not updating now.
        return

    print("Getting MWPL")

    mwpl_list = []

    # Get the data of mwpl
    mwpl_df = optionsMWPL.optionsMWPL()
    if portfolio_positions_response:
        unique_stock_codes_portfolio = set(item['stock_code'] for item in portfolio_positions_response)
        unique_stock_codes_mwpl = mwpl_df.drop_duplicates(subset=['Symbol', 'Price', 'Chg', 'Cur.MWPL', 'Pre.MWPL'])[
            'Symbol'].tolist()

        matched_stock_codes = \
            fuzzMatch.get_stock_code_pairs_using_fuzzy_match(unique_stock_codes_portfolio, unique_stock_codes_mwpl)

        similar_code = ''
        for stock in unique_stock_codes_portfolio:
            for x in matched_stock_codes:
                if x[0] == stock:
                    similar_code = x[1]
                    break

            for index, row in mwpl_df.iterrows():
                if row['Symbol'].upper() == similar_code:
                    mwpl_list.append((row['Symbol'], row['Price'], row['Chg'], row['Cur.MWPL'], row['Pre.MWPL']))
                    print(row['Symbol'], row['Price'], row['Chg'], row['Cur.MWPL'], row['Pre.MWPL'])
                    break

    sqlt.insert_mwpl(mwpl_list)


def insert_ltp_for_positions(portfolio_positions_response):
    # Insert the LTP for the open positions so that we can plot the LTP chart
    df = pd.DataFrame(columns=["stock_code", "strike_price", "expiry_date", "right", "ltp"])

    for item in portfolio_positions_response:
        if item['segment'] == 'fno':
            # Sample DataFrame
            ltp_data = {
                'stock': item['stock_code'],
                'pnl': float(item['ltp']),
                'expiry_date': item['expiry_date'],
                'right': item['right'],
                'strike_price': item['strike_price'],
                'ltp': float(item['ltp'])
            }

            df = pd.concat([df, pd.DataFrame.from_records([ltp_data])], ignore_index=True)

    sqlt.insert_ltp_df(df)


def update_funds(api):
    if sqlt.get_last_updated_time("funds") > (
            datetime.datetime.now() - datetime.timedelta(minutes=constants.FUNDS_DELAY_TIME)):
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
