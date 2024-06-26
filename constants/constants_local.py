import datetime

from dao.Option import Expiry

# Option trading constants
REFRESH_TIME_SECONDS = 150

# Refresh time fastens up by this factor during market start
# and ending hours, as we need frequent updates during that time.
REFRESH_TIME_FASTEN_FACTOR = 5

TEST_RUN = False

# All Times in mins
MARGIN_DELAY_TIME = 15
MWPL_DELAY_TIME = 60
FUNDS_DELAY_TIME = 15
PORTFOLIO_DELAY_TIME = 120
OPTION_STRATEGIES_DELAY_TIME = 15

#Slack alert for low margin amount threashold
LOW_MARGIN_MONEY_THRESHOLD = 50000

# Value of the sold contract to be sq off
# This is the minimum value of the contract which should be sq off, and will be visible on Sq off dashboard.
# If the value of the contract is less than this value, it will be sq off
# This value is in Rs.
# This value is used in contract_value() method in trading_helper.py file
# This value is used in get_pnl_target() method in trading_helper.py file
CONTRACT_MIN_VALUE_TO_BE_SQ_OFFED = 1000

# OPTION Strategies constants
OPTIONS_STRATEGIES_EXPIRY_MONTH = Expiry.NEXT
OPTIONS_STRATEGIES_TEST_RUN = False
OPTIONS_STRATEGIES_WRITE_TO_FILE = False
OPTIONS_STRATEGIES_WRITE_TO_DB = True
# Percent up and down from the current price it will consider while selecting the strikes
# for building different option strategies.
# Percent has to be given in absolute number like to give 8% give 8 as input.
OPTIONS_STRATEGIES_STRIKE_RANGE_PERCENTAGE = 8
OPTIONS_STRATEGIES_EXEL_FILE = output_file = '../data/output/' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xlsx'

PROCESS_STARTED = 'Started'
PROCESS_COMPLETED = 'Completed'
PROCESS_FAILED = 'Failed'

#Brokers
ZERODHA_BROKER = 'ZERODHA'
ICICI_DIRECT_BROKER = 'ICICI'
NUVAMA_BROKER = 'NUVAMA'

#Order Status
ORDER_STATUS_OPEN = 'OPEN'
ORDER_STATUS_COMPLETE = 'COMPLETE'
ORDER_STATUS_CANCELLED = 'CANCELLED'
ORDER_STATUS_REJECTED = 'REJECTED'

#Date formats
ICICI_DATE_FORMAT = "%Y-%m-%d"
NUVAMA_DATE_FORMAT = "%m/%d/%Y"


# LTP constants
GET_LTP_FROM_ICICI = False
GET_LTP_FROM_NSE = True


PROTFOLIO_POSITIONS_TABLE_NAME = 'portfolio_positions'
ICICI_HISTORICAL_ORDERS_TABLE_NAME = 'icici_historical_orders'
NUVAMA_HISTORICAL_ORDERS_TABLE_NAME = 'nuvama_historical_orders'
OPTIONS_STRATEGIES_STATUS_TABLE_NAME = 'os_status'
MWLP_TABLE_NAME = 'mwpl'
PORTFOLIO_HOLDINGS_TABLE_NAME = 'portfolio_holdings'
ICICI_PORTFOLIO_HONDINGS_VIEW_NAME = 'view_icici_portfolio_holdings'
NUVAMA_PORTFOLIO_HONDINGS_VIEW_NAME = 'view_nuvama_portfolio_holdings'

#Timeout seconds, if there is no response from external API, method will be timedout
TIMEOUT_SECONDS = 20

#Slack Channels
MWPL_CHANNEL = 'mwpl'