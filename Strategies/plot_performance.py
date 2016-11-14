#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#============= plot_performance.py ==============
#==========================================================

# Purpose
#----------------------------------------------------------
# All strategies will return data including: portfolio growth (in terms of %
# value over time), Period of returns, and Drawdown. These time series will be
# plotted in this script

import os.path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    data = pd.io.parsers.read_csv(
        "equity.csv", header=0, parse_dates_True, index_col=0
    ).sort()

    # Plot three charts: Equity curve, period returns, drawdowns
    fig = plt.figure()
    # Set the outer color to white
    fig.patch.set_facecolor('white')

    # Plot the equity curve
    ax1 = fig.add_subplot(311, ylabel='Portfolio value, %')
    data['returns'].plot(ax=ax2, color="black", lw=2.)
    plt.grid(True)

    # Plot the figure
    plt.show()
