
import numpy as np
import math
import datetime
import pystore
import sqlite3
from decimal import *

# Local Imports
from src.utility import *
from src.enums import *
from src.mathematics import *

from src.algorithms.__algorithm import *
from src.ml.recommendation import *
from src.tools.etfdb import *

conn = sqlite3.connect('quantico.sqlite')
cursor = conn.cursor()



etf = etfHoldings('EQLT')
holdings = etf.get_holdings()
total_holdings = etf.get_total_holdings()
analyst_report = etf.get_analyst_report()   

etf_fundamentals = self.query.get_fundamentals_by_symbols(holdings)
                    
for holding in holdings:
    for row in cursor.execute("SELECT id,candidate_id, symbol, parent_symbol, etfdb_weight FROM etf_holdings"):
        id,candidate_id,symbol,parent_symbol,etfdb_weight = row
        update = False
                        
        if holding[0] == symbol:
            etfdb_weight,update = (str(holding[1]),True)  if str(holding[1])  != etfdb_weight else (etfdb_weight,False)				
            if update == True:
                # Update stock in sqlite if any values don't match	
                cursor.execute("UPDATE etf_holdings SET etfdb_weight = ? WHERE symbol = ?", \
                    (holding[1],holding[0])) 
                        
                holding_id = id
                        
            # Delete stock from sqlite if it does not exist in new 
            if not any(holding[0] == symbol for holding in holdings):		
                cursor.execute("DELETE FROM etf_holdings WHERE symbol = ?", (holding[0]));
                    
    else:
        # Insert stock to sqlite 				
        cursor.execute("INSERT INTO etf_holdings (candidate_id,symbol,parent_symbol,etfdb_weight) \
            VALUES (?, ?, ?, ?)", (candidate_id,str(holding[0]),str(fund['symbol']),holding[1]))
            
        holding_id = cursor.lastrowid