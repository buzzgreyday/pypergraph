from datetime import datetime
from typing import Optional

from pypergraph.dag_core.models.transaction import Proof


class GlobalSnapshotValue:

    def __init__(self, value: dict):
        self.ordinal: int = value["ordinal"]
        self.height: int = value["height"]
        self.sub_height: int = value["subHeight"]
        self.last_snapshot_hash: str = value["lastSnapshotHash"]
        self.blocks: list = value["blocks"]
        self.state_channel_snapshots: dict = value["stateChannelSnapshot"]
        self.rewards: list = value["rewards"]
        self.epoch_progress: int = value["epochProgress"]
        self.next_facilitators: list = value["nextFacilitators"]
        self.tips: dict = value["tips"]
        self.state_proof: dict = value["stateProof"]
        self.version: str = value["version"]


class GlobalSnapshot:

    def __init__(self, response):
        self.value: GlobalSnapshotValue = GlobalSnapshotValue(response["value"])
        self.proofs: list = Proof.process_snapshot_proofs(response["proofs"])

"""BE MODELS: DTO"""
class Snapshot:
    def __init__(self, data):

        self.hash: str = data["hash"]
        self.ordinal: int = data["ordinal"]
        self.height: int = data["height"]
        self.sub_height:int = data["subHeight"]
        self.last_snapshot_hash: str = data["lastSnapshotHash"]
        self.blocks: list = data["blocks"]
        self.timestamp: datetime = datetime.fromisoformat(data["timestamp"])

class CurrencySnapshot(Snapshot):
    def __init__(self, data: dict, meta: Optional[dict]=None):
        super().__init__(data=data)

        self.fee: int = data["fee"]
        self.owner_address: str = data["ownerAddress"]
        self.staking_address: str = data["stakingAddress"]
        self.size_in_kb: int = data["sizeInKB"]
        self.meta: Optional[dict] = meta
