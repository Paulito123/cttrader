from typing import Union
from eth_typing.evm import Address, ChecksumAddress
from enum import Enum


AddressLike = Union[Address, ChecksumAddress]


class ListenLoopModus(Enum):
    CANCEL_ALL = 1
