from tabulate import  tabulate
def get_closed_open_pnl(df_order_history):
    if df_order_history is None:
        return None

    print("Inside get_closed_open_pnl of NUVAMA")

    # amount paid or received for the given contract
    df_order_history['amount'] = df_order_history['average_price'].astype(float) * \
                                 df_order_history['quantity'].astype(float) * -1
    df_order_history['amount'] = round(df_order_history['amount'], 2)

    print(tabulate(df_order_history, headers='keys', tablefmt='pretty', showindex=True))

    # Group by specific columns
    grouped_df = df_order_history.groupby(['stock_code', 'expiry_date', 'right', 'strike_price'])

    # Perform aggregation or other operations on the grouped data
    result_df = grouped_df.agg(
        {'quantity': 'sum', 'amount': 'sum', 'ltp': 'mean', 'action': 'count'}).reset_index()

    result_df['Realized'] = 0
    result_df['Unrealized'] = 0

    return result_df