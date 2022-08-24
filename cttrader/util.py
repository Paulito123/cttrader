import os
import json
import functools
from typing import Union

from web3 import Web3
from web3.exceptions import NameNotFound
from web3.contract import Contract

from cttrader.types import AddressLike, Address


def _str_to_addr(s: Union[AddressLike, str]) -> Address:
    """Idempotent"""
    if isinstance(s, str):
        if s.startswith("0x"):
            return Address(bytes.fromhex(s[2:]))
        else:
            raise NameNotFound(f"Couldn't convert string '{s}' to AddressLike")
    else:
        return s


def _addr_to_str(a: AddressLike) -> str:
    if isinstance(a, bytes):
        # Address or ChecksumAddress
        addr: str = Web3.toChecksumAddress("0x" + bytes(a).hex())
        return addr
    elif isinstance(a, str) and a.startswith("0x"):
        addr = Web3.toChecksumAddress(a)
        return addr

    raise NameNotFound(a)


def is_same_address(a1: Union[AddressLike, str], a2: Union[AddressLike, str]) -> bool:
    return _str_to_addr(a1) == _str_to_addr(a2)


def _validate_address(a: AddressLike) -> None:
    assert _addr_to_str(a)


def _load_abi(name: str) -> str:
    path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/"
    with open(os.path.abspath(path + f"{name}.abi")) as f:
        abi: str = json.load(f)
    return abi


@functools.lru_cache()
def _load_contract(w3: Web3, abi_name: str, address: AddressLike) -> Contract:
    address = Web3.toChecksumAddress(address)
    return w3.eth.contract(address=address, abi=_load_abi(abi_name))


def _load_contract_erc20(w3: Web3, address: AddressLike) -> Contract:
    return _load_contract(w3, "erc20", address)


if __name__ == '__main__':
    print(1)
