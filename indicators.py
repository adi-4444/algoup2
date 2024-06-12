
import pandas as pd
from stock_indicators import indicators, Quote , PivotPointType, PeriodSize # use for macd, ema, super trend, pivot points
import os
from stock_indicators.indicators.common.enums import EndType
import pickle
from utils.helpers import sanitize_filename
from stock_indicators.indicators.common import Quote

def run_indicators(data, interval, instrument_key): 
    df = pd.DataFrame(data)
    
    qdf = pd.DataFrame(data)
    qdf['date'] = pd.to_datetime(qdf['date'])
    # Convert 'date' column to datetime objects
    candle_quotes = [Quote(date,open,high,low,close,volume) for date,open,high,low,close,volume in zip(qdf['date'], qdf['open'], qdf['high'], qdf['low'], qdf['close'], qdf['volume'])]
    # renko using si
    
    renko_results = indicators.get_renko(candle_quotes, brick_size=5,end_type=EndType.CLOSE)
    renko_df = pd.DataFrame(
    [{
        'date': result.date,
        'open': round(result.open, 2),
        'high': round(result.high, 2),
        'low': round(result.low, 2),
        'close': round(result.close, 2),
        'volume': round(result.volume, 2),
        'is_up': result.is_up
    } 
        for result in renko_results
    ])
    
    renko_quotes = [Quote(date,open,high,low,close,volume) for date,open,high,low,close,volume in zip(renko_df['date'], renko_df['open'], renko_df['high'], renko_df['low'], renko_df['close'], renko_df['volume'])]
    renko_df_macd = indicators.get_macd(renko_quotes, 12, 26, 9)
    
    renko_macd_df = pd.DataFrame(
        [{
            'macd_fast_blue': round(float(0 if macd_result.macd is None else macd_result.macd), 2),
            'macd_slow_red':  round(float(0 if macd_result.signal is None else macd_result.signal), 2),
            'macd_signal-hist': round(float(0 if macd_result.histogram is None else macd_result.histogram), 2)
        }
         for macd_result in renko_df_macd
        ]
    )
    
    renko_df["macd_fast_blue"] = renko_macd_df['macd_fast_blue']
    renko_df['macd_slow_red'] = renko_macd_df['macd_slow_red']
    renko_df["macd_signal-hist"] = renko_macd_df['macd_signal-hist']
    
    renko_csvfile = os.path.join('data', f"renko_{sanitize_filename(str(instrument_key))}_{interval}.csv")
    renko_df.to_csv(renko_csvfile, index=False)

