# Options Strategy Builder
This helps people to look at different options strategies on NSE stocks.
Stock option Strategies calculator calculates the Max profit and loss which you can incurs in this strategy.
The final output is printed to an excel sheet in a sorted format for all the Fno stocks of NSE
This will help you decide which option strategy you can take on a stock for your best profit based on current market conditons.
There are list of predifined strategies already been created

- Long Call Condor
- Long Iron Butterfly
- Long Put Condor
- Short Call Butterfly
- Short Call Condor
- Short Guts
- Short Iron Butterfly
- Short Put Butterfly
- Short Put Condor
- Short Straddle
- Short Strangle
- Naked Call
- Naked Put

When write to Excel is enalbled it will create an excel file. For each of these strategies you will get a separate tab in excel sheet.
Whne write to SQL is enabled it will create a table for each strategy in DB and that can be visualized on Metabase

Metabase Strategies looks like this:
<img width="1356" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/b30698a0-654a-4f8f-b369-89c0d84da46e">

<img width="1385" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/d1c2d70c-0a88-42db-a0d6-89635d24490b">
All Strategies Profitable is a special case, which goes throught each of the above strategy and check if max loss is less than a given threashold and profit probablity is high. It scans for all stocks across all given strategies.

<img width="1378" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/4fc94f21-285a-4db8-9878-b6c0837d0124">

In constants file you can configure, how much strike difference it should look for these strategies. This is very usefull specially for Sort Strangle, Naked Call, Naked Put etc.



The sample output file looks like this:

![image](https://user-images.githubusercontent.com/3658490/232991057-11ee44a8-c231-4aea-b196-762cc7f62960.png)

Columns explanation:

- Stock	- NSE symbol of stock
- PremiumCredit	- Premium which will be credited for this strategy
- MaxProfit	- Max profit which you will get in this strategy
- MaxLoss	- Max loss which you can incur in this strategy
- PE_sell_price	- Sell price of put
- PE_sell_strike - Strike at which put is sold
- PE_buy_price	- Buy price of put
- PE_buy_strike	- Strike price of put buy
- lot_size - option lot size
- pl_on_strikes - It gives you a range of pices and what is the profit and loss in that range. E.g. [(-430.0, 1120, 1420), (2320.0, 1420, 1440), (-430.0, 1440, 1800)] -- This tells at expirty if stock closes between 1120 to 1420 you will incur a loss of 430 Rs and if stock closes between 1420 and 1440 you will get a profit of 2320 Rs. 
- Strikes - Different strikes traded for the options. E.g. [1120, 1140, 1160, 1180, 1190, 1200, 1210, 1220, 1230, 1240, 1250, 1260, 1270, 1280, 1290, 1300, 1310, 1320, 1330, 1340, 1350, 1360, 1370, 1380, 1390, 1400, 1410, 1420, 1430, 1440, 1450, 1460, 1470, 1480, 1490, 1500, 1510, 1520, 1530, 1540, 1550, 1560, 1570, 1580, 1590, 1600, 1610, 1620, 1630, 1640, 1660, 1680, 1700, 1720, 1740, 1760, 1780, 1800]

It will also calcualte the greeks for the option price:

Below greeks are calcualted for the whole option strategy 

- IV - Implied Volatility for the whole strategy.
- Theta - Theta is the measure of the sensitivity of the option price relative to the option's time to maturity. If the option's time to maturity goes down in one day, the option's price will change by the theta amount.
- Total Theta - Total theta decay amount for the whole option lot in the strategy
- Delta - It's a measure of the sensitivity of an option's price changes that are relative to the changes in the underlying asset' prices.
- Total Delta - Total delta for the whole option lots in the strategy
- Gamma  - Gamma is a measure of the Delta's change relative to the changes in the price of the underlying asset.
- Vega - Vega is an option Greek that would measure the sensitivity of the option price that is relative to the volatility of the asset

## Option Strategies

### Long Call Condor

Long Call Condor is a strategy that must be devised when the  __investor is neutral on the market direction and expects volatility to be less in the market.__

A Long Call Condor strategy is formed by buying Out-of-the-Money Call Option (lower strike), buying In- the-Money Call Option (lower strike), selling Out-of-the-Money Call Option (higher middle) and selling In- the-Money Call Option (higher middle). All Call Options must have the same underlying security and expiration month.

This strategy is very similar to a Long Call Butterfly. The difference is that the sold options have different strikes. The profit pay off profile is wider than that of the Long Butterfly.

Investor view: Neutral on direction and bearish on Stock/ Index volatility.

**Risk:** Limited.

**Reward:** Limited.

**Lower breakeven:** Lowest Strike + net premium paid. 

**Higher breakeven:** Highest Strike – net premium paid. 

![image](https://user-images.githubusercontent.com/3658490/233072905-24081545-ffcf-4577-9dd9-02ebd5194ced.png)

# Added intergration with multiple brokes

This section of code is added to solve the following problems:

As a option trader, when you do trading on multiple platfrom, its difficult to manage positions across different brokers. So to get a consolidated positons accross different borkers I started this idea.
Now as the code is growing its helping me to visulize lot of things on a single nice dashboard.
- Nice Dashboard for get the consolidated total PnL across different borkers.
- Nice charts to view the PnL over time. Which is not possible in any of the brokers tools or apps.

As a option trader when you create different strategies, on different stocks there is no way to keep track of profit and loss across different stock strategies. So to solve that problem, this dashboards, help in:
- Getting nice charts to view the loss profit bar graphs across different Stock strategies.
  <img width="1356" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/dae464e0-c903-4721-9725-e80827281e67">


- View the timeseries chart of PnL across each stock strategy.
<img width="1277" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/0f9c76e0-eca1-4466-83f3-0fa18c56afae">



When the stock is about to go to ban list its difficult to exit the positions or add new ones to safegaurd your strategies. Its very difficult, to get the MWPL (Market wide open positions), to handle that problem, i have added a nice MWPL dashboard, which will not only show the MWPL for your stocks but will also hightlight the possible entrants.

<img width="847" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/32953db0-0350-4b91-83d0-dbd290d9b13e">


When you have different option strategies open, there is no tool to show you the historical price chart for the price of given strike for a stock. I have added a charting option to plot the option price charts of your open positions.

<img width="1290" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/32813d73-abdc-4687-a7de-09ee03bb481c">

As a option writer, when you have many open positions its difficult to track which positions you should exit based on different rules. There could be automated triggers to exit, but you know whne you exit with Market order how much loss you will face even for profitiable exits. So to handle this problem there are few solutions implemented:
- Charts with continous PnL at strategy level, so that can get a quick view.
- PnL tracker alerts - In the excel sheet profit_loss.xlsx fill in the trigger prices for profit and loss and it will alert you.

Margin is the most killing thing to manage as a option writer. It just vanishes in your open positions, so to keep an track of margin used realtime, I have added nice chart to track total Margin used and split across strategies of different stocks positions.
<img width="998" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/f4c42c0b-f820-4fba-afa7-5acc5fa6c431">

When you place multiple orders and as a Strangle or Straddle writer, you might have to put multiple orders together, and if one gets execcuted its urgent to trigger the other one(s) at the current market price to stop the loss or prevent your strategy from spoiling. So its difficult to keep track orders, therefore added the orders dashbaords as well. It will help in following ways:
- Get all the open orders list at realtime, along with LTP which is most important thing as most brokers do not show LTP and its difficult to figure out when your order will be triggered.
- Get the list of executed orders.
- It also shows the nice chart along with executed orders, to find out how much Mark to market loss or profit you have for for your executed orders. Its nice to figure out how good was your decision to place that order.

Option price LTP charts for all your open positions, very helpful in looking at the option price.
<img width="803" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/a7b344fa-189a-4737-a699-a675fc4446c3">


## ICICI Direct

Gets following data from ICICI Direct:

- Get the Current Positions
- Margins used
- Order list of executed orders
- Order list of pendng orders
  

**How to run ICICI Direct positions:**
Run icici_direct_main.py file in your IDE or via console.

# Added Metabase
A nice dashboard which will help you with the following:

Consolidated total loss and profit across all option strategies across all borkers
Charts of profit and loss of total PnL 
Charts of profit and loss of each stock option strategy -- This is the very important feature i was looking for and was not available any where including Sensibull and Quantsapp.

<img width="1272" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/3580e74e-ac6f-4dc4-bc17-5d26daa6b1f4">

<img width="1061" alt="image" src="https://github.com/mirajgodha/options/assets/3658490/5b7f4eb6-d764-4bc8-86e8-026625bd54cc">

**How to Run Metabase:**
- Download the Metabase jar https://www.metabase.com/start/oss/jar inside the metabase folder
- Please install java if not installed
- Run the command on your command line:
- cd to the metabase directory in the code and from there run the below command, as this directory contains the metabase dashboards files.
- java -jar metabase.jar
- Once it starts, on your browser type: http://localhost:3000/dashboard/1-pnl?tab=1-tab-1

# Points to note
- Broker positions and other stuff runs only when Market is open on weekdays, for test run if you want to run update the flag TEST_RUN to True in file helper.constants.py
- 

