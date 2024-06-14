# import requests as rq


# with open('access_token.txt', 'r') as f:
#       access_token = f.read().strip()
# headers = {
#             "Accept": "application/json",
#             'Api-version': '2.0',
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {access_token}'
#         }

# order_id = '240612000891778'
# url = f"https://api.upstox.com/v2/order/details?order_id={order_id}"
# # url = f"https://api.upstox.com/v2/order/trades/get-trades-for-day"
# payload={}
# res = rq.get(url, headers=headers, data=payload)
# print(res.json())
