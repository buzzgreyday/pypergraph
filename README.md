# Pypergraph
---
**Hypergraph Python Tool**

> **This tool is currently under development, contact me if you wish to contribute. Please do not rely on this for production purposes.**

Pypergraph is a simple tool written in Python only, inspired by [DAG4.js](https://github.com/StardustCollective/dag4.js).

![Version](https://img.shields.io/badge/version-0.0.2-yellow.svg)
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

The following code is meant to demonstrate how easy interacting with the network is using Pypergraph. More extensive documentation coming.

### WALLET

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

#### GET DAG WALLET ADDRESS
```
address = wallet.address
```

#### GET DAG WALLET PUBLIC KEY
```
public_key = wallet.public_key
```

#### GET DAG WALLET PRIVATE KEY
```
private_key = wallet.private_key
```

#### GET DAG WALLET MNEMONIC PHRASE
```
words = wallet.words
```

#### GET DAG WALLET BALANCE
```
await wallet.get_address_balance()
```

#### SET NON-DEFAULT DAG WALLET API
> Default network is "mainnet" and layer is 1
```
wallet = wallet.set_api(network="testnet", layer=1)
```

### TRANSACTION

How to create a new transaction and send it.

#### NEW TRANSACTION
```
tx = await wallet.build_transaction(to_address='SOME_VALID_DAG_ADDRESS', amount=1.0, fee=0.0002)
```

#### SEND TRANSACTION
```
response = await wallet.send(tx)
```