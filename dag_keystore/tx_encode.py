from dataclasses import dataclass, field
from decimal import Decimal
import random

from dag_network import API


@dataclass
class PostTransactionV2:
    value: dict = field(default_factory=lambda: {
        "source": None,
        "destination": None,
        "amount": None,
        "fee": 0,
        "parent": None,
        "salt": None,
    })
    proofs: list = field(default_factory=list)


class TransactionV2:
    MIN_SALT = Decimal("1e8")

    def __init__(self, from_address=None, to_address=None, amount=None, fee=None, last_tx_ref=None, salt=None):
        self.tx = PostTransactionV2()

        if from_address:
            self.tx.value["source"] = from_address
        if to_address:
            self.tx.value["destination"] = to_address
        if amount is not None:
            self.tx.value["amount"] = amount
        if fee is not None:
            self.tx.value["fee"] = fee
        if last_tx_ref:
            self.tx.value["parent"] = last_tx_ref
        if salt is None:
            salt = self.MIN_SALT + int(random.getrandbits(48))
        self.tx.value["salt"] = salt

    @staticmethod
    def to_hex_string(val):
        val = Decimal(val)
        if val < 0:
            b_int = (1 << 64) + int(val)
        else:
            b_int = int(val)
        return format(b_int, "x")

    def get_post_transaction(self, proof=None):
        """
        Returns the dictionary representation of the transaction, optionally including proofs.
        """
        post_transaction = {
            "value": {
                **self.tx.value,
                "salt": str(self.tx.value["salt"]).replace("n", ""),
            },
            "proofs": self.tx.proofs.copy(),
        }
        if proof:
            post_transaction["proofs"].append(proof)
        return post_transaction

    def get_encoded(self):
        parent_count = "2"  # Always 2 parents
        source_address = self.tx.value["source"]
        dest_address = self.tx.value["destination"]
        amount = format(self.tx.value["amount"], "x")  # amount as hex
        parent_hash = self.tx.value["parent"]["hash"]
        ordinal = str(self.tx.value["parent"]["ordinal"])
        fee = str(self.tx.value["fee"])
        salt = self.to_hex_string(self.tx.value["salt"])

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

    def add_proof(self, proof):
        """
        Adds a signature proof to the transaction.
        """
        self.tx.proofs.append(proof)

    def send(self):
        return API.post_transaction(self.get_post_transaction())

class TxEncode:
    @staticmethod
    def get_tx_v2(amount, to_address, from_address, last_ref, fee=None):
        return TransactionV2(
            amount=amount,
            to_address=to_address,
            from_address=from_address,
            last_tx_ref=last_ref,
            fee=fee,
        )

    def kryo_serialize(self, msg: str, set_references: bool = True) -> str:
        """
        Serialize a message using a custom kryo-like serialization method.
        :param msg: The string message to serialize.
        :param set_references: Whether to include references in the prefix.
        :return: The serialized message as a hexadecimal string.
        """
        prefix = "03" + ("01" if set_references else "") + self.utf8_length(len(msg) + 1).hex()
        coded = msg.encode("utf-8").hex()
        return prefix + coded

    def utf8_length(self, value: int) -> bytes:
        """
        Encodes the length of a UTF8 string as a variable-length encoded integer.
        :param value: The value to encode.
        :return: The encoded length as a bytes object.
        """
        buffer = bytearray()

        if value >> 6 == 0:
            # Requires 1 byte
            buffer.append(value | 0x80)  # Set bit 8.
        elif value >> 13 == 0:
            # Requires 2 bytes
            buffer.append(value | 0x40 | 0x80)  # Set bits 7 and 8.
            buffer.append(value >> 6)
        elif value >> 20 == 0:
            # Requires 3 bytes
            buffer.append(value | 0x40 | 0x80)  # Set bits 7 and 8.
            buffer.append((value >> 6) | 0x80)  # Set bit 8.
            buffer.append(value >> 13)
        elif value >> 27 == 0:
            # Requires 4 bytes
            buffer.append(value | 0x40 | 0x80)  # Set bits 7 and 8.
            buffer.append((value >> 6) | 0x80)  # Set bit 8.
            buffer.append((value >> 13) | 0x80)  # Set bit 8.
            buffer.append(value >> 20)
        else:
            # Requires 5 bytes
            buffer.append(value | 0x40 | 0x80)  # Set bits 7 and 8.
            buffer.append((value >> 6) | 0x80)  # Set bit 8.
            buffer.append((value >> 13) | 0x80)  # Set bit 8.
            buffer.append((value >> 20) | 0x80)  # Set bit 8.
            buffer.append(value >> 27)

        return bytes(buffer)