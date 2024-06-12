import requests as rq
import json
import logging
import pandas as pd
from utils.helpers import sanitize_filename

class TradeHandler():
    def __init__(self):
        self.uri = "https://api.upstox.com/v2/order/place"
        with open('access_token.txt', 'r') as f:
            self.access_token = f.read().strip()
        self.headers = {
            "Accept": "application/json",
            'Api-version': '2.0',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        self.target = 5  # Target price increase
        self.stop_loss = 5  # Stop-loss price decrease
        self.entry_price = None
        
        # these two are for auto entry and exit flags
        self.trade_auto_triggered_entry = False
        self.trade_auto_triggered_exit = False
        
        # these two are for manual entry and exit flags
        self.trade_triggered_entry = False
        self.trade_triggered_exit = False
        
        
        self.trade_quantity = 40
        self.BN_Lot_Size = 15
        self.NF_Lot_Size = 25

    def handle_trade(self, ltp, instrument_key):
        
        minute = pd.read_csv(f'data/renko_{sanitize_filename(instrument_key)}_1min.csv')
        minute_open = minute['open'][-1:]
        minute_high = minute['high'][-1:]
        minute_low = minute['low'][-1:]
        minute_close = minute['close'][-1:]
        minute_volume = minute['volume'][-1:]
        minute_is_up = minute['is_up'][-1:]
        minute_macd_fast_blue = minute['macd_fast_blue'][-1:]
        minute_macd_slow_red = minute['macd_slow_red'][-1:]
        minute_macd_hist = minute['macd_signal-hist'][-1:]

#-----------from here they are for auto trades -------------------
        print(f"ltp: {ltp}")
        if not self.trade_auto_triggered_entry and ltp <= 220:
            logging.info(f"Trade condition met. Placing buy market order at {ltp}")
            new_quant = round(self.trade_quantity / self.BN_Lot_Size) * self.BN_Lot_Size
            self.place_auto_buy_market_order(instrument_key, new_quant)
            

        if self.trade_auto_triggered_entry and not self.trade_auto_triggered_exit:
            target_price = self.entry_price + self.target
            stop_loss_price = self.entry_price - self.stop_loss

            if ltp >= target_price:
                logging.info(f"Target hit. Placing sell market order at {ltp}")
                new_quant = round(self.trade_quantity / self.BN_Lot_Size) * self.BN_Lot_Size
                self.place_auto_sell_market_order(instrument_key, new_quant)
            elif ltp <= stop_loss_price:
                logging.info(f"Stop-loss hit. Placing sell market order at {ltp}")
                new_quant = round(self.trade_quantity / self.BN_Lot_Size) * self.BN_Lot_Size
                self.place_auto_sell_market_order(instrument_key, new_quant)
                

    def place_auto_buy_market_order(self, instrument_key, quantity):
        payload = {
            "quantity": quantity,
            "product": "D",
            "validity": "DAY",
            "price": 0,
            "tag": "string",
            "instrument_token": instrument_key,
            "order_type": "MARKET",
            "transaction_type": "BUY",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        data = json.dumps(payload)
        response = rq.post(self.uri, headers=self.headers, data=data)
        if response.status_code == 200 and response.json()['status'] == 'success':
            order_id = response.json()['data']['order_id']
            executed_price = self.get_order_data(order_id)
            self.entry_price = executed_price
            logging.info(f"Buy order placed successfully at: {executed_price}")
            self.trade_auto_triggered_entry = True
        else:
            logging.error("Failed to place buy order")
            logging.error(response.text)
    
    def place_auto_sell_market_order(self, instrument_key, quantity):
        payload = {
            "quantity": quantity,
            "product": "D",
            "validity": "DAY",
            "price": 0,
            "tag": "string",
            "instrument_token": instrument_key,
            "order_type": "MARKET",
            "transaction_type": "SELL",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        data = json.dumps(payload)
        response = rq.post(self.uri, headers=self.headers, data=data)
        if response.status_code == 200 and response.json()['status'] == 'success':
            order_id = response.json()['data']['order_id']
            executed_price = self.get_order_data(order_id)
            logging.info(f"Sell order placed successfully at: {executed_price}")
            self.trade_auto_triggered_exit = True
        else:
            logging.error("Failed to place sell order")
            logging.error(response.text)
            
#-----------upto here they are for auto trades -------------------


#-----------from here they are for manual trades -------------------
            
    def place_buy_market_order(self, instrument_key, quantity):
        payload = {
            "quantity": quantity,
            "product": "D",
            "validity": "DAY",
            "price": 0,
            "tag": "string",
            "instrument_token": instrument_key,
            "order_type": "MARKET",
            "transaction_type": "BUY",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        data = json.dumps(payload)
        response = rq.post(self.uri, headers=self.headers, data=data)
        if response.status_code == 200 and response.json()['status'] == 'success':
            order_id = response.json()['data']['order_id']
            executed_price = self.get_order_data(order_id)
            logging.info(f"Buy order placed successfully at: {executed_price}")
            self.trade_triggered_entry = True
        else:
            logging.error("Failed to place buy order")
            logging.error(response.text)      
            
    def place_sell_market_order(self, instrument_key, quantity):
        payload = {
            "quantity": quantity,
            "product": "D",
            "validity": "DAY",
            "price": 0,
            "tag": "string",
            "instrument_token": instrument_key,
            "order_type": "MARKET",
            "transaction_type": "SELL",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        data = json.dumps(payload)
        response = rq.post(self.uri, headers=self.headers, data=data)
        if response.status_code == 200 and response.json()['status'] == 'success':
            order_id = response.json()['data']['order_id']
            executed_price = self.get_order_data(order_id)
            logging.info(f"Sell order placed successfully at: {executed_price}")
            self.trade_triggered_exit = True
        else:
            logging.error("Failed to place buy order")
            logging.error(response.text) 
            
#-----------upto here they are for auto trading -------------------
            
    def get_order_data(self, order_id):
        url = f"https://api.upstox.com/v2/order/details?order_id={order_id}"
        payload={}
        res = rq.get(url, headers=self.headers, data=payload)
        executed_price = res.json()['average_price']
        return executed_price
    
    