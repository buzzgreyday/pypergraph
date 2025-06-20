from typing import Optional, Any, List

from pypergraph.account.models.key_trio import KeyTrio
from pypergraph.account.utils import normalize_public_key
from pypergraph.network.models.allow_spend import AllowSpend, SignedAllowSpend
from pypergraph.network.models.token_lock import TokenLock, SignedTokenLock


async def allow_spend(
    destination: str,
    amount: int,
    approvers: List[str],
    network: Any,  # Should be a shared abstract class DagTokenNetwork, MetagraphTokenNetwork
    key_trio: KeyTrio,
    source: Optional[str] = None,
    fee: int = 0,
    currency_id: Optional[str] = None,
    valid_until_epoch: Optional[int] = None,
):
    from pypergraph import KeyStore

    # Validate schemas
    # Validate source address
    if source != key_trio.address:
        raise ValueError('"source" must be the same as the account address')

    try:
        # Get last reference
        allow_spend_last_ref = await network.cl1_api.get_allow_spend_last_reference(
            key_trio.address
        )
        if not allow_spend_last_ref:
            raise ValueError("Unable to find allow spend last reference")
        body = AllowSpend(
            source=source,
            destination=destination,
            approvers=approvers,
            amount=amount,
            fee=fee or 0,
            parent=allow_spend_last_ref,
            last_valid_epoch_progress=valid_until_epoch,
            currency=currency_id or None,
        )
        # Generate signature
        signed_allow_spend = KeyStore().brotli_sign(
            body=body.model_dump(),
            public_key=normalize_public_key(key_trio.public_key),
            private_key=key_trio.private_key,
        )
        if not signed_allow_spend:
            raise ValueError("Unable to generate signed allow spend")

        # Submit transaction
        allow_spend_response = await network.cl1_api.post_allow_spend(
            SignedAllowSpend(**signed_allow_spend)
        )
        if not allow_spend_response or not allow_spend_response.get("hash"):
            raise ValueError("Unable to get allow spend response")

        return allow_spend_response

    except Exception as e:
        # Handle specific error cases
        if "last reference" in str(e):
            print("Error getting the allow spend last reference")
        elif "generating" in str(e):
            print("Error generating the signed allow spend")
        elif "sending" in str(e):
            print("Error sending the allow spend transaction")
        raise


async def token_lock(
    source: str,
    amount: int,
    fee: int,
    currency_id: Optional[str],
    unlock_epoch: Optional[int],
    network: Any,  # Should be a shared abstract class DagTokenNetwork, MetagraphTokenNetwork
    key_trio: KeyTrio,
):
    from pypergraph import KeyStore
    # Validate schema

    # Validate source address
    if source != key_trio.address:
        raise ValueError('"source" must be the same as the account address')

    try:
        # Get last reference
        token_lock_last_ref = await network.cl1_api.get_token_lock_last_reference(
            key_trio.address
        )
        if not token_lock_last_ref:
            raise ValueError("Unable to find token lock last reference")
        body = TokenLock(
            source=source,
            amount=amount,
            fee=fee,
            parent=token_lock_last_ref,
            currency_id=currency_id,
            unlock_epoch=unlock_epoch,
        )

        # Generate signature
        signed_token_lock = KeyStore().brotli_sign(
            body=body.model_dump(),
            public_key=normalize_public_key(key_trio.public_key),
            private_key=key_trio.private_key,
        )
        if not signed_token_lock:
            raise ValueError("Unable to generate signed token lock")

        # Submit transaction
        token_lock_response = await network.cl1_api.post_token_lock(
            SignedTokenLock(**signed_token_lock)
        )
        if not token_lock_response or not token_lock_response.get("hash"):
            raise ValueError("Unable to get token lock response")

        return token_lock_response

    except Exception as e:
        # Handle specific error cases
        if "last reference" in str(e):
            print("Error getting the token lock last reference")
        elif "generating" in str(e):
            print("Error generating the signed token lock")
        elif "sending" in str(e):
            print("Error sending the token lock transaction")
        raise
