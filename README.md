# Pypergraph
---
**Hypergraph Python Tool**

Pypergraph is a Python package that enables secure wallet functionalities and interaction with Constellation Network APIs. Inspired by [DAG4.js](https://github.com/StardustCollective/dag4.js).

> ⚠️ **Caution:** This tool is currently in early development.  
> **Do not use it for production purposes** as it may contain bugs or incomplete features. Contributions are welcome—please contact me if you'd like to get involved.

[![Read the Docs](https://img.shields.io/readthedocs/pypergraph-dag)](https://pypergraph-dag.readthedocs.io)
![Version](https://img.shields.io/badge/version-2025.0.0a8-yellow.svg)
![LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)
---

## Table of Contents
- [Pypergraph](#pypergraph)
- [Install](#install)
- [Usage](#usage)
  - [Wallet](#wallet)
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

## INSTALL

```
git clone https://github.com/buzzgreyday/pypergraph
cd pypergraph
pip install -r requirements.txt
```
---
## USAGE
**Full documentation available [here](https://pypergraph-dag.readthedocs.io/en/latest/index.html).**

The following code is meant to demonstrate how easy interacting with the network is using Pypergraph. More extensive documentation coming.

### WALLET

A Pypergraph `wallet` is essentially a Constellation Network Hypergraph `account`, or `key trio`, with the addition of a `words` variable (the mnemonic phrase) and a `network` object variable with the current network configuration of the `wallet` object.

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

<details>
<summary><strong>How is the public key and DAG address derived from a private key?</strong></summary>

```
from pypergraph.dag_keystore import KeyStore

public_key = KeyStore.get_public_key_from_private_key(private_key)
address = KeyStore.get_dag_address_from_public_key(public_key)
valid = KeyStore.validate_dag_address(address=address)
if not valid:
    raise ValueError("Wallet :: Not a valid DAG address.")
```

</details>

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

<details>
<summary><strong>How is DAG address generated from a public key?</strong></summary>

The DAG address is derived from the public key and stored in the `wallet.address` object variable.

```
import base58
from hashlib import sha256

PKCS_PREFIX = "3056301006072a8648ce3d020106052b8104000a034200"

if len(public_key_hex) == 128:
    public_key = PKCS_PREFIX + "04" + public_key_hex
elif len(public_key_hex) == 130 and public_key_hex[:2] == "04":
    public_key = PKCS_PREFIX + public_key_hex
else:
    raise ValueError("Not a valid public key")

public_key = sha256(bytes.fromhex(public_key)).hexdigest()
public_key = base58.b58encode(bytes.fromhex(public_key)).decode()
public_key = public_key[len(public_key) - 36:]

check_digits = "".join([char for char in public_key if char.isdigit()])
check_digit = 0
for n in check_digits:
    check_digit += int(n)
    if check_digit >= 9:
        check_digit = check_digit % 9

address = f"DAG{check_digit}{public_key}"
```

</details>

#### GET DAG WALLET BALANCE
> **Default:** `dag_address=wallet.address, metagraph_id=None`
```
balance = await wallet.get_address_balance()
```

#### SET NON-DEFAULT DAG WALLET NETWORK

Reconfigures the `wallet.network` object variable used to handle interaction with Constellation APIs. The parameters `l0_host` and `l1_host` is required if `metagraph_id` is set.

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

<details>
<summary><strong>How is a new transaction created?</strong></summary>

```
last_ref = await self.network.get_last_reference(address_hash=self.address)
tx, tx_hash, encoded_tx = KeyStore.prepare_tx(amount=amount, to_address=to_address, from_address=self.address,
                                              last_ref=last_ref.to_dict(), fee=fee)
signature = KeyStore.sign(private_key_hex=self.private_key, tx_hash=tx_hash)
valid = KeyStore.verify(public_key_hex=self.public_key, tx_hash=tx_hash, signature_hex=signature)
if not valid:
    raise ValueError("Wallet :: Invalid signature.")
proof = {"id": self.public_key[2:], "signature": signature}
tx.add_proof(proof=proof)
```

</details>

#### SEND TRANSACTION
```
hash = await wallet.send(tx)
```

#### GET PENDING TRANSACTION
> Default: returns an object if transaction is pending, `None` if transaction has been processed.

```
pending = await wallet.get_pending_transaction(hash)
```

<details>
<summary><strong>How can I check if a transaction was sent?</strong></summary>

The following code is an example of how to check if the transaction is processed or not.

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

</details>

---
<a href="https://www.buymeacoffee.com/buzzgreyday" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
