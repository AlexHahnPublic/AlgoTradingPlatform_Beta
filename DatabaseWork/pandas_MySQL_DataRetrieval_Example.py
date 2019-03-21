#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#========= pandas_MySQL_DataRetrieval_Example.py ==========
#==========================================================

# Purpose
#----------------------------------------------------------
# A solid template on how to retrieve data from our MySQL db set up
# Result, print the tail of the OHLC data for specified criteria

from __future__ import print_function

import pandas as pd
import MySQLdb as mdb

if __name__ == "__main__":
    # Connect to the MySQL instance
    db_host = 'localhost'
    db_user = 'sec_user'
    db_pass = '##*****##'
    db_name = 'securities_master'
    con = mdb.connect(db_host, db_user, db_pass, db_name)

    # SELECT all of the historic Google adjusted close data
    sql = """SELECT dp.price_date, dp.adj_close_price
             FROM symbol as sym
             INNER JOIN daily_price AS dp
             ON dp.symbol_id = sym.id
             WHERE sym.ticker = 'GOOG'
             ORDER BY dp.price_date ASC;"""

    # Create a pandas dataframe from the SQL query
    goog = pd.read_sql_query(sql, con=con,
            index_col='price_date')

    # Output the dataframe tail
    print(goog.tail())

