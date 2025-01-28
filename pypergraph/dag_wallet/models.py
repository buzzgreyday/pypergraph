from typing import Optional
from pydantic import BaseModel, model_validator, Field
from pypergraph.dag_core.constants import KeyringNetwork

class NetworkInfo(BaseModel):
    # TODO: KeyringNetwork should be renamed to fit globallly?
    network: str = Field(default=KeyringNetwork.Constellation.value, description="'Constellation', 'Ethereum' (unsupported)")
    network_id: str = Field(default="mainnet", description="The ID name of the network (Constellation: 'mainnet, testnet, 'integrationnet'; Ethereum (unsupported): 'sepolia', ...).")
    be_url: Optional[str] = Field(default=None, description="Block explorer URL.")
    l0_host: str = Field(..., description="Layer 0 host URL or IP:PORT.")
    cl1_host: str = Field(..., description="Layer 1 host URL or IP:PORT.")
    l0_lb_url: Optional[str] = Field(default=None, description="Layer 0 load balancer URL.")
    l1_lb_url: Optional[str] = Field(default=None, description="Layer 1 load balancer URL.")

    @model_validator(mode="before")
    def populate_missing_fields(cls, values):
        # Ensure network_id has a default and is normalized
        values["network"] = values["network"] or values.get("network", KeyringNetwork.Constellation.value)
        network_id = values.get("network_id", "mainnet").lower()

        values["be_url"] = None if 'be_url' not in values else values["be_url"]
        values["l0_lb_url"] = None if 'l0_lb_url' not in values else values["l0_lb_url"]
        values["l1_lb_url"] = None if 'l1_lb_url' not in values else values["l1_lb_url"]

        # Populate default URLs based on network_id
        # TODO: Networks should not be hardcoded
        if network_id in ("mainnet", "integrationnet", "testnet"):
            values["be_url"] = values["be_url"] or f"https://be-{network_id}.constellationnetwork.io"
            values["l0_lb_url"] = values["l0_lb_url"] or f"https://l0-lb-{network_id}.constellationnetwork.io"
            values["l1_lb_url"] = values["l1_lb_url"] or f"https://l1-lb-{network_id}.constellationnetwork.io"

        # Ensure l0_host and cl1_host have fallbacks
        values["l0_host"] = values.get("l0_host") or values.get("l0_lb_url")
        values["cl1_host"] = values.get("cl1_host") or values.get("l1_lb_url")

        return values