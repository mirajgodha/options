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

For each of these strategies you will get a separate tab in excel sheet.

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
