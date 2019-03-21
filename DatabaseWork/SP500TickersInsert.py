#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#================= SP500TickersInsert.py ==================
#==========================================================

# Purpose
#----------------------------------------------------------
# To scrape wikipedia for the S&P500 symbols and insert into our MySQL database
# tables


from __future__ import print_function # Note that this has to be first because
                                      # it will change the fundamental nature 
                                      # of how the compiler should compile  (ie
                                      # borrow print_function from python3)

import datetime as dt
import bs4
import MySQLdb
import requests

from math import ceil

def download_parse_wiki_SP500():
    """
    This function will leverage the BeautifulSoup4 library to download and
    parse the S&P 500 tickers from Wikipedia

    It will return a list of tuples to insert via MySQL
    """

    # Store the time to later insert into our created_at column
    time = dt.datetime.utcnow()

    # Download the symbol list from wikipedia, note the link
    page = requests.get(
            "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    )
    soup = bs4.BeautifulSoup(page.text)

    # Grab the first table, and ignore the header row
    rawSymbolsList = soup.select('table')[0].select('tr')[1:]

    # Gather symbol info row by row in "S&P 500 Component Stocks" table
    syms = []
    for i, symbol in enumerate(rawSymbolsList):
        tds = symbol.select('td')
        syms.append(
                (
                    tds[0].select('a')[0].text, # Symbol
                    'stock',                    # denote Equity asset
                    tds[1].select('a')[0].text, # Name
                    tds[3].text,                # Sector
                    'USD',                      # Currency
                    time, time                  # Time stamps
                    )
                )
    return syms

def insert_SP500_syms(symbols):
    """
    Take the tuple of symbols and insert into our MySQL database
    """

    # Connect to our instance of the db
    db_host = 'localhost'
    db_user = 'sec_user'
    db_pass = '##****##'
    db_name = 'securities_master'
    con = MySQLdb.connect(
            host=db_host, user=db_user, passwd=db_pass, db=db_name
            )

    # Create the insert strings
    col_str = """ticker, instrument, name, sector, currency, created_date,
    last_updated_date
    """
    ins_str = ("%s, "*7)[:-2]
    final_str = "INSERT INTO symbol (%s) VALUES (%s)" % \
            (col_str, ins_str)
    
    # Lastly, using the MySQL connection, perform the inserts for every symbol
    with con:
        cur = con.cursor()
        cur.executemany(final_str, symbols)


# The standard script execution block
if __name__ == "__main__":
    symbols = download_parse_wiki_SP500()
    insert_SP500_syms(symbols)
    print("%s symbols were successfully added." % len(symbols))
