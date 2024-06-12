import os
import asyncio
from web_socket_data import websocket_handler
from auto_login import auto_login
from utils.helpers import check_upstox_token_validity, get_instruments, get_instrument_key_by_tradingsymbol
from upstox_client import api, UserApi
from get_historical_data import get_historical_data
from data_handler import DataHandler
from strategies import strategies
from trade import TradeHandler


ACCESS_TOKEN_FILE = 'access_token.txt'
trading_symbols = ['BANKNIFTY24JULFUT']

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
        for tick in tick_data['feeds']:
            # print('----------live feed------------------')
            # print(tick_data['feeds'][tick]['ff']['marketFF']['ltpc']['ltp'])
            # print('-----------------------------------')
            handler.tick_handler(tick_data['feeds'][tick],tick)
            # strategies(tick_data['feeds'][tick],tick)
            # trade.handle_trade(tick_data['feeds'][tick]['ff']['marketFF']['ltpc']['ltp'],tick)
        pass
        
    async def on_close():
        print("Connection closed")

    async def on_order_update(order_data):
        # print("Received order update:", order_data)
        pass

    await websocket_handler(access_token, instrument_keys, on_connect, on_ticks, on_close, on_order_update)

if __name__ == '__main__':
    asyncio.run(main())