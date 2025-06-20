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
def mock_block_explorer_responses():
    """Centralized mock responses for block explorer tests"""
    return {
        "latest_snapshot": {
            "data": {
                "hash": "e97fcfec1e0e4b298767324545b09084bb85d30afb0b567e6cb86db7a0773d6e",
                "ordinal": 4493725,
                "height": 47275,
                "subHeight": 174,
                "lastSnapshotHash": "997b85121e082bb1b19f6a3bf0fc4aa9083ed92d551d63063267e7a4ce80a113",
                "blocks": [],
                "epochProgress": 2330207,
                "timestamp": "2025-06-05T11:14:29.933Z",
                "metagraphSnashotCount": 2,
            }
        },
        "snapshot_by_id": {
            "data": {
                "hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "ordinal": 2404170,
                "height": 29108,
                "subHeight": 11,
                "lastSnapshotHash": "9ec173e487b16958f276d1bb7a84f7aede3d0b8cbb01925b2f1ae76b92a4f662",
                "blocks": [
                    "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                    "b058dbf4f5f1994db57b60d24ea06204dae754cad95df5d4a0fe0bb02c815aa9",
                    "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                    "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                ],
                "epochProgress": 1894273,
                "timestamp": "2024-07-16T22:37:37.697Z",
                "metagraphSnashotCount": 1,
            }
        },
        "transactions_by_snapshot": {
            "data": [
                {
                    "hash": "f1982b22291beb83c069b3e078cc6c58afd5f52e18e02e68b405d7bd19e3f94d",
                    "ordinal": 614,
                    "amount": 1103443620000,
                    "source": "DAG6cStT1VYZdUhpoME23U5zbTveYq78tj7EihFV",
                    "destination": "DAG7Nh7EosCZVfwCrSr7E3yckN5jiVw6JJj852Lm",
                    "fee": 0,
                    "parent": {
                        "hash": "5da74f959a95fdf9196324d4b5cbec677c20525ab1af08b4cee7f19d0508821e",
                        "ordinal": 613,
                    },
                    "salt": 8858357374944805,
                    "blockHash": "b7b5e3397aea811c17348d5b70fe465623494409095ef779a4631379a9119817",
                    "snapshotHash": "7950924cf05fa027d295c04125fa2f8582a00b4297925eadaf8c59b58a057bcb",
                    "snapshotOrdinal": 33406,
                    "transactionOriginal": None,
                    "timestamp": "2022-10-19T21:43:38.814Z",
                }
            ]
        },
        "transactions_limit_3": {
            "data": [
                {
                    "hash": "6e4e25a8a9a5dbe39bca2322ae58f80b3ce333f6c96997e68436abcb3a6ab216",
                    "ordinal": 10865,
                    "amount": 13643621075697,
                    "source": "DAG1pLpkyX7aTtFZtbF98kgA9QTZRzrsGaFmf4BT",
                    "destination": "DAG6Lsj1t5WQLbtqCdVkJxwdBzuBUzkCiaJzENUq",
                    "fee": 1,
                    "parent": {
                        "hash": "b63b4f1ec4530495e2927af02bee167d44fbc91e1b17f0d4c0dccc0b0345f477",
                        "ordinal": 10864,
                    },
                    "salt": 8906187503181324,
                    "blockHash": "2cc086a5d57c68c93701ea4cd9583e39f46126c1674c201033613d7a9fa5ed80",
                    "snapshotHash": "4f71c410c1da02bd68c7a84eb14642354884cdeaaeb741feef85975db3641580",
                    "snapshotOrdinal": 4495698,
                    "transactionOriginal": {
                        "value": {
                            "fee": 1,
                            "salt": 8906187503181324,
                            "amount": 13643621075697,
                            "parent": {
                                "hash": "b63b4f1ec4530495e2927af02bee167d44fbc91e1b17f0d4c0dccc0b0345f477",
                                "ordinal": 10864,
                            },
                            "source": "DAG1pLpkyX7aTtFZtbF98kgA9QTZRzrsGaFmf4BT",
                            "destination": "DAG6Lsj1t5WQLbtqCdVkJxwdBzuBUzkCiaJzENUq",
                        },
                        "proofs": [
                            {
                                "id": "3882eeaff4c7b9e2f6a94d1c5af75f71cf0a8dc2013b34e31b35181888b9813ac9dbaea5293a70b3e2d60429faa08c7f21bc54ee1cb0d9b660132838b3b797be",
                                "signature": "3045022100a6c225e01eee2f655a37005779b1267f8573beded7fac70d01d3861f7e3754da022020ee74e6a1b1becf6306d066fc3d569d79ca75783f5646b5d3f5cdf03a70b872",
                            }
                        ],
                    },
                    "timestamp": "2025-06-05T20:41:32.766Z",
                },
                {
                    "hash": "2ceed1c3ec357195d12bb04326b19eb904b332f4a49f5760534c58aad6f42b28",
                    "ordinal": 694,
                    "amount": 200000000000,
                    "source": "DAG0PEvPnPDykeebpLh46Y7rjcWsYwQQutz6Nio4",
                    "destination": "DAG3WnpWbwnnKBLtu8FvBp3VUkmxJgdcs41dTHg5",
                    "fee": 0,
                    "parent": {
                        "hash": "1e49d2bfbec0aead3db67134bf073d263f8391a4b266466580a8aa7071e36b0a",
                        "ordinal": 693,
                    },
                    "salt": 8731248817505500,
                    "blockHash": "2408025bc273e5a576b373542b846d09fd94d18f3be6686eced617f23a50bbe4",
                    "snapshotHash": "144c18df245c15d3154b8330cb8b3955b0821a39f8fe61e6262d196fa183fcf9",
                    "snapshotOrdinal": 4495658,
                    "transactionOriginal": {
                        "value": {
                            "fee": 0,
                            "salt": 8731248817505500,
                            "amount": 200000000000,
                            "parent": {
                                "hash": "1e49d2bfbec0aead3db67134bf073d263f8391a4b266466580a8aa7071e36b0a",
                                "ordinal": 693,
                            },
                            "source": "DAG0PEvPnPDykeebpLh46Y7rjcWsYwQQutz6Nio4",
                            "destination": "DAG3WnpWbwnnKBLtu8FvBp3VUkmxJgdcs41dTHg5",
                        },
                        "proofs": [
                            {
                                "id": "4484f7efe7420708c2ca05c6eed33c21fc010e7f3ddd9dacacf8d26e4e8e5f4f6823bd16c5da5a6e27c2459bfa6f351dff23743396844b758993178b3212c6bf",
                                "signature": "304402206ebacce89093ebb486e59c9e4298a7564407caf88eb9bf897592ae15b520028402207eb58c5d5b24464bc4cca60758b4ae5c84797dd5b9f9e62e27b41710196a4adb",
                            }
                        ],
                    },
                    "timestamp": "2025-06-05T20:31:25.121Z",
                },
                {
                    "hash": "80e1cc75cd85f0013568abb08d95141963692c6ad27e16fe4f7c0ddf16fed25f",
                    "ordinal": 5522,
                    "amount": 1995324670302,
                    "source": "DAG5yqn4JRkW5oAMthhBayBtkZzfAvRQnkH1dCG4",
                    "destination": "DAG5ZWKeHm7ZujoHtPeCFtLtUVrTQ7QjmpzaaeCt",
                    "fee": 0,
                    "parent": {
                        "hash": "285ca4cdf3fcf00fe445944948d0592dd646841cf29785d17f0e1488b8fbacfc",
                        "ordinal": 5521,
                    },
                    "salt": 8826802699366249,
                    "blockHash": "1cf5d3615ead2e00f9267c4c24a41869c3e4b76c06971062ab5bf4f27819f915",
                    "snapshotHash": "45bb21796c19237ddf274a160cb3b5cf3707348eaf3f9aa80f9baf0d34ff623f",
                    "snapshotOrdinal": 4495652,
                    "transactionOriginal": {
                        "value": {
                            "fee": 0,
                            "salt": 8826802699366249,
                            "amount": 1995324670302,
                            "parent": {
                                "hash": "285ca4cdf3fcf00fe445944948d0592dd646841cf29785d17f0e1488b8fbacfc",
                                "ordinal": 5521,
                            },
                            "source": "DAG5yqn4JRkW5oAMthhBayBtkZzfAvRQnkH1dCG4",
                            "destination": "DAG5ZWKeHm7ZujoHtPeCFtLtUVrTQ7QjmpzaaeCt",
                        },
                        "proofs": [
                            {
                                "id": "056a53a04a62c6a62a53876658fc8433fab5b2ec36ab6c3f7adb294930dccc10459efda425c8ff9becce95c52d1bd679fb2e64b2aa8975bc8f30ac49c74c40b3",
                                "signature": "3045022100b74d2b0ce58d0170c26299459c7b2f648f6502489a62c446a891b278aad2461a022027490aecd15809b48bb095f07a184068791e327708920c44d50818c5d4678a6f",
                            }
                        ],
                    },
                    "timestamp": "2025-06-05T20:29:52.958Z",
                },
            ],
            "meta": {
                "next": "eyJjcmVhdGVkX2F0IjoiMjAyNS0wNi0wNVQyMDoyNzo1NS4wOTFaIiwib3JkaW5hbCI6IjIiLCJoYXNoIjoiYWYwYWI2ZjljZGI5NGNlNzNiYmM3NWQ1Njg4MmVhOTZiOThlMzgzMWI2MThiNGYzZDY0MjUxN2JiZmZlZjBkMSJ9"
            },
        },
        "rewards_by_snapshot": {
            "data": [
                {
                    "destination": "DAG06wEy9UBdU98N1Asac6JtDM6sxAXggokWQYoP",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG08DvaErwTrKDostbSSmbq8Zarw2WZWcmMRCiG",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG08FQh9jur6wfRE34AA3o9QTDXEor4mu4Vgk4M",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG0b1oYHGygCHCiqf7YRMQ8FHLXwrZ2Jyray9dq",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0BAeUPXtRTBLkYtvZKuzwwCXNBLKuNQiWjrug",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0ceKhXa2D2VJW2zpqbQWybSyC6f6vTfKPJcWz",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG0eQ9XLSyrup6bUQrCq9nMn8rQkxYu4miXNqUQ",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG0ERVjvgupgv6LbHTwWrgnxsV3mh9hbLGxGGjq",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0FUZ8hTVPNfXHj9uCsaj5tYYy7R7wijbddnit",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0gFzy3ppsRp1p8bowxGM2ce3A154k9WMkMPVB",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0HpRCXaZg2owY9EWJrpBnuoaLxMssbZ5Eg2Kh",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0JmQj2GCb6KwRAt1qWRAGibLLmpqrKhHuUFwN",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG0Jw4C1VzmjWZUN76QtgzAMoupgDDbUunxZkhz",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0jyeBjXYJTGTBuHQrtWt9crUReHKx477WKWYx",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0LJ9m4G6Cp1mDYciHGGYUmaiT6zXDre7Doi3Z",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG0LUc9yV31AACCLN1MLh7LUKejEGoBU6xZGQSH",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0q5kRpygdGvdL4T7d3MJfk6wBWsb6g79HCc7E",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0qE5tkz6cMUD5M2dkqgfV4TQCzUUdAP5MFM9P",
                    "amount": 658436213,
                },
                {
                    "destination": "DAG0Qn1u3H6J2k2dcykQ68UHfMhjewQyRN3Uubp5",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0re4ZLZvsNGLi5sjrfyD9t86FHnBcwasTXwd4",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG0Ubr4hTTiegkqhunHG79DDTWKdb4eHBnBVEY3",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0yNA9kaMNGbb5GeEPsVS46ziy8kgPspYmnFg4",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG0zpms3gwK9v7UeEKEG5MET9h3SxbVVTzrkjBQ",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG138fzgR4uRHjEdVgPFAVf1SZ1wXjw2sGCSmxQ",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG15wa5RzkfKnJWXgk5yxwc4FBcDwLcFmennuRZ",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG19xdcZ4HvbQ2bfNL6qsKFzM4FZDBN3zbVfAgg",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1CRYE1xxk6Tu5oDfAu9ptmZs6vsH1MSzsmfVL",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1Dbj6HqaRMD6QCX8higZ3nQ5We72bZ9JFbLkj",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1F6eBTq2MB3AeEv33iMMBngujc89BPo3kiAdy",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1HEfcAwRSWRk9yw2MNZhkS5qY3VTVTscjvmYR",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1K7K9eMktXK1C2b5g94tZiFjAmHWtMcVEdNNx",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1q5j7SkX2fNwjDmmYimdYct4QcCp3ZdphB16P",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1Qck1KGau44zWvK371KPTKiaSUqPKwikg8YYo",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1RkMyh3xEdMLTyzbHs8hTtYN6u99ok5E6sSQS",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1sQu7hpGFqsShm8GPsiyi8NSSBisBvWRRPd5Q",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG1uNcGtH2Q7TMjDDezrVFozy8x9ELaTnxTt56k",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG1uXtfBL24v19xfVMCA1TJStgv2PqjqscPpLwJ",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG21No4p5qjRwsgPRm7ektKizJnvXEGJCc3WdVp",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG25Sh9uSXW6spFBm681HW8gw5DHJKVJcHR8sPb",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG27HGQ5acUx7ANkGTo8gfVyXbDjzKq5kRt6khw",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG27oHNunypJhnWZ5hfd1zSECgzetDVmP8bBDc8",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG29AfZ7B6B81af4K3h8UwGyVyZVTC7baLMZ3JK",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2berQfd4Xsr148STQyAdpBCwmS6LAU4UKyqn2",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2bJvkJ8pDx5t7kUsdcf7BuAtDXbRwbK6q5FTi",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2CQWEFswoY2yqeZbiLsYEacaPSB16UKJd2XWM",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2firRv5GHKsc7K6d38qy3jP6dzrPEe3eCNB6a",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2gkZzvVDiwM58K7cBEJCST9xasSjFbwTeMMSk",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2JYspEfMcTZqc2jtruJzVUEbwac729AExispN",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2MDzcmHDWP1mewsBmaFzTSxQModoBiXB1rNaK",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2MJ4nKMCmnAP1Vm4kBi555c5hsCQ5PYC4GRp9",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2NgwTK5cz1z2KgambsiN9nJy2x2N8KtHKGHfz",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2oia7E7EfNnFhn6KSTdZ97BFXz2HtJZaSg5c4",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG2PL8Yo8a4jnVYsWPxHkCLpaoo1csnK8GkArdT",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG2Pnadb6t21UbvT7qy3kdmHwjHW59cm14FXedi",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2q7asGwGCgeYmJwpEiY2kpZdPv9KArfGYdoY2",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2QUApEoBGGsGiJb6JmTpjVAXcSXaWNbZgAV5z",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2toosbkesck3TKaUvKyWkru3FN5jSFdxabNhB",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2tSRzK4oRM3m9Hs68f98qpgaTJL5co8wScp5F",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG2WPPHuX3C1dEequkDjCmmchUo8Jxz8vPA4j5C",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG2YFMP2HHwzYYiH7weStJF1kZCqwD6pkabyv4S",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG2ZxgDk2ect5zFxMUWPPBJB7ZyW6vBCSWpJvNG",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG34CFTRfCQFv6pp4YEYGCbqA3y6uWJcHVb7oNN",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG363rkhJhdC439SS3sVUXa2PYHicgo3ioVNN15",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG38gJ6Wf1VYhT9a9r3Y8STwao9QATGCzQEGnL4",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG39sRE7nVQyBkVFwFejHMRDBk5UJkXZtHYWXGm",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3aFzhWYMp1F4aGbcjNuENwazPDJeqXgWrg3P4",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3bD6oRgc3f74uT2QKw1hHgoDyCykgLGR5QC2A",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3BvWfyYbpKabxWzNjNvSoJWHD4BJM5JiR93nH",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG3c27VBMXgJX6vGLXh3UwLy6GiTN8eBzr3hxu4",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG3GaQwxJTUHx47hQxkBusCKX4STBvprTB96KPc",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3GuGPJXqFvnGpZLewpzb76V8hikbPFreoyuGx",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3HBLr6bX6t6uhih73pA3qJDdqg6k623JChNGV",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3ifN7Pg421t9eYzeVrAqsWpHDy7aSPgLPBrfi",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3JuTfrsBCPC3UMCpifaxKmLNMHRHxDWPDMxqW",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3jYsCbqtacwpLJCtEL2hWPrCZYW1ZjKCmzRae",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3m2UbVSgVR6qQ2jtemo3ed93DQb5XgFnZyHSi",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3MAyhKZ1gxK3Z3fPz3TiBN11ayZcKRgvtLzvk",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG3QpVQ2gPJ9GofXvvDJqN9Lba5A67PxLS8A2eS",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3RXBWBJq1Bf38rawASakLHKYMbRhsDckaGvGu",
                    "amount": 42798353902,
                },
                {
                    "destination": "DAG3u9U9CbquLut5EYrfJZwi8LNytVUc3wm5PE9Q",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3V8vdPKJKY3Af5DiNmkQodRiGi5kvPxwoYSkz",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3xwHRRReiRhqMm6tZ4sqskuGiXkUDJzbX4E43",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG3yDN5ZB3FD2rdyef3ksvrDTMVxwDnq1dBYAh7",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG3yTR5M4ompthLNwuG3UH52YVkjRE2gZfHKypJ",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG443thRbxSTs6o8BnByWDD1kpFBzoVeKEUgtBw",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG44oDVskGBx4vt9JPeJ3DxVMYtr1jLr2mrhJ8e",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG45HuBQTTGHiRr5EyWy6NiepYH1x5dpoTzc9vL",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG48sv4cakA12EyR8ScYvyd5kPeEox3RgvyZtB9",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG49nTkRpPRogCr9EukH1f2vw7GGURdhM3bYSKT",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG4aCEr9tzww94LhHzGgCTWB9guaNYFAigex9Cg",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG4aPovGkMVJjJ5ZfNec998LkZVgszvCqcsqzyB",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG4c3LwtBEZzh93USekMYXSdY4twzbN1Vgm1H1E",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG4dsPw3kA1VZX6Dvq4qrrRMcjvBZ9S41F3KsxY",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG4fWEaFVgnrbxueUzrdkKk1DMxaczhfi3vhEZW",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG4FYvH1HptoqmopE7JQeJ5cC4uXQU1Y32ys8PS",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG4h7nTVBD3PSbUTwtuhLQAs6ML4cH1fX1rGznW",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG4HsTwBMUya6tTiumL1Df6ZebLC7csiu6cu14r",
                    "amount": 13168725,
                },
                {
                    "destination": "DAG4izuM7aE1MRuJ4bfqALt5z5Zt6HwF1ayf4Q61",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG4j376VdosxzW3qoTNL9CJ76aQccd5PpwjXyT3",
                    "amount": 13168724,
                },
                {
                    "destination": "DAG4J6gixVGKYmcZs9Wmkyrv8ERp39vxtjwbjV5Q",
                    "amount": 13168725,
                },
            ],
            "meta": {
                "next": "eyJnbG9iYWxfc25hcHNob3RfaGFzaCI6Ijc0NGNiNWU3OGVhMmQ2N2Q1ODNmY2M4MTBkNGNhNTRjZTg0YjA1YmJhNjVkODhkYTEzZGY1MDRlNzVmYWNhN2IiLCJkZXN0aW5hdGlvbl9hZGRyIjoiREFHNG1iTE1VRmQ2c1lXM2k3dUZIY3RDb3F1TjVrNGFkS3BUNkFQYSJ9"
            },
        },
        "transaction_by_hash": {
            "data": {
                "hash": "dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e",
                "ordinal": 78,
                "amount": 25000110000000,
                "source": "DAG2AhT8r7JoQb8fJNEKFLNEkaRSxjNmZ6Bbnqmb",
                "destination": "DAG7b166Y3dzREaLxfTsrFdbwzScxHZSdVrQaQUA",
                "fee": 0,
                "parent": {
                    "hash": "ff765b26b12e2f63fbda7d33efb6728be3dec86856fb85922c8fa2d8d7062555",
                    "ordinal": 77,
                },
                "salt": 8940539553876237,
                "blockHash": "85f034cf2df202ced872da05ef3eaf00cd1117e0f8deef9d56022505457072e9",
                "snapshotHash": "baa81574222c46c9ac37baa9eeea97b83f4f02aa46e187b19064a64188f5132f",
                "snapshotOrdinal": 2829094,
                "transactionOriginal": None,
                "timestamp": "2024-09-15T18:47:33.082Z",
            }
        },
        "paca_snapshot": {
            "data": {
                "hash": "0eefc8e08edf7a0933a546103c22cbfb090bfc54264977bba0240684150de5f9",
                "ordinal": 1488009,
                "height": 1119,
                "subHeight": 3450,
                "lastSnapshotHash": "c3c7eef84d57df264faff5a0589b6f7049170408131514c1a81db0b6be08ecb2",
                "blocks": [],
                "epochProgress": 610262,
                "timestamp": "2025-06-06T05:19:13.917Z",
                "fee": 400000,
                "stakingAddress": None,
                "ownerAddress": "DAG5VxUBiDx24wZgBwjJ1FeuVP1HHVjz6EzXa3z6",
                "sizeInKB": 4,
            }
        },
        "paca_rewards": {
            "data": [
                {
                    "destination": "DAG2ACig4MuEPit149J1mEjhYqwn8SBvXgVuy2aX",
                    "amount": 300000000,
                },
                {
                    "destination": "DAG2YaNbtUv35YVjJ5U6PR9r8obVunEky2RDdGJb",
                    "amount": 100000000,
                },
                {
                    "destination": "DAG3dQwyG69DmcXxqAQzfPEp39FEfepc3iaGGQVg",
                    "amount": 200000000,
                },
                {
                    "destination": "DAG4eVyr7kUzr7r2oPoxnUfLDgugdXYXLDh6gxZS",
                    "amount": 200000000,
                },
            ]
        },
        "paca_address_balance": {
            "data": {
                "ordinal": 1488505,
                "balance": 0,
                "address": "b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364",
            }
        },
        "paca_transaction": {
            "data": {
                "hash": "121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
                "ordinal": 20,
                "amount": 1300000000,
                "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                "fee": 0,
                "parent": {
                    "hash": "d29fdbc9b560f49387d0d8539ecdeca12314c6c5829919a0cdac0e6ab24d1f7a",
                    "ordinal": 19,
                },
                "salt": 8896174606352968,
                "blockHash": "3f78913ae81bb1a288fa859c2901c00587960c8555e40978ae1b4dbcbf9c4478",
                "snapshotHash": "c1c9215f51e8016e7fcf3714b6118bda8349348207fb40f7e6fb6ec27cfc2b33",
                "snapshotOrdinal": 952394,
                "transactionOriginal": None,
                "timestamp": "2025-02-13T01:10:05.098Z",
            }
        },
        "paca_transactions_limit_3": {
            "data": [
                {
                    "hash": "511d91ef0eb9ba1a5e429272ecaa2a0cde0e8f374190bf90918864f206bfd8b9",
                    "ordinal": 79,
                    "amount": 600000000,
                    "source": "DAG6zf62WYMWeVwgUNhFix8Mthg7kx1QNwhB9gZi",
                    "destination": "DAG37nSDXT4dvy8oGD4v57DbnyjZvQJW22adPios",
                    "fee": 0,
                    "parent": {
                        "hash": "8815bd4ca675b1d409c95593971b615536a10749f7016090dff78624080f0be9",
                        "ordinal": 78,
                    },
                    "salt": 8990155151566018,
                    "blockHash": "08249a2552505ac4708164f406528277a884d91ab3cc2fb7e55cfd72cd0dc54a",
                    "snapshotHash": "4bd1782b4a46bd28427bc1255f424fc46ff8ac8cb48a629ab0e2ca1cbc3d7535",
                    "snapshotOrdinal": 1488077,
                    "transactionOriginal": {
                        "value": {
                            "fee": 0,
                            "salt": 8990155151566018,
                            "amount": 600000000,
                            "parent": {
                                "hash": "8815bd4ca675b1d409c95593971b615536a10749f7016090dff78624080f0be9",
                                "ordinal": 78,
                            },
                            "source": "DAG6zf62WYMWeVwgUNhFix8Mthg7kx1QNwhB9gZi",
                            "destination": "DAG37nSDXT4dvy8oGD4v57DbnyjZvQJW22adPios",
                        },
                        "proofs": [
                            {
                                "id": "3bb65c6b143a05f51f9fa6118f1b435327965f5a421221f8e067910fb10e91b59e17a3b2ed71cff2f2ddee0f44a354e6205a335be8032edab8f400f079832a89",
                                "signature": "30450220162203840f95a1427974e5db7996f52d54a4b1cb33f18bbc50def617e1c783a9022100c8fe884ab93882200e0a04d34380dd157cf18ddc5f661c3f7a348b749503852f",
                            }
                        ],
                    },
                    "timestamp": "2025-06-06T05:30:19.874Z",
                },
                {
                    "hash": "75a08637d324da7204d69eb4e8cc5d01c06b59645936ef1523aeb3e443673725",
                    "ordinal": 40,
                    "amount": 600000000,
                    "source": "DAG6hATvmSysoj6CBFizXd45rcDPEMGDVKagSEch",
                    "destination": "DAG821Nrd3Rhf3JeejwXyDyKZ1TDqeJax25RvHxw",
                    "fee": 0,
                    "parent": {
                        "hash": "6241965526b087be3f9044210579167f354c430aebb5b4ae3e567b0a7f51f3fc",
                        "ordinal": 39,
                    },
                    "salt": 8937389281996647,
                    "blockHash": "640df3556d5963f000a6516cf9f357270ef15ab2c52e47cec1ff72f23a66ac40",
                    "snapshotHash": "10fb5b65f9de9eb1fedd45629f43ded72e4b137236064efed03cd13270c97695",
                    "snapshotOrdinal": 1487734,
                    "transactionOriginal": {
                        "value": {
                            "fee": 0,
                            "salt": 8937389281996647,
                            "amount": 600000000,
                            "parent": {
                                "hash": "6241965526b087be3f9044210579167f354c430aebb5b4ae3e567b0a7f51f3fc",
                                "ordinal": 39,
                            },
                            "source": "DAG6hATvmSysoj6CBFizXd45rcDPEMGDVKagSEch",
                            "destination": "DAG821Nrd3Rhf3JeejwXyDyKZ1TDqeJax25RvHxw",
                        },
                        "proofs": [
                            {
                                "id": "42a0a36f8354d64d511627538ea63413cfddfd0588723c6f91f10d0d06708aa42382f6911f77c30883118ec3fb31af60984c2d8602698adcfb41844f47606138",
                                "signature": "3045022100d0b9d5ad16efbc29a3fd2a0c5bd5d5b11f95672a3ea1c644756357a963f8bb1502206ca4e3043bbd88b6bf7e20161145166cb1dc0fdbf4d46c99b540bf96e5cb99d9",
                            }
                        ],
                    },
                    "timestamp": "2025-06-06T04:08:33.912Z",
                },
                {
                    "hash": "a5505d5b664e03388eb4e7000995acaf3145e4c392a052ab441cb6c49df30189",
                    "ordinal": 69,
                    "amount": 1300000000,
                    "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                    "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                    "fee": 0,
                    "parent": {
                        "hash": "72f0d835343f4b28c5c3439b6e064f8a5ad175c59252fdd91ac09d515b337a6c",
                        "ordinal": 68,
                    },
                    "salt": 8770718881675292,
                    "blockHash": "d904916e35376fa588276da71c06d4ba37979ead03a08d8a907cdd0e6910c436",
                    "snapshotHash": "01c9f0803e665b63b025bc555628a0c5a8c8d9c06439fd1ddf214ea2e8fd1f21",
                    "snapshotOrdinal": 1487440,
                    "transactionOriginal": {
                        "value": {
                            "fee": 0,
                            "salt": 8770718881675292,
                            "amount": 1300000000,
                            "parent": {
                                "hash": "72f0d835343f4b28c5c3439b6e064f8a5ad175c59252fdd91ac09d515b337a6c",
                                "ordinal": 68,
                            },
                            "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                            "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                        },
                        "proofs": [
                            {
                                "id": "82cba6939d21f2009d7f13fe685f8096c51b8d53446ceac502c8979450efb0d5aec35b315c38464d96cac3a5b4c69181fe00292a5b940c78b1111aee6f58ada4",
                                "signature": "3044022056a0d2200dfbaa2cbf8f32cd6593333f68560c134e512f7bd37cdb64f2990ece02207e0674636688cc30620dda27fec422d19e029ee82665a86a04e4c3f197869ae0",
                            }
                        ],
                    },
                    "timestamp": "2025-06-06T02:42:39.224Z",
                },
            ],
            "meta": {
                "next": "eyJtZXRhZ3JhcGhfaWQiOiJEQUc3Q2huaFVGN3VLZ244dFh5NDVhajR6bjlBRnVoYVpyOFZYWTQzIiwiaGFzaCI6IjNhNzM1MTJlOGIwMmYyYmMyZjQ0MTY1MzdiNTVhMDBiMDBjOTNhYWExMDdiYTdiMjFlMWQwZWZjODJmNzdkMTQifQ=="
            },
        },
        "paca_snapshot_by_ordinal": {
            "data": [
                {
                    "hash": "121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
                    "ordinal": 20,
                    "amount": 1300000000,
                    "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                    "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                    "fee": 0,
                    "parent": {
                        "hash": "d29fdbc9b560f49387d0d8539ecdeca12314c6c5829919a0cdac0e6ab24d1f7a",
                        "ordinal": 19,
                    },
                    "salt": 8896174606352968,
                    "blockHash": "3f78913ae81bb1a288fa859c2901c00587960c8555e40978ae1b4dbcbf9c4478",
                    "snapshotHash": "c1c9215f51e8016e7fcf3714b6118bda8349348207fb40f7e6fb6ec27cfc2b33",
                    "snapshotOrdinal": 952394,
                    "transactionOriginal": None,
                    "timestamp": "2025-02-13T01:10:05.098Z",
                }
            ]
        },
    }


@pytest.fixture
def mock_l1_api_responses():
    return {
        "cluster_info": [
            {
                "id": "615b72d69facdbd915b234771cd4ffe49692a573f7ac05fd212701afe9b703eb8ab2ab117961f819e6d5eaf5ad073456cf56a0422c67b17606d95f50460a919d",
                "ip": "5.161.233.213",
                "publicPort": 9000,
                "p2pPort": 9001,
                "clusterSession": "1748981238300",
                "session": "1748983955866",
                "state": "Ready",
                "jar": "88900372e74f9dbd13166232d1641d94687366b28765e931b3df4662122c8d1a",
            }
        ],
        "total_supply": {"ordinal": 3381985, "total": 97227345262286877},
        "last_ref": {
            "ordinal": 0,
            "hash": "0000000000000000000000000000000000000000000000000000000000000000",
        },
        "pending_transaction": {
            "hash": "121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
            "ordinal": 20,
            "amount": 1300000000,
            "fee": 0,
            "timestamp": "2025-02-13T01:10:05.098Z",
        },
        "post_transaction": {
            "data": {
                "hash": "39a46885844a9f775ef4e3f0514e5a758e6c7a0acfec9145959de2205b1af176"
            }
        },
    }
