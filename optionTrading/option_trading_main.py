import pandas as pd

import iciciDirect.icici_helper
import iciciDirect.icici_helper as iciciDirectHelper
import iciciDirect.icici_direct_main as iciciDirect
import nuvama.nuvama_main as nuvama
from datetime import datetime, timedelta
import traceback
import time

from constants import constants_local as constants
from dao import historicalOrderBookDF
from helper.colours import Colors
import trading_helper as trading_helper
import optionStrategies.optionStrategyBuilder as optionStrategyBuilder
from dao.historicalOrderBookDF import convert_to_historical_df



today_date = datetime.today().date()
yesterday_date = today_date - timedelta(days=1)

# Get the current date
current_date = datetime.now()

# Calculate the 23th date of the last month
last_month_start_date = datetime(current_date.year if current_date.month != 1 else current_date.year - 1,
                                  current_date.month - 1 if current_date.month != 1 else 12,
                                  25)


def main():
    # Your main code goes here
    try:
        while trading_helper.is_market_open() | True:
            print(f"{Colors.ORANGE}Options Trading Dashboarding Toolbox Running at {datetime.today()}{Colors.WHITE}")
            api = iciciDirect.get_api_session()

            print(f"{Colors.PURPLE}Getting Portfolio Positions ...{Colors.WHITE}")
            # Get portfolio positions from all brokers accounts.
            icici_portfolio_positions = iciciDirect.get_portfolio_positions()
            nuvama_portfolio_positions = nuvama.get_portfolio_positions()
            # print(icici_portfolio_positions)
            # print(nuvama_portfolio_positions)
            portfolio_positions_df = pd.concat([icici_portfolio_positions, nuvama_portfolio_positions])

            print(f"{Colors.PURPLE}Going to persist the Portfolio Positions ...{Colors.WHITE}")
            trading_helper.persist(portfolio_positions_df, constants.PROTFOLIO_POSITIONS_TABLE_NAME)

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting to calculate the PnL for the open positions ...{Colors.WHITE}")
            # Calculates the real time PnL for the option open positions in all the accounts
            trading_helper.get_pnl_target(portfolio_positions_df)
            print(f"{Colors.PURPLE}Finished calculating the PnL for the open positions ...{Colors.WHITE}")

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting to get the LTP for the open positions ...{Colors.WHITE}")
            # Get ltp for the stocks and its change prices, so that its easy to track all positions.
            trading_helper.get_ltp_stock(portfolio_positions_df)
            print(f"{Colors.PURPLE}Finished getting the LTP for the open positions ...{Colors.WHITE}")

            # # Update the LTP for the open positions so that we can plot the LTP chart
            # Getting charts on Sensibull so not doing now.
            # iciciDirectHelper.insert_ltp_for_positions(portfolio_positions_response)

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting calculating Margins Used for the open positions ...{Colors.WHITE}")
            # # Calculate margin used for all open option positions and update in margin table
            trading_helper.calculate_margin_used(portfolio_positions_df, api)
            print(f"{Colors.PURPLE}Finished calculating Margins Used for the open positions ...{Colors.WHITE}")

            ############################################################################

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting updating todays Order List ...{Colors.WHITE}")
            # # Get the order status real time, also gets and update the ltp
            # for traders and update the ltp in ltp table
            # Get portfolio positions from all brokers accounts.
            icici_orders = iciciDirect.get_order_book()
            nuvama_orders = nuvama.get_order_book()
            # print(icici_orders)
            # print(nuvama_orders)
            order_book_df = pd.concat([icici_orders, nuvama_orders])

            trading_helper.order_list(order_book_df)
            print(f"{Colors.PURPLE}Finished updating todays Order List ...{Colors.WHITE}")
            # End the todays order list update in DB
            ############################################################################

            ############################################################################

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting Historical Pnl Booked for closed positions ...{Colors.WHITE}")
            # Used to figure out historical pnl booked on positions.
            icici_order_history = iciciDirect.get_historical_order_book(
                from_date=last_month_start_date.strftime(constants.ICICI_DATE_FORMAT),
                to_date=yesterday_date.strftime(constants.ICICI_DATE_FORMAT))

            nuvama_order_history = nuvama.get_historical_order_book(
                from_date=last_month_start_date.strftime(constants.ICICI_DATE_FORMAT),
                to_date=yesterday_date.strftime(constants.ICICI_DATE_FORMAT))

            # As todays executed orders does not comes in order history, we will also use the todays order book
            # Concat the todays order book executed orders with order history, to calculate the
            # real booked pnl till current time.
            icici_orders_today = convert_to_historical_df(icici_orders)
            nuvama_orders_today = convert_to_historical_df(nuvama_orders)

            icici_order_history = pd.concat([icici_order_history, icici_orders_today])
            nuvama_order_history = pd.concat([nuvama_order_history, nuvama_orders_today])

            order_history = pd.concat([icici_order_history, nuvama_order_history])

            pnl_df = trading_helper.get_closed_pnl(order_history)

            print(f"{Colors.PURPLE}Finished Historical Pnl Booked for closed positions ...{Colors.WHITE}")
            # End historical pnl
            ############################################################################

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting Getting MWPL for open positions ...{Colors.WHITE}")
            # # Update the Market wide open positions in mwpl table, for the stocks options in the portfolio
            trading_helper.get_mwpl(portfolio_positions_df=portfolio_positions_df)
            print(f"{Colors.PURPLE}Finished Getting MWPL for open positions ...{Colors.WHITE}")

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting getting Strategies Breakeven ...{Colors.WHITE}")
            # Calculate the breakeven points for the strategies.
            trading_helper.get_strategy_breakeven(portfolio_positions_df)
            print(f"{Colors.PURPLE}Finished getting Strategies Breakeven ...{Colors.WHITE}")

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting getting ICICI Funds and Limits...{Colors.WHITE}")
            # # Update the funds and limits available in a demat account hourly
            iciciDirectHelper.update_funds(api)
            print(f"{Colors.PURPLE}Finished getting ICICI Funds and Limits...{Colors.WHITE}")

            print("#####################################################################################")
            print(f"{Colors.PURPLE}Starting building option strategies...{Colors.WHITE}")
            # Build option strategies
            optionStrategyBuilder.option_strategies_builder()
            print(f"{Colors.PURPLE}Finished building option strategies...{Colors.WHITE}")

            print("\n#######################################")
            print(f"{Colors.ORANGE}All done going to sleep for {constants.REFRESH_TIME_SECONDS} sec. {Colors.WHITE}")
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


def test():
    # Your main code goes here
    try:
        icici_order_history = iciciDirect.get_historical_order_book(
            from_date=last_month_start_date.strftime(constants.ICICI_DATE_FORMAT),
            to_date=today_date.strftime(constants.ICICI_DATE_FORMAT))

        nuvama_order_history = nuvama.get_historical_order_book(
            from_date=last_month_start_date.strftime(constants.NUVAMA_DATE_FORMAT),
            to_date=today_date.strftime(constants.NUVAMA_DATE_FORMAT))


        order_history = pd.concat([icici_order_history, nuvama_order_history])

        pnl_df = trading_helper.get_closed_pnl(order_history)
        from tabulate import tabulate
        print(tabulate(pnl_df, headers='keys', tablefmt='psql'))



        # # Get portfolio positions from all brokers accounts.
        # icici_portfolio_positions = iciciDirect.get_portfolio_positions()
        # nuvama_portfolio_positions = nuvama.get_portfolio_positions()
        # # print(icici_portfolio_positions)
        # # print(nuvama_portfolio_positions)
        # portfolio_positions_df = pd.concat([icici_portfolio_positions, nuvama_portfolio_positions])
        #
        # # trading_helper.persist(portfolio_positions_df)
        #
        #
        # trading_helper.get_strategy_breakeven(portfolio_positions_df)

    except Exception as e:
        print(f"{Colors.RED}Error in test{Colors.WHITE}")
        traceback.print_exc()
    finally:
        print(f"{Colors.PURPLE}All done")



# Main function to be executed in the main thread
if __name__ == "__main__":
    # Call the main function to start the program
    print(f"{Colors.ORANGE}Starting Options Trading Dashboarding Toolbox {Colors.WHITE}")
    if constants.TEST_RUN:
        print(f"{Colors.ORANGE}Test run Started{Colors.WHITE}")
        test()
    else:
        print(f"{Colors.ORANGE}Starting Live Trading{Colors.WHITE}")
        main()
