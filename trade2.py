import requests as rq
import json
import logging
import pandas as pd
from utils.helpers import sanitize_filename, get_instrument_sybmbol_by_key
import os

class TradeHandler2():
    def __init__(self):
        self.uri = "https://api.upstox.com/v2/order/place"
        self.get_order_details_url = "https://api.upstox.com/v2/order/details"
        self.modify_order_url = "https://api.upstox.com/v2/order/modify"
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
        self.filepath = None
        
        # these two are for auto entry and exit flags
        self.trade_auto_triggered_entry = False
        self.trade_auto_triggered_exit = False
        
        # these falgs are for buy order with target and stop loss
        
        self.trade_buy_with_target = False
        self.trade_buy_with_stoploss = False
        
        # these two are for manual entry and exit flags
        self.trade_triggered_entry = False
        self.trade_triggered_exit = False

        self.trade_quantity = 10
        self.BN_Lot_Size = 15
        self.NF_Lot_Size = 25
        self.BN_MAX_ORDER_QUANTITY = 900
        self.NF_MAX_ORDER_QUANTITY = 1800

    def handle_trades(self, ltp, instrument_key):
       # can place trades from here or from where ltp is passing
       pass

   #-----for placing sliced order call these functinos----------------
   
    def place_buy_market_order(self, instrument_key, quantity):
        trading_symbol = get_instrument_sybmbol_by_key(instrument_key)       
         # Determine if the symbol is BankNifty or Nifty
        if "BANKNIFTY" in trading_symbol:
            lot_size = self.BN_Lot_Size
            max_order_quantity = self.BN_MAX_ORDER_QUANTITY
        elif "NIFTY" in trading_symbol:
            lot_size = self.NF_Lot_Size
            max_order_quantity = self.NF_MAX_ORDER_QUANTITY
        else:
            raise ValueError("Invalid trading symbol: must be either BankNifty or Nifty")

        new_quant = round(quantity / lot_size) * lot_size
        remaining_quantity = new_quant
        buy_count = 0
        executed_buy_price_total=0
        executed_buy_quantity_total=0
        while remaining_quantity > 0:
            buy_count += 1
            order_quantity = min(remaining_quantity, max_order_quantity)
            executed_price, executed_quantity, executed_symbol = self.buy_market_order(instrument_key, order_quantity)
            executed_buy_price_total += executed_price
            remaining_quantity -= order_quantity
            executed_buy_quantity_total += executed_quantity
            logging.info(f"Placed {order_quantity}-{order_quantity/lot_size} units. Remaining: {order_quantity}-{remaining_quantity/lot_size}")
        
        if executed_buy_quantity_total > 0:
            buy_average = executed_buy_price_total/buy_count
            buy_executed_symbol = executed_symbol
            return buy_average, executed_buy_quantity_total, buy_executed_symbol  # catch with these names
        else :
            return 0, 0, None
        
    def place_sell_market_order(self, instrument_key, quantity):
        trading_symbol = get_instrument_sybmbol_by_key(instrument_key)       
         # Determine if the symbol is BankNifty or Nifty
        if "BANKNIFTY" in trading_symbol:
            lot_size = self.BN_Lot_Size
            max_order_quantity = self.BN_MAX_ORDER_QUANTITY
        elif "NIFTY" in trading_symbol:
            lot_size = self.NF_Lot_Size
            max_order_quantity = self.NF_MAX_ORDER_QUANTITY
        else:
            raise ValueError("Invalid trading symbol: must be either BankNifty or Nifty")

        new_quant = round(quantity / lot_size) * lot_size
        remaining_quantity = new_quant
        sell_count = 0
        executed_sell_price_total=0
        executed_sell_quantity_total=0
        while remaining_quantity > 0:
            sell_count += 1
            order_quantity = min(remaining_quantity, max_order_quantity)
            executed_price, executed_quantity, executed_symbol = self.sell_market_order(instrument_key, order_quantity)
            executed_sell_price_total += executed_price
            remaining_quantity -= order_quantity
            executed_sell_quantity_total += executed_quantity
            logging.info(f"Placed {order_quantity}-{order_quantity/lot_size} units. Remaining: {order_quantity}-{remaining_quantity/lot_size}")
        
        if executed_sell_quantity_total > 0:
            sell_average = executed_sell_price_total/sell_count
            sell_executed_symbol = executed_symbol
            return sell_average, executed_sell_quantity_total, sell_executed_symbol # catch with these names
        else :
            return 0, 0, None
        
    def place_sell_stop_loss_limit_order(self, instrument_key, quantity, stop_loss_price):
        trading_symbol = get_instrument_sybmbol_by_key(instrument_key)       
         # Determine if the symbol is BankNifty or Nifty
        if "BANKNIFTY" in trading_symbol:
            lot_size = self.BN_Lot_Size
            max_order_quantity = self.BN_MAX_ORDER_QUANTITY
        elif "NIFTY" in trading_symbol:
            lot_size = self.NF_Lot_Size
            max_order_quantity = self.NF_MAX_ORDER_QUANTITY
        else:
            raise ValueError("Invalid trading symbol: must be either BankNifty or Nifty")

        new_quant = round(quantity / lot_size) * lot_size
        remaining_quantity = new_quant
        sell_count = 0
        executed_sell_price_total=0
        executed_sell_quantity_total=0
        while remaining_quantity > 0:
            sell_count += 1
            order_quantity = min(remaining_quantity, max_order_quantity)
            executed_price, executed_quantity, executed_symbol = self.sell_stop_loss_limit_order(instrument_key, order_quantity, stop_loss_price)
            executed_sell_price_total += executed_price
            remaining_quantity -= order_quantity
            executed_sell_quantity_total += executed_quantity
            logging.info(f"Placed {order_quantity}-{order_quantity/lot_size} units. Remaining: {order_quantity}-{remaining_quantity/lot_size}")
        
        if executed_sell_quantity_total > 0:
            sell_average = executed_sell_price_total/sell_count
            sell_executed_symbol = executed_symbol
            return sell_average, executed_sell_quantity_total, sell_executed_symbol
         
   #-----for placing sliced order call these functinos END----------------




   #-----for placing single order call these functinos----------------
    
    def buy_market_order(self, instrument_key, quantity):
        payload = {
            "quantity": quantity,
            "product": "D",
            "validity": "DAY",
            "price": 0,
            "tag": "algoup",
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
            executed_price, executed_quantity, executed_symbol = self.get_order_data(order_id)
            logging.info(f"Buy order placed successfully at: {executed_price}")
            return executed_price, executed_quantity, executed_symbol
        else:
            logging.error("Failed to place buy order")
            logging.error(response.text)      
            
    def sell_market_order(self, instrument_key, quantity):
        payload = {
            "quantity": quantity,
            "product": "D",
            "validity": "DAY",
            "price": 0,
            "tag": "algoup",
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
            executed_price, executed_quantity, executed_symbol = self.get_order_data(order_id)
            logging.info(f"Sell order placed successfully at: {executed_price}")
            return executed_price, executed_quantity, executed_symbol
        else:
            logging.error("Failed to place buy order")
            logging.error(response.text) 
            
    def sell_stop_loss_limit_order(self, instrument_key, quantity, stop_loss_price):
        payload = {
            "quantity": quantity,
            "product": "D",
            "validity": "DAY",
            "price": stop_loss_price,
            "tag": "algoup",
            "instrument_token": instrument_key,
            "order_type": "SL",
            "transaction_type": "SELL",
            "disclosed_quantity": 0,
            "trigger_price": stop_loss_price + 0.50,
            "is_amo": False
        }
        data = json.dumps(payload)
        response = rq.post(self.uri, headers=self.headers, data=data)
        if response.status_code == 200 and response.json()['status'] == 'success':
            order_id = response.json()['data']['order_id']
            executed_price, executed_quantity, executed_symbol = self.get_order_data(order_id)
            # save these in a json for modify orders later
            
            order_data = {
                  order_id: {
                     "order_id": order_id,
                     "price": executed_price,
                     "quantity": executed_quantity,
                     "symbol": executed_symbol
                  }
            }
            filepath = f"stop_loss_orders_{sanitize_filename(str(instrument_key))}.json"
            self.filepath = filepath
            
            if os.path.exists(filepath):
                  with open(filepath, 'r') as f:
                     existing_data = json.load(f)
            else:
                  existing_data = {}
            
            existing_data.update(order_data)
            
            with open(filepath, 'w') as f:
                  json.dump(existing_data, f, indent=4)
            
                  logging.info(f"Stop-loss order placed successfully at: {executed_price}")
                  return executed_price, executed_quantity, executed_symbol
        
        else:
            logging.error("Failed to place stop-loss order")
            logging.error(response.text)
                     
    def modify_stop_loss_limit_order(self, order_id, price, quantity):
         payload = {
            "quantity": quantity,
            "validity": "DAY",
            "price": price,
            "order_id": order_id,
            "order_type": "SL",
            "disclosed_quantity": 0,
            "trigger_price": price + 0.50
         }
         data = json.dumps(payload)
         response = rq.put(self.modify_order_url, headers=self.headers, data=data)
         if response.status_code == 200 and response.json()['status'] == 'success':
            if hasattr(self, 'filepath') and self.filepath:
                  filepath = self.filepath
                  with open(filepath, 'r') as f:
                     existing_data = json.load(f)
                  
                  # Update the respective order details
                  if order_id in existing_data:
                     existing_data[order_id] = {
                        "order_id": order_id,
                        "price": price,
                        "quantity": quantity,
                     }
                     
                     with open(filepath, 'w') as f:
                        json.dump(existing_data, f, indent=4)
                     
                     logging.info("Order modified successfully")
                  else:
                     logging.error(f"Order ID {order_id} not found in the records")
            else:
                  logging.error("Filepath for orders not set")
         else:
            logging.error("Failed to modify order")
            logging.error(response.text)
            
   #------------------this function will get the order details----------------
   
    def get_order_data(self, order_id):
        params = {'order_id': order_id}
        try:
            response = rq.get(self.get_order_details_url, headers=self.headers, params=params)
            response.raise_for_status()
            if response.get('status') == 'success':
                data = response.json().get('data', {})

                executed_price = data.get('average_price')
                executed_quantity = data.get('quantity')
                executed_symbol = data.get('trading_symbol')

                if executed_price is None or executed_quantity is None or executed_symbol is None:
                    raise ValueError("Missing data in the API response")
                return executed_price, executed_quantity, executed_symbol

        except rq.exceptions.RequestException as e:
            print(f"HTTP error occurred: {e}")
        except ValueError as ve:
            print(f"Value error: {ve}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return None, None, None  # Return default values in case of error
    
    
    