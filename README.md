# Pypergraph
---
**Hypergraph Python Tool**

> **This tool is currently in early development, contact me if you wish to contribute. Please do not rely on this for production purposes just yet.**

Pypergraph is a Python package that enables secure wallet functionalities and interaction with Constellation Network APIs. Inspired by [DAG4.js](https://github.com/StardustCollective/dag4.js).

[![Read the Docs](https://img.shields.io/readthedocs/pypergraph-dag)](https://pypergraph-dag.readthedocs.io)
![Version](https://img.shields.io/badge/version-2025.0.0a7-yellow.svg)
![LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)
---
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

#### IMPORT WALLET FROM MNEMONIC PHRASE
```
wallet = Wallet.from_mnemonic("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon")
```

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
