# Get the historical bank nifty option prices on close and next day open
# The prices it gets from wed and thrus
# helps to understand if it makes sense to sell bank nifty on wed and sqoff it on Thrus morning

import datetime
from datetime import date

import pandas as pd
from nsepy import get_history
from tabulate import tabulate

start_day = date.today() - datetime.timedelta(weeks=520)
end_day = date.today() - datetime.timedelta(days=2)

banknifty_df = pd.DataFrame()


def get_banknifty():
    banknifty_df = get_history(symbol="BANKNIFTY",
                               start=date(start_day.year, start_day.month, start_day.day),
                               end=date(end_day.year, end_day.month, end_day.day),
                               option_type="CE",
                               strike_price=300,
                               expiry_date=date(2015, 1, 29))

    print(tabulate(banknifty_df, headers='keys'))
    output_file = './data/output/banknifty' + '.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        banknifty_df.to_excel(writer, sheet_name='PE prices')


get_banknifty()
