#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#=================== hft_dataHandler.py ===================
#==========================================================

# Purpose
#----------------------------------------------------------
# Intraday data requires a slightly modified data_handler class. Most intraday
# data is not free unlike EOD data. As a result this data handler will be built
# (slightly modified from the daily data_handler) to adhere to DTN IQFeed data
# feed specifications.

