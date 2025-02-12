from typing import List, Type

class Reward:

    destination: str
    amount: float

    @classmethod
    def process_snapshot_rewards(cls, data: List) -> List[Type["Reward"]]:
        rewards = []
        for item in data:
            cls.destination: str = item["destination"]
            cls.amount: int = item["amount"]
            rewards.append(cls)
        return rewards
