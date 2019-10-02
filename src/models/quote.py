# Anthony Krivonos
# Nov 9th, 2018
# src/models/quote.py

# Imports
import sys

# Abstract: Simple model that maps symbols to quantities.

class Quote:

    def __init__(self, symbol, count = 0, weight = 0.0, average_buy_price = 0, equity = 0, percent_change = 0, equity_change = 0, type = '', name = '', id = '', pe_ratio = 0):

        # Set properties
        self.symbol = symbol
        self.count = count
        self.weight = weight
        self.average_buy_price = average_buy_price
        self.equity = equity
        self.percent_change = percent_change
        self.equity_change = equity_change
        self.type = type
        self.name = name
        self.id = id
        self.pe_ratio = pe_ratio