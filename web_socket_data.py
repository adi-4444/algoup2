import asyncio
import json
import ssl
import upstox_client
import websockets
from google.protobuf.json_format import MessageToDict
import MarketDataFeed_pb2 as pb

def get_market_data_feed_authorize(api_version, configuration):
    """Get authorization for market data feed."""
    api_instance = upstox_client.WebsocketApi(upstox_client.ApiClient(configuration))
    api_response = api_instance.get_market_data_feed_authorize(api_version)
    return api_response

def decode_protobuf(buffer):
    """Decode protobuf message."""
    feed_response = pb.FeedResponse()
    feed_response.ParseFromString(buffer)
    return feed_response

def get_portfolio_stream_feed_authorize(api_version, configuration):
    api_instance = upstox_client.WebsocketApi(upstox_client.ApiClient(configuration))
    api_response = api_instance.get_portfolio_stream_feed_authorize(api_version)
    return api_response

async def websocket_handler(access_token, instrument_keys, on_connect, on_ticks, on_close, on_order_update):
    """Unified WebSocket handler for market data and order updates."""
    
    # Create default SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Configure OAuth2 access token for authorization
    configuration = upstox_client.Configuration()
    api_version = '2.0'
    configuration.access_token = access_token

    # Get market data feed authorization
    market_data_response = get_market_data_feed_authorize(api_version, configuration)
    portfolio_response = get_portfolio_stream_feed_authorize(api_version, configuration)

    async with websockets.connect(market_data_response.data.authorized_redirect_uri, ssl=ssl_context) as market_ws, \
               websockets.connect(portfolio_response.data.authorized_redirect_uri, ssl=ssl_context) as portfolio_ws:
        
        await on_connect()

        # Data to be sent over the WebSocket
        data = {
            "guid": "someguid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": instrument_keys
            }
        }

        # Convert data to binary and send over WebSocket
        binary_data = json.dumps(data).encode('utf-8')
        await market_ws.send(binary_data)

        async def receive_market_data():
            try:
                while True:
                    message = await market_ws.recv()
                    decoded_data = decode_protobuf(message)
                    data_dict = MessageToDict(decoded_data)
                    await on_ticks(data_dict)
            except websockets.exceptions.ConnectionClosed:
                await on_close()

        async def receive_order_updates():
            try:
                while True:
                    message = await portfolio_ws.recv()
                    await on_order_update(json.loads(message))
            except websockets.exceptions.ConnectionClosed:
                await on_close()

        await asyncio.gather(receive_market_data(), receive_order_updates())
