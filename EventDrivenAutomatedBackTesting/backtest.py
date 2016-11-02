#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#====================== backtest.py =======================
#==========================================================

# Purpose
#----------------------------------------------------------
# Encapsulates the event-handling logic tying together all the class files. The
# Backtest object is composed of an outer "heartbeat" while-loop for event
# driven simulation and an inner while-loop that actually processes the signals
# and sends them to the correct component determined by the event type. The
# Event Queue is there for continually being populated and depopulated with
# events

from __future__ import print_function

import datetime as dt
import pprint
try:
    import Queue as queue
except ImportError:
    import queue
import time

class Backtest(object):
    """
    Encapsulates the settings and components for carrying out an event-driven
    backtest
    """

    def __init__(
        self, csv_dir, symbol_list, initial_capital, heartbeat, data_handler,
        execution_handler, portfolio, strategy):
        """
        Initialize the backtest

        Parameters:
            csv_dir - The absolute root to the CSV data directory
            symbol_list - The list of symbol strings
            initial_capital - The starting capital for the portfolio
            heartbeat - The backtests temporal clock tick in seconds
            start_date - The start datetime of the strategy
            data_handler - (Class) Handles the market data feed
            execution_handler - (Class) Handles the orders/fills for trades
            portfolio - (Class) Keeps track of portfolio current and prior
            positions
            strategy - (Class) Generates signals based on market data
        """

        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.evebts = queue.Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from their class types
        """

        print("Creating DataHandler, Strategy, Portfolio, and ExecutionHander")

        self.date_handler = self.data_handler_cls(self.events, self.csv_dir,
            self.symbol_list)

        self.strategy = self.strategy_cls(self.data_handler, self.events)

        self.portfolio = self.portfolio_cls(self.data_handler, self.events,
                self.start_date, self.initial_capital)

        self.execution_handler = self.execution_handler_cls(self.events)

    def _run_backtest(self):
        """
        This is orchestrator of the backtest and ties the backtesting programs
        together in a hopefully very clear manner.

        For a MarketEvent, the Strategy object is told to recalculate new
        signals, while the Portfolio object is told to reindex the time. If a
        SignalEvent Object is received the Portfolio is told to handle the new
        signal and convert it into a set of OrderEvents, if appropriate. If an
        OrderEvent is received the ExecutionHandler is sent the order to be
        transmitted to the broker (if in a real trading setting). Finally, if a
        FillEvent is received, the Portfolio will update itself to be aware of
        the new positions.
        """

        cycle = 0

        while True:
            cycle += 1
            print cycle

            # Update the market bars
            if self.data_handler.continue_backtest == True:
                self.data_handler.update_bars()
            else:
                break

            # Handle the events
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)

                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)

                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Once the backtest simulation is complete the performance of the
        strategy can be displayed to the terminal/console. The pandas DataFrame
        representing the Equity curve can be created along with summary
        statistics
        """

        self.portfolio.create_equity_curve_dataframe()

        print("Creating summary statistics...")
        stats = self.portfolio.output_summary_stats()

        print("Creating the Equity curve (display tail(10))...")
        print(self.portfolio.equity_curve.tail(10))
        pprint.pprint(stats)

        print("Signals generated: %s" % self.signals)
        print("Order generated: %s" % self.orders)
        print("Fills: %s" self.fills)

    def simulate_trading(self):
        """
        Runs the backtest then output performance methods sequentially
        """

        self._run_backtest()
        self.output_performance()

