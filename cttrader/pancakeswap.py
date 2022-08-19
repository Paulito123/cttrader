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
            version: int = 2,
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

        self.address = _str_to_addr(
            address or "0x0000000000000000000000000000000000000000"
        )
        self.private_key = (
                private_key
                or "0x0000000000000000000000000000000000000000000000000000000000000000"
        )

        self.version = version
        if self.version not in [2]:
            raise Exception(
                f"Invalid version '{self.version}', only 2 supported"
            )  # pragma: no cover

        # TODO: Write tests for slippage
        self.default_slippage = default_slippage
        self.use_estimate_gas = use_estimate_gas

        if web3:
            self.w3 = web3
        else:
            # Initialize web3. Extra provider for testing.
            if not provider:
                provider = os.environ["PROVIDER"]
            self.w3 = Web3(Web3.HTTPProvider(provider, request_kwargs={"timeout": 60}))

        # Cache netid to avoid extra RPC calls
        self.netid = int(self.w3.net.version)
        if self.netid in _netid_to_name:
            self.netname = _netid_to_name[self.netid]
        else:
            raise Exception(f"Unknown netid: {self.netid}")  # pragma: no cover
        logger.info(f"Using {self.w3} ('{self.netname}', netid: {self.netid})")

        self.last_nonce: Nonce = self.w3.eth.get_transaction_count(self.address)

        # This code automatically approves you for trading on the exchange.
        # max_approval is to allow the contract to exchange on your behalf.
        # max_approval_check checks that current approval is above a reasonable number
        # The program cannot check for max_approval each time because it decreases
        # with each trade.
        max_approval_hex = f"0x{64 * 'f'}"
        self.max_approval_int = int(max_approval_hex, 16)
        max_approval_check_hex = f"0x{15 * '0'}{49 * 'f'}"
        self.max_approval_check_int = int(max_approval_check_hex, 16)
