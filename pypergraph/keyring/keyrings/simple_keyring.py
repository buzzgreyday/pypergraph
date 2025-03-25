from typing import List, Dict, Any, Union

from pydantic import BaseModel, Field, model_serializer
from typing_extensions import Self

from pypergraph.core.constants import NetworkId
from pypergraph.keyring.keyrings.registry import KeyringRegistry

from ..accounts.eth_account import EthAccount
from ..accounts.dag_account import DagAccount

class SimpleKeyring(BaseModel):

    account: Union[DagAccount, EthAccount] = Field(default=None) #IKeyringAccount;
    network: str = Field(default=NetworkId.Constellation.value)#KeyringNetwork

    # Serialize all accounts
    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        return {
            "network": self.network,
            "accounts": [self.account.serialize(True)]
        }

    def create_for_network(self, network, private_key: str) -> Self:
        inst = SimpleKeyring()
        inst.network = network
        registry = KeyringRegistry()
        account = registry.create_account(network)
        inst.account = account.create(private_key)
        return inst


    def get_state(self):
        return {
          "network": self.network,
          "account": self.account.serialize(False)
        }

    def deserialize(self, network: str, accounts: list):
        self.network = network
        registry = KeyringRegistry()
        account = registry.create_account(network)
        self.account = account.deserialize(**accounts[0])

    def add_account_at(self, index: int):
        raise NotImplementedError("SimpleKeyring :: Accounts can't be added to SimpleKeyrings.")

    def get_accounts(self) -> List[Union[DagAccount, EthAccount]]:
        return [self.account]

    def get_account_by_address(self, address: str):
        return self.account if address == self.account.get_address() else None

    def remove_account(self, account):
        raise NotImplementedError("SimpleKeyring :: Removal of SimpleKeyring accounts isn't supported.")