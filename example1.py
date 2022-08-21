from typing import List

from web3 import Web3

from cttrader.uniswap import Uniswap
from cttrader.pancakeswap import Pancakeswap
from cttrader.types import AddressLike

eth = Web3.toChecksumAddress("0x0000000000000000000000000000000000000000")
# weth = Web3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
weth = Web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c") # wbnb
# usdt = Web3.toChecksumAddress("0xdac17f958d2ee523a2206206994597c13d831ec7")
usdt = Web3.toChecksumAddress("0x55d398326f99059ff775485246999027b3197955")
# agix = Web3.toChecksumAddress("0x5B7533812759B45C2B44C19e320ba2cD2681b542")
agix = Web3.toChecksumAddress("0xd21d29B38374528675C34936bf7d5Dd693D2a577")
tokenname = "PRQ"

address = None  # or None if you're not going to make transactions
private_key = None  # or None if you're not going to make transactions
version = 2  # specify which version of Uniswap to use
provider = "https://mainnet.infura.io/v3/3b2863eb398844cca2ac969710a21c3e"  # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)

provider = "https://little-tiniest-snowflake.bsc.discover.quiknode.pro/6d0fe661d7ab2115aafcee849d39369fe9c85551/"
pancake = Pancakeswap(address=address, private_key=private_key, version=version, provider=provider)



def _perc(f: float) -> str:
    return f"{round(f * 100, 3)}%"


def usdt_to_agix_v2():
    """
    Checks impact for a pool with very little liquidity.

    This particular route caused a $14k loss for one user: https://github.com/uniswap-python/uniswap-python/discussions/198
    """
    # uniswap = Uniswap(address=None, private_key=None, version=2)

    route: List[AddressLike] = [usdt, weth, agix]

    # Compare the results with the output of:
    # https://app.uniswap.org/#/swap?use=v2&inputCurrency=0xdac17f958d2ee523a2206206994597c13d831ec7&outputCurrency=0x5B7533812759B45C2B44C19e320ba2cD2681b542
    qty = 100 * 10 ** 8

    # price = uniswap.get_price_input(usdt, agix, qty, route=route) / 10 ** 18
    # print(price)

    impact = pancake.estimate_price_impact(usdt, agix, qty, route=route)
    # NOTE: Not sure why this differs from the quote in the UI?
    #       Getting -27% in the UI for 10 USDT, but this returns >95%
    #       The slippage for v3 (in example below) returns correct results.
    print(f"Impact for buying {tokenname} on v{version} with {qty / 10 ** 8} USDT:  {_perc(impact)}")

    qty = 1000 * 10 ** 8
    impact = pancake.estimate_price_impact(usdt, agix, qty, route=route)
    print(f"Impact for buying {tokenname} on v{version} with {qty / 10 ** 8} USDT:  {_perc(impact)}")


def eth_to_agix_v3():
    """Checks price impact for a pool with liquidity."""
    # uniswap = Uniswap(address=None, private_key=None, version=3)

    # Compare the results with the output of:
    # https://app.uniswap.org/#/swap?use=v3&inputCurrency=ETH&outputCurrency=0x5B7533812759B45C2B44C19e320ba2cD2681b542
    qty = 1 * 10 ** 16
    impact = pancake.estimate_price_impact(eth, agix, qty, fee=10000)
    print(f"Impact for buying {tokenname} on v{version} with {qty / 10**18} ETH:  {_perc(impact)}")

    # qty = 1 * 10 ** 18
    # impact = pancake.estimate_price_impact(eth, agix, qty, fee=10000)
    # print(f"Impact for buying {tokenname} on v{version} with {qty / 10**18} ETH:  {_perc(impact)}")


if __name__ == "__main__":
    # usdt_to_agix_v2()
    eth_to_agix_v3()
