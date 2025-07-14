import time
from ipaddress import IPv4Network

import httpx
import pytest
from pytest_httpx import HTTPXMock

from pypergraph.account import DagAccount, MetagraphTokenClient
from .secret import mnemo, to_address
from ... import KeyStore
from ...core.exceptions import NetworkError


@pytest.mark.mock
class TestMockedL1API:
    METAGRAPH_ID = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"

    @pytest.mark.asyncio
    async def test_get_l1_cluster_info(
        self, network, httpx_mock: HTTPXMock, mock_l1_api_responses
    ):
        network.config("integrationnet")
        httpx_mock.add_response(
            url="https://l1-lb-integrationnet.constellationnetwork.io/cluster/info",
            json=mock_l1_api_responses["cluster_info"],
        )
        results = await network.cl1_api.get_cluster_info()
        assert [r.model_dump() for r in results] == [
            {
                "alias": None,
                "id": "615b72d69facdbd915b234771cd4ffe49692a573f7ac05fd212701afe9b703eb8ab2ab117961f819e6d5eaf5ad073456cf56a0422c67b17606d95f50460a919d",
                "ip": IPv4Network("5.161.233.213/32"),
                "state": "Ready",
                "session": 1748983955866,
                "public_port": 9000,
                "p2p_port": 9001,
                "reputation": None,
            }
        ]

    @pytest.mark.asyncio
    async def test_get_last_ref(
        self, network, httpx_mock: HTTPXMock, mock_l1_api_responses
    ):
        network.config("integrationnet")
        address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
        httpx_mock.add_response(
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/last-reference/DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw",
            json=mock_l1_api_responses["last_ref"],
        )
        result = await network.get_address_last_accepted_transaction_ref(address)
        assert result.model_dump() == {
            "ordinal": 0,
            "hash": "0000000000000000000000000000000000000000000000000000000000000000",
        }

    @pytest.mark.asyncio
    async def test_get_not_pending(
        self, network, httpx_mock: HTTPXMock, mock_l1_api_responses
    ):
        # TODO: This might be deprecated
        network.config("integrationnet")
        httpx_mock.add_response(
            status_code=404,
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429",
        )
        result = await network.get_pending_transaction(
            hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429"
        )
        assert not result  # This transaction isn't pending.

    @pytest.mark.asyncio
    async def test_post_transaction_success(
        self, network, httpx_mock: HTTPXMock, mock_l1_api_responses
    ):
        network.config("integrationnet")
        httpx_mock.add_response(
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/last-reference/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
            json=mock_l1_api_responses["last_ref"],
        )
        account = DagAccount()
        account.connect(network_id="integrationnet")
        account.login_with_seed_phrase(mnemo)
        tx, hash_ = await account.generate_signed_transaction(
            to_address=to_address, amount=100000000, fee=200000000
        )
        httpx_mock.add_response(
            method="POST",
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions",  # adjust if needed
            json={"data": {"hash": hash_}},
            status_code=200,
        )
        r = await account.network.post_transaction(tx)
        assert r == hash_

    # @pytest.mark.asyncio
    # async def test_post_metagraph_currency_transaction(
    #     self, network, httpx_mock: HTTPXMock, mock_l1_api_responses
    # ):
    #     from .secret import mnemo, to_address, from_address
    #
    #     account = DagAccount()
    #     account.login_with_seed_phrase(mnemo)
    #     account_metagraph_client = MetagraphTokenClient(
    #         account=account,
    #         metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
    #         l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
    #         currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
    #     )
    #     httpx_mock.add_response(
    #         url="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200/transactions/last-reference/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
    #         json=mock_l1_api_responses["last_ref"],
    #     )
    #     # Generate signed tx
    #     last_ref = await account_metagraph_client.network.get_address_last_accepted_transaction_ref(
    #         address=from_address
    #     )
    #     tx, hash_ = await account_metagraph_client.account.generate_signed_transaction(
    #         to_address=to_address, amount=10000000, fee=2000000, last_ref=last_ref
    #     )
    #     httpx_mock.add_response(
    #         method="POST",
    #         url="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200/transactions",  # adjust if needed
    #         json={"data": {"hash": hash_}},
    #         status_code=200,
    #     )
    #     r = await account_metagraph_client.network.post_transaction(tx=tx)
    #     assert r == hash_

    @pytest.mark.asyncio
    async def test_post_voting_pool_metagraph_data_transaction_with_prefix_base64_encoding(
        self, network, httpx_mock: HTTPXMock
    ):
        """
        The VOTING and NFT template does use the dag4JS dataSign (prefix=True), the encoding (before data_sign) is done first by stringifying, then converting to base64:
        encoded = json.dumps(tx_value, separators=(',', ':'))
        encoded = base64.b64encode(encoded.encode()).decode()
        signature, hash_ = keystore.data_sign(pk, tx_value, prefix=True, encoding="base64") # Default prefix is True

        """
        from .secret import mnemo, from_address

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account_metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id=self.METAGRAPH_ID,
            l0_host="http://localhost:9200",
            currency_l1_host="http://localhost:9300",
            data_l1_host="http://localhost:9400",
        )
        keystore = KeyStore()
        pk = keystore.get_private_key_from_mnemonic(phrase=mnemo)

        msg = {
            "CreatePoll": {
                "name": "test_poll",
                "owner": f"{from_address}",
                "pollOptions": ["true", "false"],
                "startSnapshotOrdinal": 1000,  # start_snapshot, you should replace
                "endSnapshotOrdinal": 100000,  # end_snapshot, you should replace
            }
        }

        signature, hash_ = keystore.data_sign(
            pk, msg, encoding="base64"
        )  # Default prefix is True

        public_key = account_metagraph_client.account.public_key[
            2:
        ]  # Remove '04' prefix
        proof = {"id": public_key, "signature": signature}
        tx = {"value": msg, "proofs": [proof]}

        # Test verification: to verify msg, encoding must be done the same way
        encoded_msg = keystore.encode_data(msg=msg, encoding="base64")
        assert keystore.verify_data(public_key, encoded_msg, signature)
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:9400/data",  # adjust if needed
            json={"hash": hash_},
            status_code=200,
        )
        r = await account_metagraph_client.network.post_data(tx)
        assert "hash" in r

    @pytest.mark.asyncio
    async def test_post_water_energy_metagraph_data_transaction(
        self, network, httpx_mock: HTTPXMock
    ):
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
                            (
                                now + timedelta(milliseconds=one_day_in_millis)
                            ).timestamp()
                            * 1000
                        )
                    ),
                    "optStatus": {"type": "InProgress"},
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

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account_metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id=self.METAGRAPH_ID,
            l0_host="http://localhost:9200",
            currency_l1_host="http://localhost:9300",
            data_l1_host="http://localhost:9400",
        )
        keystore = KeyStore()
        pk = keystore.get_private_key_from_mnemonic(phrase=mnemo)

        # msg = build_todo_tx()
        msg = build_water_and_energy_usage_tx()

        """ TO-DO """
        # signature, hash_ = keystore.data_sign(pk, msg, prefix=False) # Default encoding = json.dumps(msg, separators=(',', ':'))
        """ WATER AND ENERGY """
        signature, hash_ = keystore.data_sign(pk, msg, prefix=False)
        """ TO-DO "CUSTOM" """
        # def encode(data: dict):
        #     return json.dumps(msg, separators=(',', ':'))
        # signature, hash_ = keystore.data_sign(pk, msg, prefix=False, encoding=encode)

        public_key = account_metagraph_client.account.public_key[
            2:
        ]  # Remove '04' prefix
        proof = {"id": public_key, "signature": signature}
        tx = {"value": msg, "proofs": [proof]}

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
        encoded_msg = keystore.encode_data(msg=msg, prefix=False, encoding="base64")
        assert not keystore.verify_data(public_key, encoded_msg, signature)
        encoded_msg = keystore.encode_data(msg=msg)
        assert not keystore.verify_data(public_key, encoded_msg, signature)
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:9400/data",  # adjust if needed
            json={"hash": hash_},
            status_code=200,
        )
        r = await account_metagraph_client.network.post_data(tx)
        assert r["hash"] == hash_


@pytest.mark.integration
class TestIntegrationL1API:
    METAGRAPH_ID = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"

    @pytest.mark.asyncio
    async def test_get_l1_cluster_info(self, network):
        network.config("integrationnet")
        results = await network.cl1_api.get_cluster_info()
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_get_last_ref(self, network):
        network.config("integrationnet")
        address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
        result = await network.get_address_last_accepted_transaction_ref(address)
        assert result.ordinal >= 0 and isinstance(result.hash, str)

    @pytest.mark.asyncio
    async def test_get_pending(self, network):
        # TODO: This might be deprecated
        network.config("integrationnet")
        result = await network.get_pending_transaction(
            hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429"
        )
        assert not result  # This transaction isn't pending.

    @pytest.mark.asyncio
    async def test_post_transaction(self, network, l1_transaction_error_msgs):
        account = DagAccount()
        account.connect(network_id="integrationnet")
        account.login_with_seed_phrase(mnemo)
        tx, hash_ = await account.generate_signed_transaction(
            to_address=to_address, amount=10000000, fee=200000000
        )

        try:
            response = await account.network.post_transaction(tx)
            assert response == hash_
        except NetworkError as e:
            for error, description in l1_transaction_error_msgs.items():
                if error in str(e):
                    pytest.skip(
                        f"Skipping due to expected error '{error}': {description}"
                    )
            raise

    @pytest.mark.asyncio
    async def test_post_metagraph_currency_transaction(
        self, network, l1_transaction_error_msgs
    ):
        from .secret import mnemo, to_address, from_address

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account_metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
            l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
            currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
        )
        try:
            # Generate signed tx
            last_ref = await account_metagraph_client.network.get_address_last_accepted_transaction_ref(
                address=from_address
            )
            (
                tx,
                hash_,
            ) = await account_metagraph_client.account.generate_signed_transaction(
                to_address=to_address, amount=10000000, fee=2000000, last_ref=last_ref
            )
            r = await account_metagraph_client.network.post_transaction(tx=tx)
            assert r == hash_
        except NetworkError as e:
            for error, description in l1_transaction_error_msgs.items():
                if error in str(e):
                    pytest.skip(
                        f"Skipping due to expected error '{error}': {description}"
                    )
            if e.status == 502:
                pytest.skip(
                    "Metagraph currency transaction skipped due to 'Bad Gateway'"
                )
            raise
        except httpx.ReadTimeout:
            pytest.skip("Skipping due to timeout")
        except httpx.ReadError:
            pytest.skip("Did not receive any data from the network.")

    @pytest.mark.asyncio
    async def test_post_voting_pool_metagraph_data_transaction_with_prefix_base64_encoding(
        self, network
    ):
        """
        The VOTING and NFT template does use the dag4JS dataSign (prefix=True), the encoding (before data_sign) is done first by stringifying, then converting to base64:
        encoded = json.dumps(tx_value, separators=(',', ':'))
        encoded = base64.b64encode(encoded.encode()).decode()
        signature, hash_ = keystore.data_sign(pk, tx_value, prefix=True, encoding="base64") # Default prefix is True

        """
        from .secret import mnemo, from_address

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account_metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id=self.METAGRAPH_ID,
            l0_host="http://localhost:9200",
            currency_l1_host="http://localhost:9300",
            data_l1_host="http://localhost:9400",
        )
        keystore = KeyStore()
        pk = keystore.get_private_key_from_mnemonic(phrase=mnemo)

        msg = {
            "CreatePoll": {
                "name": "test_poll",
                "owner": f"{from_address}",
                "pollOptions": ["true", "false"],
                "startSnapshotOrdinal": 1000,  # start_snapshot, you should replace
                "endSnapshotOrdinal": 100000,  # end_snapshot, you should replace
            }
        }

        signature, hash_ = keystore.data_sign(
            pk, msg, encoding="base64"
        )  # Default prefix is True

        public_key = account_metagraph_client.account.public_key[
            2:
        ]  # Remove '04' prefix
        proof = {"id": public_key, "signature": signature}
        tx = {"value": msg, "proofs": [proof]}

        encoded_msg = keystore.encode_data(msg=msg, encoding="base64")
        assert keystore.verify_data(public_key, encoded_msg, signature)

        try:
            r = await account_metagraph_client.network.post_data(tx)
            assert r["hash"] == hash_
            # Returns the full response from the metagraph
        except (httpx.ConnectError, httpx.ReadTimeout):
            pytest.skip("No locally running Metagraph")
        except KeyError:
            pytest.fail(f"Post data didn't return a hash, returned value: {r}")

    @pytest.mark.asyncio
    async def test_post_water_energy_metagraph_data_transaction(self, network):
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
                            (
                                now + timedelta(milliseconds=one_day_in_millis)
                            ).timestamp()
                            * 1000
                        )
                    ),
                    "optStatus": {"type": "InProgress"},
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

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account_metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id=self.METAGRAPH_ID,
            l0_host="http://localhost:9200",
            currency_l1_host="http://localhost:9300",
            data_l1_host="http://localhost:9400",
        )
        keystore = KeyStore()
        pk = keystore.get_private_key_from_mnemonic(phrase=mnemo)

        # msg = build_todo_tx()
        msg = build_water_and_energy_usage_tx()

        """ TO-DO """
        # signature, hash_ = keystore.data_sign(pk, msg, prefix=False) # Default encoding = json.dumps(msg, separators=(',', ':'))
        """ WATER AND ENERGY """
        signature, hash_ = keystore.data_sign(pk, msg, prefix=False)
        """ TO-DO "CUSTOM" """
        # def encode(data: dict):
        #     return json.dumps(msg, separators=(',', ':'))
        # signature, hash_ = keystore.data_sign(pk, msg, prefix=False, encoding=encode)

        public_key = account_metagraph_client.account.public_key[
            2:
        ]  # Remove '04' prefix
        proof = {"id": public_key, "signature": signature}
        tx = {"value": msg, "proofs": [proof]}

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
        encoded_msg = keystore.encode_data(msg=msg, prefix=False, encoding="base64")
        assert not keystore.verify_data(public_key, encoded_msg, signature)
        encoded_msg = keystore.encode_data(msg=msg)
        assert not keystore.verify_data(public_key, encoded_msg, signature)

        try:
            r = await account_metagraph_client.network.post_data(tx)
            assert r["hash"] == hash_
            # Returns the full response from the metagraph
        except (httpx.ConnectError, httpx.ReadTimeout):
            pytest.skip("No locally running Metagraph")
        except KeyError:
            pytest.fail(f"Post data didn't return a hash, returned value: {r}")
