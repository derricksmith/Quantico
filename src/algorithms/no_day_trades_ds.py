# Anthony Krivonos
# Oct 29, 2018
# src/algorithms/no_day_trades.py

# Global Imports
import numpy as np
import math
import datetime
import pystore
import sqlite3
from decimal import *

# Local Imports
from utility import *
from enums import *
from mathematics import *

from algorithms.__algorithm import *
from ml.recommendation import *
from tools.etfdb import *

# Abstract: Algorithm employing a no-day-trades tactic.
#           For more info on this algorithm, see:
#           https://www.quantopian.com/algorithms/5bf47d593f88ef0045e55e55

class NoDayTradesDSAlgorithm(Algorithm):

    # __init__:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    def __init__(self, query, portfolio, sec_interval = 60, age_file = None, test = False, cash = 0.00):

        # Initialize properties

        # Range of prices for stock purchasing
        self.buy_range = (1.00, 10.00)

        # Minimum PE Ratio for stock purchasing
        self.min_pe_ratio = (10)
		
        # All stocks available to buy/sell
        self.candidates = []

        # List of stocks to trade
        self.candidates_to_trade = []

        # Weight of stocks to trade
        self.candidates_to_trade_weight = 0.00

        # Total number of stocks to trade in this algorithm
        self.max_candidates = 100

        # Number of buy orders that can be placed concurrently
        self.max_simult_buy_orders = 30

        # Price of any stock that must immediately be sold
        self.immediate_sale_price = self.buy_range[0]
        
        # Number of sell orders that can be placed concurrently
        self.max_simult_sell_orders = 30
        
        # Number of days to hold a stock until it must be sold
        self.immediate_sale_age = 6
        
        # PCT Threshhold to sell
        self.pct_threshold_to_sell= 0.02

        # Over simplistic tracking of position age
        self.age = {}

        # File keeping track of ages
        self.age_file = age_file

        # List of categories for stocks to be traded
        self.categories = [ Tag.ETF ]
		
        # Is the Algorithm generating candidates_to_trade, DO NOT CHANGE
        self.generating_candidates = 0

        # Call super.__init__
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "No Day Trades DS", buy_range = self.buy_range, test = test, cash = cash)

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):
        Algorithm.initialize(self)
        self.update_from_age_file()
        pass

    #
    # Event Functions
    #
    
    # run once:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called once when algorithm is run.
    def run_once(self, cash = None, prices = None):
        Algorithm.run_once(self, cash, prices)
        self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight = self.generate_candidates()
        pass

    # on_market_will_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self, cash = None, prices = None):
        Algorithm.on_market_will_open(self, cash, prices)
       
        # Generate Candidates
        # self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight = self.generate_candidates()

        #lowest_price = self.buy_range[0]
        #for quote in self.portfolio.get_quotes():
        #    current_price = self.price(quote.symbol)
        #    if current_price < lowest_price:
        #        lowest_price = current_price
        #    if quote.symbol in self.age:
        #        self.age[quote.symbol] += 1
        #    else:
        #        self.age[quote.symbol] = 1
        #for symbol in self.age:
        #    if not self.portfolio.is_symbol_in_portfolio(symbol):
        #        self.age[quote.symbol] = 0
        #    Algorithm.log(self, "stock.symbol: " + symbol + " : age: " + str(self.age[symbol]))

        #self.overwrite_age_file()

        pass

    # on_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market opens.
    def on_market_open(self, cash = None, prices = None):
        Algorithm.on_market_open(self, cash, prices)
        
        # Generate Candidates
        #self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight = self.generate_candidates()
        
        #self.perform_buy_sell()
        pass

    # while_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called on an interval while market is open.
    def while_market_open(self, cash = None, prices = None):
        Algorithm.while_market_open(self, cash, prices)
        
        #self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight = self.generate_candidates()
           
        #self.perform_buy_sell()
        pass

    # on_market_close:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market closes.
    def on_market_close(self, cash = None, prices = None):
        Algorithm.on_market_close(self, cash, prices)
        
        # Generate Candidates
        #self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight = self.generate_candidates()
           
        #self.perform_buy_sell()
        pass
		
    # while_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called on an interval while market is open.
    def while_market_closed(self, cash = None, prices = None):
        Algorithm.while_market_closed(self, cash, prices)
		
        # Generate Candidates        
       #self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight = self.generate_candidates()
   
        #self.perform_buy_sell()
        pass

    #
    # Algorithm
    #

    def generate_candidates(self):
        if len(self.candidates) == 0:
            if self.generating_candidates == 1:
                # Generating candidates takes time and may surpass the set interval.  Let the previous thread complete.			
                return(self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight)
            
            self.generating_candidates = 1
            # Setup DB Connection
            conn = sqlite3.connect('quantico.sqlite')
            cursor = conn.cursor()
		
            Algorithm.log(self, "Generating candidates for categories: " + str([ c.value for c in self.categories ]))
		
            # Get all fundamentals within the buy range
            unsorted_fundamentals = self.query.get_fundamentals_by_criteria(self.buy_range, self.categories)
        
            # Sort the unsorted fundamentals by low price (close would be preferred, but is unavailable)
            candidate_fundamentals = sorted(unsorted_fundamentals, key=lambda fund: fund['low'])

            # Store the symbols of each candidate fundamental into a separate array
            all_candidate_symbols = [ fund['symbol'] for fund in candidate_fundamentals ]

            # Instantiate list of long and short fundamentals, as well as the average of their low prices
            short_candidate_fundamentals = []
            short_candidate_low_avg = 0.00
            long_candidate_fundamentals = []
            long_candidate_low_avg = 0.00

            # Update long and short data
            for fund in candidate_fundamentals:
                if self.portfolio.is_symbol_in_portfolio(fund['symbol']):
                    # Stock is long
                    long_candidate_fundamentals.append(fund)
                    long_candidate_low_avg += float(fund['low'])
                else:
                    # Stock is short
                    short_candidate_fundamentals.append(fund)
                    short_candidate_low_avg += float(fund['low'])
			
                # Get stock instrument info
                fund_instrument = self.query.get_instrument(fund['symbol'])
          
                for row in cursor.execute("SELECT id,symbol,description,instrument,sector,industry,ceo,headquarters_city,headquarters_state,market_cap,pb_ratio,pe_ratio,shares_outstanding FROM candidates"):
                    id,symbol,description,instrument,sector,industry,ceo,headquarters_city,headquarters_state,market_cap,pb_ratio,pe_ratio,shares_outstanding = row
                    update = False
                    if fund['symbol'] == symbol:
                        description,update = (str(fund['description']),True) if str(fund['description']) != description else (description,False)				
                        instrument,update = (str(fund_instrument['type']),True) if str(fund_instrument['type']) != instrument else (instrument,False)				
                        sector,update = (str(fund['sector']),True) if str(fund['sector']) != sector else (sector,False)				
                        industry,update = (str(fund['industry']),True) if str(fund['industry']) != industry else (industry,False)				
                        ceo,update = (str(fund['ceo']),True) if str(fund['ceo']) != ceo else (ceo,False)				
                        headquarters_city,update = (str(fund['headquarters_city']),True) if str(fund['headquarters_city']) != headquarters_city else (headquarters_city,False)				
                        headquarters_state,update = (str(fund['headquarters_state']),True) if str(fund['headquarters_state']) != headquarters_state else (headquarters_state,False)	
                        market_cap,update = (str(self.to_decimal(fund['market_cap'])),True) if str(self.to_decimal(fund['market_cap'])) != market_cap else (market_cap,False)				
                        pb_ratio,update = (str(self.to_decimal(fund['pb_ratio'])),True) if str(self.to_decimal(fund['pb_ratio'])) != pb_ratio else (pb_ratio,False)				
                        pe_ratio,update = (str(self.to_decimal(fund['pe_ratio'])),True) if str(self.to_decimal(fund['pe_ratio'])) != pe_ratio else (pe_ratio,False)	
                        shares_outstanding,update = (str(self.to_decimal(fund['shares_outstanding'])),True)  if str(self.to_decimal(fund['shares_outstanding']))  != shares_outstanding else (shares_outstanding,False)				
                        
                        if update == True:
                            # Update stock in sqlite if any values don't match	
                            cursor.execute("UPDATE candidates SET description = ?, instrument = ?, sector = ?, industry = ?, ceo = ?, headquarters_city = ?, headquarters_state = ?, market_cap = ?, pb_ratio = ?, pe_ratio = ?, shares_outstanding = ? WHERE symbol = ?", \
                                (description,instrument,sector,industry,ceo,headquarters_city,headquarters_state,market_cap,pb_ratio,pe_ratio,shares_outstanding,fund['symbol'])) 
                        
                        candidate_id = id
                        
                    # Delete stock from sqlite if it does not exist in new 
                    if not any(f['symbol'] == symbol for f in candidate_fundamentals):		
                        cursor.execute("DELETE FROM candidates WHERE symbol = ?", (symbol,))
                        cursor.execute("DELETE FROM etf_holdings WHERE parent_symbol = ?", (symbol,))
                    
                    #break
                else:
                    # Insert stock to sqlite 				
                    cursor.execute("INSERT INTO candidates (symbol,allow_trading,description,instrument,sector,industry,ceo,headquarters_city,headquarters_state,market_cap,pb_ratio,pe_ratio,shares_outstanding,etfdb_analyst_report) \
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (str(fund['symbol']),0, str(fund['description']),str(fund_instrument['type']),str(fund['sector']),str(fund['industry']),str(fund['ceo']),str(fund['headquarters_city']),str(fund['headquarters_state']),str(self.to_decimal(fund['market_cap'])),str(self.to_decimal(fund['pb_ratio'])),str(self.to_decimal(fund['pe_ratio'])),str(self.to_decimal(fund['shares_outstanding'])),""))
            
                    candidate_id = cursor.lastrowid		
					
            long_candidate_low_avg /= max(len(long_candidate_fundamentals), 1)
            short_candidate_low_avg /= max(len(short_candidate_fundamentals), 1)

            # Create a new list of candidates to trade
            candidates_to_trade_length = min(self.max_candidates + 1, len(candidate_fundamentals) + 1)
            candidates_to_trade_symbols = [ fund['symbol'] for fund in candidate_fundamentals[0:candidates_to_trade_length] ]

            
            
            
            for fund in candidates_to_trade_symbols:
                cursor.execute("UPDATE candidates SET allow_trading = 1 WHERE symbol = ?",(fund,))	
                
            # Set a weight for trades
            to_trade_weight = 1.00 / len(candidates_to_trade_symbols)
            
            all_candidate_symbols_str = ",".join([ str(c) for c in all_candidate_symbols ])
            Algorithm.log(self, "Candidates: " + all_candidate_symbols_str)
            candidates_to_trade_symbols_str = ",".join([ str(c) for c in candidates_to_trade_symbols ])
            Algorithm.log(self, "Candidates to Trade: " + candidates_to_trade_symbols_str )
            Algorithm.log(self, "Trade Weight: " + str(to_trade_weight))
            
            # Close DB Connection
            conn.commit()
            conn.close()
            self.generating_candidates = 0
            return(all_candidate_symbols,candidates_to_trade_symbols,to_trade_weight)
        
        return(self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight)
        
    # perform_buy_sell:Void
    def perform_buy_sell(self):

        Algorithm.log(self, "Executing perform_buy_sell:")

        # Percentage of the current price to submit buy orders at
        BUY_FACTOR = 0.99

        # Percentage of the current price to submit sell orders at
        SELL_FACTOR = 1.01

        # Factor at which the stock may be higher than its average price over the past day and can still be bought
        GAIN_FACTOR = 1.15
        
        # Factor at which the stock may be lower than its average price over the past day and can still be sold
        LOSS_FACTOR = 0.85

        # Get the user's buying power, or cash
        cash = self.cash

        # Cancel all of the user's open orders
        Algorithm.cancel_open_orders(self)

        # Track the user's open orders
        open_orders = self.query.user_open_orders()
        open_order_symbols = {}
        open_buy_order_count = 0
        open_sell_order_count = 0
        for order in open_orders:

            stock = self.query.stock_from_instrument_url(order['instrument'])
            open_order_symbols[stock['symbol']] = True

            # Increment number of current buy orders
            if 'side' in order and order['side'] == 'buy':
                open_buy_order_count += 1
                
            # Increment number of current sell orders
            if 'side' in order and order['side'] == 'sell':
                open_sell_order_count += 1
        
        # Sell
        
        # Sell stocks at profit target in hope that somebody actually buys it
        for quote in self.portfolio.get_quotes():
           
           # Finish selling stocks once the limit has been reached
            if open_sell_order_count > self.max_simult_sell_orders:
                break

            # Assure the given quote is not part of any open orders
            if quote.symbol not in open_order_symbols and quote.count > 0:

                # Get the number of shares of the stock in the given portfolio
                stock_shares = quote.count

                # Current price of the given stock
                current_price = self.price(quote.symbol)

                # Get the history of the stock
                history = self.portfolio.get_symbol_history(symbol, Span.TEN_MINUTE, Span.DAY)
                
                if current_price != 0.0:
                
                    # Calculate stock close price mean over the past day
                    mean = 0.00
                    for price in history:
                        mean += price.close
                    mean /= max(len(history), 1)
                    mean = round(mean, 2)

                    if mean != 0.0:
                    
                        # Calculate buy price
                        if current_price < float(LOSS_FACTOR * mean):
                            # Set the sell_price to the current price if the stock is at a low compared to the average
                            sell_price = current_price
                        else:
                            # Otherwise, set the buy price equal to the current price
                            sell_price = current_price * SELL_FACTOR
                        sell_price = round(sell_price, 2)

                        #1 Sell if the age has exceeded the immediate sale age
                        #2 Sell if the immediate sale price is greater than the current price
                        #3 Sell if the current price is greater than the pct threshold to sell
                        if quote.symbol in self.age:
                            did_sell = False
                            if self.age[quote.symbol] < 2:
                                pass
                            if (datetime.datetime.today() - self.age[quote.symbol]['last_buy_sell']).days <= 3:
                                Algorithm.log(self, "Symbol has not been held for more than 3 days.  Cannot day-trade")
                                pass
                            elif self.immediate_sale_age <= self.age[quote.symbol]['count']:
                                Algorithm.log(self, "Symbol has exceeded the immediate sale age. Selling " + str(stock_shares) + " shares of " + str(quote.symbol) + " at " + str(sell_price) + ".")
                                #did_sell = Algorithm.sell(self, quote.symbol, stock_shares, None, current_price)
                                pass
                            elif self.immediate_sale_price >= current_price:
                                Algorithm.log(self, "Symbol has exceeded the immediate sale price. Selling " + str(stock_shares) + " shares of " + str(quote.symbol) + " at " + str(sell_price) + ".")
                                #did_sell = Algorithm.sell(self, quote.symbol, stock_shares, None, current_price)
                                pass
                            elif current_price / quote.average_buy_price - 1 > self.pct_threshold_to_sell:
                                Algorithm.log(self, "Symbol has exceeded the PCT Threshold. Selling " + str(stock_shares) + " shares of " + str(quote.symbol) + " at " + str(sell_price) + ".")
                                #did_sell = Algorithm.sell(self, quote.symbol, stock_shares, None, current_price)
                                
                            if did_sell:
                                # Increment available cash and decrement the number of sell orders
                                cash += stock_shares * sell_price
                                open_sell_order_count += 1
                                self.age[quote.symbol][last_buy_sell] = datetime.date.today()
                                self.age[quote.symbol][count] += 1
               

        # Overwrite the age file
        self.overwrite_age_file()

        # Instantiate the weight for the number of simultaneous buy orders to be made
        weight_for_buy_order = float(1.00 / self.max_simult_buy_orders)

        # Iterate over each candidate to buy
        open_buy_order_count
        for symbol in self.candidates:
            Algorithm.log(self, "Analyze candidate " + str(symbol))
            # Finish buying stocks once the limit has been reached
            if open_buy_order_count > self.max_simult_buy_orders:
                break

            # Store the current price of the candidate stock
            current_price = self.price(symbol)
            Algorithm.log(self, "Current Price " + str(current_price))

            # Get the history of the stock
            history = self.portfolio.get_symbol_history(symbol, Span.TEN_MINUTE, Span.DAY)

            if current_price != 0.0:

                # Calculate stock close price mean over the past day
                mean = 0.00
                for price in history:
                    mean += price.close
                mean /= max(len(history), 1)
                mean = round(mean, 2)
				
                Algorithm.log(self, "Mean Price " + str(mean))

                if mean != 0.0:

                    # Calculate buy price
                    if current_price > float(GAIN_FACTOR * mean):
                        # Set the buy_price to the current price if the stock is at a high compared to the average
                        buy_price = current_price
                    else:
                        # Otherwise, set the buy price equal to the current price
                        buy_price = current_price * BUY_FACTOR
                    buy_price = round(buy_price, 2)

                    Algorithm.log(self, "Buy Price " + str(buy_price))              
                    Algorithm.log(self, "Cash " + str(cash)) 
                    Algorithm.log(self, "Weight For Buy Order " + str(weight_for_buy_order))   

				    # Number of shares to buy is the weight of the buy order divided by the buy price times the number of available cash
                    stock_shares = int(weight_for_buy_order * cash / buy_price)
                    
                    Algorithm.log(self, "Stock Shares " + str(stock_shares))
                    
                    if stock_shares > 0:
                        did_buy = False					
                        if 1==1:
                            Algorithm.log(self, "A condition(1=1) was met. Buying " + str(stock_shares) + " shares of " + str(symbol) + " at " + str(buy_price) + ".")
                            #did_buy = Algorithm.buy(self, symbol, stock_shares, None, current_price)
                                
                        if did_buy:
                            # Increment available cash and decrement the number of sell orders
                            cash -= stock_shares * buy_price
                            open_buy_order_count += 1
                            self.age[symbol][last_buy_sell] = datetime.date.today()
                            self.age[symbol][count] += 1

        Algorithm.log(self, "Finished run of perform_buy_sell")		

    def recommendation(self, type, symbol):
        print("recommend")



    #
    # Event Functions
    #
	
    # Convert to Decimal
    def to_decimal(self, input):
        if input is None:
            return "0.00"
        else:
            return Decimal(input)		

    # overwrite_age_file:Void
    def overwrite_age_file(self):
        try:
            if self.age_file is not None:
                age_str = {}
                for key, value in self.age.items():
                    age_str[key] = str(value)
                Utility.set_file_from_dict(self.age_file, age_str)
            pass
        except:
            Utility.error("Could not overwrite " + self.age_file + " using the age dict.")
            pass

    # update_from_age_file:Void
    def update_from_age_file(self):
        try:
            if self.age_file is not None:
                self.age = Utility.get_file_as_dict(self.age_file)
                for key, value in self.age.items():
                    self.age[key] = int(value)
            pass
        except:
            Utility.error("Could not update the age dict from " + self.age_file + ".")
            pass
