import csv
from helper.colours import Colors
from helper.logger import logger

# CSV file containing stock codes
# This file is used to get the icici specific stock code for a given stock code
# This is used to call the icici apis for generic things, like getting ltp, margin calculations etc.
# Check if data is already cached
# If not, read the CSV file and cache the data
# If the stock code is not found in the CSV file, return an NONE
icici_csv_file = "../data/icici_stock_codes.csv"
nse_csv_file = "../data/nse_stock_codes.csv"

# Global variable to store the cached data
cached_data = {}


def read_csv(csv_file):
    global cached_data
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    cached_data[csv_file] = data
    return data


def get_icici_stock_code(stock_code):
    # First column in this CSV is icici specific stock code
    # Using the same stock code across all positions so that can get a simplified view
    # Also this helps to call the icici apis for generic things, like getting ltp, margin calculations etc.
    # Check if data is already cached
    data = cached_data.get(icici_csv_file)
    if data is None:
        data = read_csv(icici_csv_file)
    for row in data:
        if stock_code.upper() in row:
            return row[0]
    logger.error(f"{Colors.RED}Stock code {stock_code} not found in {icici_csv_file}{Colors.RESET}. Update ICICI stock codes file.")
    return stock_code.upper()


def get_nse_stock_code(stock_code):
    # First column in this CSV is nse specific stock code
    # Using the same stock code across all positions so that can get a simplified view
    # Also this helps to call the nse apis for generic things, like getting ltp, margin calculations etc.
    # Check if data is already cached
    data = cached_data.get(nse_csv_file)
    if data is None:
        data = read_csv(nse_csv_file)
    for row in data:
        if stock_code.upper() in row:
            return row[0].replace(" ", "")
    logger.error(f"{Colors.RED}Stock code {stock_code} not found in {nse_csv_file}{Colors.RESET}. Update NSE stock codes file.")
    return stock_code.upper().replace(" ", "")
