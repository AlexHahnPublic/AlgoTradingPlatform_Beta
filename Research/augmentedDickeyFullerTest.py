#==========================================================
#============= augmentedDickeyFullerTest.py ===============
#==========================================================

# Purpose
#----------------------------------------------------------
# Identifying if a price series has a degree of mean reversion inherent in it
# is a very valuable tool in quantitative and algorithmic finance. One 
# way of statistically making this determination is via the Augmented
# Dickey-Full (ADF) Test. This program leverages statsmodels and pandas
# library to output the results of the ADF test for a given input ticker

from __future__ import print_function
from datetime import datetime
import statsmodels.tsa.stattools as ts
import pandas.io.data as web

# Perform statsmodels ADF test on an input ticker from yahoo data
if __name__ == "__main__":
    import sys
    ticker = str(sys.argv[1])
    amazon = web.DataReader(ticker, "yahoo", datetime(2000,1,1), datetime(2015,1,1))
    dat = ts.adfuller(amazon['Adj Close'], 1)
    print(dat)


