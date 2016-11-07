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

form __fu
