#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#===================== portfolio.py =======================
#==========================================================

# Purpose
#----------------------------------------------------------
# The portfolio object will be in charge of tracking all open positions as well
# as generates orders of a fixed quantity of stock based on signals. In
# theory, at any given point in time we should be able to glean a first order
# approximation of how much our investments would be worth if the entire
# portfolio was instantaneously liquidated (disregarding fees and transaction
# costs). Lastly Portfolio objects can be build to include risk managemant and
# performance analysis tools.
#

from __future__ import print_function

import numpy as np
import pandas as pd

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the

