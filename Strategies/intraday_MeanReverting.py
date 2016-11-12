#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#=============== intraday_MeanReverting.py ================
#==========================================================

# Purpose
#----------------------------------------------------------
# Both the Moving Average Crossover and the S&P Forecaster proved to have
# unattractive sharpe ratio's, adjusted returns, and other performance
# statistics. This is not unusual for longer term basic algorithmic
# trading strategies. In fact we implemented these because they were fairly
# simple and could decently validate our backtesting stack.
#
# A mean reverting higher frequency (minutely) strategy could prove to have
# more attractive performance characteristics. We will check a pair of US
# equity energy sector tickers for mean reverting behavior (could use cADF.py)
# and develop a strategy leveraging that mean reverting nature
#
# NOTE: a higher frequency datahandler and portfolio program must be created
# for this strategy to function

form __future__ import print_function

import datetime as dt

import numpy as np
import pandas as pd
import statsmodels.api as sm

from strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from hft_data import HistoricCSVDataHandlerHFT
from hft_portfolio import PortfolioHFT
from execution import SimulatedExecutionHandler

class IntradayOLSMRStrategy(Strategy):
    """
    Uses ordinary least squares (OLS) to perform a rolling linear regression to
    determine the hedge ratio between a pair of equities. The z-score of the
    residuals time series is then calculated in a rolling fashion and if it
    exceeds an interval of thresholds (defaulting to [0.5, 3.0]) then a
    long/short signal pair are generated for the high threshold) or an exit
    signal pair are generated (for the low threshold)
    """
    # TODO: make tickers inputs
    def __init__(
        self, bars, events, ols_window=100, zscore_low=0.5, zscore_high=3.0
    ):
        """
        Initializes the stat arb strategy

        Parameters:
            bars - The Data Handler object that provides bar information
            events - The Event Queue object
        """

        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.ols_window = ols_window
        self.zscore_low = zscore_low
        self.zscore_high = zscore_high

        self.pair = ('AREX', 'WLL')
        self.datetime = dt.datetime.utcnow()

        self.long_market = False
        self.short_market = False

    def calculate_xy_signals(self, zscore_last):
        """
        Calculates the actual x, y signal pairings to be sent to the signal
        generator

       Parameters:
        zscore_last - The current zscore to test against
        """
        y_signal = None
        x_signal = None
        p0 = self.pair[0]
        p1 = self.pair[1]
        dt = self.datetime
        hr = abs(self.hedge_ratio)

        # If we're long the market and below the negative of the high
        # zscore threshold
        if zscore_last <= -selff.zscore_high and not self.long_market:
            self.long_market = True
            y_signal = SignalEvent(1, p0, dt, 'LONG', 1.0)
            x_signal = SignalEvent(1, p1, dt, 'SHORT', hr)

        # If we're long the market and between the absolute value of the
        # low zscore threshold
        if abs(zscore_last) <= self.zscore_low and not self.long_market:
            self.long_market = True
            y_signal = SignalEvent(1, p0, dt, 'EXIT', 1.0)
            x_signal = SignalEvent(1, p1, dt, 'EXIT', 1.0)

        # If we're short the market and above the high zscore threshold
        if zscore_last >= self.zscore_high and not self.short_market:
            self.short_market = True
            y_signal = SignalEvent(1, p0, dt, 'SHORT', 1.0)
            x_signal = SignalEvent(1, p1, dt, 'LONG', hr)

        # If we're short the market and between the absolute value of the low
        # zscore threshold
        if abs(zscore_last) <= self.zscore_low and self.short_market:
            self.short_market = False
            y_signal = SignalEvent(1, p0, dt, 'EXIT', 1.0)
            x_signal = SignalEvent(1, p1, dt, 'EXIT', 1.0)

        return y_signal, x_signal

    def calculate_signals_for_pairs(self):
        """
        Generates a new set of signals based on the mean reversion strategy.

        Calculates the hedge ratio between the pair of tickers. We will use OLS
        for this although a fleshed out CADF would be superior.
        """

        # Obtain the latest window of values for each component of the pair of
        # tickers
        y = self.bars.get_latest_bars_values(
            self.pair[0], "close", N=self.ols_window
        )
        x = self.bars.get_latest_bars_values(
            self.pair[1], "close", N=self.ols_window
        )

        if y is not None and x is not None:
            # Check that all window periods are available
            if len(y) >= self.ols_window and len(x) >= self.ols_window:
                # Calculate the current hedge ratio using OLS
                self.hedge_ratio = sm.OLS(y, x).fit().params[0]

                # Calculate the current z-score of the residuals
                spread = y - self.hedge_ratio * x
                zscore_last = ((spread - spread.mean())/spread.std())[-1]

                # Calculate signals and add to events queue if valid
                y_signal, x_signal = self.calculate_xy_signals(zscore_last)
                if y_signal is not None and x_signal is not None:
                    self.events.put(y_signal)
                    self.events.put(x_signal)

    def calculate_signals(self, event):
        """
        Override the abstract class's calculate_signals. Check to see whether a
        received event from the queue is a MarketEvent or not. If calculate and
        return SignalEvents based on the market data.
        """

        if event.type == 'Market':
            self.calculate_signals_for_pairs()

#TODO: make ticker names inputs and store in symbol_list. Dates as well
if __name__ == "__main__":
    """
    Tie together the component methods above with the backtesting function
    """

    csv_dir = 'PATH TO CSV DIR HERE'
    symbol_list = ['AREX', 'WLL']
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = dt.datetime(2007, 11, 18, 10, 41, 0)

    backtest = Backtest(
            csv_dir, symbol_list, initial_capital, heartbeat, start_date,
            HistoricCsvDataHandlerHFT, SimulatedExecutionHandler, PortfolioHFT,
            IntradayOLSMRStrategy
        )

