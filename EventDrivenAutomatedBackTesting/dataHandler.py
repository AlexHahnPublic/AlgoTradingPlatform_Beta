#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#======================= event.py =========================
#==========================================================

# Purpose
#----------------------------------------------------------
# It would be ideal to utilize the same signal generation methodology and
# portfolio management components for both historical testing and live
# trading. In order to make this compatible with both the Signals and
# Portforlio objects which provides Orders based on them, we must utilise an
# identical interface to a market feed for both historic and live running
# data. This motivates the concept of a class heirarchy based on a
# DataHandler object which gives all subclasses an interface to for providing
# market data to the remaining components within the stack.

from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime as dt
import os, os.path
import numpy as mp
import pandas as pd

from event import MarketEvent

class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for all
    subsequent (inherited) data handlers (both live an historic).

    The goal of a (derived) DataHandler object is to output a generated set of
    bars (OHLCVI) for each symbol requested.

    This will replicate how a live strategy would function as current market
    data would be sent "down the pipe". Thus a historic and live system will be
    treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta # We cannot instantiae an abstract class! only
                            # subclasses however this enables us to ensure that
                            # all Data Handling adheres to compatibility

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar updated
        """
        raise NotImplementedError("Should implement get_latest_bar()")

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars updated
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar
        """
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume, or OI from the last
        bar
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def get_latest_bar_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the latest_symbol list, or N-k if N
        is not fully available
        """
        raise NotImplementedError("Should implement get_latest_bar_values()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol in a tuple
        OHLCVI format: (datetime, open, high, low, close, volume, open
        interest).

        This is a key function to allow us to "drip feed" both our historical
        and live testing framework
        """
        raise NotImplementedError("Should implement update_bars()")

# In order to create a backtesting system based on historical data we need to
# consider a mechanism for importing data via common sources. A natural and
# smart choice would be to couple it with our Securities Master database.
# However for development and developing the overall framework first we will use
# a simpler mechanism of importing (potentially large) CSV files. This will help
# us focus on the data handler itself.

class HistoricCSVDateaHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read  CSV files for each requested
    symbol from disk and provide an interface to obtain the "latest" bar in a
    manner identical to a live trading interface
    """

    def __init__(self, events, csv_dir, symbol_list):
    """
    Initializes the historic data handler by requesting the location of the CSV
    files and a list of symbols

    It will be assumed that all filenames are of the form 'symbol.csv', where
    symbol is a string in the list.

    Parameters:
        events - The Event Queue
        csv_dir - Absolute directory path to the CSV files
        symbol_list - A list of symbol strings

    """

    self.events = events
    self.csv_dir = csv_dir
    self.symbol_list = symbol_list

    self.symbol_data = {}
    self.latest_symbol_data = {}
    self.continue_backtest = True
    self.bar_index = 0

    self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting them into
        pandas DataFrames within a symbol dictionary.

        For this handler it will be assumed that the data is pulled from
        Yahoo finance, therefore the CSVs will follow a very consistent
        layout
        """

        comb_index = None
        for s in self.symbol_list:
            # Load in the CSV file with no header information, indexed on date
            self.symbol_data[s] = pd.io.parsers.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s),
                header=0, index_col=0, parse_dates=True,
                names=[
                    'datetime', 'open', 'high', 'low', 'close', 'volume',
                    'adj_close'
                ]
            ).sort()

            # Combine the index to pad forward values
            if _comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []

        # Reindex the dataframes
        # NOTE: can be updated with "prod" data.py
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].\
                reindex(index=comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed
        """

        for b in self.symbol_data[symbol]:
            yield b

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, N-1):
        """
        Returns the last N bars from the latest_symbol list, or N-k if less
        available
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a python datetime object for the last bar
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data
            set.")
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume, or OI values from
        the pandas Bar series object
        """

        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the latest_symbol list, or N-k if
        less available
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure fo all
        symbols in the symbol list
        """

        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())

