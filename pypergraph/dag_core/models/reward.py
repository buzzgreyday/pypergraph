from typing import List
from pydantic import BaseModel


class Reward(BaseModel):
    destination: str
    amount: float

    @classmethod
    def process_snapshot_rewards(cls, data: List[dict]) -> List["Reward"]:
        return [cls(**item) for item in data]

