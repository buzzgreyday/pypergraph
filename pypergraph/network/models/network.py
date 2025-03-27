from typing import Optional, List

from pydantic import Field, BaseModel, IPvAnyNetwork, conint, constr

from pypergraph.core.constants import ALIAS_MAX_LEN, PORT_MAX

class NetworkInfo:
    def __init__(self, network_id="mainnet", block_explorer_url=None, l0_host=None, currency_l1_host=None, data_l1_host=None, metagraph_id=None):
        self.data_l1_host = None
        self.network_id = network_id.lower()

        if self.network_id in ("mainnet", "integrationnet", "testnet"):
            self.block_explorer_url = block_explorer_url or f"https://be-{self.network_id}.constellationnetwork.io"
        else:
            self.block_explorer_url = block_explorer_url

        self.l0_host = l0_host or f"https://l0-lb-{network_id}.constellationnetwork.io"
        self.currency_l1_host = currency_l1_host or f"https://l1-lb-{network_id}.constellationnetwork.io"
        self.data_l1_host = data_l1_host or self.data_l1_host
        self.metagraph_id = metagraph_id

    def __repr__(self):
        return (f"NetworkInfo(network_id={self.network_id}, block_explorer_url={self.block_explorer_url}, "
                f"l0_host={self.l0_host}, cl1_host={self.currency_l1_host}, dl1_host={self.data_l1_host}, "
                f"l0_lb_url={f'https://l0-lb-{self.network_id}.constellationnetwork.io'}, l1_lb_url={f'https://l1-lb-{self.network_id}.constellationnetwork.io'}, metagraph_id={self.metagraph_id})")


class PeerInfo(BaseModel):
    alias: Optional[str] = Field(default=None, max_length=ALIAS_MAX_LEN)
    id: constr(pattern=r"^[0-9a-f]{128}$")
    ip: IPvAnyNetwork
    state: str
    session: int
    public_port: conint(ge=0, le=PORT_MAX) = Field(..., alias="publicPort")
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
    ordinal: int = Field(..., ge=0)
    total_supply: int = Field(..., ge=0, alias="total")

    def __repr__(self):
        return f"TotalSupply(ordinal={self.ordinal}, total_supply={self.total_supply})"


class Ordinal(BaseModel):
    ordinal: int = Field(ge=0, alias="value")

    def __repr__(self):
        return f"Ordinal(value={self.value})"