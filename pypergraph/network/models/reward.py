from typing import List

import base58
from pydantic import BaseModel, field_validator, Field


class RewardTransaction(BaseModel):
    destination: str # Validated below
    amount: int = Field(ge=0)

    @classmethod
    def process_snapshot_rewards(cls, data: List[dict]) -> List["RewardTransaction"]:
        return [cls(**item) for item in data]

    @field_validator('destination')
    def validate_dag_address(cls, address):
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

        return address

