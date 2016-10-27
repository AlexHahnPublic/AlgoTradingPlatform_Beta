#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#======================= event.py =========================
#==========================================================

# Purpose
#----------------------------------------------------------
# Define the event objects/classes. Implenent the functions to initialize the
# objects with the desired attributes. Implement the few required methods
# (commission calculation, printing/ reporting, etc)

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
# When an ExecutionHandler receives an OrderEvent it must transact the
# order. Once an order has been transacted it generates a FillEvent which
# describes the cost of purchase or sale as well as the transaction costs,
# such as fees or slippage.
# 
# The FillEvent is the Event with the greatest complexity. It contains a
# timestamp for when an order was filled, the symbol of the order, and the
# exchange it was executed on, the quantity of shares transacted, the
# actual price of the purchase, and the commission incurred.
# 
# The commission is calculated using the Interactive Brokers commissions. For
# US API orders the commission is 1.30 USD minimum per order, with a flat rate
# of either 0.013 USD or 0.08 USD per share depending upon upon whether the
# trade size is below or above 500 units of stock
class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned from a
    brokerage. Stores the quantity of an instrument actually filled and at what
    price. In addition, store the commission of the trade from the brokerage
    """

    def __init__(self, timeindex, symbol, exchange, quantity, direction,
            fill_cost, commission=None):
        """
        Initialize the FillEvent object. Set the symbol, exchange, quantity,
        direction, cost of fill and optional commission.

        If the commission is not provided, the FillEvent object will
        calculate it based on the trade size and Interactive Brokers fee
        structure.

        Parameters:
        timeindex - The bar-resolution when the order was filled
        symbol - The instrument which was filled
        exchange - The exchange where the order was  filled
        quantity - The filled quantity
        direction - The direction of fill ('BUT' or 'SELL')
        fill_cost - The holding value in dollars.
        commission - An optional commission sent from IB
        """

        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

    # Calculate commission
    if commission is None:
        self.commission = self.calculate_ib_commission()
    else:
        self.commission = commission

    def calculate_ib_commission(self):
        """
        Calculates the fees of trading based on an Interactive Brokers fee
        structure for API, in USD.

        This does not include exchange or ECN fees.
        """

        full_cost = 1.3 
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013*self.quantity)
        else: # Greater than 500
            full_cost = max(1.3, 0.008*self.quantity)
        return full_cost


