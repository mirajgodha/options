

# Columns for the order status dataframe
order_status_columns = ["stock", "ltp", "average_price", "quantity",  "strike_price", "expiry_date", "right", "pnl","action"]

# Columns for the margins used dataframe
margins_used_columns = ["stock", "expiry", "non_span_margin_required", "order_value", "order_margin", "trade_margin", "block_trade_margin", "span_margin_required"]

# Columns for the pnl dataframe
pnl_columns = ["stock", "expiry", "pnl"]

# Columns for the mwpl dataframe
mwpl_columns = ["stock", "price", "chg", "cur.MWPL", "pre.MWPL"]

# Columns for the funds dataframe
funds_columns = ["available_balance", "margin_available", "total_balance"]

# Columns for the ltp dataframe
ltp_columns = ["stock", "strike_price", "expiry_date", "right", "ltp"]

__main__ = "optionDataFramesStructures.py"

if __name__ == "__main__":
    print("optionDataFramesStructures.py")