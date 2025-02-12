from typing import Optional, List, Type

from pypergraph.dag_core.convert import ddag_to_dag


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
    def process_cluster_info(cls, response: List) -> list[Type["ClusterInfo"]]:
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


class TotalSupply:

    def __init__(self, response: dict):
        self.ordinal: int = response.get("ordinal")
        self.total_supply: int | float = ddag_to_dag(response.get("total"))

    def __repr__(self):
        return f"TotalSupply(ordinal={self.ordinal}, balance={self.total_supply})"

