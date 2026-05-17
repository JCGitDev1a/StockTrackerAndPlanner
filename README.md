# StockTrackerAndPlanner
Tracks portfolios of stocks and assists with planning based on dividends.  Includes historical and future planning.

This system is based on my original spreadsheet and the math and logic I created over a multi-month process.

The background for my investing logic is I want to track when my dividends for individual holdings (stocks/funds/etfs) will reach a +1 quantity every quarter (or every dividend period).
At that point the continued growth is much more impressive and the returns continue even as share price increases.

In my spreadsheet I have two worksheets per account: Current and Future

My Current sheet tracks the following:
Sym	Company	Qty	B P	B Val	C Price	Curr Value	52 low	52 high	% Hold	Div	Div / Qtr	Div / Yr	Yld Cst	Yld Cur	Div Mnth	\ Shr drip/qtr	TTL \# 2 B 1/q	Div $ @ 1/q	\# Shr till 1/q	$ till 1/Q	\# qtrs till 1/Q	\# yr till 1/q

The Future sheet tracks the following:
Sym	Company	Cur Qty	Prj Qty	B P	B Val	C Price	Curr Value	G/L	52 low	52 high	% Hold	Div	Div / Qtr	Div / Yr	Yld Cst	Yld Cur	Div Mnth	\#ShDrip/Q	TTL \# 2B@Q	Div $ @BQ	\# Shr till B/q	$ till B/Q	\# Q till B/Q	\# Y till 1/q

The Future sheet links to the Current sheet for current pricing and quantity.  I can also track what a DRIP adds to quantity, future dividends, etc.

Later I track how many shares I buy at each DRIP, projected dividend when I am buying +1 share each quarter/DRIP, how many more shares I need to buy to reach +1 each quarter/DRIP, how much money I need to spend to buy enough shares to reach that +1 each quarter/DRIP, and then how many quarters and years at current DRIP until I reach +1 each quarter/DRIP.

Instead of doing all this manually, this system has been developed to provide a multi-user and multi-account capability in a usable web-based interface with a DB backend.  It will also have the ability to use market API's to get the current and watchlist pricing, market actions (splits), and dividends without having to manually do this.


To build:

This is being developed on Ubuntu 24.04 with Docker and Postgressql DB.  Everything else that is required should be contained within the Docker image.
