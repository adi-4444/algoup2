import pandas as pd
import logging
import datetime
import requests as rq

logging.basicConfig(level=logging.DEBUG)


def check_upstox_token_validity(access_token):
    logging.info('Checking access token validity...')
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
      }
    url ='https://api.upstox.com/v2/user/profile'
    response = rq.get(url, headers=headers)
    if response.status_code == 200:
          logging.info('Access token is valid...')
          return True
    else:
          logging.info('Access token is invalid...')
          return False  
       
def get_instruments():
      logging.info('Fetching instruments...')
      instruments = pd.read_csv('https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz')
      instruments = instruments[
      (instruments['exchange'] == 'NSE_FO') &
      (instruments['instrument_type'].isin(['FUTIDX', 'OPTIDX'])) & 
      (instruments['tradingsymbol'].str.contains('NIFTY|BANKNIFTY'))]   
      instruments.to_csv('nfo_instrument.csv', index=False)
      
def get_instrument_key_by_tradingsymbol(tradingsymbol):
      logging.info('Fetching instrument key...')
      instruments = pd.read_csv('nfo_instrument.csv')
      return instruments[instruments['tradingsymbol'] == tradingsymbol]['instrument_key'].values[0]

def sanitize_filename(filename):
    # Replace invalid characters with underscores or other valid characters
    return filename.replace('NSE_FO|', '')


