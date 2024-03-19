from Client import Client_Interface
import asyncio
import time
import argparse
import speedtest
from colorama import init, Fore

import config
from Account import Account

# colorama
init()

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
    account.balance = 120

    # Check account balance
    if int(account.balance) < config.MINIMUM_AMOUNT:
        print(Fore.RED + f'Insufficient balance ({account.balance})' + Fore.RESET)
    else:
        print(Fore.GREEN + f'Balance={account.balance}' + Fore.RESET)

        if execution_time < config.HIGH_SPEED:
            print(Fore.GREEN + f"Average execution time: {execution_time} seconds" + Fore.RESET)
        elif execution_time < config.MIDDLING_SPEED:
            print(Fore.YELLOW + f"Average execution time: {execution_time} seconds" + Fore.RESET)
        elif execution_time > config.MIDDLING_SPEED:
            print(Fore.RED + f"Average execution time: {execution_time} seconds" + Fore.RESET)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to fulfill ByBit listing conditions')
    parser.add_argument('--api', help='Public key (required)')
    parser.add_argument('--sec', help='Secret key (required)')
    parser.add_argument('--speed', action='store_true', help='Check internet speed')
    args = parser.parse_args()

    if args.speed:
        st = speedtest.Speedtest()
        download_speed = st.download() / 1024 / 1024  # в мегабитах в секунду
        upload_speed = st.upload() / 1024 / 1024  # в мегабитах в секунду

        print("Скорость загрузки:", download_speed, "Mbps")
        print("Скорость выгрузки:", upload_speed, "Mbps")

    if args.api and args.sec:
        print('api-key:', args.api)
        print('secret-key:', args.sec)

        asyncio.run(main(api=args.api, sec=args.sec))
    else:
        print('You need enter api-key and secret-key')
        