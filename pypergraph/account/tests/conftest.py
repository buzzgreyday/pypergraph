import pytest

from pypergraph import MetagraphTokenClient
from pypergraph.account import DagAccount


@pytest.fixture
def dag_account():
    from secret import mnemo

    dag_account = DagAccount()
    dag_account.login_with_seed_phrase(mnemo)
    return dag_account


@pytest.fixture
def metagraph_account():
    from secret import mnemo

    dag_account = DagAccount()
    dag_account.login_with_seed_phrase(mnemo)
    metagraph_account = MetagraphTokenClient(
        account=dag_account,
        metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
        currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
    )
    return metagraph_account


@pytest.fixture
def mock_shared_responses():
    return {"balance": {"ordinal": 4493725, "balance": 218000000}}


@pytest.fixture
def mock_metagraph_responses():
    return {
        "transactions_by_address": {
            "data": [
                {
                    "hash": "39b73f07984301a30bb3d16d5d5f32a004b65d23df958c39cfb13fd0ab1f8da7",
                    "ordinal": 147,
                    "amount": 10000000,
                    "source": "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
                    "destination": "DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN",
                    "fee": 2000000,
                    "parent": {
                        "hash": "a7b0f25c3b445464bf819fbcb500503bf41e3c085410ae4b171f6fb28884de13",
                        "ordinal": 146,
                    },
                    "salt": 211479158172002,
                    "blockHash": "e03954438db9368561a74b57da8895da7f74f42dbeb823b4541aa3a009d4c1df",
                    "snapshotHash": "0cc3efe3135aacf80ccb16e5b67d56cc6b60a52a3d2d8713f08cd717d7950b17",
                    "snapshotOrdinal": 1506586,
                    "transactionOriginal": {
                        "value": {
                            "fee": 2000000,
                            "salt": 211479158172002,
                            "amount": 10000000,
                            "parent": {
                                "hash": "a7b0f25c3b445464bf819fbcb500503bf41e3c085410ae4b171f6fb28884de13",
                                "ordinal": 146,
                            },
                            "source": "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
                            "destination": "DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN",
                        },
                        "proofs": [
                            {
                                "id": "4462191fb1056699c28607c7e8e03b73602fa070b78cad863b5f84d08a577d5d0399ccd90ba1e69f34382d678216d4b2a030d98e38c0c960447dc49514f92ad7",
                                "signature": "3044022032d2d61e4d29c012fd302fd18d86c439d0ac6528b408160796289268295d451e02205248def09471b061a4d98853c856a3086428f441b9c025148470acf380a2e13d",
                            }
                        ],
                    },
                    "timestamp": "2025-06-10T08:47:16.999Z",
                    "globalSnapshotHash": "a8c04a9550365949057ec8dbc2f4a3b6665c77bc5c4ba89c1198b0119b923826",
                    "globalSnapshotOrdinal": 4521225,
                },
                {
                    "hash": "a7b0f25c3b445464bf819fbcb500503bf41e3c085410ae4b171f6fb28884de13",
                    "ordinal": 146,
                    "amount": 10000000,
                    "source": "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
                    "destination": "DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN",
                    "fee": 2000000,
                    "parent": {
                        "hash": "96bd897261ba7f1475281450ce6fb0bfa1a1ac27a075264737996f8ce9ca1172",
                        "ordinal": 145,
                    },
                    "salt": 127252911002285,
                    "blockHash": "2be1e95618dd8d654cdc3d0ab0780bd86f77c09d37cc0c8bcd800a81e6e4871a",
                    "snapshotHash": "fc599d337ef7509fa4af6f5385c6a536c27d918e193ccef3fa38628a5388820f",
                    "snapshotOrdinal": 1506584,
                    "transactionOriginal": {
                        "value": {
                            "fee": 2000000,
                            "salt": 127252911002285,
                            "amount": 10000000,
                            "parent": {
                                "hash": "96bd897261ba7f1475281450ce6fb0bfa1a1ac27a075264737996f8ce9ca1172",
                                "ordinal": 145,
                            },
                            "source": "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
                            "destination": "DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN",
                        },
                        "proofs": [
                            {
                                "id": "4462191fb1056699c28607c7e8e03b73602fa070b78cad863b5f84d08a577d5d0399ccd90ba1e69f34382d678216d4b2a030d98e38c0c960447dc49514f92ad7",
                                "signature": "3045022100ed22bc974579574c72707cd56ee3a7be4c175e28f49365b44f9915a383e5eddb022052e9c028ca7745ada8ddbf49c0ae09d73c1f55a3d022527bfe1234aec0c76281",
                            }
                        ],
                    },
                    "timestamp": "2025-06-10T08:47:16.999Z",
                    "globalSnapshotHash": "a8c04a9550365949057ec8dbc2f4a3b6665c77bc5c4ba89c1198b0119b923826",
                    "globalSnapshotOrdinal": 4521225,
                },
                {
                    "hash": "96bd897261ba7f1475281450ce6fb0bfa1a1ac27a075264737996f8ce9ca1172",
                    "ordinal": 145,
                    "amount": 10000000,
                    "source": "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
                    "destination": "DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN",
                    "fee": 2000000,
                    "parent": {
                        "hash": "85bfbb22b3f9789407811c086ce10d9500ceb91bf41051ca0a551ce7551a290a",
                        "ordinal": 144,
                    },
                    "salt": 93680649930862,
                    "blockHash": "8a2b223651d23df27cc5b024c4b1cf33a327aa68158fa07a5d31cd160530026d",
                    "snapshotHash": "4bc3ee6bfa0fafd49fef374e58ff58043b040d749b88f3a2d8708ed2af90aac8",
                    "snapshotOrdinal": 1506560,
                    "transactionOriginal": {
                        "value": {
                            "fee": 2000000,
                            "salt": 93680649930862,
                            "amount": 10000000,
                            "parent": {
                                "hash": "85bfbb22b3f9789407811c086ce10d9500ceb91bf41051ca0a551ce7551a290a",
                                "ordinal": 144,
                            },
                            "source": "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
                            "destination": "DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN",
                        },
                        "proofs": [
                            {
                                "id": "4462191fb1056699c28607c7e8e03b73602fa070b78cad863b5f84d08a577d5d0399ccd90ba1e69f34382d678216d4b2a030d98e38c0c960447dc49514f92ad7",
                                "signature": "304402205c299c5c353eb0488e11b7203ff87681ca04da9ef4bc5b0359c91579753a567d0220187b52cec247154b37fc457083be86cfb56be49fb9cc137a4d73151378cf1cf4",
                            }
                        ],
                    },
                    "timestamp": "2025-06-10T08:39:36.646Z",
                    "globalSnapshotHash": "c9c08164eaeccb3b482b69803a8c90ad220f7a0725ac4c155c80964b649c050f",
                    "globalSnapshotOrdinal": 4521195,
                },
            ],
            "meta": {
                "next": "eyJoYXNoIjoiNjQzY2NjYjlkMDIzNjA0NzdlNmM1MjNjMGNiMDNiYWNhYzVjZGJhNTUxYjA1MTUxY2Y0Y2EzZjg2NTU3ZmYzMCJ9"
            },
        }
    }
