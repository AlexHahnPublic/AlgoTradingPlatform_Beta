#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#============= movingAverageCrossover_MAC.py ==============
#==========================================================

# Purpose
#----------------------------------------------------------
# Although a well documented and generally low Sharpe strategy the Moving
# Average Crossover is a good first strategy to check a backtesting system on.
# Each ticker generates on average only a handful of signals over longer time
# frame which makes it convenient to spot check if our stack, event-processing,
# and databases are all functioning properly. The logic behind the strategy is
# also not overly complex.

from __future__ import print_function

import datetime as dt
import numpy as np
import pandas as pd
import statsmodels.apu as sm

# We will need most components from our Backtesting suite
from strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from portfolio import Portfolio

class MovingAverageCrossStrategy(Strategy):
    """
    Carries out a basic Moving Average Crossover strategy with a short/long
    simple weighted moving average. Default short/long windows are 100/400
    periods respectively.
    """

    def __init__(self, bars, events, short_window=100, long_window=400):
        """ Initializes the Moving Average Cross Strategy

        Parameters:
            bars - The DataHandler object that provides bar information
            events - The event Queue object
            short_window - The short moving average lookback
            long_window - The long moving average lookback
        """

        self.bars = bars
        self.symbols_list = self.bars.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window

        # Set to True if a symbol is "in the market"
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Since the strategy begins out of the market, set the initial "bought"
        value to be "OUT" for each symbol.

        Simply add keys to the bought dictionary for all symbols and set them
        to 'OUT'.
        """

        bought = {}
        for s in s.symbol_list:
            bought[s] = 'OUT'
        return bought

    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the Moving Average Crossover
        SMA with the short window crossing the long window meaning a long entry
        and vice versa for a short entry.

        Parameters:
            event - A MarketEvent object
        """

        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars_values(
                    s, "adj_close", N=self.long_window
                    )
                bar_date = self.bars.get_latest_bar_datetime(s)
                if bars is not None and bars != []:
                    short_sma = np.mean(bars[-self.short_window:])
                    long_sma = np.mean(bars[-self.long_window:])

                    symbol = s
                    dt = dt.datetime.utcnow()
                    sig_dir = ""

                    if short_sma > long_sma and self.bought[s] == "OUT"
                        print("LONG: %s" % bar_date)
                        sig_dir = 'LONG'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.boughht[s] = 'LONG'
                    elif short_sma < long_sma and self.bought[s] == "LONG":
                        print("SHORT: %s" % bar_date)
                        sig_dir = 'EXIT'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'

if __name__ == "__main__":
    csv_dir = 'ENTER PATH IN UBUNTU OS HERE (developing on Mac os partition at
    the moment'
    symbo_list = ['AAPL']
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = dt.datetime(1990, 1, 1, 0, 0, 0)

    backtest = Backtest(
        csv_dir, symbol_list, initial capital, heartbeat, start_date,
        HistoricCSVDataHandler, SimulatedExecutionHandler, Portfolio,
        MovingAverageCrossStrategt
    )
    backtest.simulate_trading()

