# accounts.ecdsa_accounts
from eth_account import Account
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from eth_account.messages import encode_defunct


class EcdsaAccount:
    def __init__(self):
        self.tokens: Optional[List[str]] = None
        self.wallet = None  # Placeholder for Wallet instance
        self.assets: Optional[List[Any]] = None
        self.bip44_index: Optional[int] = None
        self.decimals = 18 # Should be set dynamically
        self.supported_assets = [KeyringAssetType.ETH.value]
        self.network = KeyringNetwork.Ethereum.value
        self.has_token_support = False
        self._provider = None
        self._label = None

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        message = encode_defunct(text=msg)
        recovered_address = Account.recover_message(message, signature=signature)
        return recovered_address.lower() == says_address.lower()

    def get_decimals(self) -> int:
        return self.decimals

    def get_label(self) -> str:
        return self._label

    def create(self, private_key: Optional[str]):
        if private_key:
            self.wallet = Account.from_key(bytes.fromhex(private_key))
        else:
            self.wallet = Account.create()
        return self

    def save_token_info(self, address: str):
        pass

    def get_web3_provider(self):
        return self._provider

    def set_web3_provider(self, provider):
        self._provider = provider

    def get_tokens(self) -> Optional[List[str]]:
        return self.tokens.copy() if self.tokens else None

    def set_tokens(self, tokens: List[str]):
        if tokens:
            self.tokens = tokens.copy()

    def get_bip44_index(self) -> Optional[int]:
        return self.bip44_index

    def get_state(self) -> Dict[str, Any]:
        result = {
            "address": self.get_address(),
            "supportedAssets": self.supported_assets,
        }
        if self._label:
            result["label"] = self._label
        if self.tokens:
            result["tokens"] = self.tokens
        return result

    def get_network(self):
        return self.network

    def serialize(self, include_private_key: bool = True) -> Dict[str, Any]:
        result = {}
        if include_private_key:
            result["privateKey"] = self.get_private_key()
        if self._label:
            result["label"] = self._label
        if self.tokens:
            result["tokens"] = self.tokens.copy()
        if self.bip44_index is not None:
            result["bip44Index"] = self.bip44_index
        return result

    def deserialize(self, data: Dict[str, Any]):
        private_key = data.get("privateKey")
        public_key = data.get("publicKey")
        tokens = data.get("tokens")
        bip44_index = data.get("bip44Index")
        label = data.get("label")

        if private_key:
            self.wallet = Account.from_key(private_key)
            #self.wallet = "THIS_IS_NOT_A_PRIVATE_KEY_WALLET"
        else:
            raise NotImplementedError("EcdsaAccount :: Wallet instance from public key isn't supported.")
            # TODO: This doesn't work since the library doens't seem to have any equivalent
            #self.wallet = Wallet.from_public_key(bytes.fromhex(public_key))

        self._label = label
        self.bip44_index = bip44_index
        self.tokens = tokens or self.tokens
        return self

    # def sign_message(self, msg: str) -> str:
    #     private_key = self.get_private_key_buffer()
    #     msg_hash = eth_util.hash_personal_message(msg.encode())
    #
    #     v, r, s = eth_util.ecsign(msg_hash, private_key)
    #
    #     if not eth_util.is_valid_signature(v, r, s):
    #         raise ValueError("Sign-Verify failed")
    #
    #     return eth_util.strip_hex_prefix(eth_util.to_rpc_sig(v, r, s))

    # def recover_signed_msg_public_key(self, msg: str, signature: str) -> str:
    #     msg_hash = eth_util.hash_personal_message(msg.encode())
    #     signature_params = eth_util.from_rpc_sig("0x" + signature)
    #     public_key_buffer = eth_util.ecrecover(
    #         msg_hash, signature_params.v, signature_params.r, signature_params.s
    #     )
    #     return public_key_buffer.hex()

    def get_address(self) -> str:
        return self.wallet.get_checksum_address_string()

    def get_public_key(self) -> str:
        return self.wallet.get_public_key().hex()

    def get_private_key(self) -> str:
        return self.wallet.get_private_key().hex()

    def get_private_key_buffer(self):
        return self.wallet.get_private_key()

# accounts.dag_account

import base58
import hashlib
from typing import List
from ecdsa import VerifyingKey, SECP256k1


class DagAccount(EcdsaAccount):
    def __init__(self):
        super().__init__()
        self.decimals = 8
        self.network = "Constellation"  # Equivalent to `KeyringNetwork.Constellation`
        self.has_token_support = False
        self.supported_assets = ["DAG"]  # Equivalent to `KeyringAssetType.DAG`
        self.tokens = None  # Placeholder for default assets

    def sign_transaction(self, tx):
        # Implement transaction signing logic here if needed
        pass

    def validate_address(self, address: str) -> bool:
        if not address:
            return False

        valid_len = len(address) == 40
        valid_prefix = address.startswith("DAG")
        valid_parity = address[3].isdigit() and 0 <= int(address[3]) < 10
        base58_part = address[4:]
        valid_base58 = (
            len(base58_part) == 36 and base58_part == base58.b58encode(base58.b58decode(base58_part)).decode()
        )

        return valid_len and valid_prefix and valid_parity and valid_base58

    def get_address(self) -> str:
        return self.get_address_from_public_key(self.get_public_key())

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        public_key = self.recover_signed_msg_public_key(msg, signature)
        actual_address = self.get_address_from_public_key(public_key)
        return says_address == actual_address

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def get_address_from_public_key(self, public_key_hex: str) -> str:
        if len(public_key_hex) == 128:
            public_key_hex = "04" + public_key_hex

        pkcs_prefix = "3056301006072a8648ce3d020106052b8104000a034200"
        public_key_hex = pkcs_prefix + public_key_hex

        sha256_str = self.sha256(bytes.fromhex(public_key_hex))
        bytes_hash = bytes.fromhex(sha256_str)
        base58_encoded = base58.b58encode(bytes_hash).decode()

        end = base58_encoded[-36:]
        sum_digits = sum(int(char) for char in end if char.isdigit())
        par = sum_digits % 9

        return f"DAG{par}{end}"


# kcs
import asyncio
from enum import Enum

from bip32utils import BIP32Key

from pypergraph.dag_keystore import Bip32

class KeyringWalletType(Enum):
  MultiChainWallet = 'MCW'
  CrossChainWallet = 'CCW'
  MultiAccountWallet = 'MAW'  #Single Chain, Multiple seed accounts, MSW
  SingleAccountWallet = 'SAW'  #Single Chain, Single Key account, SKW
  MultiKeyWallet = 'MKW'      #Single Chain, Multiple Key accounts, MKW
  LedgerAccountWallet = "LAW"
  BitfiAccountWallet  = "BAW"

class KeyringAssetType(Enum):
  DAG = 'DAG'
  ETH = 'ETH'
  ERC20 = 'ERC20'


class KeyringNetwork(Enum):
  Constellation = 'Constellation'
  Ethereum = 'Ethereum'

# rings.hd_keyrings

class COIN:
    DAG = 1137
    ETH = 60

BIP_44_PATHS = {
    "CONSTELLATION_PATH": f"m/44'/{COIN.DAG}'/0'/0",
    "ETH_WALLET_PATH": f"m/44'/{COIN.ETH}'/0'/0",
    "ETH_LEDGER_PATH": "m/44'/60'",
}


# NOTE: Ring determines the secret implementation: seed or privateKey
# Hd Ring creates accounts based on Hierarchical Deterministics
class HdKeyring:

    accounts = [] # type IKeyringAccount[] interface
    hd_path: str = None
    mnemonic: str = None
    extended_key: str = None
    # TODO: find a suitable library
    root_key = None # EthereumHDKey;
    network: KeyringNetwork = None # Could be either or

    # Read-only wallet
    @staticmethod
    def createFromExtendedKey(extended_key: str, network: KeyringNetwork, number_of_accounts: int):
        inst = HdKeyring()
        inst.extendedKey = extended_key
        inst._init_from_extended_key(extended_key)
        inst.deserialize( { "network": network, "accounts": inst.create_accounts(number_of_accounts) })
        return inst

    @staticmethod
    def create(mnemonic: str, hdPath: str, network: KeyringNetwork, number_of_accounts: int):
        inst = HdKeyring()
        inst.mnemonic = mnemonic
        inst.hdPath = hdPath
        inst._init_from_mnemonic(mnemonic)
        inst.deserialize( { "network": network, "accounts": inst.create_accounts(number_of_accounts) })
        return inst

    def getNetwork(self):
        return self.network

    def get_hd_path(self):
        return self.hd_path

    def get_extended_public_key(self):
        if self.mnemonic:
            # TODO: needs a suitable library (needs testing)
            return self.root_key.ExtendedKey().hex()
            # return self.root_key.publicExtendedKey().toString('hex') # This will vary depending on the library

        return self.extended_key

    # Serialize all accounts
    def serialize(self):
        return { "network": self.network, "accounts": [acc.serialize(False) for acc in self.accounts] } # this.accounts.map(a => a.serialize(false))


    def deserialize(self, data: dict):
        if data:
            self.network = data.get("network")
            self.accounts = []
            for d in data.get("accounts"):
                account = self.add_account_at(d.get("bip44_index"))
                # TODO: Add ecdsa account and token support
                account.set_tokens(d.get("tokens"))
                self.accounts.append(account)

    def create_accounts(self, number_of_accounts=0):
        """
        When adding an account (after accounts have been removed), it will add back the ones removed first.

        Args:
            number_of_accounts (int): The number of accounts to create.

        Returns:
            list[dict]: A list of dictionaries representing the accounts.
        """
        accounts = []
        for i in range(number_of_accounts):
            accounts.append({"bip44_index": i})

        return accounts

    def remove_last_added_account(self):
        self.accounts.pop()

    def add_account_at(self, index: int):
        index = index if index >= 0 else len(self.accounts)

        print(index)
        try:
            if self.accounts[index]:
                ValueError('HdKeyring :: Trying to add an account to an index already populated')
        except IndexError:
            pass

        # TODO: This should be fitted to library
        #account = IKeyringAccount;
        if self.mnemonic:
            private_key = self.root_key.PrivateKey()
            # Create account
            #account = {"privateKey": private_key, "bip44Index": index}
            #print(self.network.value, type(KeyringNetwork.Constellation.value))
            #if self.network.value == KeyringNetwork.Constellation.value:
            #    account = DagAccount().deserialize({ "privateKey": private_key, "bip44Index": index })
            #elif self.network.value == KeyringNetwork.Ethereum.value:
            account = EcdsaAccount().deserialize({ "privateKey": private_key, "bip44Index": index }) # Could also be DAG account should be set dynamically
            #else:
            #    raise ValueError(f"HDKeyRing :: network can't be '{self.network}'")
            print(account.__dict__)


        else:
            public_key = self.root_key.PublicKey()
            # Create account

        #const wallet = child.getWallet();
        #if (this.mnemonic) {
        #  const privateKey = wallet.getPrivateKey().toString('hex');
        #  account = keyringRegistry.createAccount(this.network).deserialize({privateKey, bip44Index: index});
        #} else {
        #  const publicKey = wallet.getPublicKey().toString('hex');
        #  account = keyringRegistry.createAccount(this.network).deserialize({publicKey, bip44Index: index});
        #}

        #self.accounts.append(account)

        return account

    def get_accounts(self):
        return self.accounts

    """ PRIVATE METHODS """

    # TODO: Library
    def _init_from_mnemonic(self, mnemonic):
        from mnemonic import Mnemonic
        self.mnemonic = mnemonic
        seed_bytes = Mnemonic("english").to_seed(mnemonic)
        path = BIP_44_PATHS["CONSTELLATION_PATH"]
        path_parts = [int(part.strip("'")) for part in path.split("/")[1:]]
        purpose = path_parts[0] + 2 ** 31
        coin_type = path_parts[1] + 2 ** 31
        account = path_parts[2] + 2 ** 31
        change = 0
        index = path_parts[3]
        root_key = Bip32().get_root_key_from_seed(seed_bytes=seed_bytes)
        self.root_key = root_key.ChildKey(purpose).ChildKey(coin_type).ChildKey(account).ChildKey(change).ChildKey(index)


    def _initFromExtendedKey (self, extended_key: str):
        self.extended_key = extended_key
        # self.root_key = hdkey.fromExtendedKey(extended_key)

    def export_account (self, account) -> str: # account is IKeyringAccount
        return account.get_private_key()

    def get_account_by_address(self, address: str): # account is IKeyringAccount
        return next((acc for acc in self.accounts if acc.get_address().lower() == address.lower()), None)

    def remove_account(self, account): # account is IKeyringAccount
        self.accounts = [acc for acc in self.accounts if acc != account] # orig. == account

# rings.simple_keyring

class SimpleKeyring:

    account = None #IKeyringAccount;
    network: KeyringNetwork = None #KeyringNetwork

    def create_for_network(self, network, privateKey: str):
        inst = SimpleKeyring()
        inst.network = network
        #inst.account = keyringRegistry.createAccount(network).create(privateKey)
        inst.account = DagAccount().create(privateKey)
        return inst


    def get_state(self):
        return {
          "network": self.network,
          "account": self.account.serialize(False)
        }

    def serialize(self):
        return {
          "network": self.network,
          "accounts": [self.account.serialize(True)]
        }

    def deserialize(self, data: dict):
        self.network = data.get("network")
        #self.account = keyringRegistry.createAccount(data.get("network")).deserialize(data.get("accounts")[0])
        print(data.get("accounts"))
        self.account = EcdsaAccount().deserialize(data.get("accounts")[0])

    def add_account_at(self, index: int):
        pass
        #throw error

    def get_accounts(self):
        return [self.account]

    def get_account_by_address(self, address: str):
        return self.account if address == self.account.get_address() else None

    def remove_account(self, account):
        pass
     #throw error

# wallets.multi_chain_wallet


class MultiChainWallet:
    SID = 0
    def __init__(self):

        self.type = KeyringWalletType.MultiChainWallet.value
        self.id = f"{self.type}{self.SID + 1}"
        self.SID += 1
        #self.supported_assets =[KeyringAssetType.DAG.value, KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value] Original
        self.supported_assets =[KeyringAssetType.DAG.value, KeyringAssetType.ETH.value]
        self.label: str = ""
        self.keyrings: [] = [] # Could be many HDKeyrings
        self.mnemonic: str = ""

    # TODO: Add the ability to generate mnemonic
    def create(self, label: str, mnemonic: str):
        self.mnemonic = mnemonic # or  Bip39Helper.generateMnemonic(); Generate mnemonic if None present
        self.deserialize({ "secret":mnemonic, "type": self.type, "label": label })

    def set_label(self, val: str):
        self.label = val

    def get_label(self) -> str:
        return self.label

    def get_network(self):
        ValueError('MultiChainWallet :: Does not support this method')
        return ''

    def get_state(self):
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "supported_assets": self.supported_assets,
            "accounts": [
                {
                    "address": a.get_address(),
                    "network": a.get_network(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    def serialize(self): # Returns KeyringWalletSerialized
        return { "type": self.type, "label": self.label, "secret": self.mnemonic, "rings": [ring.serialize() for ring in self.keyrings] }

    def deserialize(self, data: dict):
        self.label = data.get("label")
        self.mnemonic = data.get("secret")
        self.keyrings = [
            HdKeyring.create(self.mnemonic, BIP_44_PATHS.get("CONSTELLATION_PATH"), KeyringNetwork.Constellation.value, 1),
            HdKeyring.create(self.mnemonic, BIP_44_PATHS.get("ETH_WALLET_PATH"), KeyringNetwork.Ethereum.value, 1)
        ]
        if data.get("rings"):
            for i, r in enumerate(data.get("rings")):
                self.keyrings[i].deserialize(r)

    def import_account(self, hd_path: str, label: str):
        ValueError('MultiChainWallet :: Does not support importAccount')
        return None


    # getAssets(): string[]
    #{
    # return this.keyrings.reduce < string[] > ((res, w) = > res.concat(w.getAssetList()), []);
    #}
    def get_accounts(self): # IKeyringAccount
        return [account for keyring in self.keyrings for account in keyring.get_accounts()]

    def get_account_by_address(self, address: str): # IKeyringAccount
        account = None
        for keyring in self.keyrings:
            account = keyring.get_account_by_address(address)
            if account:
                break
        return account

    def remove_account(self, account): # IKeyAccount {
        ValueError('MultiChainWallet :: Does not allow removing accounts.')

    def export_secret_key(self):
        return self.mnemonic


    def reset_sid(self):
        self.SID = 0

# accounts.single_account_wallet

# SingleKeyWallet
class SingleAccountWallet:

    SID = 0

    def __init__(self):
        self.type = KeyringWalletType.SingleAccountWallet.value
        self.id = f"{self.type}{self.SID + 1}"
        self.SID += 1
        self.supported_assets = []

        self.keyring = None #SimpleKeyring
        self.network = None #KeyringNetwork;
        self.label: str = ""

    def create(self, network, private_key: str, label: str):
        if not private_key:
            private_key = Account.create().key.hex()

        self.deserialize({ "type": self.type, "label": label, "network": network, "secret": private_key })

    def set_label(self, val: str):
        self.label = val

    def get_label(self) -> str:
        return self.label

    def get_network(self):
        return self.network

    def get_state(self):
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "supported_assets": self.supported_assets,
            "accounts": [
                {
                    "address": a.get_address(),
                    "network": a.get_network(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    def serialize(self):
        return {
          "type": self.type,
          "label": self.label,
          "network": self.network,
          "secret": self.export_secret_key()
        }

    def deserialize(self, data):

        self.label = data.get("label")
        self.network = data.get("network") or KeyringNetwork.Ethereum.value
        self.keyring = SimpleKeyring()

        self.keyring.deserialize({"network": self.network, "accounts": [{ "privateKey": data.get("secret") }]})

        if self.network == KeyringNetwork.Ethereum.value:
          self.supported_assets.append(KeyringAssetType.ETH.value)
          self.supported_assets.append(KeyringAssetType.ERC20.value)

        elif self.network == KeyringNetwork.Constellation.value:
          self.supported_assets.append(KeyringAssetType.DAG)

    def import_account (self, hdPath: str, label: str):
        ValueError('SimpleChainWallet :: does not support importAccount')
        return None

    def get_accounts(self):
        return self.keyring.getAccounts()

    def get_account_by_address(self, address: str):
        return self.keyring.get_account_by_address(address)

    def remove_account(self, account):
        # Does not support removing account
        pass

    def export_secret_key(self) -> str:
        return self.keyring.get_accounts()[0].wallet.key.hex()

    def reset_sid(self):
        self.SID = 0

# encryptor

import os
import json
from typing import TypeVar, Generic
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode


T = TypeVar('T')


class Encryptor(Generic[T]):

    @staticmethod
    def create() -> 'Encryptor':
        return Encryptor()

    async def encrypt(self, password: str, data: T) -> str:
        salt = self.generate_salt()

        password_derived_key = self.key_from_password(password, salt)
        payload = self.encrypt_with_key(password_derived_key, str(data))
        payload['salt'] = salt

        return json.dumps(payload)

    async def decrypt(self, password: str, text: str) -> T:
        payload = json.loads(text) if isinstance(text, str) else text
        salt = payload['salt']
        key = self.key_from_password(password, salt)

        return self.decrypt_with_key(key, payload)

    def encrypt_with_key(self, key: bytes, data: T) -> dict:
        text = json.dumps(data)
        data_bytes = text.encode('utf-8')
        iv = os.urandom(16)

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data_bytes) + encryptor.finalize()

        return {
            'data': b64encode(ciphertext).decode('utf-8'),
            'iv': b64encode(iv).decode('utf-8'),
            'tag': b64encode(encryptor.tag).decode('utf-8')
        }

    def decrypt_with_key(self, key: bytes, payload: dict) -> T:
        try:
            encrypted_data = b64decode(payload['data'])
            iv = b64decode(payload['iv'])
            tag = b64decode(payload['tag'])
        except KeyError as e:
            raise ValueError(f"Missing field in payload: {e}")
        except Exception as e:
            raise ValueError(f"Invalid payload: {e}")

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        try:
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        except Exception as e:
            raise ValueError("Decryption failed: Invalid tag or corrupted data.") from e

        return json.loads(decrypted_data.decode('utf-8'))

    @staticmethod
    def key_from_password(password: str, salt: str, iterations: int = 100_000) -> bytes:
        """
        Derives a secure key from a password and a hexadecimal salt using PBKDF2.

        Args:
            password (str): The password to derive the key from.
            salt (str): A hexadecimal string representing the salt.
            iterations (int): The number of iterations for the PBKDF2 function.

        Returns:
            bytes: The derived cryptographic key.
        """
        # Convert hex salt to bytes
        try:
            salt_bytes = bytes.fromhex(salt)
        except ValueError:
            raise ValueError("Invalid hexadecimal salt provided.")

        # Use PBKDF2 to derive the key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256 requires a 32-byte key
            salt=salt_bytes,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))

    def generate_salt(self, byte_count: int = 32) -> str:
        return os.urandom(byte_count).hex()


class KeyringManager:
    def __init__(self):
        self.encryptor = Encryptor()
        # self.storage =
        self.wallets = []
        self.password = ""

    def is_unlocked(self):
        return bool(self.password)

    def clear_wallets(self):
        self.wallets = []
        # this.memStore.updateState({
        #     wallets: [],
        # })

    def new_multi_chain_hd_wallet(self, label: str, seed: str):
        wallet = MultiChainWallet()
        label = label or 'Wallet #' + f"{len(self.wallets) + 1}"
        wallet.create(label, seed)
        self.wallets.append(wallet)
        return wallet

    async def create_or_restore_vault(self, label: str, seed: str, password: str):

        if not password:
            raise ValueError("KeyringManager :: A password is required to create or restore a Vault.")
        elif type(password) != str:
            raise ValueError("KeyringManager :: Password has invalid format.")
        else:
            self.password = password

        if not seed:
            raise ValueError("KeyringManager :: A seed is required to create or restore a Vault.")
        # TODO: Validate seed
        # new Error('Seed phrase is invalid.')

        self.clear_wallets()
        wallet = self.new_multi_chain_hd_wallet(label, seed)
        print(wallet.__dict__)
        await self.full_update()

        return wallet

    # creates a single wallet with one chain, creates first account by default, one per chain.
    async def create_single_account_wallet(self, label: str, network: KeyringNetwork, private_key: str):

        wallet = SingleAccountWallet()
        label = label or 'Wallet #' + f"{len(self.wallets) + 1}"

        wallet.create(network, private_key, label)
        self.wallets.append(wallet)

        # this.emit('newAccount', wallet.getAccounts()[0]);

        await self.full_update()

        return wallet


    async def full_update(self):

        await self.persist_all_wallets(self.password)
        #this.updateMemStoreWallets();
        #this.notifyUpdate();
        #}

    async def persist_all_wallets(self, password):
        password = password or self.password
        if type(password) != str:
            raise ValueError('KeyringManager :: Password is not a string')

        self.password = password


        s_wallets = [w.serialize() for w in self.wallets]

        print(s_wallets)

        encryptedString = await self.encryptor.encrypt(self.password, { "wallets": s_wallets })

        # TODO: Add storage
        print(encryptedString)
        decryptedString = await self.encryptor.decrypt(self.password, encryptedString)
        print(json.dumps(decryptedString))
        #await self.storage.set('vault', encryptedString);

from os import getenv

WORDS = getenv("WORDS")

if __name__ == "__main__":

    manager = KeyringManager()
    asyncio.run(manager.create_or_restore_vault(label='', seed=WORDS, password='password'))
    asyncio.run(manager.create_single_account_wallet(label="", network=KeyringNetwork.Constellation.value, private_key=""))