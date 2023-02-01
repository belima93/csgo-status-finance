import pandas as pd
from bs4 import BeautifulSoup
import xlrd
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.common.action_chains import (
    ActionChains
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import (
    frame_to_be_available_and_switch_to_it,
    element_to_be_clickable
)
from selenium.webdriver.support.expected_conditions import (
    new_window_is_opened,
    number_of_windows_to_be
)
from selenium.common.exceptions import TimeoutException, NoSuchElementException

options = Options()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)
browser.get('https://csgostash.com/')
ac = ActionChains(browser)
wdw = WebDriverWait(browser, 30)
browser.implicitly_wait(30)
wdw.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/div/div/div/div[3]/div[1]/button[2]'))).click()
browser.execute_script("window.open('');")

now = datetime.now()
now = datetime.timestamp(now)
now = datetime.fromtimestamp(now)
quote_date = now.strftime('%Y-%m-%d')

base_agent = pd.read_excel('base_agent.xlsx')
base_agent = base_agent[['id', 'name','type','date_buy', 'price', 'overall']]

df_csgostash = pd.DataFrame([])
for x_url in range(len(base_agent)):
    id_item_csgo = base_agent.loc[x_url][0]
    type_item_csgo = str(base_agent.loc[x_url][2])
    url = 'https://csgostash.com/' + type_item_csgo + '/' + str(id_item_csgo) + '/'
    browser.switch_to.window(browser.window_handles[1]) 
    browser.get(url)
   
    page_content = browser.page_source
    site = BeautifulSoup(page_content, 'html.parser')
    
    name = site.find('h2').getText()    
    quality = site.find_all('p', attrs={'class': 'nomargin'})[0].getText()
    collection = site.find_all('p')[4].getText().strip('Collection: ')
    value_steam = site.find_all('span', attrs = {'class': 'pull-right'})[0].getText().strip('R$ ')
    value_bitskins = site.find_all('span', attrs = {'class': 'pull-right'})[1].getText().strip('R$ ')
    value_listing =  site.find_all('span', attrs = {'class': 'pull-right'})[2].getText().strip('\n')
    value_median = site.find_all('span', attrs = {'class': 'pull-right'})[3].getText().strip('\nR$')
    value_volume = site.find_all('span', attrs = {'class': 'pull-right'})[4].getText().strip('\n')
    added = pd.to_datetime(site.find_all('span', attrs = {'class': 'tooltip-text cursor-default'})[0].getText())
    added_in = added.strftime('%Y-%m-%d')
    time_market_days = (now - added).days
    
    info_csgostash = {'name':name, 'quality':quality, 'collection':collection,
                 'price_steam':value_steam, 'price_bitskins':value_bitskins, 'currently_for_ sale':value_listing,
                  'sales_amount_24':value_median,'current_market_value_24':value_volume,'added_in':added_in,
                  'time_market_days':time_market_days}
    df_csgostash = df_csgostash.append(pd.Series(info_csgostash),ignore_index=True)
df_csgostash = df_csgostash.replace({',': '.'}, regex=True)
df_csgostash['quote_date'] = quote_date

csgostash = pd.merge(base_agent, df_csgostash, how = 'outer', on = ['name'])

csgostash['date_buy'] = pd.to_datetime(csgostash['date_buy'])
csgostash['added_in'] = pd.to_datetime(csgostash['added_in'])
csgostash['quote_date'] = pd.to_datetime(csgostash['quote_date'])


csgostash.to_excel(quote_date+'.xlsx')


