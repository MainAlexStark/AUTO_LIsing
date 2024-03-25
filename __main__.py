from Client import Client_Interface
import asyncio
import time
import argparse
import speedtest
from termcolor import colored

from Output import print_execution_time

import config
from Account import Account

async def main(api, sec):

    account = Account(api=api, sec=sec)
    
    # Connection to Client_Interface   
    client = Client_Interface(api_key=account.api_key, secret_key=account.secret_key)


    # Get balance and measure the request execution time
    start_time = time.time()
    account.balance = await client.get_balance()
    end_time = time.time()
    execution_time = end_time - start_time

    # TEMP
    #account.balance = 120

    # Check account balance
    print(colored(f'Total wallet balance ({account.balance})', 'green'))


    print_execution_time(execution_time)


    # Get coin balance and measure the request execution time
    coin = config.BASE_COIN

    start_time = time.time()
    account.coin_balances[coin] = await client.get_coin_balance(coin)
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Check and print account balance
    if float(account.coin_balances[coin]) < config.MINIMUM_AMOUNT:
        print(colored(f'Insufficient coin balance ({account.coin_balances[coin]})', 'red'))
    else:
        print(colored(f'Coin balance ({account.coin_balances[coin]}) (UNIFIED)', 'green'))

        print_execution_time(execution_time)


        # Get coin cost
        symbol = config.WORK_COIN + config.BASE_COIN

        start_time = time.time()
        coin_cost = await client.get_coin_price(symbol)
        end_time = time.time()
        execution_time = end_time - start_time

        print(colored(f'{symbol}={coin_cost}','blue'))

        print_execution_time(execution_time)

        # start_time = time.time()
        # order_result = await client.place_order(symbol=symbol, price=coin_cost, qty=config.QTY)
        # end_time = time.time()
        # execution_time = end_time - start_time

        # if order_result["retExtInfo"]['list'][0]['code'] == '0' and order_result["retExtInfo"]['list'][0]['code'] == '0':
        #     print(colored('order executed','green'))
        # else:
        #     print(colored(f'Order not executed, response={order_result}','red'))
        # print_execution_time(execution_time)


        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to fulfill ByBit listing conditions')
    parser.add_argument('--api', help='Public key (required)')
    parser.add_argument('--sec', help='Secret key (required)')
    parser.add_argument('--coin', help='Work coin (required)')
    parser.add_argument('--speed', action='store_true', help='Check internet speed')
    args = parser.parse_args()

    if args.speed:
        st = speedtest.Speedtest()
        download_speed = st.download() / 1024 / 1024  # в мегабитах в секунду
        upload_speed = st.upload() / 1024 / 1024  # в мегабитах в секунду

        print("Скорость загрузки:", download_speed, "Mbps")
        print("Скорость выгрузки:", upload_speed, "Mbps")

    if args.api and args.sec and args.coin:
        print('api-key:', args.api)
        print('secret-key:', args.sec)
        print('coin:', args.coin)

        config.WORK_COIN = args.coin

        asyncio.run(main(api=args.api, sec=args.sec))
    else:
        print('You need enter api-key and secret-key')
        