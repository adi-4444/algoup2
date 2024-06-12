import json
from datetime import datetime
import os
import pickle
from indicators import run_indicators
from utils.helpers import sanitize_filename
import pandas as pd

INTERVAL_MAP = {
    1: '1min',
    3: '3min',
    5: '5min',
    15: '15min'
}

class DataHandler:
    def __init__(self):
        # Initialize data structures for each instrument
        self.historical_data_loaded = False
        self.data = {}
        self.data_dir = 'data'
        self.intervals = [1]
        self.current_date = datetime.now()

        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Initialize minute data for each interval
        for interval in self.intervals:
            self.data[interval] = []  # it will create {1: [], 3: [], 5: [], 15: []}

    def tick_handler(self, tick_data, instrument_key):
        # Load historical data only once
        if not self.historical_data_loaded:
            self.load_historical_data(instrument_key) # this will update historical data in self.data[interval]
            self.historical_data_loaded = True

        # Extract the 1-minute interval data from the tick data
        ohlc_data = tick_data['ff']['marketFF']['marketOHLC']['ohlc'][2]
        current_oi = tick_data['ff']['marketFF']['eFeedDetails']['oi']
        print('---------------------------processed Ticks -----------------------------')
        print("ohlc_data", ohlc_data)
        # Convert timestamp to a datetime object
        timestamp = int(ohlc_data['ts'])
        timestamp = datetime.fromtimestamp(timestamp / 1000)
        print("timestamp", timestamp)
        print('-----------------------------------------------------------------------')
        
        open_price = ohlc_data['open']
        high_price = ohlc_data['high']
        low_price = ohlc_data['low']
        close_price = ohlc_data['close']
        volume = ohlc_data['volume']

        # Aggregate this one minute interval data into 3, 5, 15 minute interval data
        for interval in self.intervals:
            self.aggregate_data(interval, timestamp, open_price, high_price, low_price, close_price, volume, current_oi, instrument_key)

    def aggregate_data(self, interval, timestamp, open_price, high_price, low_price, close_price, volume, current_oi, instrument_key):
        if len(self.data[interval]) > 0:
            last_data = self.data[interval][-1]
            if isinstance(last_data['date'], datetime):
                prev_timestamp = last_data['date']
            else:
                prev_timestamp = datetime.strptime(last_data['date'], '%Y-%m-%d %H:%M:%S')
            curr_timestamp = timestamp

            # Calculate the number of minutes elapsed since the last data point
            elapsed_minutes = (curr_timestamp - prev_timestamp).total_seconds() / 60

            # Check if the current timestamp falls within the same interval
            if elapsed_minutes < interval:
                # Update the last data point
                last_data['high'] = max(last_data['high'], high_price)
                last_data['low'] = min(last_data['low'], low_price)
                last_data['close'] = close_price
                last_data['volume'] += volume
                last_data['oi'] = current_oi
            else:
                # Create a new data point
                new_data = {
                    'date': timestamp,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume,
                    'oi': current_oi
                }
                self.data[interval].append(new_data)
        else:
            # Create a new data point
            new_data = {
                'date': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'oi': current_oi
            }
            self.data[interval].append(new_data)

        # Pass the interval data to the indicators to calculate the indicators
        run_indicators(self.data[interval], INTERVAL_MAP[interval], instrument_key)

        # Update the data to the file on every tick data change in data[interval]
        self.update_data(instrument_key)

    # Update the interval data to the file
    def update_data(self, instrument_key):
        for interval in self.intervals:
            if self.data[interval]:
               #  filename = os.path.join(
               #      self.data_dir, f"{self.current_date.strftime('%Y-%m-%d')}-{sanitize_filename(instrument_key)}-{INTERVAL_MAP[interval]}.json"
               #  )
               #  with open(filename, 'w') as f:
               #      json.dump(self.data[interval], f, indent=4, default=str)
                # Save files as csv also
                csvfile = os.path.join(
                    self.data_dir, f"{self.current_date.strftime('%Y-%m-%d')}-{sanitize_filename(instrument_key)}-{INTERVAL_MAP[interval]}.csv"
                )
                df = pd.DataFrame(self.data[interval])
                df.to_csv(csvfile, index=False)

    def load_historical_data(self, instrument_key):
        for interval in self.intervals:
            historical_data_file = os.path.join(self.data_dir, f"{sanitize_filename(instrument_key)}-{INTERVAL_MAP[interval]}")
            if os.path.exists(historical_data_file):
                with open(historical_data_file, 'rb') as f:
                    historical_data = pickle.load(f)
                    self.data[interval] = historical_data
            else:
                self.data[interval] = []
