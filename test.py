import aiohttp
import asyncio
import time
import hashlib
import hmac
import json
import sys
import config

api_key = '9QKQ4LJJCm79DLr13t'
secret_key = 'QqvVvQKoKnkOY3mbj5JYI2n9tN0s0rONbbGM'
recv_window = str(5000)
url = "https://api.bybit.com"

async def HTTP_Request(endPoint, method, payload):
    async with aiohttp.ClientSession() as session:
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = genSignature(payload, time_stamp)
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': "application/json"
        }
        if method == "POST":
            async with session.request(method, url + endPoint, headers=headers, data=payload) as response:
                response_text = await response.text()
                print(response_text)
                return response_text
                #print(Info + " Elapsed Time : " + str(response.elapsed.total_seconds()))
        else:
            async with session.request(method, url + endPoint + "?" + payload, headers=headers) as response:
                response_text = await response.text()
                return response_text

def genSignature(payload, time_stamp):
    param_str = str(time_stamp) + api_key + recv_window + payload
    hash_func = hmac.new(secret_key.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    signature = hash_func.hexdigest()
    return signature

async def main():

    endpoint = "/v5/order/create-batch"
    method = "POST"
    params = 'accountType=UNIFIED'

    price = "30000"
    symbol = "BTCUSDT"
    qty = "1"

    # Up and low orders price
    Up_limit = (float(price) * (1 + (config.ORDERS_LIMIT / 100)))
    Low_limit = (float(price) * (1 - (config.TP_SL_trigger_LIMIT / 100)))

    # Depending on the specified percentage, orders are created, as well as stop losses and take profits for 100% order execution
    # UP order
    TP_trigger_cost_UP = (Up_limit * (1 + (config.TP_SL_trigger_LIMIT / 100)))
    SL_trigger_cost_UP = (Up_limit * (1 - (config.TP_SL_trigger_LIMIT / 100)))

    TP_cost_UP =  (TP_trigger_cost_UP * (1 + (config.TP_SL_LIMIT / 100)))
    SL_cost_UP = (SL_trigger_cost_UP * (1 - (config.TP_SL_LIMIT / 100)))

    # Low order
    TP_trigger_cost_low = (Low_limit * (1 + (config.TP_SL_trigger_LIMIT / 100)))
    SL_trigger_cost_low = (Low_limit * (1 - (config.TP_SL_trigger_LIMIT / 100)))

    TP_cost_low =  (TP_trigger_cost_low * (1 + (config.TP_SL_LIMIT / 100)))
    SL_cost_low = (SL_trigger_cost_low * (1 - (config.TP_SL_LIMIT / 100)))
    

    content = {
                "category": "spot",
                "request": [
                    {
                        "orderLinkId": "main",
                        "symbol": symbol,
                        "side": "Buy",
                        "orderType": "Limit",
                        "qty":qty,
                        "price":  str(Up_limit),
                        "timeInForce": "PostOnly",
                        "takeProfit": str(TP_trigger_cost_UP),
                        "stopLoss": str(SL_trigger_cost_UP),
                        "tpLimitPrice": str(TP_cost_UP),
                        "slLimitPrice": str(SL_cost_UP),
                        "tpOrderType": "Limit",
                        "slOrderType": "Limit"
                    },
                    {
                        "orderLinkId": "main",
                        "symbol": symbol,
                        "side": "Buy",
                        "orderType": "Limit",
                        "qty":qty,
                        "price":  str(Low_limit),
                        "timeInForce": "PostOnly",
                        "takeProfit": str(TP_trigger_cost_low),
                        "stopLoss": str(SL_trigger_cost_low),
                        "tpLimitPrice": str(TP_cost_low),
                        "slLimitPrice": str(SL_cost_low),
                        "tpOrderType": "Limit",
                        "slOrderType": "Limit"
                    }
                ]
            }
    
    json_content = json.dumps(content)

    start_time = time.time()
    
    result = await HTTP_Request(endpoint, method,json_content)

    end_time = time.time()
    execution_time = end_time - start_time

    print(execution_time)

    json_data = json.loads(result)

    print(f"result={result}")

    sys.stdout.write('\rValue: {}'.format(f'{json_data["result"]}'))
    sys.stdout.flush()

asyncio.run(main())