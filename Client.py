import aiohttp
import time
import hashlib
import hmac
import json
from loguru import logger
from typing import overload
import config


class Client():

    def __init__(self, api_key: str, secret_key: str) -> None:
        self.api_key = api_key
        self.secret_key = secret_key
        self.recv_window = str(5000)
        self.url = "https://api.bybit.com"

    async def HTTP_Request(self, endPoint, method, payload):
        async with aiohttp.ClientSession() as session:
            time_stamp = str(int(time.time() * 10 ** 3))
            signature = self.genSignature(payload, time_stamp)
            headers = {
                'X-BAPI-API-KEY': self.api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-SIGN-TYPE': '2',
                'X-BAPI-TIMESTAMP': time_stamp,
                'X-BAPI-RECV-WINDOW': self.recv_window,
                'Content-Type': "application/json"
            }
            if method == "POST":
                async with session.request(method, self.url + endPoint, headers=headers, data=payload) as response:
                    response_text = await response.text()
                    return response_text  # Возвращаем response_text
            else:
                async with session.request(method, self.url + endPoint + "?" + payload, headers=headers) as response:
                    response_text = await response.text()
                    return response_text  # Возвращаем response_text

    def genSignature(self, payload, time_stamp):
        param_str = str(time_stamp) + self.api_key + self.recv_window + payload
        hash_func = hmac.new(self.secret_key.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash_func.hexdigest()
        return signature
    


class Client_Interface():
    def __init__(self, api_key: str, secret_key: str) -> None:
        self.api_key = api_key
        self.api_keysecret_key = secret_key

        self.client = Client(api_key=api_key, secret_key=secret_key)

    async def get_balance(self):
        
        endpoint = "/v5/account/wallet-balance"
        method = "GET"
        params = 'accountType=UNIFIED&coin=USDT'

        try:

            # Тут присваиваем результат вызова HTTP_Request переменной response_text
            response = await self.client.HTTP_Request(endpoint, method, params)

            json_data = json.loads(response)

            if json_data['result']:
                total_wallet_balance = json_data["result"]["list"][0]["totalWalletBalance"]
                return total_wallet_balance
            else:
                logger.error(f'Error when processing a balance request:\nresponse={response}')
                return False

        except Exception as e:

            logger.error(f'Error when sending a balance request:\n{e}')
        
            return False

    async def get_coin_balance(self, coin: str):
        
        endpoint = "/v5/asset/transfer/query-account-coin-balance"
        method = "GET"
        params = f'accountType=UNIFIED&coin={coin}&toAccountType=FUND&withLtvTransferSafeAmount=1'

        try:

            # Тут присваиваем результат вызова HTTP_Request переменной response_text
            response = await self.client.HTTP_Request(endpoint, method, params)

            json_data = json.loads(response)

            if json_data['result']:
                coin_balance = json_data["result"]["balance"]['walletBalance']
                return coin_balance
            else:
                logger.error(f'Error when processing a coin balance request:\nresponse={response}')
                return False

        except Exception as e:

            logger.error(f'Error when sending a coin balance request:\n{e}')
        
            return False
        


    async def get_coin_price(self, coin: str):
        
        endpoint = "/v5/market/tickers"
        method = "GET"
        params = f'category=spot&symbol={coin}'

        try:

            # Тут присваиваем результат вызова HTTP_Request переменной response_text
            response = await self.client.HTTP_Request(endpoint, method, params)

            json_data = json.loads(response)

            if json_data['result']:
                coin_price = json_data["result"]["list"][0]["lastPrice"]
                return coin_price
            else:
                logger.error(f'Error when processing a coin price request:\nresponse={response}')
                return False

        except Exception as e:

            logger.error(f'Error when sending a coin price request:\n{e}')
        
            return False
        
    async def place_order(self, symbol: str, price: str, qty: str):
        endpoint = "/v5/order/create-batch"
        method = "POST"

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
        
        print(f'\nsymbol= {symbol}')
        print(f'price= {price}')
        print(f'qty= {qty} {config.BASE_COIN}\n')

        print(f'Up_limit= {round(Up_limit,2)}')
        print(f'TP_trigger_cost_UP= {round(TP_trigger_cost_UP,2)}\tTP_cost_UP= {round(TP_cost_UP,2)}')
        print(f'SL_trigger_cost_UP= {round(SL_trigger_cost_UP,2)}\tSL_cost_UP= {round(SL_cost_UP,2)}\n')

        print(f'Low_limit= {round(Low_limit,2)}')
        print(f'TP_trigger_cost_low= {round(TP_trigger_cost_low,2)}\tTP_cost_low= {round(TP_cost_low,2)}')
        print(f'SL_trigger_cost_low= {round(SL_trigger_cost_low,2)}\tSL_cost_low= {round(SL_cost_low,2)}\n')

        content = {
                    "category": "spot",
                    "request": [
                        {
                            "orderLinkId": "main",
                            "symbol": symbol,
                            "side": "Buy",
                            "orderType": "Limit",
                            "marketUnit":"quoteCoin",
                            "qty":qty,
                            "triggerPrice": str(round(Up_limit,2)),
                            "price":  str(round(Up_limit,2)),
                            "timeInForce": "PostOnly",
                            "takeProfit": str(round(TP_trigger_cost_UP,2)),
                            "stopLoss": str(round(SL_trigger_cost_UP,2)),
                            "tpLimitPrice": str(round(TP_cost_UP,2)),
                            "slLimitPrice": str(round(SL_cost_UP,2)),
                            "tpOrderType": "Limit",
                            "slOrderType": "Limit"
                        },
                        {
                            "orderLinkId": "main",
                            "symbol": symbol,
                            "side": "Buy",
                            "orderType": "Limit",
                            "marketUnit":"quoteCoin",
                            "qty":qty,
                            "triggerPrice": str(round(Low_limit,2)),
                            "price":  str(round(Low_limit,2)),
                            "timeInForce": "PostOnly",
                            "takeProfit": str(round(TP_trigger_cost_low,2)),
                            "stopLoss": str(round(SL_trigger_cost_low,2)),
                            "tpLimitPrice": str(round(TP_cost_low,2)),
                            "slLimitPrice": str(round(SL_cost_low,2)),
                            "tpOrderType": "Limit",
                            "slOrderType": "Limit"
                        }
                    ]
                }
        
        json_content = json.dumps(content)

        try:

            # Тут присваиваем результат вызова HTTP_Request переменной response_text
            response = await self.client.HTTP_Request(endpoint, method,json_content)

            json_data = json.loads(response)

            if json_data['result']:
                result = json_data
                return result
            else:
                logger.error(f'Error when processing a place orders request:\nresponse={response}')
                return False

        except Exception as e:

            logger.error(f'Error when processing a place orders request:\n{e}\nresponse={response}')
        
            return False