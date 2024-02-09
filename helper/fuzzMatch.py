import difflib
import pandas as pd
from helper.colours import Colors

from helper import optionsMWPL

stocker_list_file_path = "../data/stock_symbols.csv"
threshold = 0.8


# Function to join two lists using fuzzy matching

def get_stock_code_pairs_using_fuzzy_match(small_list, full_list):
    # Returns a list of tuples of the matched pairs
    # First value in tuple contains the stock code from small_list
    # Second value in tuple contains the stock code from full_list

    # Load the data from the file into a DataFrame
    stocks_csv_df = pd.read_csv(stocker_list_file_path, header=None)

    # Initialize an empty list to store the matched pairs
    matched_pairs = []

    # Create a set for faster lookup
    mySet = set(small_list)
    fullSet = set(full_list)

    # Iterate over each code in the first list
    for stock in mySet:
        # Find the most similar code in the second list
        match = difflib.get_close_matches(stock, fullSet, n=1, cutoff=threshold)

        # If a match is found, add it to the matched pairs list
        if match:
            matched_pairs.append((stock, match[0]))

    remaining_list = [x for x in mySet if x not in matched_pairs]

    for stock in remaining_list:
        # Find the most similar code from the csv file
        # not found the code by fuzzy algorithm
        # Iterate over each code in the stocks csv file

        for row in stocks_csv_df.iterrows():
            # Iterate over each representation and find the most similar stock code
            if row[1].str.contains(stock, case=False).any():
                for fullSetStock in fullSet:
                    if row[1].str.contains(fullSetStock, case=False).any():
                        matched_pairs.append((stock, fullSetStock))
                        break

    remaining_list = [x for x in mySet if x not in [tup[0] for tup in matched_pairs]]
    if len(remaining_list) > 0:
        print(
            f"{Colors.BOLD}{Colors.RED}Not matched Stocks symbols between "
            f"broker1 and broker2 stock codes. "
            f"Length: {len(small_list) - len(matched_pairs)}, Remaining List: {remaining_list}{Colors.RESET}")

    # print(f"{Colors.BOLD}{Colors.GREEN}Matched Length: {len(matched_pairs)}, Matched List: {matched_pairs}{Colors.RESET}")
    return matched_pairs


def test_fuzzy_match():
    mwpl_df = optionsMWPL.optionsMWPL()

    # Example usage
    list1 = unique_stock_codes_mwpl = \
        mwpl_df.drop_duplicates(subset=['Symbol', 'Price', 'Chg', 'Cur.MWPL', 'Pre.MWPL'])['Symbol'].tolist()
    list2 = ['NTPC', 'MOTSUM', 'RELIND', 'GAIL', 'BHAPET', 'NATMIN', 'PERSYS', 'AURPHA', 'TATPOW', 'TATCOM', 'DLFLIM']
    print(list1)
    print(list2)

    matched_pairs = get_stock_code_pairs_using_fuzzy_match(list2, list1)


if __name__ == '__main__':
    test_fuzzy_match()
