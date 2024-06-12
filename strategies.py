import pandas as pd
import logging
from utils.helpers import get_instrument_key_by_tradingsymbol
# from trade import TradesHandler


trade_triggered_entry = False
trade_triggered_exit = False

def strategies(tick,instrument_key):
   # trade_handler = TradesHandler(kite)
   global trade_triggered_entry
   global trade_triggered_exit
   
   
   ltp = tick['last_price']
   instrument_token = tick['instrument_token']
   
   # access data from csv file
   minute = pd.read_csv('data/indicators_data_minute.csv')
   three_minute = pd.read_csv('data/indicators_data_3minute.csv')
   five_minute = pd.read_csv('data/indicators_data_5minute.csv')
   fifteen_minute = pd.read_csv('data/indicators_data_15minute.csv')
   
   minute_renko = pd.read_csv('data/renko_data_minute.csv')
   three_minute_renko = pd.read_csv('data/renko_data_3minute.csv')
   five_minute_renko = pd.read_csv('data/renko_data_5minute.csv')
   fifteen_minute_renko = pd.read_csv('data/renko_data_15minute.csv')
   
   
   
   # minute data
   minute_open = minute['open'][-1:]
   minute_high = minute['high'][-1:]
   minute_low = minute['low'][-1:]
   minute_close = minute['close'][-1:]
   minute_volume = minute['volume'][-1:]
   minute_oi = minute['oi'][-1:]
   minute_ema50 = minute['ema50'][-1:]
   minute_ema200 = minute['ema200'][-1:]
   minute_vwap = minute['vwap'][-1:]
   minute_macd_fast_blue = minute['macd_fast_blue'][-1:]
   minute_macd_slow_red = minute['macd_slow_red'][-1:]
   minute_macd_hist = minute['macd_signal-hist'][-1:]
   minute_super_trend = minute['super_trend'][-1:]
   minute_pp = minute['pp'][-1:]
   minute_r1 = minute['r1'][-1:]
   minute_r2 = minute['r2'][-1:]
   minute_r3 = minute['r3'][-1:]
   minute_s1 = minute['s1'][-1:]
   minute_s2 = minute['s2'][-1:]
   minute_s3 = minute['s3'][-1:]
   minute_heikin_ashi_open = minute['heikin_ashi_open'][-1:]
   minute_heikin_ashi_high = minute['heikin_ashi_high'][-1:]
   minute_heikin_ashi_low = minute['heikin_ashi_low'][-1:]
   minute_heikin_ashi_close = minute['heikin_ashi_close'][-1:]
   minute_heikin_ashi_volume = minute['heikin_ashi_volume'][-1:]
   
   minute_renko_open = minute_renko['open'][-1:]
   minute_renko_high = minute_renko['high'][-1:]
   minute_renko_low = minute_renko['low'][-1:]
   minute_renko_close = minute_renko['close'][-1:]
   minute_renko_volume = minute_renko['volume'][-1:]
   minute_renko_is_up = minute_renko['is_up'][-1:]
   
   #3minute data
   three_minute_open = three_minute['open'][-1:]
   three_minute_high = three_minute['high'][-1:]
   three_minute_low = three_minute['low'][-1:]
   three_minute_close = three_minute['close'][-1:]
   three_minute_volume = three_minute['volume'][-1:]
   three_minute_oi = three_minute['oi'][-1:]
   three_minute_ema50 = three_minute['ema50'][-1:]
   three_minute_ema200 = three_minute['ema200'][-1:]
   three_minute_vwap = three_minute['vwap'][-1:]
   three_minute_macd_fast_blue = three_minute['macd_fast_blue'][-1:]
   three_minute_macd_slow_red = three_minute['macd_slow_red'][-1:]
   three_minute_macd_hist = three_minute['macd_signal-hist'][-1:]
   three_minute_super_trend = three_minute['super_trend'][-1:]
   three_minute_pp = three_minute['pp'][-1:]
   three_minute_r1 = three_minute['r1'][-1:]
   three_minute_r2 = three_minute['r2'][-1:]
   three_minute_r3 = three_minute['r3'][-1:]
   three_minute_s1 = three_minute['s1'][-1:]
   three_minute_s2 = three_minute['s2'][-1:]
   three_minute_s3 = three_minute['s3'][-1:]
   three_minute_heikin_ashi_open = three_minute['heikin_ashi_open'][-1:]
   three_minute_heikin_ashi_high = three_minute['heikin_ashi_high'][-1:]
   three_minute_heikin_ashi_low = three_minute['heikin_ashi_low'][-1:]
   three_minute_heikin_ashi_close = three_minute['heikin_ashi_close'][-1:]
   three_minute_heikin_ashi_volume = three_minute['heikin_ashi_volume'][-1:]
   
   three_minute_renko_open = three_minute_renko['open'][-1:]
   three_minute_renko_high = three_minute_renko['high'][-1:]
   three_minute_renko_low = three_minute_renko['low'][-1:]
   three_minute_renko_close = three_minute_renko['close'][-1:]
   three_minute_renko_volume = three_minute_renko['volume'][-1:]
   three_minute_renko_is_up = three_minute_renko['is_up'][-1:]
   
   #5minute data
   five_minute_open = five_minute['open'][-1:]
   five_minute_high = five_minute['high'][-1:]
   five_minute_low = five_minute['low'][-1:]
   five_minute_close = five_minute['close'][-1:]
   five_minute_volume = five_minute['volume'][-1:]
   five_minute_oi = five_minute['oi'][-1:]
   five_minute_ema50 = five_minute['ema50'][-1:]
   five_minute_ema200 = five_minute['ema200'][-1:]
   five_minute_vwap = five_minute['vwap'][-1:]
   five_minute_macd_fast_blue = five_minute['macd_fast_blue'][-1:]
   five_minute_macd_slow_red = five_minute['macd_slow_red'][-1:]
   five_minute_macd_hist = five_minute['macd_signal-hist'][-1:]
   five_minute_super_trend = five_minute['super_trend'][-1:]
   five_minute_pp = five_minute['pp'][-1:]
   five_minute_r1 = five_minute['r1'][-1:]
   five_minute_r2 = five_minute['r2'][-1:]
   five_minute_r3 = five_minute['r3'][-1:]
   five_minute_s1 = five_minute['s1'][-1:]
   five_minute_s2 = five_minute['s2'][-1:]
   five_minute_s3 = five_minute['s3'][-1:]
   five_minute_heikin_ashi_open = five_minute['heikin_ashi_open'][-1:]
   five_minute_heikin_ashi_high = five_minute['heikin_ashi_high'][-1:]
   five_minute_heikin_ashi_low = five_minute['heikin_ashi_low'][-1:]
   five_minute_heikin_ashi_close = five_minute['heikin_ashi_close'][-1:]
   five_minute_heikin_ashi_volume = five_minute['heikin_ashi_volume'][-1:]
   
   five_minute_renko_open = five_minute_renko['open'][-1:]
   five_minute_renko_high = five_minute_renko['high'][-1:]
   five_minute_renko_low = five_minute_renko['low'][-1:]
   five_minute_renko_close = five_minute_renko['close'][-1:]
   five_minute_renko_volume = five_minute_renko['volume'][-1:]
   five_minute_renko_is_up = five_minute_renko['is_up'][-1:]
   
   
   #15minute data
   fifteen_minute_open = fifteen_minute['open'][-1:]
   fifteen_minute_high = fifteen_minute['high'][-1:]
   fifteen_minute_low = fifteen_minute['low'][-1:]
   fifteen_minute_close = fifteen_minute['close'][-1:]
   fifteen_minute_volume = fifteen_minute['volume'][-1:]
   fifteen_minute_oi = fifteen_minute['oi'][-1:]
   fifteen_minute_ema50 = fifteen_minute['ema50'][-1:]
   fifteen_minute_ema200 = fifteen_minute['ema200'][-1:]
   fifteen_minute_vwap = fifteen_minute['vwap'][-1:]
   fifteen_minute_macd_fast_blue = fifteen_minute['macd_fast_blue'][-1:]
   fifteen_minute_macd_slow_red = fifteen_minute['macd_slow_red'][-1:]
   fifteen_minute_macd_hist = fifteen_minute['macd_signal-hist'][-1:]
   fifteen_minute_super_trend = fifteen_minute['super_trend'][-1:]
   fifteen_minute_pp = fifteen_minute['pp'][-1:]
   fifteen_minute_r1 = fifteen_minute['r1'][-1:]
   fifteen_minute_r2 = fifteen_minute['r2'][-1:]
   fifteen_minute_r3 = fifteen_minute['r3'][-1:]
   fifteen_minute_s1 = fifteen_minute['s1'][-1:]
   fifteen_minute_s2 = fifteen_minute['s2'][-1:]
   fifteen_minute_s3 = fifteen_minute['s3'][-1:]
   fifteen_minute_hike_open = fifteen_minute['heikin_ashi_open'][-1:]
   fifteen_minute_heikin_ashi_high = fifteen_minute['heikin_ashi_high'][-1:]
   fifteen_minute_heikin_ashi_low = fifteen_minute['heikin_ashi_low'][-1:]
   fifteen_minute_heikin_ashi_close = fifteen_minute['heikin_ashi_close'][-1:]
   fifteen_minute_heikin_ashi_volume = fifteen_minute['heikin_ashi_volume'][-1:]
   
   fifteen_minute_renko_open = fifteen_minute_renko['open'][-1:]
   fifteen_minute_renko_high = fifteen_minute_renko['high'][-1:]
   fifteen_minute_renko_low = fifteen_minute_renko['low'][-1:]
   fifteen_minute_renko_close = fifteen_minute_renko['close'][-1:]
   fifteen_minute_renko_volume = fifteen_minute_renko['volume'][-1:]
   fifteen_minute_renko_is_up = fifteen_minute_renko['is_up'][-1:]
   
   
   
   # write strategies here
  
   # to place a abuy order pass instrument_symbol, quantity based on condition
   # trade_triggered is to check order is placed or not if placed it will not place again
   # if not trade_triggered_entry and ltp <= 60:
   #    logging.info("Trade condition met. Placing buy market order.")
   #    trade_handler.place_sliced_buy_orders(instrument_symbol, 500)
   #    trade_triggered_entry = True
            
   # to place a sell order pass instrument_symbol, quantity based on condition
   # trade_triggered_exit is to check order is placed or not if placed it will not place again
   # if not trade_triggered_exit and trade_triggered_entry and ltp >= 65:
   #    logging.info("Trade closed. Resetting trade_triggered to False.")
   #    trade_handler.place_sliced_sell_orders(instrument_symbol, 500)
   #    trade_triggered_exit = True
    
   
   # print(f'minute minute_renko_close: {round(minute_renko_close,2).to_string(index=False, header=False)}')
   # print(f'minute_renko_is_up: {minute_renko_is_up.to_string(index=False, header=False)}')
   print(instrument_key , ltp)