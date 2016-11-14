#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#=================== hft_portfolio.py =====================
#==========================================================

# Purpose
#----------------------------------------------------------
# Similarly to dataHandler.py and hft_dataHandler.py, portfolio.py and its
# object structure will need to be slightly adjusted to handle intraday
# positions and conform with DTN IQFeed and Interactive Broker specifications

from __future__ import print_function

import datetime as dt
from math import floor

# For python 2 vs 3 compatibility insurance
try:
    import Queue as queue
except ImportError:
    import queue

import numpy as np
import pandas as pd

from event import FillEvent, OrderEvent
from performance import create_sharpe_ratio, create_drawdowns

class PortfolioHFT(object):
    """
    Very similar to the portfolio.py object by handles positions and market
    values at a one minute resolution for bars.

    The Sharpe Ratio calculation will need to be modified and a correct call
    to the hft_dataHandler object for the close price data with the DTN
    IQFeed bars will need to be made.

    The positions DataFrame stores a time-index of the quantity of positions
    held.

    The holdings DataFrame stores the cash and total matket holdings value of
    each symbol for a particular time-index, as well as the percentage change
    in portfolio total across bars
    """

    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
        Initializes the portfolio with bars and an event queue. Also includes a
        starting datetime index and initial capital (USD unless otherwise
        stated).

        Parameters:
            bars - The DataHandler object with current market data.
            events - the Event Queue object.
            start_date - The start date (bar) of the portfolio.
            initial_capital - The starting capital in USD.
        """

        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.all_positions = self.construct_all_positions()
        self.current_positions = dict( (k,v) for k, v in \
            [(s, 0) for s in self.symbol_list] )

        self.all_holdings = self.construct_all_positions()
        self.current_holdings = self.construct_current_holdings()

    def construct_all_positions(Self):
        """
        Constructs the positions list using the start_Date to determine
        when the time index will begin.
        """

        # Use a dictionary comprehension to generate the time - price
        # key-value pairs dictionary
        d = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date to determine when
        the time index will begin.
        Purports the notion of an 'account' for each symbol, as well as the
        cash on hand, the commission paid, and the total portfolio value.
        Note that upon first implementation there will be no margin
        requirements or shorting constraints.
        """

        d = dict( (k,v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def construct_current_holdings(self):
        """
        Constructs the dictionary which will hold the instantaneous value of
        the portfolio across all symbols.

        Note that the function is almost identical to the
        'construct_all_holdings', the only difference being that it does not
        wrap the dictionary in a list at the return. This is because we will
        only want one accumulated value/entry
        """

        d = dict( (k,v) for k, v in [(s, 0.0) for s in self.symbol_list] )
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current market data
        bar. This reflects the PREVIOUS bar, i.e. all current market data at
        this stage is known (OHLCV).
        """

        latest_datetime =
        self.bars.get_latest_bar_datetime(self.symbol_list[0])

        # Update positions:
        # =================================================
        dp = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list])
        dp['datetime'] = latest_datetime

        for s in self.symbol_list:
            dp[s] = self.current_positions

        # Append the current positions
         self.all_positions.append(dp)

        # Update holdings
        # =================================================
        dh = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * \
                self.bars.get_latest_bar_value(s, "close")
            dh[s] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):
        """
        Takes a Fill object and updates the position matrix to reflect the new
        position.

        Parameters:
            fill - The Fill object to update the position with.
        """

        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update the positions list with the new quantities (add or subtract)
        self.current_positions[fill.symbol] += fill_dir*fill.quantity

    def update_holdings_from_fill(self, fill):
        """
        Takes a Fill object and updates the holdings matrix to reflect the
        holdings value.

        Note that method does not use the cost associated with the FillEvent.
        This is because it is not necessarily indicative of what the historical
        cost would have been to fill (market impact and depth book could change
        the cost to an extent). As a result we will use the "current market
        price" as the fill cost (closing price of the latest bar). This
        approximation should work decently well with most lower frequency
        strategies in relatively liquid markets.

        Parameters:
            fill - The Fill object to update the holdings with.
        """

        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update the holdings list with new quantities
        fill_cost = self.bars.get_latest_bar_value(fill.symbol, "close")
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdingsp['commissions'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings from a FillEvent

        Note that the pure virtual update_fill method from the Portfolio class
        is implemented here and simply leverages the two preceding methods upon
        receipt of a fill event
        """

        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """
        While the Portfolio object must handle FillEvents, it must also take
        care of generating OrderEvents upon the receipt of one or more
        SignalEvents.

        For the sake of a quick build and fully functioning back testing (at
        the sake of realistic position sizing and risk/performance management)
        the method will take in a signal to go long or short an asset and will
        do so for exactly 100 shares of the asset (an arbitrary hard coded
        amount). It will be a ToDo to add a more robust position sizing and
        risk system integration. For now the method will simply handle the
        longing, shorting, and exiting of a position based on the current
        quantity and symbol, generating OrderEvents

        TLDR:
            Simply files an Order object as a constant quantity sizing of the
            signal object, without risk management or position sizing
            considerations.

        Parameters:
            signal - The tuple containing Signal information
        """

        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength

        mkt_quantity = 100 # Arbitrary

        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')

        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders based on the portfolio
        logic
        """

        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        """
        The equity curve is the most important outcome of the portfolio. In
        essence it is a returns stream that we will normalize to a percentage
        basis with the initial account size as 1.0 (rather than absolute dollar
        amount).

        Creates a pandas DataFrame from the all_holdings list of dictionaries.
        """

        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio

        Outputs:
            equity.csv

        Can be loaded into a Matplotlib script, or spreadsheet software for
        analysis
        """

        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, period=252*60*6.5)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown

        stats = [("Total Return", "%0.2f%%" % \
                ((total_return - 1.0) * 100.0)),
                ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                ("Drawdown Duration", "%d" % dd_duration)]

        self.equity_curve.to_csv('equity.csv')

        return stats

