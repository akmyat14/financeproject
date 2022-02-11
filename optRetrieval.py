from logging import exception
import requests
from datetime import datetime, timedelta
import time
import config
import numpy as np
from scipy.stats import norm


def call_Options(name):
    url = 'https://api.polygon.io/v3/reference/options/contracts'

    parameters = {
        'apiKey': config.api_key,
        'underlying_ticker': name,
        'contract_type': 'call',
        'order': 'asc',
        'limit': 1000,
        'sort': 'expiration_date'
    }

    calls_json = requests.get(url, parameters).json()
    calls_list = calls_json['results']

    while 'next_url' in calls_json:
        calls_json = requests.get(calls_json['next_url'], parameters).json()
        calls_list.extend(calls_json['results'])

        if 'next_url' not in calls_json.keys():
            break

    return calls_list


def call_Data(option, multiplier, timespan, start, to):

    current_day = datetime.today()

    optionsTicker = option
    multiplier = '1'
    timespan = 'day'
    start = (current_day-timedelta(100)).strftime("%Y-%m-%d")
    to = current_day
    url = f'https://api.polygon.io/v2/aggs/ticker/{optionsTicker}/range/{multiplier}/{timespan}/{start}/{to}'

    parameters = {
        'apiKey': config.api_key,
        'sort': 'asc',
        'limit': '120',
    }

    call_data_json = requests.get(url, parameters).json()
    call_data_list = call_data_json['results']

    return call_data_list


def expiration_strikeprice(option, calls_list):
    expir_strik = []
    maximum = len(calls_list)
    for index in range(0, maximum):
        if calls_list[index]['ticker'] == option:
            expir_strik.append(calls_list[index]['expiration_date'])
            expir_strik.append(calls_list[index]['strike_price'])

    current_day = datetime.today()
    expir_date = datetime.strptime(expir_strik[0], '%Y-%m-%d')

    expir_strik[0] = ((expir_date-current_day).days)/365

    return expir_strik


def prev_close(tickerName):
    stockTicker = tickerName

    url = f'https://api.polygon.io/v2/aggs/ticker/{stockTicker}/prev'

    parameters = {
        'apiKey': config.api_key,
    }

    prev_close_data_json = requests.get(url, parameters).json()
    prev_close_price = prev_close_data_json['results'][0]['c']

    return prev_close_price


def standard_deviation(tickerName):
    stockTicker = tickerName

    current_day = datetime.today()
    prev_day = current_day - timedelta(days=1)
    prev_year = current_day-timedelta(days=367)

    prev_day_string = prev_day.strftime("%Y-%m-%d")
    prev_year_string = prev_year.strftime("%Y-%m-%d")

    url = f'https://api.polygon.io/v2/aggs/ticker/{stockTicker}/range/1/day/{prev_year_string}/{prev_day_string}'

    parameters = {
        'apiKey': config.api_key,
        'sort': 'asc',
        'limit': '260',
    }

    closing_data_list = []

    closing_data_json = requests.get(url, parameters).json()

    for day in range(1, 255):
        daily_return = np.log(
            (closing_data_json['results'][day]['c'])/(closing_data_json['results'][day-1]['c']))
        closing_data_list.append(daily_return)

    TRADING_DAYS = len(closing_data_list)

    volatility = np.std(closing_data_list) * np.sqrt(TRADING_DAYS)

    return volatility


def black_Scholes_Call(S, K, T, r, sigma):
    d1 = ((np.log(S/K)+(r+(sigma**2)/2)*T)/(sigma*np.sqrt(T)))
    d2 = d1 - (sigma * np.sqrt(T))
    call_price = (S * norm.cdf(d1)) - (K * np.exp(-r*T) * norm.cdf(d2))
    return call_price


def extract_ticker(option):
    list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    ticker = ''

    for char in option[2:]:
        if(char not in list):
            ticker += char
        else:
            break

    return ticker


def delay():
    print('tasks done, now sleeping for 12 seconds due to API call limit')
    for i in range(12):
        time.sleep(1)


def given_option(option):
    underlying_ticker = extract_ticker(option)
    call_list = call_Options(underlying_ticker)
    delay()
    extraction = expiration_strikeprice(option, call_list)
    expire = extraction[0]
    print('Expire time:'+str(expire))
    strikePrice = extraction[1]
    print('Strike price:'+str(strikePrice))
    riskFreeRate = 0.0182
    currentPrice = prev_close(underlying_ticker)
    print(f'Current price of {underlying_ticker} stock:'+str(currentPrice))
    delay()
    volatility = standard_deviation(underlying_ticker)
    print(f'Volatility of {underlying_ticker} stock:'+str(volatility))
    delay()
    call_option_price = black_Scholes_Call(
        currentPrice, strikePrice, expire, riskFreeRate, volatility)
    actual_price = prev_close(option)
    print(
        f'Black-Scholes-Merton model-price of {option}:'+str(call_option_price))
    print(f'Actual price of {option}:'+str(actual_price))
    delay()

    if(call_option_price > actual_price):
        print('Undervalued')
    else:
        print('Overvalued')
