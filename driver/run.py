# Anthony Krivonos
# Oct 29, 2018
# driver/driver.py

# Global Imports
import sys
import os
import numpy as np
from os.path import join, dirname
from dotenv import load_dotenv
sys.path.append('src')

# Local Imports
from query import *
from utility import *
from enums import *
from algorithms import *
from models import *
from ml import *

# Plotting
import numpy as np

# Abstract: Main script to run algorithms from.

#
#   Setup
#

# Load EMAIL and PASSWORD constants from .env
dotenv = load_dotenv(join(dirname(__file__)+"/../", '.env'))
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
QR = "ZDQLU36B7G636XM3"


# Login and intialize query object with credentials from .env
query = None
try:
    query = Query(EMAIL, PASSWORD, QR)
except Exception as e:
    Utility.error("Could not log in: " + str(e))
    sys.exit()

#
#  Build DB
#
conn = sqlite3.connect('quantico.sqlite')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS candidates (
    id                    INT      PRIMARY KEY     NOT NULL,
    symbol                TEXT     NOT NULL,
    allow_trading         INT      NOT NULL,
    description           TEXT     NOT NULL,	
    instrument            TEXT     NOT NULL,
    sector                TEXT     NOT NULL,
    industry              TEXT     NOT NULL,	
    ceo                   TEXT     NOT NULL,
    headquarters_city     TEXT     NOT NULL,
    headquarters_state    TEXT     NOT NULL,
    year_founded          TEXT     NOT NULL,
    num_employees         TEXT     NOT NULL,
    market_cap            REAL     NOT NULL,
    pb_ratio              REAL     NOT NULL,
    pe_ratio              REAL     NOT NULL,
    shares_outstanding    REAL     NOT NULL);''')
	
cursor.execute('''CREATE TABLE IF NOT EXISTS eft_holdings (
    id                    INT      PRIMARY KEY     NOT NULL,
    candidate_id          INT      NOT NULL,
    symbol                TEXT     NOT NULL,
    description           TEXT     NOT NULL,	
    instrument            TEXT     NOT NULL,
    sector                TEXT     NOT NULL,
    industry              TEXT     NOT NULL,	
    ceo                   TEXT     NOT NULL,
    headquarters_city     TEXT     NOT NULL,
    headquarters_state    TEXT     NOT NULL,
    year_founded          TEXT     NOT NULL,
    num_employees         TEXT     NOT NULL,
    market_cap            REAL     NOT NULL,
    pb_ratio              REAL     NOT NULL,
    pe_ratio              REAL     NOT NULL,
    shares_outstanding    REAL     NOT NULL,
    weight                REAL     NOT NULL,
    FOREIGN KEY (candidate_id)
        REFERENCES candidates (id));''')
conn.commit()
cursor.close()

#
#   Portfolio
#

my_port = query.user_portfolio()

#
#   Driver (Your Algorithms Here)
#

#NoDayTradesAlgorithm(query, my_port, test=True, cash=1000)

NoDayTradesDSAlgorithm(query, my_port)
