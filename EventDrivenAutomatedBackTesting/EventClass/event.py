#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#======================= event.py =========================
#==========================================================

# Purpose
#----------------------------------------------------------

from __future__ import print_function

class Event(object):
    """
    Parent/ base class providing an interface for all subsequent
    (inhereted) events. This class will trigger further events in the
    automated trading infrastructure
    """
    pass

class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with corresponding bars.
    MarketEvents are triggered each event-loop cycle. It occurs when the
    DataHandler object recieves a new update of market data for any symbols
    which are currently being trackd. It is used to trigger the Strategy
    object to generate a new batch of trading signals. It simply contains an
    identification that is a market event, with no other structure
    """

    def __init__(self):
        """
        Initializes the MarketEvent
        """
        self.type = 'MARKET'

class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object. This is
    received by a Portfolio object and further action is taken. Th
    SignalEvent contains: a strategy ID, a ticker symbol, a timestamp of
    generation, a direction (usually long or short), and a 'strength;
    indicator (see correlation and mean reverting Research folder for
    specification and quantification techniques). Ultimately the
    SignalEvents are utilized by the Portfolio object as advice for how to trade
    """

    def __init__ (self, strategy_id, symbol, datetime, signal_type,
            stength):
        """ Initialized the SignalEvent

        Parameters:
            strategy_id - The unique identifier for the strategy that
            generated the signal
            symbol - The ticker symbol, e.g. 'GOOG'
            datetime - The timestamp at which the signal was generated
            signal_tpe - 'LONG' or 'SHORT'
            strength - An adjustment factor "suggestion" used to scale the
            quantity at the portfolio level. Useful for pairs strategies.
        """

        self.type = 'SIGNAL'
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength

class OrderEvent(Event):
    """
    When a Portfolio object receives SignalEvents it assesses them in a wider
    context of the portfolio in terms of risk and position sizing (see
    Research/PerformanceMeasurement). This ultimatley leads to OrderEvents that
    will be sent to an ExecutionHandler.

    The OrderEvent is slightly more complex than a Signal Event since it
    contains a quantity field in addition to the aformentioned properties of
    SignalEvent. The quantity is determined by the Portfolio constraints. In
    addition the OrderEvent has a print_order() method used to output the
    detailed order information if requested to the console.

    TLDR: Handles the event of sending an Order to the execution system
    """

    def __init__(self, symbol, order_type, quanitity, direction):
        """
        Initializes the order type, setting whether it is a Market order
        ('MKT') or Limit order ('LMT'), has a quantity (integer), and its
        direction ('BUY' or 'SELL')

        Parameters:
        symbol - The instrument to trade
        order_type - 'MKT' or 'LMT'
        quantity - Non-negative integer for quantity
        direction - 'BUY' or 'SELL' for long or short
        """
        
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        """
        Outputs the values within the Order
        """
        print(
                "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
                (self.symbol, self.order_type, self.quantity,
                    self.direction)
            )

        






