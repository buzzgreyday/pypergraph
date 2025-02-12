from typing import List, Type

from pypergraph.dag_core.convert import ddag_to_dag

class Reward:

    destination: str
    amount: float

    @classmethod
    def process_snapshot_rewards(cls, lst: List) -> List[Type["Reward"]]:
        rewards = []
        for item in lst:
            cls.destination: str = item["destination"]
            cls.amount: int = item["amount"]
            rewards.append(cls)
        return rewards
