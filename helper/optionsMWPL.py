import requests
from bs4 import BeautifulSoup
import pandas as pd

# This class scraps the research 360 to get the market wide position limit of different options.

def optionsMWPL():
    # Send a GET request to the URL
    url = 'https://www.research360.in/future-and-options/market-wide-position-limit'
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div containing the table
    div = soup.find('div', {'class': 'mwpltbl', 'id': 'mwplRolloverTable'})

    # Find the table within the div
    table = div.find('table', {'class': 'w-100 TableRowShadow table tableSmall mb-4 mwplRolloverTable text-nowrap'})

    # Extract table headers
    headers = [header.text.strip() for header in table.find_all('th')]

    # Extract table rows
    rows = []
    for row in table.find_all('tr'):
        rows.append([cell.text.strip() for cell in row.find_all('td')])

    # Create DataFrame
    df = pd.DataFrame(rows[1:], columns=headers)

    # Display DataFrame
    # print(df)
    return df