import asyncio
import json
import time
import requests
import os

from web3 import Web3
from websockets import connect
from multiprocessing.pool import ThreadPool
from config import Config
from typing import Union, Optional, List, Dict

from cttrader.util import (
    _str_to_addr
)
from cttrader.types import (
    AddressLike,
    ListenLoopModus
)


class ListenLoop:
    """
        A ListenLoop runs a specific program depending on its configured modus.
        The available modi are:
        - cancel_all: cancel all transactions that have been found as pending.
    """

    modus: ListenLoopModus
    address_list: Dict[Union[AddressLike, str, None], Union[str, None]] = {}

    w3: Web3
    ws_url: str

    def __init__(self,
                 modus: ListenLoopModus,
                 _address_list: Dict[Union[AddressLike, str, None], Union[str, None]],
                 provider: str = None,
                 web3: Web3 = None,
                 wss_url: str = None,
                 ) -> None:

        self.modus = modus
        self.listening = False
        self.wss_url = wss_url

        for addr in _address_list.keys():
            address = _str_to_addr(
                    addr
                    or "0x0000000000000000000000000000000000000000"
                )
            if address not in self.address_list.keys():
                pk = (
                        _address_list[addr]
                        or "0x0000000000000000000000000000000000000000000000000000000000000000"
                )
                self.address_list[address] = pk

        if web3:
            self.w3 = web3
        else:
            # Initialize web3. Extra provider for testing.
            if not provider:
                provider = os.environ["PROVIDER"]
            self.w3 = Web3(Web3.HTTPProvider(provider, request_kwargs={"timeout": 60}))

        self.loop = asyncio.get_event_loop()

    def evaluate(self, message):
        response = json.loads(message)
        tx = web3.eth.get_transaction(response['params']['result'])
        if tx['from'] in self.address_list.keys() and tx['value'] > 0:
            # Cancel a transaction by submitting an empty transaction with same nonce.
            # ctx = transact_base_currency(account,
            #                              key,
            #                              account,
            #                              0,
            #                              tx['gas'] + 1,
            #                              tx['gasPrice'] + 1,
            #                              tx['nonce'])
            print(f"tx={tx}")
            # print(f"ctx={ctx}")
        else:
            print(f'{tx}')

    def toggle_listen(self):
        self.listening = False if self.listening else True
        while self.listening:
            self.loop.run_until_complete(self.listen())
        return None

    async def listen(self) -> None:
        async with connect(ws_url) as ws:
            await ws.send(
                '{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}')
            subscription_response = await ws.recv()
            print(subscription_response)

            with ThreadPool() as pool:
                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=15)

                        # issue a task asynchronously
                        async_result = pool.apply_async(self.evaluate, args=(message,))
                    except Exception as ex:
                        print(f"[ERROR]:{ex}")
                        pass
        return None


if __name__ == "__main__":
    ws_url = Config.BSC_WSS_URL
    http_url = Config.BSC_HTTP_URL
    web3 = Web3(Web3.HTTPProvider(http_url))

    account = Config.BSC_ACCOUNT_KEY_1
    key = Config.BSC_ACCOUNT_ADDR_1
    account2 = Config.BSC_ACCOUNT_ADDR_2

    f = ListenLoop(ListenLoopModus.CANCEL_ALL,
                   {account: key},
                   None,
                   web3,
                   ws_url)

    print("start listening")
    f.toggle_listen()
    # print("sleepy time...")
    # time.sleep(30)
    # print("stop listening")
    # f.toggle_listen()
