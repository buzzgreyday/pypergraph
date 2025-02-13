from typing import Optional, List

from pydantic import Field, BaseModel


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


class PeerInfo(BaseModel):
    alias: Optional[str] = None
    id: str
    ip: str
    state: str
    session: str
    public_port: int = Field(..., alias="publicPort")
    p2p_port: int = Field(..., alias="p2pPort")
    reputation: Optional[float] = None

    def __repr__(self) -> str:
        return (
            f"PeerInfo(alias={self.alias!r}, id={self.id!r}, ip={self.ip!r}, "
            f"state={self.state!r}, session={self.session!r}, "
            f"public_port={self.public_port!r}, p2p_port={self.p2p_port!r}, "
            f"reputation={self.reputation!r})"
        )

    @classmethod
    def process_cluster_peers(cls, data: List[dict]) -> List["PeerInfo"]:
        return [cls.model_validate(item) for item in data]


class TotalSupply(BaseModel):
    ordinal: int
    total_supply: int = Field(..., alias="total")

    def __repr__(self):
        return f"TotalSupply(ordinal={self.ordinal}, total_supply={self.total_supply})"


