import requests
import time
import datetime
import ast
import pandas as pd 
import logging
import csv
import yaml
import math
from decimal import *
from urllib.parse import urlparse
from splinter import Browser
from selenium import webdriver
from twilio.rest import Client
import scipy.signal as sg
from scipy.signal import find_peaks
import numpy as np
from operator import itemgetter
import my_sms_quickstart_folder.run as twil
from get_all_tickers import get_tickers as gt


##varaibles ## ## ##

## var end

def time_now():
    ##time in ms and in epoch
    ts = datetime.datetime.now().timestamp()
    ts = int(ts)*1000
    return ts

def time_diff_day(time1, Xfactor=1):
    ##calculate one week time difference
    one_day_diff = 90000 *1000 *Xfactor
    time2 = time1 - one_day_diff
    return time2

def time_diff_week(time1):
    ##calculate one week 8d time difference
    ### one_month_diff = 2592000 *1000
    ### one_day_diff = 90000 *1000
    
    days_8_diff = 691200 *1000 ##ms
    time2 = time1 - days_8_diff
    return time2

def time_diff_month(time1, Xfactor=1):
    ##calculate one mon time difference x-times
    one_month_diff = 2592000 *1000 *Xfactor
    time2 = time1 - one_month_diff
    return time2

def currentDiffInTimeCheck(timeGiven, threshold=80000):
    ##calc difference in time epoch. 80000=22hours. time in miliSec
    tNow = int(time.time())
    #print(T,time,type(time),type(T), int(time))
    diff = tNow-timeGiven/1000
    if diff > threshold:
        return True
    else:
        return False
    
    
def get_filtered_tickers_mktcap(mc_min=500, mc_max=2000):
    ##get tickers filtered by market cap (in millions). Mid-cap=.5-2billion
    try:
        ft = gt.get_tickers_filtered(mktcap_min=mc_min, mktcap_max=mc_max)
        return ft
    except:
        ##library failed - due to anti-scraping stock-exchange
        return None

def get_filtered_tickers_industry(sect='Technology' ,mc_min=400):
    ##get tickers filtered by sector: Technology Finance ,Miscellaneous, consumer goods, Utilities Telecommunications..
    try:
        ft = gt.get_tickers_filtered(mktcap_min=400, sectors=sect)
        return ft
    except:
        ##library failed - due to anti-scraping stock-exchange
        return None
    


def pct_change_day_stock(ticker = '$DJI', NofDays=1):
    # by default search dow jones change. default to one day pct

    t_current = time_now()
    t_d = time_diff_day(t_current, NofDays) 

    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker)
    # define the payload
    payload = {'apikey':key_app,
               'periodType':'day',
               'frequencyType':'minute',
               'frequency':'5',
               'period':'10',
               'endDate':  t_current,
               'startDate':t_d,
               'needExtendedHoursData':'true'}

    # make a request
    content = requests.get(url = endpoint, params = payload)
    # convert it dictionary object
    data = content.json()

    df=pd.DataFrame.from_dict(data['candles'])
    df['dateStr'] = None
    for i in range(len(df['datetime'])):
        df['dateStr'][i] = datetime.datetime.fromtimestamp(df['datetime'][i]/1000).strftime('%Y-%m-%d %H:%M:%S') 
    # df.plot(kind='line',x='datetime',y='close',ax=ax)
    df['pctClose'] = df['close'].pct_change()
    sum_change = sum(df['pctClose'].fillna(0))
    sum_change = round(sum_change,3)
    return sum_change

def pct_change_week_stock(ticker = '$DJI'):
    # by default search dow jones change

    t_current = time_now()
    t_week = time_diff_week(t_current)

    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker)
    # define the payload
    payload = {'apikey':key_app,
               'periodType':'day',
               'frequencyType':'minute',
               'frequency':'5',
               'period':'10',
               'endDate':  t_current,
               'startDate':t_week,
               'needExtendedHoursData':'true'}

    # make a request
    content = requests.get(url = endpoint, params = payload)
    # convert it dictionary object
    data = content.json()

    df=pd.DataFrame.from_dict(data['candles'])
    df['dateStr'] = None
    for i in range(len(df['datetime'])):
        df['dateStr'][i] = datetime.datetime.fromtimestamp(df['datetime'][i]/1000).strftime('%Y-%m-%d %H:%M:%S') 
    # df.plot(kind='line',x='datetime',y='close',ax=ax)
    df['pctClose'] = df['close'].pct_change()
    sum_change = sum(df['pctClose'].fillna(0))
    return sum_change


def pct_change_month_stock(ticker = '$DJI'):
    # by default search dow jones change

    t_current = time_now()
    t_week = time_diff_month(t_current)

    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker)
    # define the payload
    payload = {'apikey':key_app,
               'periodType':'day',
               'frequencyType':'minute',
               'frequency':'5',
               'period':'10',
               'endDate':  t_current,
               'startDate':t_week,
               'needExtendedHoursData':'true'}

    # make a request
    content = requests.get(url = endpoint, params = payload)
    # convert it dictionary object
    data = content.json()

    df=pd.DataFrame.from_dict(data['candles'])
    df['dateStr'] = None
    for i in range(len(df['datetime'])):
        df['dateStr'][i] = datetime.datetime.fromtimestamp(df['datetime'][i]/1000).strftime('%Y-%m-%d %H:%M:%S') 
    # df.plot(kind='line',x='datetime',y='close',ax=ax)
    df['pctClose'] = df['close'].pct_change()
    sum_change = sum(df['pctClose'].fillna(0))
    return sum_change

def hist_prices(ticker = '$DJI', select=2, time=0):
    # by default search dow jones change per day. time in days

    t_current = time_now()
    if time == 0:
        if select ==1:
            t_end = time_diff_day(t_current)
        if select ==2:
            t_end = time_diff_month(t_current,4)
    else:
        t_end = time_diff_day(t_current,time)
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker)
    # define the payload
    payload = {'apikey':key_app,
               'periodType':'day',
               'frequencyType':'minute',
               'frequency':'5',
               'period':'10',
               'endDate':  t_current,
               'startDate':t_end,
               'needExtendedHoursData':'true'}

    # make a request
    content = requests.get(url = endpoint, params = payload)
    # convert it dictionary object
    data = content.json()
    return data


def loadVariablesYaml(nameFile):

    with open(nameFile, 'r') as stream:
        try:
            # print(yaml.safe_load(stream))
            documents = yaml.full_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        
    return documents


def get_pct_change_tickers(file='tickers_list_folder/ticker_misch_450mrktcap_up.yaml',Ndays=3,NdaysVariance=20,Width=5,Prom=1):
    #get sorted percent change and cycle-variance from predefined ticker list. returns [[],[]...]
    var_yaml = loadVariablesYaml(file)
    list_final = []
    for t in var_yaml:
        pC = pct_change_day_stock(t,Ndays)
        time.sleep(.45) ##prevent timeout on ameritrade hist
        avrg_pv = avrg_peak_valley_detect_scipy(t,NdaysVariance,Width,Prom)
        list_final.append([pC,t,avrg_pv])
    list_final = sorted(list_final, key=lambda x: x[0], reverse=True)
    return list_final


def start_auth():
    endpoint = 'https://api.tdameritrade.com/v1/marketdata/{}/quotes'.format('NVDA')

    payload= {

        'apikey':key_app,
        'periodType':'day',
        'frequencyType':'minute',
        'frequency':'1',
        'period':'2',
        'endDate':"1580712943000",
        'startDate':"1580756143000",
        'needExtendedHoursData':'true',
    }
    content = requests.get(url=endpoint,params=payload)
    data=content.json()
    ##
    exe_path = {'executable_path':"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"}
    # try:
    #     browser = Browser('chrome',**exe_path, headless=False)
    # except Exception as e:
    #     print(e)

    #url build
    method = 'GET'
    url = 'https://auth.tdameritrade.com/auth?'
    client_code = key_app + '@---.OAUTHAP'
    payload ={'response_type':'code','redirect_uri':'https://---/hooks/catch/---/', 'client_id':client_code}

    built_url = requests.Request(method,url,params=payload).prepare()
    built_url = built_url.url
    print(built_url)
    ##

    chromedr= r"\Users\Andrew Kubal\Downloads\chrome_driver_80v" 
    driver = webdriver.Chrome(executable_path=r'C:\Users\---\Downloads\chromeDriverWin_85\chromedriver.exe')

    driver.get(built_url)
    time.sleep(0.5)
    ##
    up = {
        'username':usrnm, 'password':pswd
    }
    # browser.find_by_id('username').first.fill(payload2['username'])
    # browser.find_by_id('password').first.fill(payload2['password'])
    # browser.find_by_id('accept').first.click
    #     username = driver.find_element_by_id("username")
    username = driver.find_element_by_id("username0")  # new since nov 2020, try username0
    password = driver.find_element_by_id("password")

    username.send_keys(up['username'])
    password.send_keys(up['password'])

    driver.find_element_by_id("accept").click()
    time.sleep(0.5)
    ##
    driver.find_element_by_css_selector('summary.row').click()
    driver.find_element_by_name('init_secretquestion').click()
    # ##secret question answer
    time.sleep(0.5)
    x_path =  driver.find_element_by_xpath( "/html/body/form/main/div[2]/p[2]" )
    t = x_path.text
    lt = t.split()
    if 'school'in lt and 'sixth' in lt:  # " Q---? ":
        print('true')

        text_elem = driver.find_element_by_id('secretquestion0')
        text_elem.click()
        text_elem.send_keys('---')
        driver.find_element_by_id("accept").click()

    elif 'favorite' in lt and 'TV' in lt:      #' Q---? ':
        print('true')

        text_elem = driver.find_element_by_id('secretquestion0')
        text_elem.click()
        text_elem.send_keys('---')
        driver.find_element_by_id("accept").click()

    elif 'graduate' in lt and 'high' in lt:    #' Q---? ':
        print('true')

        text_elem = driver.find_element_by_id('secretquestion0')
        text_elem.click()
        text_elem.send_keys('---')
        driver.find_element_by_id("accept").click()

    elif 'attend' in lt and 'city' in lt:    # " Q---? ":
        print('true')

        text_elem = driver.find_element_by_id('secretquestion0')
        text_elem.click()
        text_elem.send_keys('---')
        driver.find_element_by_id("accept").click()
    else:
        print('Not found Question')

    time.sleep(1)
    driver.find_element_by_class_name("radio").click()
    time.sleep(0.7)
    driver.find_element_by_id("accept").click()
    time.sleep(0.5)
    driver.find_element_by_id("accept").click()
#     time.sleep(0.5)
#     driver.find_element_by_class_name("accept button").click()
    ##
    time.sleep(1) ##wait to get url code
    new_url = driver.current_url

    parse_url = urlparse(new_url.split('code=')[1])
    parsed_url=parse_url.path
    parsed_url
    from urllib.parse import unquote
    url_code = unquote(parsed_url)
    url_code
    ##
    driver.quit()
    ##
    url_token = r'https://api.tdameritrade.com/v1/oauth2/token'
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    payloadN = {
        'grant_type':"authorization_code",
        'access_type':"offline",
        'code':url_code,
        'client_id':key_app,
        'redirect_uri':'https://-----/'
    }
    authreply = requests.post(url_token,headers=headers,data=payloadN)
    decode_content = authreply.json()
    return decode_content
##end


def refresh_token(key_app , auth):
    refreshT = auth['refresh_token']
    url_token = r'https://api.tdameritrade.com/v1/oauth2/token'
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    payloadN = {
        'grant_type': "refresh_token",
        'refresh_token': refreshT,
        'client_id':key_app,
    }
    authreply = requests.post(url_token,headers=headers,data=payloadN)
    decode_content = authreply.json()
    return decode_content
### returns: {'access_token': '0Fomw/U2Qy....CbC00B75E',
#  'scope': 'PlaceTrades AccountAccess MoveMoney',
#  'expires_in': 1800,
#  'token_type': 'Bearer'}


def account_data(decode_content):
    access_token = decode_content['access_token']
    headers = {'Authorization': "Bearer {}".format(access_token)}
    ## get your account info
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}".format(424634272)
    # define the payload
    payload = {'apikey':key_app}

    # make a request
    content = requests.get(url = endpoint, headers = headers)
    # convert it dictionary object
    data = content.json()
    return data


def buy_stock( access_token, ticker= '', qty=1):
    ##buy stocks as of market
    if ticker == '':
        return None
    if not isinstance(ticker,str):
        return None
    # define our headers
    header = {'Authorization':"Bearer {}".format(access_token)}

    # define the endpoint for Saved orders, including your account ID
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(acct)

    payload = {
    #   "complexOrderStrategyType": "NONE",
      "orderType": "MARKET",
      "session": "NORMAL",
    #   "price": "7.22",
      "duration": "DAY",
      "orderStrategyType": "SINGLE",
      "orderLegCollection": [
        {
          "instruction": "BUY",
          "quantity": qty,
          "instrument": {
            "symbol": ticker,
            "assetType": "EQUITY"
          }
        }
      ]
    }
    # make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
    content = requests.post(url = endpoint, json = payload, headers = header)

    data = content.json()
    ### if data shows error (Expecting value: line 1 column 1 (char 0)) then likely trade executed
    return data

def sell_stock(access_token,ticker= '', qty=1, how_to_sell='LIFO'):
    ##buy stocks as of market
    if ticker == '':
        return None
    if not isinstance(ticker,str):
        return None
    # define our headers
    header = {'Authorization':"Bearer {}".format(access_token)}

    # define the endpoint for Saved orders, including your account ID
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(acct)

    payload = {
    #   "complexOrderStrategyType": "NONE",
      "orderType": "MARKET",
      "session": "NORMAL",
    #   "price": "7.22",
      "duration": "DAY",
      "taxLotMethod": how_to_sell,
      "orderStrategyType": "SINGLE",
      "orderLegCollection": [
        {
          "instruction": "SELL",
          "quantity": qty,
          "instrument": {
            "symbol": ticker,
            "assetType": "EQUITY"
          }
        }
      ]
    }
    # make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
    content = requests.post(url = endpoint, json = payload, headers = header)

    data = content.json()
    print(data)
    ### if data shows error (Expecting value: line 1 column 1 (char 0)) then likely trade executed
    return data


def buy_limit(access_token, ticker='' , usd=100000 , qty=1):
    
    if ticker == '':
        return None
    if not isinstance(ticker,str):
        return None
    # define our headers
    header = {'Authorization':"Bearer {}".format(access_token)}

    # define the endpoint for Saved orders, including your account ID
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(acct)
    print('test-buyLim '+ticker+'#############')
    payload = {
      "complexOrderStrategyType": "NONE",
      "orderType": "LIMIT",
      "session": "NORMAL",
      "price": usd,
      "duration": "DAY",
      "orderStrategyType": "SINGLE",
      "orderLegCollection": [
        {
          "instruction": "BUY_TO_OPEN", #or BUY
          "quantity": qty,
          "instrument": {
            "symbol": ticker,
            "assetType": "EQUITY"
          }
        }
      ]
    }
    # make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
    content = requests.post(url = endpoint, json = payload, headers = header)
    data = ''
    
    try:
        data = content.json()
    except:
        None
    ### if data shows error (Expecting value: line 1 column 1 (char 0)) then likely trade executed
    return data
    
    

def sell_limit(access_token, ticker='' , usd=100000 , qty=1):
    if ticker == '':
        return None
    if not isinstance(ticker,str):
        return None
    # define our headers
    header = {'Authorization':"Bearer {}".format(access_token)}

    # define the endpoint for Saved orders, including your account ID
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(acct)

    payload = {
      "complexOrderStrategyType": "NONE",
      "orderType": "LIMIT",
      "session": "NORMAL",
      "price": usd,
      "taxLotMethod": 'LIFO',
      "duration": "DAY",
      "orderStrategyType": "SINGLE",
      "orderLegCollection": [
        {
          "instruction": "SELL_TO_CLOSE",
          "quantity": qty,
          "instrument": {
            "symbol": ticker,
            "assetType": "EQUITY"
          }
        }
      ]
    }
    # make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
    content = requests.post(url = endpoint, json = payload, headers = header)
    try:
        data = content.json()
    except:
        None
    ### if data shows error (Expecting value: line 1 column 1 (char 0)) then likely trade executed
    return data


def sell_stop_limit(access_token, sp, ticker='' , usd=100000 , qty=1):
    if ticker == '':
        return None
    if not isinstance(ticker,str):
        return None
    # define our headers
    header = {'Authorization':"Bearer {}".format(access_token)}

    # define the endpoint for Saved orders, including your account ID
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(acct)

    payload = {
      "orderType": "STOP_LIMIT",
      "session": "NORMAL",
      "price": usd,
      "stopPrice": sp,
      "taxLotMethod": 'LIFO',
      "duration": "DAY",
      "orderStrategyType": "SINGLE",
      "orderLegCollection": [
        {
          "instruction": "SELL_TO_CLOSE",
          "quantity": qty,
          "instrument": {
            "symbol": ticker,
            "assetType": "EQUITY"
          }
        }
      ]
    }
   
    # make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
    content = requests.post(url = endpoint, json = payload, headers = header)
    try:
        data = content.json()
    except:
        None
    ### if data shows error (Expecting value: line 1 column 1 (char 0)) then likely trade executed
    return data



def get_positions(auth):
    ##pass in the authorization token as a dictionary
    
    header = {'Authorization':"Bearer {}".format(auth['access_token'])}

    # define the endpoint for current investments/assets, including your account ID
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}?fields=positions".format(424634272)

    # make a post, NOTE WE ARE USING GET
    content = requests.get(url = endpoint, headers = header)

    # show the status code, we want 200
    content.status_code

    # parse the data sent back to us
    data = content.json()
    data = data['securitiesAccount']
    ##return list with three types of data [pos, $balance, cash available]
    return [ data['positions'], data['currentBalances']['cashAvailableForWithdrawal'],data]
###output: {'type': 'CASH', 'accountId': '424634272', 'roundTrips': 0, 'isDayTrader': False, 'isClosingOnlyRestricted': False, 'positions': [{'shortQuantity': 0.0, 'averagePrice': 103.6, 'currentDayProfitLoss': 2.49, 'currentDayProfitLossPercentage': 0.83, 'longQuantity': 3.0, 'settledLongQuantity': 3.0, 'settledShortQuantity': 0.0, 'instrument': {'assetType': 'EQUITY', 'cusip': '81369Y209', 'symbol': 'XLV'}, 'marketValue': 303.75, 'maintenanceRequirement': 0.0}, 


def get_transaction(auth, dateS='2020-01-15', dateE='2021-05-15', datatype='ALL' ):
    ##get all of your transactions. purpose is to keep track of stocks
    from datetime import datetime, timedelta
    
    header = {'Authorization':"Bearer {}".format(auth['access_token'])}

    # acct, all/some data or tickers, date1,date2
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/transactions?type={}&startDate={}&endDate={}".format(---, datatype,  dateS, dateE )

    # make a post, NOTE WE ARE USING GET
    content = requests.get(url = endpoint, headers = header)

    # show the status code, we want 200
    content.status_code

    # parse the data sent back to us
    data = content.json()
    return data
###input datatype:
# 'ALL', 'TRADE', 'BUY_ONLY', 'SELL_ONLY', 'CASH_IN_OR_CASH_OUT', 'CHECKING', 'DIVIDEND', 'INTEREST', 'OTHER', 'ADVISOR_FEES'
###return from transactions:
#  [ ...{'type': 'TRADE', 'subAccount': '1', 'settlementDate': '2020-03-06', 'orderId': '--', 'netAmount': -281.4, 'transactionDate': '2020-03-04T20:45:07+0000', 'orderDate': '2020-03-04T20:45:07+0000', 'transactionSubType': 'BY', 'transactionId': 25079388568, 'cashBalanceEffectFlag': True, 'description': 'BUY TRADE', 'fees': {'rFee': 0.0, 'additionalFee': 0.0, 'cdscFee': 0.0, 'regFee': 0.0, 'otherCharges': 0.0, 'commission': 0.0, 'optRegFee': 0.0, 'secFee': 0.0},
#  'transactionItem': {'accountId': ----, 'amount': 1.0, 'price': 281.4, 'cost': -281.4, 'instruction': 'BUY', 'instrument': {'symbol': 'NVDA', 'cusip': '67066G104', 'assetType': 'EQUITY'}}}, ...]


def extract_trade_history(transactions):
    ###extract the trades from our history. purpose is to get price at buy/sell date
    ###use output from get_transaction() as input here
    ll=[]
    for k in transactions:
        if k['type']=='TRADE':
            date_trans = k['transactionDate'].split('T')[0]
            listnew = [k['type'],k['transactionItem']['instrument']['symbol'],k['transactionItem']['price'],date_trans]
            ll.append(listnew)
    return ll
###returns [['TRADE', 'NVDA', 281.4, '2020-03-04'],...]
##next grouby ticker and take min and max 

def extraction(mssg):
    tick = ''
    p= '' 
    q=''
    typ = ''
    note = ''
    #ticker
    try:
        listt = mssg.split('ticker')
        tick = listt[1].split()[0].strip('-').strip(':')
        tick = tick.upper()
    except:
        None
    #price
    try:
        listp = mssg.split('price')
        p = listp[1].split()[0].strip('-').strip(':')
    except:
        None
    #qty
    try:
        listq = mssg.split('quantity')
        q = listq[1].split()[0].strip('-').strip(':')
    except:
        None
    #type
    try:
        listn = mssg.split('type')
        typ = listns[1].split()[0].strip('-').strip(':')
    except:
        None
        
    return [tick,p,q,typ]


def pull_token():
    '''  check if token exists and works, otherwise put new one in'''
    file = open("access_token_file.txt","r+") 
    inside = file.readlines()
    if len(inside) >0:
        file.close() 
        inside = inside[0]
        ins = inside #
        #         print(ins)
        res = ast.literal_eval(ins) 
            #res= inside[0]
            #res = json.loads(res)
        return res
    else:
        file.close()
        return False
#         file.write(acc_tok['Authorization'])
#     file.close() 
#     return acc_tok

def save_token(acc_tok):
    '''  check if token exists and works, otherwise put new one in'''
    file = open("access_token_file.txt","w+") 
    #inside = file.readlines()
    file.truncate()
    file.write(str(acc_tok))
    file.close() 
    return True

def check_acct(key_app , decode_content):
    ''' try getting your acct'''
    access_token = decode_content['access_token']
    headers = {'Authorization': "Bearer {}".format(access_token)}
    try:
        endpoint = r"https://api.tdameritrade.com/v1/accounts/{}".format(424634272)
        payload = {'apikey':key_app}
        content = requests.get(url = endpoint, headers = headers)
        data = content.json()
        ###data may return {'error': 'The access token being passed has expired or is invalid.'}
        data['securitiesAccount']
        return True
    except:
        return False
    

def decision_tree(mssg=''):
    if mssg == '':
        return 0
    if 'buy' in mssg and 'sell' in mssg:
        return 'bad request'
    
    note = ''
    
    decod = pull_token()
    valid = check_acct(key_app, decod)
    if not valid:
        decod = start_auth()
        saveCheck = save_token(decod)
        
    acc_tok = decod['access_token']
    mssg = str(mssg).lower()
    ticker,usd,qty,how_to_sell = extraction(mssg)
    print('test_ticker' + ticker)
    if 'limit' in mssg and 'buy' in mssg:
        buy_limit(acc_tok, ticker , usd , qty)
        note = '-Order LBuy placed-'
        return note
    if 'limit' in mssg and 'sell' in mssg:
        sell_limit(acc_tok, ticker , usd , qty)
        note = '-Order LSell placed-'
        return note
    if 'market' in mssg and 'buy' in mssg:
        buy_stock( acc_tok, ticker, qty)
        note = '-Order MBuy placed-'
        return note
    if 'market' in mssg and 'sell' in mssg:
        sell_stock(acc_tok,ticker, qty, how_to_sell)
        note = '-Order MSell placed-'
        return note
    if 'account' in mssg and 'position' in mssg:
        listp = get_positions(decod)
        pos = listp[0]
        return pos
    else:
        return 'NoRequest'
    
    
def lpf(df , cutoff = 1.0 , N = 3 , Nmin=180 , denom=110):
    ##input df and output the filtered y axis on 'close' on the latest N-minutes
    cutoff = cutoff/denom
    s= len(df['close'])-Nmin
    s=0 #consider all points
    Yclosing = df['close'].loc[s:len(df['close'])]  #.append(sr2)
    date = df['dateStr'].loc[s:len(df['dateStr'])] 
    # datet = df['datetime']
    #lpf window define
    b, a = sg.butter(N, cutoff) ##(Order, Cutoff-f)
    y_axis = sg.filtfilt(b, a, Yclosing )
    y_axis = np.round(y_axis, 3)
    ##return numpy array
    return y_axis


def slope_change_index(y):
    ###for checking the slope change read and then place an order.
    ##input array, output array of 1's with change on location.
    m = np.diff(y)
    a = m
    asign = np.sign(a)
    signchange = ((np.roll(asign, 1) - asign) != 0).astype(int)
    idx = np.nonzero(signchange)[0]   
    #remove zero values 
    for i in idx:
        if m[i] ==0:
            idx = idx[idx != i]
        if m[i] < 0:
            signchange[i] = signchange[i]*(-1)
     ## idx=array-position, m=slope, signchange=the new slope direction 1or-1.   
    return idx , m , signchange

def check_slope_change_index(idx, m, signchange, df):
    ##check & filter the slope change positions and signage. filter out flat zeroes
    m = list(m)
    idx = list(idx)
    sc = list(signchange)
    m0=  []
    idx0=[]
    sc0= []
    time0=[]
    for i in range( len(idx)-1 ):
        pos = idx[i]
        pos1= idx[i+1]
        if sc[pos]==sc[pos1]:
            continue
        elif (sc[pos]) == (sc[pos1]*-1):
            if sc[pos] !=0 and sc[pos1] !=0:
                m0.append(m[pos])
                idx0.append(idx[i])
                sc0.append(sc[pos])
                time0.append(df['datetime'][pos])
        else:
            continue
            
    return idx0,m0,sc0,time0
    
    
    
# 2570 -0.0009999999999994458 -1
# 1597700700000
# 2574 -0.0009999999999994458 -1
# 1597703100000
# 2579 -0.0010000000000012221 -1
# 1597706100000
# 2596 0.0010000000000012221 1
# 1597754400000
# 2601 0.0009999999999994458 1
# 1597757400000
# 2605 0.0009999999999994458 1


def avrg_peak_valley_detect_scipy(ticker, days=50 , Width=5 , Prom=1):
    ##get  peak to valley averages. aka cyclical variance
    data = hist_prices(ticker, 2, days)
    x = [k['close'] for k in data['candles'] ]
    avrgPrice = sum(x) / len(x)
    x = np.array(x)  ##convert for scipy
    peaks, properties = find_peaks(x, prominence=Prom, width=Width)
    valleys, propertiesV = find_peaks(-x, prominence=Prom, width=Width)
    ##get avrg
    if len(x[peaks])!=len(x[valleys]):
        print('Lengths of peaks and valleys are off for %s' % ticker)
        #return None
    
    count=0;total=0
    for p,v in zip(x[peaks],x[valleys]):
        count+=1
        total += p-v
    if count==0:
        return 0
    ##normalize
    theoryValue = ((total/count)/avrgPrice)*100
    return theoryValue

    

def compareCurve(file , df, y_lpf , Nmin ,save=True ):
    ## compare current curve to past curve (file - past, df/ylpf - current)
    ##return true if no difference
    dfold = pd.read_csv(file)
    ###if dfold == empty --> need code
    pos, m , sc = slope_change_index(y_lpf)
    dfnew=pd.DataFrame()
    slopeDate = []
    slopePos = []
    slopeChange = []
    slopeCalc = []
    for i in pos:
        if i ==0:
            continue
        # print(i, m[i] , sc[i])
        ##grab time axis from current data
        d=list(df['datetime']) #[i-Nmin]
        slopeDate.append(d)
        slopePos.append(i)
        slopeChange.append(sc[i])
        slopeCalc.append(m[i])
    dfnew['position']= slopePos
    dfnew['slope']= slopeCalc
    dfnew['change']= slopeChange
    dfnew['time']= slopeDate
    
    po = list(dfnew['position'].tail(1))
    sl = list(dfnew['slope'].tail(1))
    ch = list(dfnew['change'].tail(1))
    ti = list(dfnew['time'].tail(1))

    MemorySlopeChange=True
    for j in dfnew['time']:
        listTimes = list(dfold['time'])
        if j not in listTimes:
            #diffTime = abs(j-listTimes[-1])
            # diffTimeCurrent = abs()
#             if diffTime > 300000:
            MemorySlopeChange=False
            
    if (len(sl)==0 or len(ti)==0):
        save=False
    ##save new data
    if save == True:
        dfnew.to_csv(file,index=False)
    
    ## returns slopeDecision , pos, slope 1/-1, change 1/0, date 
    return [MemorySlopeChange , po, sl, ch, ti]


def compareCurve2(file , df, y_lpf , Nmin ,save=True ):
    ## compare current curve to past curve (file - past, df/ylpf - current)
    ## this method creates more datapoints
    ##return true if no difference
    try:
        dfold = pd.read_csv(file)
    except:
        dfold = pd.DataFrame()
        dfold['position']= None
        dfold['slope']= None
        dfold['change']= None
        dfold['time']= None
    dfold.sort_values(by=['time'], inplace=True, ascending=True)
    ###if dfold == empty --> need code

    pos, m , sc = slope_change_index(y_lpf)
    dfnew=pd.DataFrame()
    dictMid={}
    listMid=[]
    slopeDate = []
    slopePos = []
    slopeChange = []
    slopeCalc = []
    for i in pos:
        if i ==0:
            continue
        print(i, m[i] , sc[i])
        ##grab entire time axis points from current data
        d=list(df['datetime'])  #[i-Nmin]
        slopeDate.append(d)
        slopePos.append(i)
        slopeChange.append(sc[i])
        slopeCalc.append(m[i])
    dfnew['position']= slopePos
    dfnew['slope']= slopeCalc
    dfnew['change']= slopeChange
    dfnew['time']= slopeDate[0]

    po = list(dfnew['position'].tail(1))
    sl = list(dfnew['slope'].tail(1))
    ch = list(dfnew['change'].tail(1))
    ti = list(dfnew['time'].tail(1))

#     import csv
#     fields=['first','second','third']
#     with open(r'name', 'a') as f:
#         writer = csv.writer(f)
#         writer.writerow(fields)

    MemorySlopeChange=True
    for k in range(len(dfnew['time'])):
        print('k loop in dfnew time: ', k , len(dfnew['time']))
        j = dfnew['time'][k]
        listTimes = list(dfold['time'])
        if j not in listTimes:
#             diffTime = abs(j-listTimes[-1])
#             diffTimeCurrent = abs(time.time()-j)
#             ## time diff +- to count as legit. about 6minutes
#             if diffTime > 400000:
#                 print('compareCurve loop number: ',k)
#                 if diffTimeCurrent < 1500000:
            ##append new point, 5min overlap ignore & within 15min, get current point if not near other points
            listMid.append(dfnew['position'][k])
            listMid.append(dfnew['slope'][k])
            listMid.append(dfnew['change'][k])
            listMid.append(dfnew['time'][k])
            listMid.append("\n")
            MemorySlopeChange=False

    if (len(sl)==0 or len(ti)==0):
        save=False
    ##save new data
    if save == True:
        #dfnew.append(dictMid, ignore_index=True)
        #dfnew.sort_values(by=['time'], inplace=True, ascending=True)
        import csv

        with open(file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(listMid)

        #dfnew.to_csv(file,index=False)

    ## returns slopeDecision , pos, slope 1/-1, change 1/0, date
    return [MemorySlopeChange , po, sl, ch, ti]


def compareCurveFinal(file , df, y_lpf , Nmin ,save=True ):
    ## compare current curve to past curve (file - past, df/ylpf - current)
    ## this method needs to save df to_csv, DONT USE write row
    ##return true if no difference
    headers = ['position','slope','change','time']
    try:
        dfold = pd.read_csv(file)
    except:
        dfold = pd.DataFrame()
        dfold['position']= None
        dfold['slope']= None
        dfold['change']= None
        dfold['time']= None
    dfold.sort_values(by=['time'], inplace=True, ascending=True)
    print(dfold['change'])
    print('dfold^^^')
    ###if dfold == empty --> need code

    pos, m , sc = slope_change_index(y_lpf)
    dfnew=pd.DataFrame()
    dictMid={}
    listMid=[]
    slopeDate = []
    slopePos = []
    slopeChange = []
    slopeCalc = []
    for i in pos:
        if i ==0:
            continue
        print('slopes')
        print(i, m[i] , sc[i])
        ##grab entire time axis points from current data
        d=list(df['datetime'])[i-Nmin]
        slopeDate.append(d)
        slopePos.append(i)
        slopeChange.append(sc[i])
        slopeCalc.append(m[i])
    dfnew['position']= slopePos
    dfnew['slope']= slopeCalc
    dfnew['change']= slopeChange
    dfnew['time']= slopeDate
    print('slopeDate: ' , slopeDate  ,  dfnew['time'])
    print( 'dfnew ', (dfnew))
    print( 'mid ', len(listMid))
    po = list(dfnew['position'].tail(1))
    sl = list(dfnew['slope'].tail(1))
    ch = list(dfnew['change'].tail(1))
    ti = list(dfnew['time'].tail(1))
    
    MemorySlopeChange=True
    for k in range(len(dfnew['time'])):
        print('k loop in dfnew time: ', k , len(dfnew['time']))
        j = dfnew['time'][k]
        listTimes = list(dfold['time'])
        if j not in listTimes:
            MemorySlopeChange=False
            
    delete_csv(file)
    ##do not write rows to csv -> issues
    if (len(sl)==0 or len(ti)==0):
        save=False
    if save == True:
        dfnew.to_csv(file, index=False)
            
    return MemorySlopeChange




def delete_csv(file):
    try:
        f = open(file, "w+")
        f.close()
        return True
    except:
        return False


def margin(positions , current , ticker):
    ##uses first element in get_positions(), and hist_prices() as input
    for i in positions:
        if i['instrument']['symbol'] == ticker:
            avg_price = i['averagePrice']
            break
    cur_price = current['candles'][-1]['close']
    total =  cur_price - avg_price
    return total



def have_current_stock(positions , ticker):
    ##ues first element in get_positions() to check if we hold the stock 
    for i in positions:
        if i['instrument']['symbol'] == ticker:
            return True
    return False


def log_data(mssg , level):
    ##log information , levels = error,debug,info,dateNow
    logging.basicConfig(filename="logTrading.log", level=logging.INFO)
    datetime.datetime.now()
    if level == 'dateNow':
        dateStr = str(datetime.datetime.now() )
        logging.info(dateStr)
        return 1
    if level == 'info':
        logging.info(mssg)
        return 1
    if level == 'error':
        logging.error(mssg)
        return 1
    if level == 'debug':
        logging.debug(mssg)
        return 1
    return 0



def send_mssg_twil(mssg=''):
    a = twil.sms_send(mssg)
    return a


