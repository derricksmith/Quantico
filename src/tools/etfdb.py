import sys, getopt, time, re
from importlib import reload
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class etfHoldings():
    etf = ""
    holdings = []
    total_holdings = ""
    liquidity_rating = ""
    expenses_rating = ""
    performance_rating = ""
    volatility_rating = ""
    dividend_rating = ""
    concentration_rating = ""
    analyst_report = ""

    def __init__(self, etf):
        self.etf = etf
        self.scrape(etf)
        self.total_holdings = len(self.holdings)
        
    def scrape(self, etf):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('log-level=3')
        browser = webdriver.Chrome(options=options)
        
        browser.get('http://etfdb.com/etf/{}'.format(etf))
        
        self.parse_holdings(browser)
        self.parse_analyst_report(browser)
        
    def parse_holdings(self, browser):
        soup = BeautifulSoup(browser.page_source, "html.parser")
        
        for row in soup.find(id='etf-holdings').tbody.find_all('tr'):      
            print(row)
            cells = row.find_all('td')
            try:
                ticker = re.search('\(([^)]+)', cells[0].text.strip().replace(',', '')).group(1)
            except:
                text = cells[0].text.strip().replace(',', '').encode('UTF-8')
                if(b'\xc2\xa9' in text):
                    ticker = "c"
                else:
                    pass
            weight = cells[1].text.strip().replace(',', '').replace('%', '')
  
            row = [ticker, weight]
            self.holdings.append(row)
               
        
        # Check for a link to the next results
        try:
            next_link = browser.find_element_by_css_selector('li.page-next:not(.disabled) a')
            if next_link:
                modal_dialog = browser.find_element_by_css_selector('li.page-next:not(.disabled) a')
                try:
                    next_link.click() 
                    time.sleep(1.5)
                    self.parse_holdings(browser)
                except:
                    
        except NoSuchElementException:
            pass
        
    def parse_analyst_report(self, browser):
        try:
            soup = BeautifulSoup(browser.page_source, "html.parser")
            analyst_html = soup.find(id='analyst-collapse').find('div').find('p')
            if analyst_html.text == "The Analyst Take for {} is not available".format(self.etf):
                self.analyst_report = ""
            else:
                self.analyst_report = analyst_html.text
        except NoSuchElementException:
            pass
            
    def get_holdings(self):
        return self.holdings
        
    def get_analyst_report(self):
        return self.analyst_report 
    
if __name__ == "__main__":
    etf = input("Enter a ETF: ") 
    etf = etfHoldings(etf)
    print(etf.holdings)
    print(etf.analyst_report)