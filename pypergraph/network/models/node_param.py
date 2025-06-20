from typing import List

from pydantic import BaseModel, Field, constr

from pypergraph.network.models.transaction import SignatureProof


class UpdateNodeParametersReference(BaseModel):
    ordinal: int
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")


class NodeMetadataParameters(BaseModel):
    name: str
    description: str


class DelegatedStakeRewardParameters(BaseModel):
    reward_fraction: int = Field(alias="rewardFraction", ge=0, le=100000000)


class UpdateNodeParameters(BaseModel):
    source: str
    delegated_stake_reward_parameters: DelegatedStakeRewardParameters = Field(
        alias="delegatedStakeRewardParameters"
    )
    nodeMetadataParameters: NodeMetadataParameters = Field(
        alias="nodeMetadataParameters"
    )
    parent: UpdateNodeParametersReference


class SignedUpdateNodeParameters(BaseModel):
    value: UpdateNodeParameters
    proofs: List[SignatureProof]


class NodeParametersInfo(BaseModel):
    node: str
    delegated_stake_reward_parameters: DelegatedStakeRewardParameters = Field(
        alias="delegatedStakeRewardParameters"
    )
    node_metadata_parameters: NodeMetadataParameters = Field(
        alias="nodeMetadataParameters"
    )
    total_amount_delegated: int = Field(alias="totalAmountDelegated", ge=0)
    total_addresses_assigned: int = Field(alias="totalAddressesAssigned", ge=0)

    @classmethod
    def process_node_parameters(cls, data: List[dict]) -> List["NodeParametersInfo"]:
        return [cls.model_validate(item) for item in data]
