#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#======================= sharpe.py ========================
#==========================================================

# Purpose
#----------------------------------------------------------
# Calculate the annualized Sharpe Ratio for a certain series of returns

from __future__ import print_function

import datetime as dt
import numpy as np
import pandas as pd
import pandas.io.data as web

def annualized_sharpe(returns, N=252):
    """
    Calculate the annualized Sharpe Ratio of a return series based on
    the number of trading periods (default N=252 assuming daily returns).
    Note that the function assumes returns ABOVE a comparable benchmark
    """
    return np.sqrt(N) * returns.mean() / returns.std()

# TODO: add dates as inputs
def equity_sharpe(ticker):
    """
    Let's implement one common use case of the Sharpe Ratio on a trading
    strategy: a straightforward buy and hold strategy. This function leverages
    a call(s) to Google Finance.
    """

    start = dt.datetime(2000,1,1)
    end = dt.datetime(2013,1,1)

    # Obtain the daily equities historic data for the time period and put in
    # pandas DataFrame
    pdf = web.DataReader(ticker, 'google', start, end)

    # Use the percentage change method to calculate daily returns
    pdf['daily_ret'] = pdf['Close'].pct_change()

    # Assume an average annual risk-free rate over the period of 5%
    pdf['excess_daily_ret'] = pdf['daily_ret'] - 0.05/252

    # Return the annualized Sharpe Ratio based on the excess daily returns
    return annualized_sharpe(pdf['excess_daily_ret'])

# TODO: take dates as inputs
def market_neutral_sharpe(ticker, benchmark):
    """
    Calculate the annualized Sharpe Ratio of a market neutral long/short 
    strategy. Here we will subtract the short position benchmark tracker in
    order to calculate the net (isolate the equity's performance from the market
    in general) daily returns
    """

    start = dt.datetime(2000, 1, 1)
    end = dt.datetime(2013, 1, 1)

    # Get historical data for both a symbol/ticker and a benchmark ticker
    tick = web.DataReader(ticker, 'google', start, end)
    bench = web.DataReader(benchmark, 'google', start, end)

    # Calculate the percentage returns on each of the time series
    tick['daily_ret'] = tick['Close'].pct_change()
    bench['daily_ret'] = bench['Close'].pct_change()

    # Create a new DataFrame to store the strategy information
    # The net returns are (long - short)/2, since there is twice the trading
    # capital for this strategy
    strat = pd.DataFrame(index=tick.index)
    strat['net_ret'] = (tick['daily_ret'] - bench['daily_ret'])/2.0

    # Return the annualized Sharpe Ratio for this strategy
    return annualized_sharpe(strat['net_ret'])


if __name__ == "__main__":
    import sys
    ticker = str(sys.argv[1])
    print("%s Sharpe Ratio: %s" % (ticker, equity_sharpe(ticker)))
    print('%s Market Neutral Sharpe Ratio (against SPY benchmark): %s' % (ticker, market_neutral_sharpe(ticker,'SPY')))





    

