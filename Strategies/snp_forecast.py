#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#============= movingAverageCrossover_MAC.py ==============
#==========================================================

# Purpose
#----------------------------------------------------------
# Construct a basic SPY forcaster and create the corresponding strategy. The
# goal would be to see if the strategy beats a basic buy and hold strategy of
# the ETF.
#
# Note that for this strategy we will only be going long and exiting, not short
# selling. Similarly there should be a proper analysis done of the confusion
# matrix to dynamically hedge/ proportion our positions

from __future__ import print_function

import datetime as dt

import pandas as pd
from sklearn.qda import QDA

from strategy import Strategy
from event import Signal Event
from backtest import Backtest
from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from create_lagged_series import create_lagged_series

class SPYDailyForecastStrategy(Strategy):
    """
    Use a Quadratic Discriminant (sklear) Analyser to create an S&P500 forecast
    strategy. The strategy will predict the returns for a subsequent time
    period and then generate long/exit signals based on the prediction.
    """

    def __init__(self, bars, events):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.datetime_now = dt.datetime.utcnow()

        self.model_start_date = dt.datetime(2001,1,10)
        self.model_end_date = dt.datetime(2005,1,10)
        self.model_start_test_date = dt.datetime(2005,1,1)

        self.long_market = False
        self.short_market = False
        self.bar_index = 0

        self.model = self.create_symbol_forecast_model()

    def create_symbol_forecast_model(self):
        # Create a lagged series of the S&P500 US stock market index
        snpret = create_lagged_series(
            self.symbol_list[0], self.model_start_date,
            self.model_end_date, lags=5
        )

        # Use the prior two days of returns as predictor values, with direction
        # as the response
        X = snpret[["LAG1","Lag2"]]
        y = snpret['Direction']

        # Create training and test sets
        start_test = self.model_start_test_date
        X_train = X[X.index < start_test]
        X_test = X[X.index >= start_test]
        y_train = y[y.index < start_test]
        y_test = y[y.index >= start_test]

        model = QDA() # Can easily switch to other ML techniques here
        model.fit(X_train, y_train)
        return model

    def calculate_signals(self, event):
        """
        Calculate the SignalEvents based on market data
        """
        sym = self.symbol_list[0]
        dt = self.datetime_now

        if event.type == 'Market':
            self.bar_index += 1
            if self.bar_index >5:
                lags = self.bars.get_latest_bars_value(
                    self.symbol_list[0], "returns", N=3
                )
                pred_series = pd.Series(
                    {
                        'Lag1': lags[1]*100.0,
                        'Lag2': lags[2]*100.0
                    }
                )
                pred = self.model.predict(pred_series)
                if pred > 0 and not self.long_market:
                    self.long_market = True
                    signal = ASignalEvent(1, sym, dt, 'LONG', 1.0)
                    self.events.put(signal)

                if pred < 0 and self.long_market:
                    self.long_market = False
                    signal = SignalEvent(1, sym, dt, 'EXIT', 1.0)
                    self.events.put(signal)

if __name__ == "__main__":
    csv_dir = 'INPUT PATH TO CSV DIR HERE'
    symbol_list = ['SPY']
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = dt.datetime(3006,1,3)

    backtest = Backtest(
        csv_dir, symbol_list, initial_capital, heartbeat, start_date,
        HistoricCSVDataHandler, SimulatedExecutionHandler, Portfolio,
        SPYDailyForecastsStrategy
    )
    backtest.simulate_trading()

