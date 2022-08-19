import os
import time
import logging
import functools
from typing import List, Any, Optional, Union, Tuple, Iterable

from web3 import Web3
from web3.contract import Contract, ContractFunction
from web3.exceptions import BadFunctionCallOutput, ContractLogicError
from web3.types import (
    TxParams,
    Wei,
    Nonce,
)
from eth_typing.evm import Address, ChecksumAddress
from hexbytes import HexBytes

from .types import AddressLike
from .token import ERC20Token
from .tokens import get_tokens
from .exceptions import InvalidToken, InsufficientBalance
from .util import (
    _str_to_addr,
    _addr_to_str,
    _validate_address,
    _load_contract,
    _load_contract_erc20,
    is_same_address,
)
from .decorators import supports, check_approval
from .constants import (
    _netid_to_name,
    _factory_contract_addresses_v1,
    _factory_contract_addresses_v2,
    _router_contract_addresses_v2,
    ETH_ADDRESS,
)

logger = logging.getLogger(__name__)


class Pancakeswap:
    """
        Wrapper around Pancakeswap contracts.
        """

    address: AddressLike
    version: int

    w3: Web3
    netid: int
    netname: str

    default_slippage: float
    use_estimate_gas: bool

    def __init__(
            self,
            address: Union[AddressLike, str, None],
            private_key: Optional[str],
            provider: str = None,
            web3: Web3 = None,
            version: int = 1,
            default_slippage: float = 0.01,
            use_estimate_gas: bool = True,
            factory_contract_addr: str = None,
            router_contract_addr: str = None,
    ) -> None:
        """
        :param address: The public address of the ETH wallet to use.
        :param private_key: The private key of the ETH wallet to use.
        :param provider: Can be optionally set to a Web3 provider URI. If none set, will fall back to the PROVIDER environment variable, or web3 if set.
        :param web3: Can be optionally set to a custom Web3 instance.
        :param version: Which version of the Uniswap contracts to use.
        :param default_slippage: Default slippage for a trade, as a float (0.01 is 1%). WARNING: slippage is untested.
        :param factory_contract_addr: Can be optionally set to override the address of the factory contract.
        :param router_contract_addr: Can be optionally set to override the address of the router contract (v2 only).
        """
        ...
