import asyncio
import json
import requests
from web3 import Web3
from websockets import connect


# ws_url = 'wss://little-tiniest-snowflake.bsc.discover.quiknode.pro/6d0fe661d7ab2115aafcee849d39369fe9c85551/'
ws_url = 'wss://side-empty-ensemble.bsc-testnet.discover.quiknode.pro/4711d1023c738d1b9da7e781f6506b76045210b3/'
# http_url = 'https://little-tiniest-snowflake.bsc.discover.quiknode.pro/6d0fe661d7ab2115aafcee849d39369fe9c85551/'
http_url = 'https://side-empty-ensemble.bsc-testnet.discover.quiknode.pro/4711d1023c738d1b9da7e781f6506b76045210b3/'
web3 = Web3(Web3.HTTPProvider(http_url))

# Used if you want to monitor ETH transactions to a specific address
account = '<YOUR_PUBLIC_ADDRESS>'


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
