# Pypergraph
**Hypergraph Python Tool**

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
## INSTALL
```
git clone https://github.com/buzzgreyday/pypergraph
cd pypergraph
pip install -r requirements.txt
```

## USAGE

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
### TRANSACTIONS
#### CREATE A TRANSACTION
```
tx = wallet.build_transaction(to_address='SOME_VALID_DAG_ADDRESS', amount=1.0, fee=0.0002)
```
#### SEND TRANSACTION
```
response = tx.send()
```