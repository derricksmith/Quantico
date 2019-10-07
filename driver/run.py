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
    id                    INTEGER      PRIMARY KEY    AUTOINCREMENT,
    symbol                TEXT         NOT NULL,
    allow_trading         INT          NOT NULL,
    description           TEXT         NOT NULL,	
    instrument            TEXT         NOT NULL,
    sector                TEXT         NOT NULL,
    industry              TEXT         NOT NULL,	
    ceo                   TEXT         NOT NULL,
    headquarters_city     TEXT         NOT NULL,
    headquarters_state    TEXT         NOT NULL,
    market_cap            REAL         NOT NULL,
    pb_ratio              REAL         NOT NULL,
    pe_ratio              REAL         NOT NULL,
    shares_outstanding    REAL         NOT NULL,
	etfdb_analyst_report  REAL         NOT NULL);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS etf_holdings (
    id                    INTEGER      PRIMARY KEY    AUTOINCREMENT,
    candidate_id          INT          NOT NULL,
	symbol                TEXT         NOT NULL,
    parent_symbol         TEXT         NOT NULL,
    etfdb_weight          REAL         NOT NULL);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS trades (
    id                    INTEGER      PRIMARY KEY    AUTOINCREMENT,
	date                  REAL         NOT NULL,
	symbol                TEXT         NOT NULL,
	price                 REAL         NOT NULL,
	action                TEXT         NOT NULL);''')
conn.commit()
cursor.close()

#
#   Portfolio
#

my_port = query.user_portfolio()

#
#   Driver (Your Algorithms Here)
#

#NoDayTradesAlgorithm(query,for row in cursor.execute("SELECT id,symbol,description,instrument,sector,industry,ceo,headquarters_city,headquarters_state,market_cap,pb_ratio,pe_ratio,shares_outstanding FROM candidates"):

NoDayTradesDSAlgorithm(query, my_port)
