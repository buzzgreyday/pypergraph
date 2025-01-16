# Pypergraph
---
**Hypergraph Python Tool**

> **This tool is currently in early development, contact me if you wish to contribute. Please do not rely on this for production purposes just yet.**

Pypergraph is a Python package that enables secure wallet functionalities and interaction with Constellation Network APIs. Inspired by [DAG4.js](https://github.com/StardustCollective/dag4.js).

[![Read the Docs](https://img.shields.io/readthedocs/pypergraph-dag)](https://pypergraph-dag.readthedocs.io)
![Version](https://img.shields.io/badge/version-2025.0.0a7-yellow.svg)
![LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)
---

## Table of Contents
- [Pypergraph](#pypergraph)
- [Install](#install)
- [Usage](#usage)
  - [Wallet](#wallet)
    - [The Constellation Key Trio](#the-constellation-key-trio)
    - [New Wallet](#new-wallet)
    - [Import Wallet from Mnemonic Phrase](#import-wallet-from-mnemonic-phrase)
    - [Import Wallet from Private Key](#import-wallet-from-private-key)
    - [Get DAG Wallet Mnemonic Phrase](#get-dag-wallet-mnemonic-phrase)
    - [Get DAG Wallet Private Key](#get-dag-wallet-private-key)
    - [Get DAG Wallet Public Key](#get-dag-wallet-public-key)
    - [Get DAG Wallet Address](#get-dag-wallet-address)
    - [Get DAG Wallet Balance](#get-dag-wallet-balance)
    - [Set Non-Default DAG Wallet Network](#set-non-default-dag-wallet-network)
  - [Transaction](#transaction)
    - [New Transaction](#new-transaction)
    - [Send Transaction](#send-transaction)
    - [Get Pending Transaction](#get-pending-transaction)
- [Support](#support)

## INSTALL

```
git clone https://github.com/buzzgreyday/pypergraph
cd pypergraph
pip install -r requirements.txt
```
---
## USAGE

The following code is meant to demonstrate how easy interacting with the network is using Pypergraph. More extensive documentation coming. Full documentation available [here](https://pypergraph-dag.readthedocs.io/en/latest/index.html).

### WALLET

A Pypergraph wallet is essentially a Constellation **key trio** with the addition of a `words` variable (the mnemonic phrase) and a `network` object variable with the current network configuration of the `wallet` object.

<details>
<summary><strong>The Constellation Key Trio</strong></summary>

In the Constellation Network, accounts are composed of a key trio consisting of the private key, public key, and an address.

### Private Key
The private key is a highly confidential piece of information that plays a crucial role in authenticating an address to the network. With the private key, you can execute sensitive actions like signing messages or sending transactions.

### Public Key
The public key serves as a unique identifier for nodes on the network and is derived from the private key. It is crucial for establishing trust relationships between nodes, enabling secure communication, and verifying digital signatures.

### Address
The address is the public-facing component of the Key Trio and represents a public wallet address for receiving payments or other digital transactions. It can be derived from either the private or public key and is widely used for peer-to-peer transactions. Sharing your address with others enables them to send you payments while keeping your private key confidential.

Source: [Accounts and Keys](https://docs.constellationnetwork.io/metagraphs/accounts/)
</details>

#### NEW WALLET
```
wallet = Wallet.new()
```
<details>
<summary><strong>How is a new wallet object created?</strong></summary>

```
from pypergraph.dag_keystore import KeyStore

mnemonic_values = KeyStore.get_mnemonic()
private_key = KeyStore.get_private_key_from_seed(seed=mnemonic_values["seed"])
public_key = KeyStore.get_public_key_from_private_key(private_key)
address = KeyStore.get_dag_address_from_public_key(public_key=public_key)
valid = KeyStore.validate_dag_address(address=address)
if not valid:
    raise ValueError("Wallet :: Not a valid DAG address.")
```

</details>

#### IMPORT WALLET FROM MNEMONIC PHRASE
```
wallet = Wallet.from_mnemonic("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon")
```

<details>
<summary><strong>How is the private key, public key and DAG address derived from the mnemonic phrase?</strong></summary>

The private key, public key and DAG address is generated from a 12 word seed.

```
from pypergraph.dag_keystore import KeyStore, Bip39

valid = KeyStore.validate_mnemonic(mnemonic_phrase=words)
if not valid:
    raise ValueError("Wallet :: Not a valid mnemonic.")
mnemonic = Bip39()
seed_bytes = mnemonic.get_seed_from_mnemonic(words)
private_key = KeyStore.get_private_key_from_seed(seed_bytes)
public_key = KeyStore.get_public_key_from_private_key(private_key)
address = KeyStore.get_dag_address_from_public_key(public_key)
valid = KeyStore.validate_dag_address(address=address)
if not valid:
    raise ValueError("Wallet :: Not a valid DAG address.")
```

</details>

#### IMPORT WALLET FROM PRIVATE KEY
```
wallet = Wallet.from_private_key("SOME_VALID_PRIVATE_KEY")
```

#### GET DAG WALLET MNEMONIC PHRASE
```
words = wallet.words
```

#### GET DAG WALLET PRIVATE KEY
```
private_key = wallet.private_key
```

#### GET DAG WALLET PUBLIC KEY
```
public_key = wallet.public_key
```

#### GET DAG WALLET ADDRESS
```
address = wallet.address
```

#### GET DAG WALLET BALANCE
> **Default:** `dag_address=wallet.address, metagraph_id=None`
```
balance = await wallet.get_address_balance()
```

#### SET NON-DEFAULT DAG WALLET NETWORK
> **Default:** `network="mainnet", l0_host=None, l1_host=None, metagraph_id=None`
```
wallet = wallet.set_network(network="testnet")
```

### TRANSACTION

How to create a new transaction and send it.

#### NEW TRANSACTION
```
tx = await wallet.transaction(to_address='SOME_VALID_DAG_ADDRESS', amount=1.0, fee=0.0002)
```

#### SEND TRANSACTION
```
hash = await wallet.send(tx)
```

#### GET PENDING TRANSACTION
> Default: returns an object if transaction is pending, `None` if transaction has been processed.
```
   import asyncio

   async def check_pending_transaction(wallet):
       while True:
           pending = await wallet.get_pending_transaction(hash)
           if not pending:
               break
           await asyncio.sleep(5)
       print("Transaction sent.")
```
---
<a href="https://www.buymeacoffee.com/buzzgreyday" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
