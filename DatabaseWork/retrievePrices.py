#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#================= retrievePrices.py ====================
#==========================================================

# Purpose
#----------------------------------------------------------
# Obtain historical data for the S&P500 symbols we've retrieved and
# stored in the MySQL symbols table.

from __future__ import print_function

import datetime as dt
import warnings
import MySQLdb
import requests

# Connect to our MySQL database instance
db_host = 'localhost'
db_user = 'sec_user'
db_pass = '##****##'
db_name = 'securities_master'
con = MySQLdb.connect(db_host, db_user, db_pass, db_name)

def get_db_tickers():
    """
    Pull the S&P500 equity tickets from our symbol table
    """
    with con:
        cur = con.cursor()
        cur.execute("SELECT id, ticker FROM symbol")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]

def retrieve_yahoo_historical_prices(ticker, start_date=(2000,1,1), end_date=dt.date.today().timetuple()[0:3]):
    """
    Obtain daily ticker data per symbol, returns a list of tuples,
    NOTE: date format is (YYYY,MM,DD) format
    """
    # For the next part we will need to construct the Yahoo URL per ticker
    # with dates
    ticker_tup = (
        ticker, start_date[1]-1, start_date[2],
        start_date[0], end_date[1]-1, end_date[2],
        end_date[0]
    )
    yahoo_url = "http://ichart.finance.yahoo.com/table.csv"
    yahoo_url += "?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s"
    yahoo_url = yahoo_url % ticker_tup

    # Connect to Yahoo Finance and obtain the ticker data, if unsuccesful
    # print an error message
    try:
        yf_data = requests.get(yahoo_url).text.split("\n")[1:-1]
        prices = []
        for y in yf_data:
            p = y.strip().split(',')
            prices.append(
                (dt.datetime.strptime(p[0], '%Y-%m-%d'), p[1], p[2], p[3], p[4], p[5], p[6])
            )
    except Exception as e:
        print("Could not download Yahoo data: %s" % e)
    return prices

def prices_into_MySQLdb(data_vendor_id, symbol_id, daily_data):
    """
    Inputs: list of tuples containing daily price data
    daily_data - List of tuples of OHLC data, contains adj_close and
    volume
    Note that we will append the vendor ID and symbol ID into the data we
    insert into the db
    """
    # Log time for last_updated_date field in table
    time = dt.datetime.utcnow()

    # Set up daily data row formats, also including vendor ID and symbol ID
    daily_data = [
        (data_vendor_id, symbol_id, d[0], time, time, d[1], d[2],
        d[3], d[4], d[5], d[6])
        for d in daily_data
    ]

    # Create the SQL insert strings
    col_str = """data_vendor_id, symbol_id, price_date, created_date,
              last_updated_date, open_price, high_price, low_price,
              close_price, volume, adj_close_price"""
    ins_str = ("%s, "*11)[:-2]
    final_str = "INSERT INTO daily_price (%s) VALUES (%s)" % \
            (col_str, ins_str)

    # Using the MySQL connection, perform the INSERT statements by symbol
    with con:
        cur = con.cursor()
        cur.executemany(final_str,daily_data)


# The usual commandline interface template
if __name__ == "__main__":
    warnings.filterwarnings('ignore') #ignore data truncation warnings from Yahoo caused by precision to Decimal(19,4) datatypes

    ticks = get_db_tickers()
    lenticks = len(ticks)
    for i, t in enumerate(ticks):
        print("Adding data for %s: %s out of %s" % (t[1], i+1, lenticks))
        yf_data = retrieve_yahoo_historical_prices(t[1])
        prices_into_MySQLdb('1', t[0], yf_data)
    print("Successfully added Yahoo Finance pricing data to MySQL db")

