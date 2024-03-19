import aiohttp
import time
import hashlib
import hmac
import json
from loguru import logger


class Client():

    def __init__(self, api_key: str, secret_key: str) -> None:
        self.api_key = api_key
        self.secret_key = secret_key
        self.recv_window = str(5000)
        self.url = "https://api.bybit.com"

    async def HTTP_Request(self, endPoint, method, payload, Info):
        async with aiohttp.ClientSession() as session:
            time_stamp = str(int(time.time() * 10 ** 3))
            signature = self.genSignature(payload, time_stamp)
            headers = {
                'X-BAPI-API-KEY': self.api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-SIGN-TYPE': '2',
                'X-BAPI-TIMESTAMP': time_stamp,
                'X-BAPI-RECV-WINDOW': self.recv_window,
                'Content-Type': 'application/json'
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
            response = await self.client.HTTP_Request(endpoint, method, params, "UnFilled")

            json_data = json.loads(response)

            if len(json_data["result"]["list"]) > 0:
                total_wallet_balance = json_data["result"]["list"][0]["totalWalletBalance"]
                return total_wallet_balance
            else:
                logger.error(f'Error when processing a balance request:\nresponse={response}')

        except Exception as e:

            logger.error(f'Error when sending a balance request:\n{e}')
        
            return False