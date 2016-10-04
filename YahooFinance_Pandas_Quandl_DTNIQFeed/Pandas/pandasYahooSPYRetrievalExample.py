#==========================================================
#========== pandasYahooSPYRetrievalExample.py =============
#==========================================================

# Purpose
#----------------------------------------------------------
# Use pandas and its DataReader component to download Yahoo finance EOD 
# SPY series data into a pandas DataFrame

from __future__ import print_function

import datetime as dt
import pandas.io.data as web

if __name__ == "__main__":
        spy = web.DataReader(
                "SPY", "yahoo",
                dt.datetime(2007,1,1),
                dt.datetime(2016,9,20)
                )
        print(spy.tail)


