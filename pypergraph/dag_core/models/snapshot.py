from datetime import datetime

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
    def __init__(self, response):

        self.hash: str = response["hash"]
        self.ordinal: int = response["ordinal"]
        self.height: int = response["height"]
        self.sub_height:int = response["subHeight"]
        self.last_snapshot_hash: str = response["lastSnapshotHash"]
        self.blocks: list = response["blocks"]
        self.timestamp: datetime = datetime.fromisoformat(response["timestamp"])
