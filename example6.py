import asyncio
import json
import requests
from web3 import Web3
from websockets import connect
from config import Config


ws_url = Config.BSC_WSS_URL
http_url = Config.BSC_HTTP_URL
web3 = Web3(Web3.HTTPProvider(http_url))

# Used if you want to monitor ETH transactions to a specific address
account = Config.BSC_ACCOUNT_KEY_1
key = Config.BSC_ACCOUNT_ADDR_1
account2 = Config.BSC_ACCOUNT_ADDR_2


async def get_event():
    async with connect(ws_url) as ws:
        await ws.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}')
        subscription_response = await ws.recv()
        # print(subscription_response)

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=15)
                response = json.loads(message)
                tx = web3.eth.get_transaction(response['params']['result'])
                # txHash = response['params']['result']
                print(tx)
                # Uncomment lines below if you want to monitor transactions to
                # a specific address
                # tx = web3.eth.get_transaction(txHash)
                # if tx.to == account:
                #     print("Pending transaction found with the following details:")
                #     print({
                #         "hash": txHash,
                #         "from": tx["from"],
                #         "value": web3.fromWei(tx["value"], 'ether')
                #     })
                pass
            except:
                print("[ERROR]")
                pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(get_event())
