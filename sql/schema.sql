CREATE TABLE if not exists option_pnl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock TEXT NOT NULL,
    expiry TEXT NOT NULL,
    pnl float,
    timestamp dateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock, expiry)
);