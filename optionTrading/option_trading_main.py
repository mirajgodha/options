import urllib.request
from urllib.error import URLError

import pandas as pd
# from urllib3.exceptions import NotOpenSSLWarning

from helper.logger import logger
import iciciDirect.icici_helper

import iciciDirect.icici_direct_main as iciciDirect
import nuvama.nuvama_main as nuvama
from datetime import datetime, timedelta
import traceback
import time
from tabulate import tabulate

from constants import constants_local as c

from helper.colours import Colors
import trading_helper as trading_helper
import optionStrategies.optionStrategyBuilder as optionStrategyBuilder
from dao.historicalOrderBookDF import convert_to_historical_df
import warnings

# Filter out FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)
# warnings.filterwarnings("ignore", category=NotOpenSSLWarning)


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
        while trading_helper.is_market_open() :
            logger.info(f"{Colors.ORANGE}Options Trading Dashboarding Toolbox Running at {datetime.today()}{Colors.WHITE}")
            api = iciciDirect.get_api_session()

            logger.info(f"{Colors.PURPLE}Getting Portfolio Positions ...{Colors.WHITE}")
            # Get portfolio positions from all brokers accounts.
            icici_portfolio_positions = iciciDirect.get_portfolio_positions(timeout=c.TIMEOUT_SECONDS)
            nuvama_portfolio_positions = nuvama.get_portfolio_positions()
            # print(icici_portfolio_positions)
            # print(nuvama_portfolio_positions)
            portfolio_positions_df = pd.concat([icici_portfolio_positions, nuvama_portfolio_positions])
            portfolio_positions_df.reset_index(drop=True, inplace=True)

            logger.info(f"{Colors.PURPLE}Going to persist the Portfolio Positions ...{Colors.WHITE}")
            trading_helper.persist_portfolio_positions_df(portfolio_positions_df)

            logger.info("#####################################################################################")
            logger.info(f"{Colors.PURPLE}Starting to calculate the PnL for the open positions ...{Colors.WHITE}")
            # Calculates the real time PnL for the option open positions in all the accounts
            trading_helper.get_pnl_target(portfolio_positions_df)
            logger.debug(f"{Colors.PURPLE}Finished calculating the PnL for the open positions ...{Colors.WHITE}")

            logger.info("#####################################################################################")
            logger.info(f"{Colors.PURPLE}Starting to get the LTP for the open positions ...{Colors.WHITE}")
            # Get ltp for the stocks and its change prices, so that its easy to track all positions.
            trading_helper.get_and_persist_ltp_stock(portfolio_positions_df)
            logger.debug(f"{Colors.PURPLE}Finished getting the LTP for the open positions ...{Colors.WHITE}")

            # # Update the LTP for the open positions so that we can plot the LTP chart
            # Getting charts on Sensibull so not doing now.
            # iciciDirectHelper.insert_ltp_for_positions(portfolio_positions_response)

            logger.info("#####################################################################################")
            logger.info(f"{Colors.PURPLE}Starting calculating Margins Used for the open positions ...{Colors.WHITE}")
            # # Calculate margin used for all open option positions and update in margin table
            trading_helper.calculate_margin_used(portfolio_positions_df, api)
            logger.debug(f"{Colors.PURPLE}Finished calculating Margins Used for the open positions ...{Colors.WHITE}")

            ############################################################################

            logger.info("#####################################################################################")
            logger.info(f"{Colors.PURPLE}Starting updating todays Order List ...{Colors.WHITE}")
            # # Get the order status real time, also gets and update the ltp
            # for traders and update the ltp in ltp table
            # Get portfolio positions from all brokers accounts.
            icici_orders = iciciDirect.get_order_book(timeout=c.TIMEOUT_SECONDS)
            nuvama_orders = nuvama.get_order_book()
            # print(icici_orders)
            # print(nuvama_orders)
            order_book_df = pd.concat([icici_orders, nuvama_orders])
            order_book_df.reset_index(drop=True, inplace=True)

            trading_helper.order_list(order_book_df)
            logger.debug(f"{Colors.PURPLE}Finished updating todays Order List ...{Colors.WHITE}")
            # End the todays order list update in DB
            ############################################################################

            ############################################################################

            logger.info("#####################################################################################")
            logger.info(f"{Colors.PURPLE}Starting Historical Pnl Booked for closed positions ...{Colors.WHITE}")
            # Used to figure out historical pnl booked on positions.
            icici_order_history = iciciDirect.get_historical_order_book(
                from_date=last_month_start_date.strftime(c.ICICI_DATE_FORMAT),
                to_date=yesterday_date.strftime(c.ICICI_DATE_FORMAT),timeout=c.TIMEOUT_SECONDS)

            nuvama_order_history = nuvama.get_historical_order_book(
                from_date=last_month_start_date.strftime(c.ICICI_DATE_FORMAT),
                to_date=yesterday_date.strftime(c.ICICI_DATE_FORMAT))

            # As todays executed orders does not comes in order history, we will also use the todays order book
            # Concat the todays order book executed orders with order history, to calculate the
            # real booked pnl till current time.
            icici_orders_today = convert_to_historical_df(icici_orders)
            nuvama_orders_today = convert_to_historical_df(nuvama_orders)

            icici_order_history = pd.concat([icici_order_history, icici_orders_today])
            nuvama_order_history = pd.concat([nuvama_order_history, nuvama_orders_today])

            order_history = pd.concat([icici_order_history, nuvama_order_history])
            order_history.reset_index(drop=True, inplace=True)

            pnl_df = trading_helper.get_closed_pnl(order_history)

            logger.debug(f"{Colors.PURPLE}Finished Historical Pnl Booked for closed positions ...{Colors.WHITE}")
            # End historical pnl
            ############################################################################

            logger.info("#####################################################################################")
            logger.info(f"{Colors.PURPLE}Starting Getting MWPL for open positions ...{Colors.WHITE}")
            # # Update the Market wide open positions in mwpl table, for the stocks options in the portfolio
            trading_helper.get_and_update_mwpl(portfolio_positions_df=portfolio_positions_df)
            logger.debug(f"{Colors.PURPLE}Finished Getting MWPL for open positions ...{Colors.WHITE}")

            logger.info("#####################################################################################")
            logger.info(f"{Colors.PURPLE}Starting getting Strategies Breakeven ...{Colors.WHITE}")
            # Calculate the breakeven points for the strategies.
            trading_helper.get_strategy_breakeven(portfolio_positions_df)
            logger.debug(f"{Colors.PURPLE}Finished getting Strategies Breakeven ...{Colors.WHITE}")

            logger.debug("#####################################################################################")
            logger.debug(f"{Colors.PURPLE}Starting getting ICICI Funds and Limits...{Colors.WHITE}")
            # # Update the funds and limits available in a demat account hourly
            iciciDirect.update_funds(timeout=c.TIMEOUT_SECONDS)
            nuvama.update_funds()
            logger.debug(f"{Colors.PURPLE}Finished getting ICICI Funds and Limits...{Colors.WHITE}")

            logger.info("#####################################################################################")
            logger.info(f"{Colors.PURPLE}Starting building option strategies {datetime.today()}...{Colors.WHITE}")
            # Build option strategies
            optionStrategyBuilder.option_strategies_builder(timeout=300)
            logger.debug(f"{Colors.PURPLE}Finished building option strategies...{Colors.WHITE}")

            logger.info("\n###################################################################################")
            logger.info(f"{Colors.PURPLE}Getting Portfolio Positions ...{Colors.WHITE}")
            # Get portfolio positions from all brokers accounts.
            icici_portfolio_holdings = iciciDirect.get_portfolio_holdings(timeout=c.TIMEOUT_SECONDS)
            nuvama_portfolio_holdings = nuvama.get_portfolio_holdings(timeout=c.TIMEOUT_SECONDS)
            if icici_portfolio_holdings is not None or nuvama_portfolio_holdings is not None:
                portfolio_holdings_df = pd.concat([icici_portfolio_holdings, nuvama_portfolio_holdings])
                portfolio_holdings_df.reset_index(drop=True, inplace=True)
                trading_helper.persist(portfolio_holdings_df, c.PORTFOLIO_HOLDINGS_TABLE_NAME, if_exists='append')

            logger.info("\n###################################################################################")
            logger.info(f"{Colors.ORANGE}All done going to sleep for {c.REFRESH_TIME_SECONDS/60} min at {datetime.today().strftime('%I:%M %p')} {Colors.WHITE}")
            time.sleep(c.REFRESH_TIME_SECONDS)
    except Exception as e:
        if isinstance(e, URLError):
            logger.error(f"{Colors.RED}Check if internet is connected{Colors.RESET}")
        else:
            logger.error(f"{Colors.RED}Error in main{Colors.WHITE}")
            traceback.print_exc()
    finally:
        if trading_helper.is_market_open() | c.TEST_RUN:
            time.sleep(c.REFRESH_TIME_SECONDS)
            main()
        else:
            if not trading_helper.is_market_open():
                logger.info(f"{Colors.PURPLE}Market Closed{Colors.WHITE}")


def test():
    # Your main code goes here
    try:
        logger.info(f"{Colors.PURPLE}Getting Portfolio Positions ...{Colors.WHITE}")
        # Get portfolio positions from all brokers accounts.
        icici_portfolio_holdings = iciciDirect.get_portfolio_holdings(timeout=c.TIMEOUT_SECONDS)
        nuvama_portfolio_holdings = nuvama.get_portfolio_holdings(timeout=c.TIMEOUT_SECONDS)
        if icici_portfolio_holdings is not None or nuvama_portfolio_holdings is not None:
            portfolio_holdings_df = pd.concat([icici_portfolio_holdings, nuvama_portfolio_holdings])
            portfolio_holdings_df.reset_index(drop=True, inplace=True)
            trading_helper.persist(portfolio_holdings_df,c.PORTFOLIO_HOLDINGS_TABLE_NAME, if_exists='append')



    except Exception as e:
        logger.error(f"{Colors.RED}Error in test{Colors.WHITE}")
        traceback.print_exc()
    finally:
        logger.info(f"{Colors.PURPLE}All done")



# Main function to be executed in the main thread
if __name__ == "__main__":
    # Call the main function to start the program
    logger.info(f"{Colors.ORANGE}Starting Options Trading Dashboarding Toolbox {Colors.WHITE}")
    if c.TEST_RUN:
        logger.info(f"{Colors.ORANGE}Test run Started{Colors.WHITE}")
        test()
    else:
        logger.info(f"{Colors.ORANGE}Starting Live Trading{Colors.WHITE}")
        main()

