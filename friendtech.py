# This file periodically checks for a list of accounts on friend.tech api and sends a notification to the user if any of the accounts are found.

import requests
import json
import time
import threading
import telegram
from web3 import Web3
import asyncio
from private import private_key, telegram_bot_token, telegram_chat_id

amount_to_buy = 4
delay = 1


api_url = "https://prod-api.kosetto.com/search/users?username="
abi = """[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"trader","type":"address"},{"indexed":false,"internalType":"address","name":"subject","type":"address"},{"indexed":false,"internalType":"bool","name":"isBuy","type":"bool"},{"indexed":false,"internalType":"uint256","name":"shareAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"protocolEthAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"subjectEthAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"supply","type":"uint256"}],"name":"Trade","type":"event"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"buyShares","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getBuyPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getBuyPriceAfterFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"supply","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getSellPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getSellPriceAfterFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFeeDestination","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFeePercent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"sellShares","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_feeDestination","type":"address"}],"name":"setFeeDestination","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_feePercent","type":"uint256"}],"name":"setProtocolFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_feePercent","type":"uint256"}],"name":"setSubjectFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"sharesBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"sharesSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"subjectFeePercent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]"""
w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))

def check_for_user(user_pair):
    try:
        user = user_pair[0]
        print("Checking for user "+user)
        r = requests.get(api_url+user)
        if r.status_code == 200:
            data = json.loads(r.text)
            for i in data["users"]:
                
                if i["twitterUsername"] == user:
                    print("Found "+user+"!")
                    #asyncio.run(send_telegram_message(message="Found "+user+"!"))
                    for x in range(1,amount_to_buy):
                        result = buy(i["address"])
                        if result == True:
                            users_list[users_list.index(user_pair)] = (user_pair[0],1)
                        else:
                            break

    except Exception as e:
        print("Error checking for user "+user)
        print(str(e))
        pass

#Uses telegram bot to send a message to the user
async def send_telegram_message(message, bot_token = telegram_bot_token, chat_id = telegram_chat_id):
    try:
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=message)
        print("Message sent successfully.")
    except Exception as e:
        print("Error sending message:", str(e))

#Uses the web3 library to buy a share of the NFT
def buy(address, contract_address = "0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4", contract_abi = abi, private_key = private_key):
    try:
        w3.eth.default_account = w3.eth.account.privateKeyToAccount(private_key).address #w3.to_checksum_address(w3.eth.account.from_key(private_key).address)
        address = w3.toChecksumAddress(address)
        #contract_address = w3.to_checksum_address(contract_address)
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)

        shares = contract.functions.sharesSupply(address).call()
        if shares > 0:
            print("User already initialized the account")

            price = float(contract.functions.getBuyPriceAfterFee(address, 1).call()) / pow(10, 18)

            #checks if the user has enough funds to buy the share
            if w3.eth.get_balance(w3.eth.default_account) < price:
                print("You don't have enough funds to buy the share")
                asyncio.run(send_telegram_message(message="You don't have enough funds to buy the share"))
                return False
            
            nonce = w3.eth.get_transaction_count(w3.eth.default_account)
            tx = contract.functions.buyShares(address, 1).buildTransaction({
                'chainId': 8453,
                'gas': 100000,
                'gasPrice': w3.toWei('5', 'gwei'),
                'nonce': nonce,
                'value': price * pow(10, 18)
            })

            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            print("Transaction sent:", tx_hash.hex())
            asyncio.run(send_telegram_message(message="Transaction sent: https://basescan.org/tx/" + tx_hash.hex()))

            return True
        else:
            print("User didn't initialize the account")
            return False

    except Exception as e:
        print("Error buying share:", str(e))
        return False

#Reads the users from the users.txt file
def read_users():
    try:
        users_list = []
        with open("users.txt", "r") as f:
            for line in f.readlines():
                users_list.append((line.strip(),0))
        return users_list
    except Exception as e:
        print("Error reading users:", str(e))
        return []

#Main loop
if __name__ == "__main__":
    users_list = read_users()

    while True:
        threads = []
        for user in users_list:
            if user[1] == 0:
                x = threading.Thread(target=check_for_user, args=(user,))
                threads.append(x)
                x.start()
        time.sleep(delay)