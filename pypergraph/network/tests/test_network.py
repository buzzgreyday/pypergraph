import time

import httpx
import pytest
import random

import requests
from httpx import ReadTimeout

import pypergraph.account
from pypergraph.core.exceptions import NetworkError
from pypergraph.keystore import KeyStore
from pypergraph.network.models.network import NetworkInfo
from pypergraph.network import DagTokenNetwork
from pypergraph.network.models.transaction import SignedData, TransactionReference, SignatureProof


@pytest.fixture
def network():
    return DagTokenNetwork()

""" NETWORK CONFIGURATION """

@pytest.mark.parametrize("network_id, expected", [
    ("testnet", NetworkInfo(
        network_id='testnet',
        block_explorer_url='https://be-testnet.constellationnetwork.io',
        l0_host='https://l0-lb-testnet.constellationnetwork.io',
        currency_l1_host='https://l1-lb-testnet.constellationnetwork.io'
        )
    ),
    ("integrationnet", NetworkInfo(
        network_id='integrationnet',
        block_explorer_url='https://be-integrationnet.constellationnetwork.io',
        l0_host='https://l0-lb-integrationnet.constellationnetwork.io',
        currency_l1_host='https://l1-lb-integrationnet.constellationnetwork.io'
        )
    ),
    ("mainnet", NetworkInfo(
        network_id='mainnet',
        block_explorer_url='https://be-mainnet.constellationnetwork.io',
        l0_host='https://l0-lb-mainnet.constellationnetwork.io',
        currency_l1_host='https://l1-lb-mainnet.constellationnetwork.io'
        )
    ),
    (None, NetworkInfo(
        network_id='mainnet',
        block_explorer_url='https://be-mainnet.constellationnetwork.io',
        l0_host='https://l0-lb-mainnet.constellationnetwork.io',
        currency_l1_host='https://l1-lb-mainnet.constellationnetwork.io'
        )
    )
])

def test_init_network(network_id, expected):
    net = DagTokenNetwork(network_id) if network_id else DagTokenNetwork()
    assert net.get_network() == expected.__dict__

@pytest.mark.asyncio
async def test_init_custom(network):
    try:
        l0_api_cluster_data = [[d.ip, d.public_port] for d in await network.l0_api.get_cluster_info()]
        if not l0_api_cluster_data:
            pytest.skip("No L0 cluster nodes available")
        l0_api_cluster_node = random.choice(l0_api_cluster_data)
        l1_api_cluster_data = [[d.ip, d.public_port] for d in await network.cl1_api.get_cluster_info()]
        if not l1_api_cluster_data:
            pytest.skip("No L1 cluster nodes available")
        l1_api_cluster_node = random.choice(l1_api_cluster_data)

        net = DagTokenNetwork(
            network_id="mainnet",
            l0_host=f"http://{l0_api_cluster_node[0]}:{l0_api_cluster_node[1]}",
            currency_l1_host=f"http://{l1_api_cluster_node[0]}:{l1_api_cluster_node[1]}"
        )

        expected = NetworkInfo(
            network_id="mainnet",
            block_explorer_url='https://be-mainnet.constellationnetwork.io',
            l0_host=f"http://{l0_api_cluster_node[0]}:{l0_api_cluster_node[1]}",
            currency_l1_host=f"http://{l1_api_cluster_node[0]}:{l1_api_cluster_node[1]}"
        )
        assert net.get_network() == vars(expected)

    except httpx.ReadTimeout:
        pytest.skip("Timeout")

def test_config_network(network):
    assert network.connected_network.network_id == "mainnet"
    network.config("integrationnet")
    expected = NetworkInfo(
        network_id='integrationnet',
        block_explorer_url='https://be-integrationnet.constellationnetwork.io',
        l0_host='https://l0-lb-integrationnet.constellationnetwork.io',
        currency_l1_host='https://l1-lb-integrationnet.constellationnetwork.io'
    )
    assert network.get_network() == expected.__dict__

""" Block Explorer """

@pytest.mark.asyncio
async def test_get_latest_snapshot(network):
    result = await network.get_latest_snapshot()
    assert isinstance(result.hash, str)
    assert result.ordinal >= 3921360


@pytest.mark.asyncio
async def test_get_snapshot_by_id(network):
    result = await network.be_api.get_snapshot(
        "2404170"
    )

    model = result.model_dump()
    del model["timestamp"]
    assert model == {
        'hash': '3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708',
        'ordinal': 2404170,
        'height': 29108,
        'sub_height': 11,
        'last_snapshot_hash': '9ec173e487b16958f276d1bb7a84f7aede3d0b8cbb01925b2f1ae76b92a4f662',
        'blocks': [
            '0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a',
            'b058dbf4f5f1994db57b60d24ea06204dae754cad95df5d4a0fe0bb02c815aa9',
            '6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063',
            '8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3'
        ]#,
        #'timestamp': datetime.datetime(2024, 7, 16, 22, 37, 37, 697000, tzinfo=datetime.timezone.utc)
    }
    assert result.hash and result.timestamp and result.ordinal, "Snapshot data should not be empty"

@pytest.mark.asyncio
async def test_get_transactions_by_snapshot(network):
    results = await network.be_api.get_transactions_by_snapshot("2404170")
    assert (results[0].source == "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz" and
            results[0].destination == "DAG29HwuP2PKU8SBj38x5qq2Z4JcgvKkXA7QS71F" and
            results[0].amount == 100000000), "Transaction data should not be empty"

@pytest.mark.asyncio
async def test_get_rewards_by_snapshot(network):
    results = await network.be_api.get_rewards_by_snapshot(2404170)
    assert (results[0].destination == "DAG8nfZEeGaQAZfVsr3BFYMq8THb3XCTr36g3fGs" and
            results[0].amount == 24020206), "Snapshot data should not be empty"

@pytest.mark.asyncio
async def test_get_latest_snapshot_transactions(network):
    results = await network.be_api.get_latest_snapshot_transactions()
    assert isinstance(results, list), "Snapshot data should be a list"

@pytest.mark.asyncio
async def test_get_latest_snapshot_rewards(network):
    results = await network.be_api.get_latest_snapshot_rewards()
    assert isinstance(results, list), "Snapshot data should be a list"

@pytest.mark.asyncio
async def test_get_transactions(network):
    num_of_snapshots = 12
    results = await network.be_api.get_transactions(limit=num_of_snapshots)
    assert len(results) == num_of_snapshots, "Snapshot data should be a list"

@pytest.mark.asyncio
async def test_get_transaction(network):
    result = await network.be_api.get_transaction(
        "dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e"
    )
    model = result.model_dump()
    del model['timestamp']
    assert model == {
        'source': 'DAG2AhT8r7JoQb8fJNEKFLNEkaRSxjNmZ6Bbnqmb',
        'destination': 'DAG7b166Y3dzREaLxfTsrFdbwzScxHZSdVrQaQUA',
        'amount': 25000110000000,
        'fee': 0,
        'hash': 'dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e',
        'parent': {
            'ordinal': 77,
            'hash': 'ff765b26b12e2f63fbda7d33efb6728be3dec86856fb85922c8fa2d8d7062555'
        },
        'salt': None,
        'block_hash': '85f034cf2df202ced872da05ef3eaf00cd1117e0f8deef9d56022505457072e9',
        'snapshot_hash': 'baa81574222c46c9ac37baa9eeea97b83f4f02aa46e187b19064a64188f5132f',
        'snapshot_ordinal': 2829094,
        'transaction_original': {
            'value': {
                'source': 'DAG2AhT8r7JoQb8fJNEKFLNEkaRSxjNmZ6Bbnqmb',
                'destination': 'DAG7b166Y3dzREaLxfTsrFdbwzScxHZSdVrQaQUA',
                'amount': 25000110000000,
                'fee': 0,
                'parent': {
                    'ordinal': 77,
                    'hash': 'ff765b26b12e2f63fbda7d33efb6728be3dec86856fb85922c8fa2d8d7062555'
                },
                'salt': 8940539553876237,
                'encoded': '240DAG2AhT8r7JoQb8fJNEKFLNEkaRSxjNmZ6Bbnqmb40DAG7b166Y3dzREaLxfTsrFdbwzScxHZSdVrQaQUA1216bccaad078064ff765b26b12e2f63fbda7d33efb6728be3dec86856fb85922c8fa2d8d706255527710141fc35f9435890d'
            },
            'proofs': [
                {
                    'id': '0c56484b24a71a08f505493ede440aead8bd85f94402693d963dd5161c2c42ee638c7c89a500f8cb86c05fb69c8650e297b101851951108b1b77e3ee8b6df5ab',
                    'signature': '30440220537019100fce3f7dd150beb52f7de2e887e44712e08073e5808debc5871a4394022026a96f644f378fb74a96f6aed520a3e606d0fbd5af89ecb402dac8087006ea1b'
                }
            ]
        },
        # 'timestamp': datetime.datetime(2024, 9, 15, 18, 47, 33, 82000, tzinfo=TzInfo(UTC)), Removed for testing purposes
        'proofs': [],
        'meta': None
    }

@pytest.mark.asyncio
async def test_get_latest_currency_snapshot(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    result = await network.be_api.get_latest_currency_snapshot(el_paca_metagraph_id)
    assert isinstance(result.hash, str)
    assert result.ordinal >= 1032801
    assert result.fee >= 0

@pytest.mark.asyncio
async def test_get_currency_snapshot(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    result = await network.be_api.get_currency_snapshot(el_paca_metagraph_id, 950075)
    model = result.model_dump()
    del model["timestamp"]
    assert model == {
        'hash': 'd412e81203f6a3dfaf5c9c442ccdc8e80524ba3ffb7e0a2f832920d39d590e12',
        'ordinal': 950075,
        'height': 754,
        'sub_height': 2250,
        'last_snapshot_hash': '05d473f31887b1e556ac7742b397becbdf5e717abd9ce0aa7f1133ebb48c27c0',
        'blocks': [],
        #'timestamp': datetime.datetime(2025, 2, 12, 13, 52, 37, 633000, tzinfo=datetime.timezone.utc),
        'fee': 500000,
        'owner_address': 'DAG5VxUBiDx24wZgBwjJ1FeuVP1HHVjz6EzXa3z6',
        'staking_address': None,
        'size_in_kb': 5,
        'meta': None
    }

@pytest.mark.asyncio
async def test_get_latest_currency_snapshot_rewards(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_latest_currency_snapshot_rewards(el_paca_metagraph_id)
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_get_currency_snapshot_rewards(network):
    from pypergraph.network.models.reward import RewardTransaction
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_currency_snapshot_rewards(el_paca_metagraph_id, 950075)
    assert results == [
        RewardTransaction(destination='DAG2ACig4MuEPit149J1mEjhYqwn8SBvXgVuy2aX', amount=300000000),
        RewardTransaction(destination='DAG2YaNbtUv35YVjJ5U6PR9r8obVunEky2RDdGJb', amount=100000000),
        RewardTransaction(destination='DAG3dQwyG69DmcXxqAQzfPEp39FEfepc3iaGGQVg', amount=200000000),
        RewardTransaction(destination='DAG4eVyr7kUzr7r2oPoxnUfLDgugdXYXLDh6gxZS', amount=200000000)
    ]

@pytest.mark.asyncio
async def test_get_currency_address_balance(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    result = await network.be_api.get_currency_address_balance(
        metagraph_id=el_paca_metagraph_id,
        hash="b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364",
    )
    assert hasattr(result, "balance")

@pytest.mark.asyncio
async def test_get_currency_transaction(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    result = await network.be_api.get_currency_transaction(
        metagraph_id=el_paca_metagraph_id,
        hash="121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
    )
    assert hasattr(result, "destination")

@pytest.mark.asyncio
async def test_get_currency_transactions(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_currency_transactions(metagraph_id=el_paca_metagraph_id, limit=10)
    assert len(results) == 10

@pytest.mark.asyncio
async def test_get_currency_transactions_by_address(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_currency_transactions_by_address(
        metagraph_id=el_paca_metagraph_id, address="DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY", limit=10
    )
    assert len(results) == 10

@pytest.mark.asyncio
async def test_get_currency_transactions_by_snapshot(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_currency_transactions_by_snapshot(
        metagraph_id=el_paca_metagraph_id, hash_or_ordinal=952394, limit=10
    )
    assert len(results) == 1


""" L0 API """

@pytest.mark.asyncio
async def test_get_address_balance(network):
    address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
    result = await network.get_address_balance(address)
    assert result.balance >= 0

@pytest.mark.asyncio
async def test_get_total_supply(network):
    try:
        result = await network.l0_api.get_total_supply()
        assert bool(result.total_supply)
    except (httpx.ReadTimeout, NetworkError) as e:
        pytest.skip(f"Error: {e}")

@pytest.mark.asyncio
async def test_get_cluster_info(network):
    try:
        result = await network.l0_api.get_cluster_info()
        assert bool(result)
    except (httpx.ReadTimeout, NetworkError) as e:
        pytest.skip(f"Error: {e}")


@pytest.mark.asyncio
async def test_get_latest_l0_snapshot(network):
    try:
        result = await network.l0_api.get_latest_snapshot()
        print(result)
    except (httpx.ReadTimeout, NetworkError) as e:
        pytest.skip(f"Error: {e}")

@pytest.mark.asyncio
async def test_get_latest_snapshot_ordinal(network):
    try:
        result = await network.l0_api.get_latest_snapshot_ordinal()
        assert result.ordinal >= 3953150
    except (httpx.ReadTimeout, NetworkError) as e:
        pytest.skip(f"Error: {e}")


""" L1 API """

@pytest.mark.asyncio
async def test_get_l1_cluster_info(network):
    try:
        results = await network.cl1_api.get_cluster_info()
    except ReadTimeout as e:
        pytest.skip(f'Timeout: {e}')
    else:
        assert isinstance(results, list)

@pytest.mark.asyncio
async def test_get_last_ref(network):
    address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
    result = await network.get_address_last_accepted_transaction_ref(address)
    assert result.ordinal >= 5 and isinstance(result.hash, str)

@pytest.mark.asyncio
async def test_get_pending(network):
    try:
        result = await network.get_pending_transaction(
            hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429"
        )
    except ReadTimeout as e:
        pytest.skip(f'Timeout: {e}')
    else:
        if result:
            pytest.skip(f"Pending transaction: {result}")
        else:
            pytest.skip("No pending transactions.")

@pytest.mark.asyncio
async def test_post_transaction(network):
    from .secret import mnemo, to_address
    account = pypergraph.account.DagAccount()
    account.connect(network_id="integrationnet")

    if account.network.connected_network.network_id == "integrationnet":
        account.login_with_seed_phrase(mnemo)
        tx, hash_ = await account.generate_signed_transaction(
            to_address=to_address,
            amount=100000000,
            fee=200000000
        )

        try:
            await account.network.post_transaction(tx)
        except (httpx.NetworkError, NetworkError) as e:
            if any(msg in str(e) for msg in ["InsufficientBalance", "TransactionLimited"]):
                pytest.skip(f"Skipping due to expected error: {e}")
            raise

@pytest.mark.asyncio
async def test_post_metagraph_currency_transaction(network):
    from .secret import mnemo, to_address, from_address
    account = pypergraph.account.DagAccount()
    account.login_with_seed_phrase(mnemo)
    account_metagraph_client = pypergraph.account.MetagraphTokenClient(
        account=account,
        metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
        currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200"
    )
    try:
        # Generate signed tx
        last_ref = await account_metagraph_client.network.get_address_last_accepted_transaction_ref(address=from_address)
        tx, hash_ = await account_metagraph_client.account.generate_signed_transaction(
            to_address=to_address, amount=100000000, fee=0, last_ref=last_ref
        )
        await account_metagraph_client.network.post_transaction(tx=tx)
    except (httpx.NetworkError, NetworkError) as e:
            if any(msg in str(e) for msg in ["InsufficientBalance", "TransactionLimited"]):
                pytest.skip(f"Skipping due to expected error: {e}")
            raise
    except httpx.ReadTimeout:
        pytest.skip("Skipping due to timeout")

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
                "dueDate": str(int((now + timedelta(milliseconds=one_day_in_millis)).timestamp() * 1000)),
                "optStatus": {
                    "type": "InProgress"
                }
            }
        }

    def build_voting_poll_tx():
        """ VOTING TEMPLATE """
        return {
           "CreatePoll": {
               "name": 'test_poll',
               "owner": f'{from_address}',
               "pollOptions": [ 'true', 'false' ],
               "startSnapshotOrdinal": 1000, #start_snapshot, you should replace
               "endSnapshotOrdinal": 100000 #end_snapshot, you should replace
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
        account=account, metagraph_id=METAGRAPH_ID, l0_host=L0, currency_l1_host=CL1, data_l1_host=DL1
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
    proof = {
        "id": public_key,
        "signature": signature
    }
    tx = {
    "value": msg,
    "proofs": [
        proof
    ]
    }

    #tx = SignedData(value=msg, proofs=[SignatureProof(**proof)])

    encoded_msg = keystore.encode_data(msg=msg, prefix=False)
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
    encoded_msg = keystore.encode_data(msg=false_msg, prefix=False)
    assert not keystore.verify_data(public_key, encoded_msg, signature)
    encoded_msg = keystore.encode_data(msg=msg, prefix=False, encoding='base64')
    assert not keystore.verify_data(public_key, encoded_msg, signature)
    encoded_msg = keystore.encode_data(msg=msg)
    assert not keystore.verify_data(public_key, encoded_msg, signature)


    try:
        r = await account_metagraph_client.network.post_data(tx)
        assert 'hash' in r
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


#def test_get_money():
#    from .secret import from_address
#    print(requests.get(f"https://faucet.constellationnetwork.io/testnet/faucet/{from_address}").text)
#    print(requests.get(f"https://faucet.constellationnetwork.io/integrationnet/faucet/{from_address}").text)