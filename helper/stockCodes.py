import csv
from helper.colours import Colors

# CSV file containing stock codes
# This file is used to get the icici specific stock code for a given stock code
# This is used to call the icici apis for generic things, like getting ltp, margin calculations etc.
# Check if data is already cached
# If not, read the CSV file and cache the data
# If the stock code is not found in the CSV file, return an NONE
csv_file = "../data/stock_symbols.csv"

# Global variable to store the cached data
cached_data = {}


def read_csv():
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
    data = cached_data.get(csv_file)
    if data is None:
        data = read_csv()
    for row in data:
        if stock_code.upper() in row:
            return row[0]
    print(f"{Colors.RED}Stock code {stock_code} not found in {csv_file}{Colors.RESET}")
    return stock_code.upper()
