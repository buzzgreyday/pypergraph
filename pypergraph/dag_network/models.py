import json
from datetime import datetime
from typing import List, Optional, Dict

"""HOST MODELS"""
class TotalSupply:

    def __init__(self, response: dict):
        self.ordinal: int = response.get("ordinal")
        self.total_supply: int | float = ddag_to_dag(response.get("total"))

    def __repr__(self):
        return f"TotalSupply(ordinal={self.ordinal}, balance={self.total_supply})"

class Balance:

    def __init__(self, response: json):
        for key in response.keys():
            if key == "data":
                self.ordinal: int = response["data"]["ordinal"]
                self.balance: float = ddag_to_dag(response["data"]["balance"])
                self.address: str = response["data"]["address"]
                self.meta = response["meta"] if "meta" in response else None
            else:
                self.ordinal: int = response["ordinal"]
                self.balance: float = ddag_to_dag(response["balance"])
                self.address = None
                self.meta = response["meta"] if "meta" in response else None

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

    # TODO: Make to_dict serialization


class ClusterInfo:

    alias: Optional[str] = None
    id: str
    ip: str
    state: str
    session: str
    public_port: int
    p2p_port: int
    reputation: Optional[float]

    @classmethod
    def process_cluster_info(cls, response: List) -> List:
        results = []
        for d in response:
            cls.alias = d["alias"] if hasattr(d, "alias") else None
            cls.id = d["id"]
            cls.ip = d["ip"]
            cls.state = d["state"]
            cls.session = d["session"]
            cls.reputation = d["reputation"] if hasattr(d, "reputation") else None
            cls.public_port = d["publicPort"]
            cls.p2p_port = d["p2pPort"]
            results.append(cls)

        return results


class LastReference:

    def __init__(self, response: json):
        self.ordinal: int = response.get("ordinal")
        self.hash: str = response.get("hash")

    def __repr__(self):
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}')"

    def to_dict(self) -> dict:
        """
        Make LastReference object return a dictionary with the last transaction reference associated with the DAG wallet address.

        :return: Dictionary with keys "ordinal" and "hash"
        """
        return {'ordinal': self.ordinal, 'hash': f'{self.hash}'}


class PostTransactionResponse:

    def __init__(self, hash: str):
        self.hash = hash

    def __repr__(self):
        return f"PostTransactionResponse(hash='{self.hash}')"


class PendingTransaction:

    def __init__(self, response: json):
        transaction = response["transaction"]
        self.source: str = transaction["source"]
        self.destination: str = transaction["destination"]
        self.amount: int = transaction["amount"]
        self.fee: int = transaction["fee"]
        self.parent_hash: str = transaction["parent"]["hash"]
        self.parent_ordinal: int = transaction["parent"]["ordinal"]
        self.salt: str = transaction["salt"]
        self.transaction_hash: str = response["hash"]
        self.status: int = response["status"]

    def __repr__(self):
        return (f"PendingTransaction(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent_hash={self.parent_hash}, "
                f"parent_ordinal={self.parent_ordinal}, salt={self.salt}, "
                f"transaction_hash={self.transaction_hash}, status={self.status})")


class NetworkInfo:
    def __init__(self, network_id="mainnet", be_url=None, l0_host=None, cl1_host=None, l0_lb_url=None, l1_lb_url=None):
        self.network_id = network_id.lower()

        if self.network_id in ("mainnet", "integrationnet", "testnet"):
            self.be_url = be_url or f"https://be-{self.network_id}.constellationnetwork.io"
            self.l0_lb_url = l0_lb_url or f"https://l0-lb-{self.network_id}.constellationnetwork.io"
            self.l1_lb_url = l1_lb_url or f"https://l1-lb-{self.network_id}.constellationnetwork.io"
        else:
            self.be_url = be_url
            self.l0_lb_url = l0_lb_url
            self.l1_lb_url = l1_lb_url

        self.l0_host = l0_host or self.l0_lb_url
        self.cl1_host = cl1_host or self.l1_lb_url

    def __repr__(self):
        return (f"NetworkInfo(network_id={self.network_id}, be_url={self.be_url}, "
                f"l0_host={self.l0_host}, cl1_host={self.cl1_host}, "
                f"l0_lb_url={self.l0_lb_url}, l1_lb_url={self.l1_lb_url})")


def ddag_to_dag(balance: int):
    """Convert dDAG value to DAG value"""
    if balance != 0:
        return float(balance / 100000000)
    elif balance == 0:
        return 0
    else:
        raise ValueError("Network Model :: Balance can't be below 0.")


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

class Proof:
    id: str
    signature: str

    @classmethod
    def process_snapshot_proofs(cls, response: list):
        results = []
        for item in response:
            cls.id = item["id"]
            cls.signature = item["signature"]

            results.append(cls)
        return results

class GlobalSnapshot:

    def __init__(self, response):
        print(response)
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

class TransactionValue:
    def __init__(self, source: str, destination: str, amount: int, fee: int, parent: Dict, salt: int):
        self.source = source
        self.destination = destination
        self.amount = amount
        self.fee = fee
        self.parent = parent
        self.salt = salt

class Transaction:
    def __init__(self, data: dict):
        self.value = TransactionValue(**data["value"])
        self.proofs = data["proofs"] or []

    def add_proof(self, proof: Proof):
        self.proofs.append(proof)


class BETransaction:
    def __init__(
        self,
        hash: str,
        amount: float,
        source: str,
        destination: str,
        fee: float,
        parent: dict,
        salt: int,
        block_hash: str,
        snapshot_hash: str,
        snapshot_ordinal: int,
        transaction_original: "Transaction",
        timestamp: datetime,
        proofs: List = None,
    ):
        self.hash = hash
        self.amount = amount
        self.source = source
        self.destination = destination
        self.fee = fee
        self.parent = parent
        self.salt = salt
        self.block_hash = block_hash
        self.snapshot_hash = snapshot_hash
        self.snapshot_ordinal = snapshot_ordinal
        self.transaction_original = transaction_original
        self.timestamp = timestamp
        self.proofs = proofs or []

    @classmethod
    def process_be_transactions(cls, response: List[dict]) -> List["BETransaction"]:
        transactions = []
        for be_tx in response:
            print(be_tx)
            transaction = cls(
                hash=be_tx["hash"],
                amount=ddag_to_dag(be_tx["amount"]),
                source=be_tx["source"],
                destination=be_tx["destination"],
                fee=ddag_to_dag(be_tx["fee"]),
                parent=be_tx["parent"],
                salt=be_tx["salt"],
                block_hash=be_tx["blockHash"],
                snapshot_hash=be_tx["snapshotHash"],
                snapshot_ordinal=be_tx["snapshotOrdinal"],
                transaction_original=Transaction(be_tx["transactionOriginal"]),
                timestamp=datetime.fromisoformat(be_tx["timestamp"]),
                proofs=be_tx.get("proofs", []),
            )
            transactions.append(transaction)
        return transactions