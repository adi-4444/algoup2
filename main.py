import os
import asyncio
from web_socket_data import websocket_handler
from auto_login import auto_login
from utils.helpers import check_upstox_token_validity, get_instruments, get_instrument_key_by_tradingsymbol
from upstox_client import api, UserApi
from get_historical_data import get_historical_data
from data_handler import DataHandler
from trade import TradeHandler


ACCESS_TOKEN_FILE = 'access_token.txt'
trading_symbols = ['BANKNIFTY2461950000PE']

trade_entry = False
trade_exit = False

async def main():
    print('Service started...')
    if os.path.exists(ACCESS_TOKEN_FILE):
        with open(ACCESS_TOKEN_FILE, 'r') as a_file:
            access_token = a_file.read().strip()
        if check_upstox_token_validity(access_token):
            print('Using existing access token...')
            get_instruments()
        else:
            print('Access token invalid, performing auto login...')
            auto_login()
            get_instruments()
    else:
        print('Access token not found, performing auto login...')
        auto_login()
        get_instruments()

    instrument_keys = []
    
    for trading_symbol in trading_symbols:
        instrument_keys.append(get_instrument_key_by_tradingsymbol(trading_symbol))
        
    for instrument_key in instrument_keys:
        get_historical_data(instrument_key)
        
    handler = DataHandler()
    trade = TradeHandler()

    async def on_connect():
        
        print("Connection established")

    async def on_ticks(tick_data):
        global trade_entry, trade_exit
        
        for tick in tick_data['feeds']:
                        
            ltp = tick_data['feeds'][tick]['ff']['marketFF']['ltpc']['ltp']
            print('ltp :',ltp)
            if not trade_entry and ltp <= 370:
                print('----------entry ----------------')
                buy_average, executed_buy_quantity_total, buy_executed_symbol = trade.place_buy_market_order(tick,15)
                print('buy_average :',buy_average)
                print('executed_buy_quantity_total :',executed_buy_quantity_total)
                print('buy_executed_symbol :',buy_executed_symbol)
                trade_entry = True
                
            elif trade_entry and not trade_exit and ltp >=375:
                print('----------target ----------------')
                sell_average, executed_sell_quantity_total, sell_executed_symbol = trade.place_sell_market_order(tick,15)
                print('sell_average :',sell_average)
                print('executed_sell_quantity_total :',executed_sell_quantity_total)
                print('sell_executed_symbol :',sell_executed_symbol)
                trade_exit = True
                
            elif trade_entry and not trade_exit and ltp <=365:
                print('----------stop loss ----------------')
                sell_average, executed_sell_quantity_total, sell_executed_symbol = trade.place_sell_market_order(tick,15)
                print('sell_average :',sell_average)
                print('executed_sell_quantity_total :',executed_sell_quantity_total)
                print('sell_executed_symbol :',sell_executed_symbol)
                trade_exit = True
        pass
        
    async def on_close():
        print("Connection closed")

    async def on_order_update(order_data):
        # print("Received order update:", order_data)
        pass

    await websocket_handler(access_token, instrument_keys, on_connect, on_ticks, on_close, on_order_update)

if __name__ == '__main__':
    asyncio.run(main())