from typing import List

from pydantic import constr, BaseModel, Field

from pypergraph.network.models.transaction import SignatureProof

"""
Methods
-------

    GET /delegated-stakes/{address}/info
    GET /delegated-stakes/last-reference/{address}
    GET /delegated-stakes/rewards-info
    POST /delegated-stakes
    PUT /delegated-stakes
    
"""


class DelegatedStakeReference(BaseModel):
    ordinal: int = Field(ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")


class CreateDelegatedStake(BaseModel):
    """Used as value in SignedCreateDelegatedStake"""

    source: str
    node_id: constr(pattern=r"^[a-fA-F0-9]{128}$") = Field(alias="nodeId")
    amount: int = Field(ge=0)
    fee: int = Field(ge=0)
    token_lock_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="tokenLockRef")
    parent: DelegatedStakeReference


class SignedCreateDelegatedStake(BaseModel):
    """
    For creating or updating delegated stake.

    To create a delegated stake, provide a tokenLockRef for a TokenLock with a null unlockEpoch value.

    To update an existing delegated stake record, you must provide the same tokenLockRef as the original stake with a new nodeId. The lock and rewards will be transferred to the new node without waiting for the unlock period.
    CREATE OR UPDATE: POST /delegated-stakes
    """

    value: CreateDelegatedStake
    proofs: List[SignatureProof]


class WithdrawDelegatedStake(BaseModel):
    source: str = Field()
    stake_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="stakeRef")


class SignedWithdrawDelegatedStake(BaseModel):
    """
    Withdraw a delegated stake.

    Withdraws the TokenLock balance and all available rewards after the unlock period.
    WITHDRAW: PUT /delegated-stakes
    """

    value: WithdrawDelegatedStake
    proofs: List[SignatureProof]


class DelegatedStakeInfo(BaseModel):
    node_id: constr(pattern=r"^[a-fA-F0-9]{128}$") = Field(alias="nodeId")
    accepted_ordinal: int = Field(alias="acceptedOrdinal", ge=0)
    token_lock_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="tokenLockRef")
    amount: int = Field(ge=0)
    fee: int = Field(ge=0)
    withdrawal_start_epoch: int = Field(alias="withdrawalStartEpoch", ge=0)
    withdrawal_end_epoch: int = Field(alias="withdrawalEndEpoch", ge=0)
    reward_amount: int = Field(alias="rewardAmount")
    total_balance: int = Field(alias="totalBalance")


class DelegatedStakesInfo(BaseModel):
    address: str
    active_delegated_stakes: List[DelegatedStakeInfo] = Field(
        alias="activeDelegatedStakes"
    )
    pending_withdrawals: List[DelegatedStakeInfo] = Field(alias="pendingWithdrawals")


class NextDagPrice(BaseModel):
    """Information about the next DAG price and when it will take effect"""

    price: int = Field(description="The next DAG price in datum/USD format", ge=0)
    as_of_epoch: int = Field(
        description="Progress throughout epochs used for rewards minting"
    )


class DelegatedRewardsInfo(BaseModel):
    """
    Information about rewards configuration on the network for calculating APY
    """

    epochs_per_year: int = Field(alias="epochsPerYear")
    current_dag_price: int = Field(
        description="Current DAG price in datum/USD format", alias="currentDagPrice"
    )
    next_dag_price: NextDagPrice = Field(alias="nextDagPrice")
    total_delegated_amount: int = Field(
        description="Total amount delegated across all active delegated stakes, including accrued rewards",
        alias="totalDelegatedAmount",
    )
    latest_average_reward_per_dag: int = Field(
        description="Average reward rate per DAG per epoch in datums",
        ge=0,
        alias="latestAverageRewardPerDag",
    )
    total_dag_amount: int = Field(
        description="Current total supply of all DAG balances in datums",
        alias="totalDagAmount",
    )
    total_rewards_per_latest_epoch: int = Field(
        description="Total incremental rewards added in the latest epoch in datums",
        ge=0,
    )
    total_rewards_per_year_estimate: int = Field(
        description="Total reward APY per DAG in datums (latestAverageRewardPerDag * epochsPerYear)"
    )
