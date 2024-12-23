from pydantic import BaseModel

class TransactionReference(BaseModel):
    hash: str
    ordinal: int

class TransactionValueV2(BaseModel):
    source: str
    destination: str
    amount: float
    fee: float
    parent: TransactionReference
    salt: int | str

class TransactionV2(BaseModel):
    hash: str
    source: str
    destination: str
    amount: float
    fee: float
    parent: TransactionReference
    snapshot: str
    block: str
    timestamp: str
    transactionOriginal: TransactionReference

class Proof(BaseModel):
    signature: str
    id: str

class PostTransactionV2(BaseModel):
    value: TransactionValueV2
    proofs: Proof

class PostTransactionResponseV2(BaseModel):
    hash: str

class GetTransactionResponseV2(BaseModel):
    data: TransactionV2

class KeyTrio(BaseModel):
    privateKey: str
    publicKey: str
    address: str