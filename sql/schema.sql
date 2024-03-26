
CREATE TABLE if not exists option_pnl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock TEXT NOT NULL,
    expiry TEXT NOT NULL,
    pnl float,
    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists margins_used (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock TEXT NOT NULL,
    expiry TEXT NOT NULL,
    non_span_margin_required float,
    order_value float,
    order_margin float,
    trade_margin float,
    block_trade_margin float,
    span_margin_required float,
    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists order_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    broker TEXT NOT NULL,
    stock TEXT NOT NULL,
    expiry TEXT NOT NULL,
    ltp float,
    order_price float,
    order_status TEXT NOT NULL,
    order_time dateTime NOT NULL,
    action TEXT NOT NULL,
    quantity int,
    right TEXT NOT NULL,
    strike_price float,
    pending_quantity int,
    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists ltp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock TEXT NOT NULL,
    expiry TEXT NOT NULL,
    right TEXT NOT NULL,
    strike_price float,
    ltp float,
    ltt dateTime,
    best_bid_price float,
    best_bid_quantity int,
    best_offer_price float,
    best_offer_quantity int,
    open float,
    high float,
    low float,
    previous_close float,
    ltp_percent_change float,
    upper_circuit float,
    lower_circuit float,
    total_quantity_traded int,
    spot_price float,
    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists ltp_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock TEXT NOT NULL,
    ltp float,
    ltt dateTime,
    best_bid_price float,
    best_bid_quantity int,
    best_offer_price float,
    best_offer_quantity float,
    open float,
    high float,
    low float,
    previous_close float,
    ltp_percent_change float,
    upper_circuit float,
    lower_circuit float,
    total_quantity_traded int,
    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists mwpl(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock TEXT NOT NULL,
    price float,
    price_change_percent float,
    mwpl_prev float,
    mwpl_current float,
   timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists contracts_to_be_sq_off(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock TEXT NOT NULL,
    price_left float,
    pnl float,
    strike_price float,
    expiry_date TEXT NOT NULL,
    right TEXT NOT NULL,
   timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists icici_funds(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_bank_balance float,
    allocated_equity float,
    allocated_fno float,
    block_by_trade_equity float,
    block_by_trade_fno float,
    block_by_trade_balance float,
    available_balance float,
    unallocated_balance float,
    limit_used float,
    limit_available float,
    limit_total float,
    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists nuvama_funds(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adhoc_margin float,
    day_open_balance float,
    funds_added float,
    margin_available float,
    stock_collateral_value float,
    blocked_released_for_delivery float,
    funds_withdrawn float,
    margin_utilized float,
    premium_paid_received float,
    realized_pnl float,
    unrealized_mark_to_market float,
    mtom_margin float,
    nvl float,
    nvl_percent float,
    dpcharges float,
    dpdues float,
    fnopenality float,
    ist float,
    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists os_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT,
    timestamp dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists icici_historical_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT,
    last_updated dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE if not exists nuvama_historical_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT,
    last_updated dateTime NOT NULL DEFAULT (datetime('now','localtime'))
);


CREATE VIEW if not exists last_ltp_stock AS
SELECT ltp, stock
FROM ltp_stock
WHERE id = (SELECT MAX(id) FROM ltp_stock);

CREATE view if not exists view_icici_funds as
select * from icici_funds where id = (select max(id) from icici_funds);

CREATE view if not exists view_nuvama_funds as
select * from nuvama_funds where id = (select max(id) from nuvama_funds);

-- portfolio_holdings definition

CREATE TABLE if not exists "portfolio_holdings" (
  "broker" TEXT,
  "stock" TEXT,
  "broker_stock_code" TEXT,
  "average_price" REAL,
  "quantity" INTEGER,
  "ltp" REAL,
  "change_percentage" REAL,
  "timestamp" TIMESTAMP
);

create view if not exists view_icici_portfolio_holdings as
select *,  round((ltp-average_price )* quantity,0) as profit , ROUND(average_price * quantity,0) as invested_amount,
ROUND(ltp* quantity,0) as current_value  from portfolio_holdings where timestamp =
(select  max(timestamp) from portfolio_holdings where  broker = 'ICICI' )
and   broker = 'ICICI';

create view if not exists view_nuvama_portfolio_holdings as
select *,  round((ltp-average_price )* quantity,0) as profit , ROUND(average_price * quantity,0) as invested_amount,
ROUND(ltp* quantity,0) as current_value  from portfolio_holdings where timestamp =
(select  max(timestamp) from portfolio_holdings where  broker = 'NUVAMA' )
and   broker = 'NUVAMA';
