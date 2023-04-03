# Get the options trick prices by parsing groww webiste
import math

from nsepy import get_history
import pandas as pd
import requests


def get_strike_prices(stock):
    # the target we want to open
    url = "https://groww.in/options/" + stock["Name"].lower().replace(" ", "-")
    url = url.replace("limited", "ltd")
    url = url.replace("&", "and")
    url = url.replace("ltd.", "ltd")
    url = url.replace("-lt", "-ltd") if url.endswith("lt") else url
    url = url.replace("-serv-", "-services-")
    url = url.replace("-sez-", "-special-economic-zone-")
    url = url.replace("-ent-", "-enterprises-")
    url = url.replace("-fin-", "-financial-")
    url = url.replace("-soft-", "-software-")
    url = url.replace("-co-", "-company-")
    url = url.replace("-int-","-international-")
    url = url.replace("-ind-", "-india-")
    url = url.replace("-INTERNTL-", "-international-")
    #url = url.replace("-corp-", "-corporation-")
    url = url.replace("(", "")
    url = url.replace(")", "")
    url = url.replace(".", "")
    url = url.replace("growwin", "groww.in")

    print("Browsing url: ", url)

    # open with GET method
    try:
        resp = requests.get(url)

        # http_respone 200 means OK status
        if resp.status_code == 200:
            # we need a parser,Python built-in HTML parser is enough .
            x = resp.text.split("strikePrice", 10)
            # print(x)
            # print(x[5])
            # print(x[3])
            Strike_Price = int(x[2].replace("\":", "").split(",")[0])
            Tick_Size = (int(x[3].replace("\":", "").split(",")[0]) - Strike_Price)
            print("Strike: ", Strike_Price / 100, " : tick: ", Tick_Size / 100)
            stock["Strike_Price"] = Strike_Price / 100
            stock["Tick_Size"] = Tick_Size / 100
        else:
            print("Error")
    except:
        print("An exception occurred")


if __name__ == '__main__':
    stocks = pd.read_excel("./data/output.xlsx", converters={'Name': str.strip,
                                                                   'Symbol': str.strip})
    # stocks = stocks.dropna()
    print(stocks.columns)
    print("---Starting loop for each stock defined in input file----")
    for index, row in stocks.iterrows():
        if math.isnan(row["Tick_Size"]):
            print(index, "-##################################################################################-")
            get_strike_prices(row)
            print("---Getting data for", row["Symbol"], ", Strike Price any one: ", row["Strike_Price"], " , Tick Size: ",
              row["Tick_Size"], "-")
        stocks.iloc[index] = row
    stocks.to_excel('./data/output1.xlsx', engine='xlsxwriter')
