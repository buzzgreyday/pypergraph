import time

import httpx
import pytest

import pypergraph.account
from pypergraph.core.exceptions import NetworkError
from pypergraph.keystore import KeyStore


""" L1 API """


@pytest.mark.asyncio
async def test_post_metagraph_data_transaction(network):
    # TODO: error handling and documentation
    # Encode message according to serializeUpdate on your template module l1.
    #
    # 1. The TO-DO, SOCIAL and WATER AND ENERGY template doesn't add the signing prefix, it only needs the transaction to be formatted as string without spaces and None values:
    #     # encoded = json.dumps(tx_value, separators=(',', ':'))
    #     signature, hash_ = keystore.data_sign(pk, encoded, prefix=False) # Default encoding = "hex"
    # 2. The VOTING and NFT template does use the dag4JS dataSign (prefix=True), the encoding (before data_sign) is done first by stringifying, then converting to base64:
    #     # encoded = json.dumps(tx_value, separators=(',', ':'))
    #     # encoded = base64.b64encode(encoded.encode()).decode()
    #     signature, hash_ = keystore.data_sign(pk, tx_value, prefix=True, encoding="base64") # Default prefix is True
    # 3. The TO-DO, SOCIAL and WATER AND ENERGY template doesn't add the signing prefix, it only needs the transaction to be formatted as string without spaces and None values:
    #     # encoded = json.dumps(tx_value, separators=(',', ':'))
    #     signature, hash_ = keystore.data_sign(pk, encoded, prefix=False) # Default encoding = "hex"
    # X. Inject a custom encoding function:
    #     def encode(msg: dict):
    #         return json.dumps(tx_value, separators=(',', ':'))
    #
    #     signature, hash_ = keystore.data_sign(pk, tx_value, prefix=False, encoding=encode)

    from .secret import mnemo, from_address

    def build_todo_tx():
        """TO-DO TEMPLATE"""
        # Build the signature request
        from datetime import datetime

        now = datetime.now()
        one_day_in_millis = 24 * 60 * 60 * 1000
        from datetime import timedelta

        return {
            "CreateTask": {
                "description": "This is a task description",
                "dueDate": str(
                    int(
                        (now + timedelta(milliseconds=one_day_in_millis)).timestamp()
                        * 1000
                    )
                ),
                "optStatus": {"type": "InProgress"},
            }
        }

    def build_voting_poll_tx():
        """VOTING TEMPLATE"""
        return {
            "CreatePoll": {
                "name": "test_poll",
                "owner": f"{from_address}",
                "pollOptions": ["true", "false"],
                "startSnapshotOrdinal": 1000,  # start_snapshot, you should replace
                "endSnapshotOrdinal": 100000,  # end_snapshot, you should replace
            }
        }

    def build_water_and_energy_usage_tx():
        return {
            "address": f"{from_address}",
            "energyUsage": {
                "usage": 7,
                "timestamp": int(time.time() * 1000),
            },
            "waterUsage": {
                "usage": 7,
                "timestamp": int(time.time() * 1000),
            },
        }

    METAGRAPH_ID = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    L0 = "http://localhost:9200"
    CL1 = "http://localhost:9300"
    DL1 = "http://localhost:9400"
    account = pypergraph.account.DagAccount()
    account.login_with_seed_phrase(mnemo)
    account_metagraph_client = pypergraph.account.MetagraphTokenClient(
        account=account,
        metagraph_id=METAGRAPH_ID,
        l0_host=L0,
        currency_l1_host=CL1,
        data_l1_host=DL1,
    )
    keystore = KeyStore()
    pk = keystore.get_private_key_from_mnemonic(phrase=mnemo)

    # todo_tx_value = build_todo_tx()
    # poll_tx_value = build_voting_poll_tx()
    water_and_energy_tx_value = build_water_and_energy_usage_tx()

    msg = water_and_energy_tx_value

    """ TO-DO """
    # signature, hash_ = keystore.data_sign(pk, msg, prefix=False) # Default encoding = json.dumps(msg, separators=(',', ':'))
    """ VOTING POLL """
    # signature, hash_ = keystore.data_sign(pk, tx_value, encoding="base64") # Default prefix is True
    """ WATER AND ENERGY """
    signature, hash_ = keystore.data_sign(pk, msg, prefix=False)
    """ TO-DO "CUSTOM" """
    # def encode(data: dict):
    #     return json.dumps(msg, separators=(',', ':'))
    # signature, hash_ = keystore.data_sign(pk, msg, prefix=False, encoding=encode)

    public_key = account_metagraph_client.account.public_key[2:]  # Remove '04' prefix
    proof = {"id": public_key, "signature": signature}
    tx = {"value": msg, "proofs": [proof]}

    # tx = SignedData(value=msg, proofs=[SignatureProof(**proof)])

    encoded_msg = keystore._encode_data(msg=msg, prefix=False)
    assert keystore.verify_data(public_key, encoded_msg, signature)
    false_msg = {
        "address": f"{from_address}",
        "energyUsage": {
            "usage": 5,
            "timestamp": int(time.time() * 1000),
        },
        "waterUsage": {
            "usage": 1,
            "timestamp": int(time.time() * 1000),
        },
    }
    encoded_msg = keystore._encode_data(msg=false_msg, prefix=False)
    assert not keystore.verify_data(public_key, encoded_msg, signature)
    encoded_msg = keystore._encode_data(msg=msg, prefix=False, encoding="base64")
    assert not keystore.verify_data(public_key, encoded_msg, signature)
    encoded_msg = keystore._encode_data(msg=msg)
    assert not keystore.verify_data(public_key, encoded_msg, signature)

    try:
        r = await account_metagraph_client.network.post_data(tx)
        assert "hash" in r
        # Returns the full response from the metagraph
    except (httpx.ConnectError, httpx.ReadTimeout):
        pytest.skip("No locally running Metagraph")
    except KeyError:
        pytest.fail(f"Post data didn't return a hash, returned value: {r}")


@pytest.mark.asyncio
async def test_get_metrics(network):
    try:
        r = await network.l0_api.get_metrics()
        for x in r:
            print(x)
        assert isinstance(r, list)
    except httpx.ReadTimeout:
        pytest.skip("Timeout")


# def test_get_money():
#    from .secret import from_address
#    print(requests.get(f"https://faucet.constellationnetwork.io/testnet/faucet/{from_address}").text)
#    print(requests.get(f"https://faucet.constellationnetwork.io/integrationnet/faucet/{from_address}").text)
