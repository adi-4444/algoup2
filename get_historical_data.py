import requests
import datetime
import os
import pickle
import logging
import pandas as pd
from utils.helpers import sanitize_filename

def aggregate_candles(data, interval):
    aggregated_data = []
    temp_candle = None
    count = 0

    for candle in data:
        date, open_price, high_price, low_price, close_price, volume, oi = candle.values()
        if count % interval == 0:
            if temp_candle:
                aggregated_data.append(temp_candle)
            temp_candle = {
                'date': date,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'oi': oi
            }
        else:
            temp_candle['high'] = max(temp_candle['high'], high_price)
            temp_candle['low'] = min(temp_candle['low'], low_price)
            temp_candle['close'] = close_price
            temp_candle['volume'] += volume
            temp_candle['oi'] += oi
        count += 1

    if temp_candle:
        aggregated_data.append(temp_candle)
    return aggregated_data

def save_data(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)
    logging.info(f"Saved aggregated data to {filename}")

def get_historical_data(instrument_key):
    # Define market hours
    market_open = datetime.time(9, 15)
    market_close = datetime.time(15, 30)

    # Get current date and time
    now = datetime.datetime.now()

    # Calculate 'from_date' dynamically based on required trading days (26 trading days for sufficient data)
    trading_days_needed = 1

    from_date = now - datetime.timedelta(days=trading_days_needed)

    # Adjust 'from_date' to ensure it's not a weekend
    while from_date.weekday() in [5, 6]:  # 5: Saturday, 6: Sunday
        from_date -= datetime.timedelta(days=1)  # Move to previous date

    now_date = now.strftime("%Y-%m-%d")
    from_date = from_date.date()

    historical_url = f"https://api.upstox.com/v2/historical-candle/{instrument_key}/1minute/{now_date}/{from_date}"
    intraday_url = f'https://api.upstox.com/v2/historical-candle/intraday/{instrument_key}/1minute'

    payload = {}
    headers = {'Accept': 'application/json'}

    # Fetch historical data
    response = requests.request("GET", historical_url, headers=headers, data=payload)
    historical_data = response.json()['data']['candles']

    # Fetch intraday data for the current day
    intraday_response = requests.request("GET", intraday_url, headers=headers, data=payload)
    intraday_data = intraday_response.json()['data']['candles']
    

    # Check if intraday data is empty and only merge if it's not empty
    if intraday_data:
        # Merge historical and intraday data
        historical_data = intraday_data + historical_data
    else:
        logging.info("No intraday data fetched for the current day as market haven't started, only using historical data.")

    # Reverse the data to get it in ascending order
    historical_data = historical_data[::-1]
    
    
    # Convert the data to a DataFrame to make it easier to work with then convert it back to a list of dictionaries
    one_min_df = pd.DataFrame(historical_data)
    one_min_df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'oi']
    one_min_df['date']=pd.to_datetime(one_min_df['date']).apply(lambda x: str(x).split('+')[0])
    one_minute_data = one_min_df.to_dict('records')

    # save 1-minute interval data
    save_data(one_minute_data, f"data/{sanitize_filename(instrument_key)}-1min")
    # save this one as csv
    # csvfilename = os.path.join('data', f"{sanitize_filename(instrument_key)}-1min.csv")
    # one_min_df.to_csv(csvfilename, index=False)
    
    # with open(f"data/{sanitize_filename(instrument_key)}-1min", 'rb') as f:
    #     historical_data = pickle.load(f)
    #     print(pd.DataFrame(historical_data))
        
    # Aggregate and save 3-minute interval data
    # three_minute_data = aggregate_candles(one_minute_data, 3)
    # save_data(three_minute_data, f"data/{sanitize_filename(instrument_key)}-3min")
    # with open(f"data/{sanitize_filename(instrument_key)}-3min", 'rb') as f:
    #     historical_data = pickle.load(f)
    #     print(pd.DataFrame(historical_data))
    
    # Aggregate and save 5-minute interval data
    # five_minute_data = aggregate_candles(one_minute_data, 5)
    # save_data(five_minute_data, f"data/{sanitize_filename(instrument_key)}-5min")
    # with open(f"data/{sanitize_filename(instrument_key)}-5min", 'rb') as f:
    #     historical_data = pickle.load(f)
    #     print(pd.DataFrame(historical_data))

    # Aggregate and save 15-minute interval data
    # fifteen_minute_data = aggregate_candles(one_minute_data, 15)
    # save_data(fifteen_minute_data, f"data/{sanitize_filename(instrument_key)}-15min")
    # with open(f"data/{sanitize_filename(instrument_key)}-15min", 'rb') as f:
    #     historical_data = pickle.load(f)
    #     print(pd.DataFrame(historical_data))