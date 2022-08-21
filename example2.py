import asyncio
import json
import requests
from web3 import Web3
from websockets import connect
from multiprocessing.pool import ThreadPool
from config import Config


ws_url = Config.BSC_WSS_URL
http_url = Config.BSC_HTTP_URL
web3 = Web3(Web3.HTTPProvider(http_url))

# Used if you want to monitor ETH transactions to a specific address
account = Config.BSC_ACCOUNT_KEY_1
key = Config.BSC_ACCOUNT_ADDR_1
account2 = Config.BSC_ACCOUNT_ADDR_2


def transact_base_currency(from_addr,
                           from_key,
                           to_addr,
                           gwei_amt,
                           gas,
                           gas_price=0,
                           nonce=None):
    try:
        # Get the nonce.  Prevents one from sending the transaction twice
        nonce = nonce if nonce else web3.eth.getTransactionCount(from_addr)
        gas_price = gas_price if gas_price > 0 else web3.eth.gas_price
        # Build a transaction in a dictionary
        tx = {
            'nonce': nonce,
            'to': to_addr,
            'value': gwei_amt,
            'gas': gas,
            'gasPrice': gas_price
        }

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, from_key)

        # Send transaction
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        output = web3.toHex(tx_hash)
    except Exception as ex:
        print(ex)
        output = None

    # Return transaction hash
    return output


def evaluate(message):
    response = json.loads(message)
    tx = web3.eth.get_transaction(response['params']['result'])
    if tx['from'] == account and tx['value'] > 0:
        # Cancel a transaction by submitting an empty transaction with same nonce.
        ctx = transact_base_currency(account,
                               key,
                               account2,
                               0,
                               tx['gas'],
                               tx['gasPrice']*2,
                               tx['nonce'])
        print(f"tx={tx}")
        print(f"ctx={ctx}")

    # else:
    #     print('.')


async def get_event():
    async with connect(ws_url) as ws:
        await ws.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}')
        subscription_response = await ws.recv()
        print(subscription_response)

        with ThreadPool() as pool:
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=15)

                    # issue a task asynchronously
                    async_result = pool.apply_async(evaluate, args=(message,))

                    # wait for the task to complete
                    # async_result.wait()

                    # txHash = response['params']['result']
                    # print(tx)
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
