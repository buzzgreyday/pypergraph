from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional, Any

import base58
from pydantic import BaseModel, Field, model_validator, constr, conint

from pypergraph.dag_core.constants import DAG_MAX
from pypergraph.dag_core.models.account import LastReference


class PostTransactionResponse(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

    def __repr__(self) -> str:
        return f"PostTransactionResponse(hash={self.hash!r})"

class PendingTransaction(BaseModel):
    source: str # Validated below
    destination: str # Validated below
    amount: int = Field(ge=0, le=DAG_MAX)
    fee: int = Field(ge=0, le=DAG_MAX)
    parent_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(..., alias="parentHash")
    parent_ordinal: int = Field(..., alias="parentOrdinal", ge=0)
    salt: int = Field(ge=0)
    transaction_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="hash")
    status: conint(ge=100, le=599)

    @model_validator(mode="before")
    def flatten_data(cls, values: dict) -> dict:
        transaction = values.get("transaction", {})
        parent = transaction.get("parent", {})
        return {
            "source": transaction.get("source"),
            "destination": transaction.get("destination"),
            "amount": transaction.get("amount"),
            "fee": transaction.get("fee"),
            "parent_hash": parent.get("hash"),
            "parent_ordinal": parent.get("ordinal"),
            "salt": transaction.get("salt"),
            "hash": values.get("hash"),
            "status": values.get("status"),
        }

    def __repr__(self):
        return (f"PendingTransaction(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent_hash={self.parent_hash}, "
                f"parent_ordinal={self.parent_ordinal}, salt={self.salt}, "
                f"transaction_hash={self.transaction_hash}, status={self.status})")

    @model_validator(mode='before')
    def validate_dag_address(cls, values):
        for address in (values.get('source'), values.get('destination')):
            if address:

                valid_len = len(address) == 40
                valid_prefix = address.startswith("DAG")
                valid_parity = address[3].isdigit() and 0 <= int(address[3]) < 10
                base58_part = address[4:]
                valid_base58 = (
                    len(base58_part) == 36 and base58_part == base58.b58encode(base58.b58decode(base58_part)).decode()
                )

                # If any validation fails, raise an error
                if not (valid_len and valid_prefix and valid_parity and valid_base58):
                    raise ValueError(f"CurrencySnapshot :: Invalid address: {address}")

        return values


class TransactionValue(BaseModel):
    source: str # Validated below
    destination: str # Validated below
    amount: int = Field(ge=0, le=DAG_MAX)
    fee: int = Field(ge=0, le=DAG_MAX)
    parent: LastReference
    salt: int = Field(default=None, ge=0)

    def __repr__(self):
        return (f"TransactionValue(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent={self.parent}, salt={self.salt})")

    @model_validator(mode='before')
    def validate_dag_address(cls, values):
        for address in (values.get('source'), values.get('destination')):
            if address:

                valid_len = len(address) == 40
                valid_prefix = address.startswith("DAG")
                valid_parity = address[3].isdigit() and 0 <= int(address[3]) < 10
                base58_part = address[4:]
                valid_base58 = (
                    len(base58_part) == 36 and base58_part == base58.b58encode(base58.b58decode(base58_part)).decode()
                )

                # If any validation fails, raise an error
                if not (valid_len and valid_prefix and valid_parity and valid_base58):
                    raise ValueError(f"CurrencySnapshot :: Invalid address: {address}")

        return values

    def get_encoded(self) -> str:
        """
        :return: An encoded version of the transaction used for signing
        """
        parent_count = "2"  # Always 2 parents
        source_address = self.source
        dest_address = self.destination
        amount = format(self.amount, "x")  # amount as hex
        parent_hash = self.parent.hash
        ordinal = str(self.parent.ordinal)
        fee = str(self.fee)
        salt = self.to_hex_string(self.salt)

        return "".join([
            parent_count,
            str(len(source_address)),
            source_address,
            str(len(dest_address)),
            dest_address,
            str(len(amount)),
            amount,
            str(len(parent_hash)),
            parent_hash,
            str(len(ordinal)),
            ordinal,
            str(len(fee)),
            fee,
            str(len(salt)),
            salt,
        ])

    @staticmethod
    def to_hex_string(val):
        val = Decimal(val)
        if val < 0:
            b_int = (1 << 64) + int(val)
        else:
            b_int = int(val)
        return format(b_int, "x")



class Proof(BaseModel):
    id: constr(pattern=r"^[a-fA-F0-9]{128}$")
    signature: constr(pattern=r"^[a-fA-F0-9]") = Field(min_length=138, max_length=144)

    @classmethod
    def process_snapshot_proofs(cls, data: list) -> List["Proof"]:
        return [cls(**item) for item in data]

    def __repr__(self):
        return f"Proof(id={self.id}, signature={self.signature})"


class Transaction(BaseModel):
    value: TransactionValue
    proofs: List[Proof] = Field(default_factory=list)

    def __repr__(self):
        return f"Transaction(value={self.value}, proofs={self.proofs})"

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            value=TransactionValue(**data["value"]),
            proofs=Proof.process_snapshot_proofs(data.get("proofs", []))
        )

    def add_value(self, value: TransactionValue) -> None:
        self.value = value

    def add_proof(self, proof: Proof) -> None:
        self.proofs.append(proof)




class BlockExplorerTransaction(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")
    amount: int = Field(ge=0, le=DAG_MAX)
    source: str # Validated below
    destination: str # Validate below
    fee: int = Field(ge=0, lt=DAG_MAX)
    parent: LastReference
    salt: Optional[int] = Field(default=None, ge=0)
    block_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="blockHash")
    snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="snapshotHash")
    snapshot_ordinal: int = Field(alias="snapshotOrdinal", ge=0)
    transaction_original: Transaction = Field(alias="transactionOriginal")
    timestamp: datetime
    proofs: List[Proof] = Field(default_factory=list)
    meta: Optional[Dict] = None # TODO: Validate

    def __repr__(self):
        return (f"BlockExplorerTransaction(hash={self.hash}, amount={self.amount}, "
                f"source={self.source}, destination={self.destination}, fee={self.fee}, "
                f"parent={self.parent}, salt={self.salt}, block_hash={self.block_hash}, "
                f"snapshot_hash={self.snapshot_hash}, snapshot_ordinal={self.snapshot_ordinal}, "
                f"transaction_original={self.transaction_original}, timestamp={self.timestamp}, "
                f"proofs={self.proofs}, meta={self.meta})")

    @classmethod
    def process_transactions(cls, data: List[dict], meta: Optional[dict] = None) -> List["BlockExplorerTransaction"]:
        return [cls.model_validate({**tx, "meta": meta}) for tx in data]

    @model_validator(mode='before')
    def validate_dag_address(cls, values):
        for address in (values.get('source'), values.get('destination')):
            if address:

                valid_len = len(address) == 40
                valid_prefix = address.startswith("DAG")
                valid_parity = address[3].isdigit() and 0 <= int(address[3]) < 10
                base58_part = address[4:]
                valid_base58 = (
                    len(base58_part) == 36 and base58_part == base58.b58encode(base58.b58decode(base58_part)).decode()
                )

                # If any validation fails, raise an error
                if not (valid_len and valid_prefix and valid_parity and valid_base58):
                    raise ValueError(f"CurrencySnapshot :: Invalid address: {address}")

        return values

    class ConfigDict:
        population_by_name = True