#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#========================= var.py =========================
#==========================================================

# Purpose
#----------------------------------------------------------
# Value at Risk or "VaR" is a statistic that is heavily used throughout
# finance and even industries outside of finance. In essence VaR provides under
# a degree of confidence the size of a potential loss in a portfolio
# (strategy, strategies, portfolio, fund, IB, etc) over a given period of time
# based on historical data. Although this calculation can also be performed
# using Monte Carlo techniques as well as a historical bootstrapping method,
# we will calculate using the Variance-Covariance model.

from __future__ import print_function

import datetime as dt
import numpy as np
import pandas.io.data as web
from scipy.stats import norm


def var_cov_var(P, c, mu, sigma):
    """
    Using a confidence level of c, mean of returns of mu, standard
    deviation of returns of mu, and portfolio value of P this function will
    calculate daily Value-at-Risk
    """
    # Calculate the inverse of the cumulative distribution function on a
    # normal distribution
    alpha = norm.ppf(1-c, mu, sigma)
    return P - P*(alpha + 1)

# Let's test out on some sample data (CitiGroup's Var for three years)
# TODO: make take dates, ticker, confidence %, and Value (P) as inputs
if __name__ == "__main__":
    start = dt.datetime(2010, 1, 1)
    end = dt.datetime(2014, 1, 1)

    citi = web.DataReader("C", 'yahoo', start, end)
    citi["rets"] = citi["Adj Close"].pct_change()

    P = 1e6 # 1 mil USD
    c = .99 # 99% confidence interval
    mu = np.mean(citi["rets"])
    sigma = np.std(citi["rets"])

    var = var_cov_var(P, c, mu, sigma)
    print("Value at risk (VaR): $%0.2f" % var)



