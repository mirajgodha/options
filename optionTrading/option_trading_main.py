import traceback

import pandas as pd

import iciciDirect.icici_helper
import iciciDirect.icici_helper as iciciDirectHelper
import iciciDirect.icici_direct_main as iciciDirect
import nuvama.nuvama_main as nuvama
from datetime import datetime
import configparser
import time

from constants import constants_local as constants
from helper.colours import Colors
import trading_helper as trading_helper
import optionStrategies.optionStrategyBuilder as optionStrategyBuilder

today_date = datetime.today().date().strftime("%Y-%m-%d")


def main():
    # Your main code goes here
    try:
        while trading_helper.is_market_open() | constants.TEST_RUN:
            print(f"{Colors.PURPLE}Options Trading Dashboarding Toolbox Running at {datetime.today()}{Colors.WHITE}")
            api = iciciDirect.get_api_session()

            # Get portfolio positions from all brokers accounts.
            icici_portfolio_positions = iciciDirect.get_portfolio_positions()
            nuvama_portfolio_positions = nuvama.get_portfolio_positions()
            # print(icici_portfolio_positions)
            # print(nuvama_portfolio_positions)
            portfolio_positions_df = pd.concat([icici_portfolio_positions, nuvama_portfolio_positions])

            # print(portfolio_positions_df)

            # Calculates the real time PnL for the option open positions in all the accounts
            trading_helper.get_pnl_target(portfolio_positions_df)

            # # Update the LTP for the open positions so that we can plot the LTP chart
            # Getting charts on Sensibull so not doing now.
            # iciciDirectHelper.insert_ltp_for_positions(portfolio_positions_response)

            # # Calculate margin used for all open option positions and update in margin table
            trading_helper.calculate_margin_used(portfolio_positions_df, api)

            # # Get the order status real time, also gets and update the ltp
            # for traders and update the ltp in ltp table
            # Get portfolio positions from all brokers accounts.
            icici_orders = iciciDirect.get_order_book()
            nuvama_orders = nuvama.get_order_book()
            # print(icici_orders)
            # print(nuvama_orders)
            order_book_df = pd.concat([icici_orders, nuvama_orders])

            trading_helper.order_list(order_book_df)

            # # Update the Market wide open positions in mwpl table, for the stocks options in the portfolio
            trading_helper.get_mwpl(portfolio_positions_df=portfolio_positions_df)
            #
            # # Update the funds and limits available in a demat account hourly
            iciciDirectHelper.update_funds(api)

            # Build option strategies
            optionStrategyBuilder.option_strategies_builder()

            print("\n#######################################")
            print(f"{Colors.PURPLE}All done going to sleep for {constants.REFRESH_TIME_SECONDS} sec. {Colors.WHITE}")
            time.sleep(constants.REFRESH_TIME_SECONDS)
    except Exception as e:
        print(f"{Colors.RED}Error in main{Colors.WHITE}")
        traceback.print_exc()
    finally:
        if trading_helper.is_market_open() | constants.TEST_RUN:
            time.sleep(constants.REFRESH_TIME_SECONDS)
            main()
        else:
            if not trading_helper.is_market_open():
                print(f"{Colors.PURPLE}Market Closed{Colors.WHITE}")


# Main function to be executed in the main thread


if __name__ == "__main__":
    # Call the main function to start the program
    print(f"{Colors.PURPLE}Starting Options Trading Dashboarding Toolbox {Colors.WHITE}")
    main()
