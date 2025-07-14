from datetime import datetime, timezone

import httpx
import pytest
from pytest_httpx import HTTPXMock


@pytest.mark.mock
class TestMockedBlockExplorerAPI:
    """Test Block Explorer API endpoints with mocked responses"""

    @pytest.mark.asyncio
    async def test_get_latest_snapshot_success(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        """Test successful latest snapshot retrieval"""
        network.config("integrationnet")
        httpx_mock.add_response(
            url="https://be-integrationnet.constellationnetwork.io/global-snapshots/latest",
            json=mock_block_explorer_responses["latest_snapshot"],
        )
        result = await network.be_api.get_latest_snapshot()
        assert result.model_dump() == {
            "hash": "e97fcfec1e0e4b298767324545b09084bb85d30afb0b567e6cb86db7a0773d6e",
            "ordinal": 4493725,
            "height": 47275,
            "sub_height": 174,
            "last_snapshot_hash": "997b85121e082bb1b19f6a3bf0fc4aa9083ed92d551d63063267e7a4ce80a113",
            "blocks": [],
            "timestamp": datetime(2025, 6, 5, 11, 14, 29, 933000, tzinfo=timezone.utc),
        }

    @pytest.mark.asyncio
    async def test_get_snapshot_by_id(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        network.config("mainnet")
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/global-snapshots/2404170",
            json=mock_block_explorer_responses["snapshot_by_id"],
        )
        result = await network.be_api.get_snapshot("2404170")
        assert result.model_dump() == {
            "hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
            "ordinal": 2404170,
            "height": 29108,
            "sub_height": 11,
            "last_snapshot_hash": "9ec173e487b16958f276d1bb7a84f7aede3d0b8cbb01925b2f1ae76b92a4f662",
            "blocks": [
                "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "b058dbf4f5f1994db57b60d24ea06204dae754cad95df5d4a0fe0bb02c815aa9",
                "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
            ],
            "timestamp": datetime(2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc),
        }

    @pytest.mark.asyncio
    async def test_get_transactions_by_snapshot(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        network.config("mainnet")
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/global-snapshots/33406/transactions",
            json=mock_block_explorer_responses["transactions_by_snapshot"],
        )
        results = await network.be_api.get_transactions_by_snapshot("33406")
        assert [r.model_dump() for r in results] == [
            {
                "source": "DAG6cStT1VYZdUhpoME23U5zbTveYq78tj7EihFV",
                "destination": "DAG7Nh7EosCZVfwCrSr7E3yckN5jiVw6JJj852Lm",
                "amount": 1103443620000,
                "fee": 0,
                "hash": "f1982b22291beb83c069b3e078cc6c58afd5f52e18e02e68b405d7bd19e3f94d",
                "parent": {
                    "ordinal": 613,
                    "hash": "5da74f959a95fdf9196324d4b5cbec677c20525ab1af08b4cee7f19d0508821e",
                },
                "salt": 8858357374944805,
                "block_hash": "b7b5e3397aea811c17348d5b70fe465623494409095ef779a4631379a9119817",
                "snapshot_hash": "7950924cf05fa027d295c04125fa2f8582a00b4297925eadaf8c59b58a057bcb",
                "snapshot_ordinal": 33406,
                "transaction_original": None,
                "timestamp": datetime(
                    2022, 10, 19, 21, 43, 38, 814000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            }
        ]

    @pytest.mark.asyncio
    async def test_get_rewards_by_snapshot(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        network.config("integrationnet")
        httpx_mock.add_response(
            url="https://be-integrationnet.constellationnetwork.io/global-snapshots/2504170/rewards",
            json=mock_block_explorer_responses["rewards_by_snapshot"],
        )
        results = await network.be_api.get_rewards_by_snapshot(2504170)
        assert [r.model_dump() for r in results] == [
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
        ]

    @pytest.mark.asyncio
    async def test_get_latest_snapshot_transactions(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        network.config("mainnet")
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/global-snapshots/latest/transactions",
            json=mock_block_explorer_responses["transactions_by_snapshot"],
        )
        results = await network.be_api.get_latest_snapshot_transactions()
        assert [r.model_dump() for r in results] == [
            {
                "source": "DAG6cStT1VYZdUhpoME23U5zbTveYq78tj7EihFV",
                "destination": "DAG7Nh7EosCZVfwCrSr7E3yckN5jiVw6JJj852Lm",
                "amount": 1103443620000,
                "fee": 0,
                "hash": "f1982b22291beb83c069b3e078cc6c58afd5f52e18e02e68b405d7bd19e3f94d",
                "parent": {
                    "ordinal": 613,
                    "hash": "5da74f959a95fdf9196324d4b5cbec677c20525ab1af08b4cee7f19d0508821e",
                },
                "salt": 8858357374944805,
                "block_hash": "b7b5e3397aea811c17348d5b70fe465623494409095ef779a4631379a9119817",
                "snapshot_hash": "7950924cf05fa027d295c04125fa2f8582a00b4297925eadaf8c59b58a057bcb",
                "snapshot_ordinal": 33406,
                "transaction_original": None,
                "timestamp": datetime(
                    2022, 10, 19, 21, 43, 38, 814000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            }
        ]

        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/global-snapshots/latest/transactions",
            json={"data": []},
        )
        results = await network.be_api.get_latest_snapshot_transactions()
        assert results == []

    @pytest.mark.asyncio
    async def test_get_latest_snapshot_rewards(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        network.config("mainnet")
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/global-snapshots/latest/rewards",
            json=mock_block_explorer_responses["rewards_by_snapshot"],
        )
        results = await network.be_api.get_latest_snapshot_rewards()
        assert [r.model_dump() for r in results] == [
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
        ]

        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/global-snapshots/latest/rewards",
            json={"data": []},
        )
        results = await network.be_api.get_latest_snapshot_rewards()
        assert results == []

    @pytest.mark.asyncio
    async def test_get_transactions(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        num_of_snapshots = 3
        network.config("mainnet")
        httpx_mock.add_response(
            url=f"https://be-mainnet.constellationnetwork.io/transactions?limit={num_of_snapshots}",
            json=mock_block_explorer_responses["transactions_limit_3"],
        )
        results = await network.be_api.get_transactions(limit=num_of_snapshots)
        assert len(results) == num_of_snapshots, "Snapshot data should be a list"
        assert [r.model_dump() for r in results] == [
            {
                "source": "DAG1pLpkyX7aTtFZtbF98kgA9QTZRzrsGaFmf4BT",
                "destination": "DAG6Lsj1t5WQLbtqCdVkJxwdBzuBUzkCiaJzENUq",
                "amount": 13643621075697,
                "fee": 1,
                "hash": "6e4e25a8a9a5dbe39bca2322ae58f80b3ce333f6c96997e68436abcb3a6ab216",
                "parent": {
                    "ordinal": 10864,
                    "hash": "b63b4f1ec4530495e2927af02bee167d44fbc91e1b17f0d4c0dccc0b0345f477",
                },
                "salt": 8906187503181324,
                "block_hash": "2cc086a5d57c68c93701ea4cd9583e39f46126c1674c201033613d7a9fa5ed80",
                "snapshot_hash": "4f71c410c1da02bd68c7a84eb14642354884cdeaaeb741feef85975db3641580",
                "snapshot_ordinal": 4495698,
                "transaction_original": {
                    "value": {
                        "source": "DAG1pLpkyX7aTtFZtbF98kgA9QTZRzrsGaFmf4BT",
                        "destination": "DAG6Lsj1t5WQLbtqCdVkJxwdBzuBUzkCiaJzENUq",
                        "amount": 13643621075697,
                        "fee": 1,
                        "parent": {
                            "ordinal": 10864,
                            "hash": "b63b4f1ec4530495e2927af02bee167d44fbc91e1b17f0d4c0dccc0b0345f477",
                        },
                        "salt": 8906187503181324,
                        "encoded": "240DAG1pLpkyX7aTtFZtbF98kgA9QTZRzrsGaFmf4BT40DAG6Lsj1t5WQLbtqCdVkJxwdBzuBUzkCiaJzENUq11c68a7300af164b63b4f1ec4530495e2927af02bee167d44fbc91e1b17f0d4c0dccc0b0345f47751086411141fa4215e6e1e0c",
                    },
                    "proofs": [
                        {
                            "id": "3882eeaff4c7b9e2f6a94d1c5af75f71cf0a8dc2013b34e31b35181888b9813ac9dbaea5293a70b3e2d60429faa08c7f21bc54ee1cb0d9b660132838b3b797be",
                            "signature": "3045022100a6c225e01eee2f655a37005779b1267f8573beded7fac70d01d3861f7e3754da022020ee74e6a1b1becf6306d066fc3d569d79ca75783f5646b5d3f5cdf03a70b872",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 5, 20, 41, 32, 766000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJjcmVhdGVkX2F0IjoiMjAyNS0wNi0wNVQyMDoyNzo1NS4wOTFaIiwib3JkaW5hbCI6IjIiLCJoYXNoIjoiYWYwYWI2ZjljZGI5NGNlNzNiYmM3NWQ1Njg4MmVhOTZiOThlMzgzMWI2MThiNGYzZDY0MjUxN2JiZmZlZjBkMSJ9"
                },
            },
            {
                "source": "DAG0PEvPnPDykeebpLh46Y7rjcWsYwQQutz6Nio4",
                "destination": "DAG3WnpWbwnnKBLtu8FvBp3VUkmxJgdcs41dTHg5",
                "amount": 200000000000,
                "fee": 0,
                "hash": "2ceed1c3ec357195d12bb04326b19eb904b332f4a49f5760534c58aad6f42b28",
                "parent": {
                    "ordinal": 693,
                    "hash": "1e49d2bfbec0aead3db67134bf073d263f8391a4b266466580a8aa7071e36b0a",
                },
                "salt": 8731248817505500,
                "block_hash": "2408025bc273e5a576b373542b846d09fd94d18f3be6686eced617f23a50bbe4",
                "snapshot_hash": "144c18df245c15d3154b8330cb8b3955b0821a39f8fe61e6262d196fa183fcf9",
                "snapshot_ordinal": 4495658,
                "transaction_original": {
                    "value": {
                        "source": "DAG0PEvPnPDykeebpLh46Y7rjcWsYwQQutz6Nio4",
                        "destination": "DAG3WnpWbwnnKBLtu8FvBp3VUkmxJgdcs41dTHg5",
                        "amount": 200000000000,
                        "fee": 0,
                        "parent": {
                            "ordinal": 693,
                            "hash": "1e49d2bfbec0aead3db67134bf073d263f8391a4b266466580a8aa7071e36b0a",
                        },
                        "salt": 8731248817505500,
                        "encoded": "240DAG0PEvPnPDykeebpLh46Y7rjcWsYwQQutz6Nio440DAG3WnpWbwnnKBLtu8FvBp3VUkmxJgdcs41dTHg5102e90edd000641e49d2bfbec0aead3db67134bf073d263f8391a4b266466580a8aa7071e36b0a369310141f0506483684dc",
                    },
                    "proofs": [
                        {
                            "id": "4484f7efe7420708c2ca05c6eed33c21fc010e7f3ddd9dacacf8d26e4e8e5f4f6823bd16c5da5a6e27c2459bfa6f351dff23743396844b758993178b3212c6bf",
                            "signature": "304402206ebacce89093ebb486e59c9e4298a7564407caf88eb9bf897592ae15b520028402207eb58c5d5b24464bc4cca60758b4ae5c84797dd5b9f9e62e27b41710196a4adb",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 5, 20, 31, 25, 121000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJjcmVhdGVkX2F0IjoiMjAyNS0wNi0wNVQyMDoyNzo1NS4wOTFaIiwib3JkaW5hbCI6IjIiLCJoYXNoIjoiYWYwYWI2ZjljZGI5NGNlNzNiYmM3NWQ1Njg4MmVhOTZiOThlMzgzMWI2MThiNGYzZDY0MjUxN2JiZmZlZjBkMSJ9"
                },
            },
            {
                "source": "DAG5yqn4JRkW5oAMthhBayBtkZzfAvRQnkH1dCG4",
                "destination": "DAG5ZWKeHm7ZujoHtPeCFtLtUVrTQ7QjmpzaaeCt",
                "amount": 1995324670302,
                "fee": 0,
                "hash": "80e1cc75cd85f0013568abb08d95141963692c6ad27e16fe4f7c0ddf16fed25f",
                "parent": {
                    "ordinal": 5521,
                    "hash": "285ca4cdf3fcf00fe445944948d0592dd646841cf29785d17f0e1488b8fbacfc",
                },
                "salt": 8826802699366249,
                "block_hash": "1cf5d3615ead2e00f9267c4c24a41869c3e4b76c06971062ab5bf4f27819f915",
                "snapshot_hash": "45bb21796c19237ddf274a160cb3b5cf3707348eaf3f9aa80f9baf0d34ff623f",
                "snapshot_ordinal": 4495652,
                "transaction_original": {
                    "value": {
                        "source": "DAG5yqn4JRkW5oAMthhBayBtkZzfAvRQnkH1dCG4",
                        "destination": "DAG5ZWKeHm7ZujoHtPeCFtLtUVrTQ7QjmpzaaeCt",
                        "amount": 1995324670302,
                        "fee": 0,
                        "parent": {
                            "ordinal": 5521,
                            "hash": "285ca4cdf3fcf00fe445944948d0592dd646841cf29785d17f0e1488b8fbacfc",
                        },
                        "salt": 8826802699366249,
                        "encoded": "240DAG5yqn4JRkW5oAMthhBayBtkZzfAvRQnkH1dCG440DAG5ZWKeHm7ZujoHtPeCFtLtUVrTQ7QjmpzaaeCt111d0929e415e64285ca4cdf3fcf00fe445944948d0592dd646841cf29785d17f0e1488b8fbacfc4552110141f5bee2765ef69",
                    },
                    "proofs": [
                        {
                            "id": "056a53a04a62c6a62a53876658fc8433fab5b2ec36ab6c3f7adb294930dccc10459efda425c8ff9becce95c52d1bd679fb2e64b2aa8975bc8f30ac49c74c40b3",
                            "signature": "3045022100b74d2b0ce58d0170c26299459c7b2f648f6502489a62c446a891b278aad2461a022027490aecd15809b48bb095f07a184068791e327708920c44d50818c5d4678a6f",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 5, 20, 29, 52, 958000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJjcmVhdGVkX2F0IjoiMjAyNS0wNi0wNVQyMDoyNzo1NS4wOTFaIiwib3JkaW5hbCI6IjIiLCJoYXNoIjoiYWYwYWI2ZjljZGI5NGNlNzNiYmM3NWQ1Njg4MmVhOTZiOThlMzgzMWI2MThiNGYzZDY0MjUxN2JiZmZlZjBkMSJ9"
                },
            },
        ]

    @pytest.mark.asyncio
    async def test_get_transaction(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        network.config("mainnet")
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/transactions/dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e",
            json=mock_block_explorer_responses["transaction_by_hash"],
        )
        result = await network.be_api.get_transaction(
            "dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e"
        )
        assert result.model_dump() == {
            "source": "DAG2AhT8r7JoQb8fJNEKFLNEkaRSxjNmZ6Bbnqmb",
            "destination": "DAG7b166Y3dzREaLxfTsrFdbwzScxHZSdVrQaQUA",
            "amount": 25000110000000,
            "fee": 0,
            "hash": "dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e",
            "parent": {
                "ordinal": 77,
                "hash": "ff765b26b12e2f63fbda7d33efb6728be3dec86856fb85922c8fa2d8d7062555",
            },
            "salt": 8940539553876237,
            "block_hash": "85f034cf2df202ced872da05ef3eaf00cd1117e0f8deef9d56022505457072e9",
            "snapshot_hash": "baa81574222c46c9ac37baa9eeea97b83f4f02aa46e187b19064a64188f5132f",
            "snapshot_ordinal": 2829094,
            "transaction_original": None,
            "timestamp": datetime(2024, 9, 15, 18, 47, 33, 82000, tzinfo=timezone.utc),
            "proofs": [],
            "meta": None,
        }

    @pytest.mark.asyncio
    async def test_get_latest_currency_snapshot(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/snapshots/latest",
            json=mock_block_explorer_responses["paca_snapshot"],
        )
        result = await network.be_api.get_latest_currency_snapshot(el_paca_metagraph_id)
        assert result.model_dump() == {
            "hash": "0eefc8e08edf7a0933a546103c22cbfb090bfc54264977bba0240684150de5f9",
            "ordinal": 1488009,
            "height": 1119,
            "sub_height": 3450,
            "last_snapshot_hash": "c3c7eef84d57df264faff5a0589b6f7049170408131514c1a81db0b6be08ecb2",
            "blocks": [],
            "timestamp": datetime(2025, 6, 6, 5, 19, 13, 917000, tzinfo=timezone.utc),
            "fee": 400000,
            "owner_address": "DAG5VxUBiDx24wZgBwjJ1FeuVP1HHVjz6EzXa3z6",
            "staking_address": None,
            "size_in_kb": 4,
            "meta": None,
        }

    @pytest.mark.asyncio
    async def test_get_currency_snapshot(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/snapshots/1488009",
            json=mock_block_explorer_responses["paca_snapshot"],
        )
        result = await network.be_api.get_currency_snapshot(
            el_paca_metagraph_id, 1488009
        )
        assert result.model_dump() == {
            "hash": "0eefc8e08edf7a0933a546103c22cbfb090bfc54264977bba0240684150de5f9",
            "ordinal": 1488009,
            "height": 1119,
            "sub_height": 3450,
            "last_snapshot_hash": "c3c7eef84d57df264faff5a0589b6f7049170408131514c1a81db0b6be08ecb2",
            "blocks": [],
            "timestamp": datetime(2025, 6, 6, 5, 19, 13, 917000, tzinfo=timezone.utc),
            "fee": 400000,
            "owner_address": "DAG5VxUBiDx24wZgBwjJ1FeuVP1HHVjz6EzXa3z6",
            "staking_address": None,
            "size_in_kb": 4,
            "meta": None,
        }

    @pytest.mark.asyncio
    async def test_get_latest_currency_snapshot_rewards(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/snapshots/latest/rewards",
            json=mock_block_explorer_responses["paca_rewards"],
        )
        results = await network.be_api.get_latest_currency_snapshot_rewards(
            el_paca_metagraph_id
        )
        assert [r.model_dump() for r in results] == [
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

    @pytest.mark.asyncio
    async def test_get_currency_snapshot_rewards(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/snapshots/950075/rewards",
            json=mock_block_explorer_responses["paca_rewards"],
        )
        results = await network.be_api.get_currency_snapshot_rewards(
            el_paca_metagraph_id, 950075
        )
        assert [r.model_dump() for r in results] == [
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

    @pytest.mark.asyncio
    async def test_get_currency_address_balance(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/addresses/b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364/balance",
            json=mock_block_explorer_responses["paca_address_balance"],
        )
        result = await network.be_api.get_currency_address_balance(
            metagraph_id=el_paca_metagraph_id,
            hash="b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364",
        )
        assert result.model_dump() == {
            "ordinal": 1488505,
            "balance": 0,
            "address": "b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364",
            "meta": None,
        }

    @pytest.mark.asyncio
    async def test_get_currency_transaction(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/transactions/121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
            json=mock_block_explorer_responses["paca_transaction"],
        )
        result = await network.be_api.get_currency_transaction(
            metagraph_id=el_paca_metagraph_id,
            hash="121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
        )
        assert result.model_dump() == {
            "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
            "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
            "amount": 1300000000,
            "fee": 0,
            "hash": "121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
            "parent": {
                "ordinal": 19,
                "hash": "d29fdbc9b560f49387d0d8539ecdeca12314c6c5829919a0cdac0e6ab24d1f7a",
            },
            "salt": 8896174606352968,
            "block_hash": "3f78913ae81bb1a288fa859c2901c00587960c8555e40978ae1b4dbcbf9c4478",
            "snapshot_hash": "c1c9215f51e8016e7fcf3714b6118bda8349348207fb40f7e6fb6ec27cfc2b33",
            "snapshot_ordinal": 952394,
            "transaction_original": None,
            "timestamp": datetime(2025, 2, 13, 1, 10, 5, 98000, tzinfo=timezone.utc),
            "proofs": [],
            "meta": None,
        }

    @pytest.mark.asyncio
    async def test_get_currency_transactions(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/transactions?limit=3",
            json=mock_block_explorer_responses["paca_transactions_limit_3"],
        )
        results = await network.be_api.get_currency_transactions(
            metagraph_id=el_paca_metagraph_id, limit=3
        )
        assert [r.model_dump() for r in results] == [
            {
                "source": "DAG6zf62WYMWeVwgUNhFix8Mthg7kx1QNwhB9gZi",
                "destination": "DAG37nSDXT4dvy8oGD4v57DbnyjZvQJW22adPios",
                "amount": 600000000,
                "fee": 0,
                "hash": "511d91ef0eb9ba1a5e429272ecaa2a0cde0e8f374190bf90918864f206bfd8b9",
                "parent": {
                    "ordinal": 78,
                    "hash": "8815bd4ca675b1d409c95593971b615536a10749f7016090dff78624080f0be9",
                },
                "salt": 8990155151566018,
                "block_hash": "08249a2552505ac4708164f406528277a884d91ab3cc2fb7e55cfd72cd0dc54a",
                "snapshot_hash": "4bd1782b4a46bd28427bc1255f424fc46ff8ac8cb48a629ab0e2ca1cbc3d7535",
                "snapshot_ordinal": 1488077,
                "transaction_original": {
                    "value": {
                        "source": "DAG6zf62WYMWeVwgUNhFix8Mthg7kx1QNwhB9gZi",
                        "destination": "DAG37nSDXT4dvy8oGD4v57DbnyjZvQJW22adPios",
                        "amount": 600000000,
                        "fee": 0,
                        "parent": {
                            "ordinal": 78,
                            "hash": "8815bd4ca675b1d409c95593971b615536a10749f7016090dff78624080f0be9",
                        },
                        "salt": 8990155151566018,
                        "encoded": "240DAG6zf62WYMWeVwgUNhFix8Mthg7kx1QNwhB9gZi40DAG37nSDXT4dvy8oGD4v57DbnyjZvQJW22adPios823c34600648815bd4ca675b1d409c95593971b615536a10749f7016090dff78624080f0be927810141ff07f9c48e4c2",
                    },
                    "proofs": [
                        {
                            "id": "3bb65c6b143a05f51f9fa6118f1b435327965f5a421221f8e067910fb10e91b59e17a3b2ed71cff2f2ddee0f44a354e6205a335be8032edab8f400f079832a89",
                            "signature": "30450220162203840f95a1427974e5db7996f52d54a4b1cb33f18bbc50def617e1c783a9022100c8fe884ab93882200e0a04d34380dd157cf18ddc5f661c3f7a348b749503852f",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 6, 5, 30, 19, 874000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            },
            {
                "source": "DAG6hATvmSysoj6CBFizXd45rcDPEMGDVKagSEch",
                "destination": "DAG821Nrd3Rhf3JeejwXyDyKZ1TDqeJax25RvHxw",
                "amount": 600000000,
                "fee": 0,
                "hash": "75a08637d324da7204d69eb4e8cc5d01c06b59645936ef1523aeb3e443673725",
                "parent": {
                    "ordinal": 39,
                    "hash": "6241965526b087be3f9044210579167f354c430aebb5b4ae3e567b0a7f51f3fc",
                },
                "salt": 8937389281996647,
                "block_hash": "640df3556d5963f000a6516cf9f357270ef15ab2c52e47cec1ff72f23a66ac40",
                "snapshot_hash": "10fb5b65f9de9eb1fedd45629f43ded72e4b137236064efed03cd13270c97695",
                "snapshot_ordinal": 1487734,
                "transaction_original": {
                    "value": {
                        "source": "DAG6hATvmSysoj6CBFizXd45rcDPEMGDVKagSEch",
                        "destination": "DAG821Nrd3Rhf3JeejwXyDyKZ1TDqeJax25RvHxw",
                        "amount": 600000000,
                        "fee": 0,
                        "parent": {
                            "ordinal": 39,
                            "hash": "6241965526b087be3f9044210579167f354c430aebb5b4ae3e567b0a7f51f3fc",
                        },
                        "salt": 8937389281996647,
                        "encoded": "240DAG6hATvmSysoj6CBFizXd45rcDPEMGDVKagSEch40DAG821Nrd3Rhf3JeejwXyDyKZ1TDqeJax25RvHxw823c34600646241965526b087be3f9044210579167f354c430aebb5b4ae3e567b0a7f51f3fc23910141fc082195f6f67",
                    },
                    "proofs": [
                        {
                            "id": "42a0a36f8354d64d511627538ea63413cfddfd0588723c6f91f10d0d06708aa42382f6911f77c30883118ec3fb31af60984c2d8602698adcfb41844f47606138",
                            "signature": "3045022100d0b9d5ad16efbc29a3fd2a0c5bd5d5b11f95672a3ea1c644756357a963f8bb1502206ca4e3043bbd88b6bf7e20161145166cb1dc0fdbf4d46c99b540bf96e5cb99d9",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 6, 4, 8, 33, 912000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            },
            {
                "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                "amount": 1300000000,
                "fee": 0,
                "hash": "a5505d5b664e03388eb4e7000995acaf3145e4c392a052ab441cb6c49df30189",
                "parent": {
                    "ordinal": 68,
                    "hash": "72f0d835343f4b28c5c3439b6e064f8a5ad175c59252fdd91ac09d515b337a6c",
                },
                "salt": 8770718881675292,
                "block_hash": "d904916e35376fa588276da71c06d4ba37979ead03a08d8a907cdd0e6910c436",
                "snapshot_hash": "01c9f0803e665b63b025bc555628a0c5a8c8d9c06439fd1ddf214ea2e8fd1f21",
                "snapshot_ordinal": 1487440,
                "transaction_original": {
                    "value": {
                        "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                        "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                        "amount": 1300000000,
                        "fee": 0,
                        "parent": {
                            "ordinal": 68,
                            "hash": "72f0d835343f4b28c5c3439b6e064f8a5ad175c59252fdd91ac09d515b337a6c",
                        },
                        "salt": 8770718881675292,
                        "encoded": "240DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY40DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK84d7c6d006472f0d835343f4b28c5c3439b6e064f8a5ad175c59252fdd91ac09d515b337a6c26810141f28ec1f5df81c",
                    },
                    "proofs": [
                        {
                            "id": "82cba6939d21f2009d7f13fe685f8096c51b8d53446ceac502c8979450efb0d5aec35b315c38464d96cac3a5b4c69181fe00292a5b940c78b1111aee6f58ada4",
                            "signature": "3044022056a0d2200dfbaa2cbf8f32cd6593333f68560c134e512f7bd37cdb64f2990ece02207e0674636688cc30620dda27fec422d19e029ee82665a86a04e4c3f197869ae0",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 6, 2, 42, 39, 224000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_currency_transactions_by_address(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/addresses/DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY/transactions?limit=3",
            json=mock_block_explorer_responses["paca_transactions_limit_3"],
        )
        results = await network.be_api.get_currency_transactions_by_address(
            metagraph_id=el_paca_metagraph_id,
            address="DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
            limit=3,
        )
        assert [r.model_dump() for r in results] == [
            {
                "source": "DAG6zf62WYMWeVwgUNhFix8Mthg7kx1QNwhB9gZi",
                "destination": "DAG37nSDXT4dvy8oGD4v57DbnyjZvQJW22adPios",
                "amount": 600000000,
                "fee": 0,
                "hash": "511d91ef0eb9ba1a5e429272ecaa2a0cde0e8f374190bf90918864f206bfd8b9",
                "parent": {
                    "ordinal": 78,
                    "hash": "8815bd4ca675b1d409c95593971b615536a10749f7016090dff78624080f0be9",
                },
                "salt": 8990155151566018,
                "block_hash": "08249a2552505ac4708164f406528277a884d91ab3cc2fb7e55cfd72cd0dc54a",
                "snapshot_hash": "4bd1782b4a46bd28427bc1255f424fc46ff8ac8cb48a629ab0e2ca1cbc3d7535",
                "snapshot_ordinal": 1488077,
                "transaction_original": {
                    "value": {
                        "source": "DAG6zf62WYMWeVwgUNhFix8Mthg7kx1QNwhB9gZi",
                        "destination": "DAG37nSDXT4dvy8oGD4v57DbnyjZvQJW22adPios",
                        "amount": 600000000,
                        "fee": 0,
                        "parent": {
                            "ordinal": 78,
                            "hash": "8815bd4ca675b1d409c95593971b615536a10749f7016090dff78624080f0be9",
                        },
                        "salt": 8990155151566018,
                        "encoded": "240DAG6zf62WYMWeVwgUNhFix8Mthg7kx1QNwhB9gZi40DAG37nSDXT4dvy8oGD4v57DbnyjZvQJW22adPios823c34600648815bd4ca675b1d409c95593971b615536a10749f7016090dff78624080f0be927810141ff07f9c48e4c2",
                    },
                    "proofs": [
                        {
                            "id": "3bb65c6b143a05f51f9fa6118f1b435327965f5a421221f8e067910fb10e91b59e17a3b2ed71cff2f2ddee0f44a354e6205a335be8032edab8f400f079832a89",
                            "signature": "30450220162203840f95a1427974e5db7996f52d54a4b1cb33f18bbc50def617e1c783a9022100c8fe884ab93882200e0a04d34380dd157cf18ddc5f661c3f7a348b749503852f",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 6, 5, 30, 19, 874000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            },
            {
                "source": "DAG6hATvmSysoj6CBFizXd45rcDPEMGDVKagSEch",
                "destination": "DAG821Nrd3Rhf3JeejwXyDyKZ1TDqeJax25RvHxw",
                "amount": 600000000,
                "fee": 0,
                "hash": "75a08637d324da7204d69eb4e8cc5d01c06b59645936ef1523aeb3e443673725",
                "parent": {
                    "ordinal": 39,
                    "hash": "6241965526b087be3f9044210579167f354c430aebb5b4ae3e567b0a7f51f3fc",
                },
                "salt": 8937389281996647,
                "block_hash": "640df3556d5963f000a6516cf9f357270ef15ab2c52e47cec1ff72f23a66ac40",
                "snapshot_hash": "10fb5b65f9de9eb1fedd45629f43ded72e4b137236064efed03cd13270c97695",
                "snapshot_ordinal": 1487734,
                "transaction_original": {
                    "value": {
                        "source": "DAG6hATvmSysoj6CBFizXd45rcDPEMGDVKagSEch",
                        "destination": "DAG821Nrd3Rhf3JeejwXyDyKZ1TDqeJax25RvHxw",
                        "amount": 600000000,
                        "fee": 0,
                        "parent": {
                            "ordinal": 39,
                            "hash": "6241965526b087be3f9044210579167f354c430aebb5b4ae3e567b0a7f51f3fc",
                        },
                        "salt": 8937389281996647,
                        "encoded": "240DAG6hATvmSysoj6CBFizXd45rcDPEMGDVKagSEch40DAG821Nrd3Rhf3JeejwXyDyKZ1TDqeJax25RvHxw823c34600646241965526b087be3f9044210579167f354c430aebb5b4ae3e567b0a7f51f3fc23910141fc082195f6f67",
                    },
                    "proofs": [
                        {
                            "id": "42a0a36f8354d64d511627538ea63413cfddfd0588723c6f91f10d0d06708aa42382f6911f77c30883118ec3fb31af60984c2d8602698adcfb41844f47606138",
                            "signature": "3045022100d0b9d5ad16efbc29a3fd2a0c5bd5d5b11f95672a3ea1c644756357a963f8bb1502206ca4e3043bbd88b6bf7e20161145166cb1dc0fdbf4d46c99b540bf96e5cb99d9",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 6, 4, 8, 33, 912000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            },
            {
                "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                "amount": 1300000000,
                "fee": 0,
                "hash": "a5505d5b664e03388eb4e7000995acaf3145e4c392a052ab441cb6c49df30189",
                "parent": {
                    "ordinal": 68,
                    "hash": "72f0d835343f4b28c5c3439b6e064f8a5ad175c59252fdd91ac09d515b337a6c",
                },
                "salt": 8770718881675292,
                "block_hash": "d904916e35376fa588276da71c06d4ba37979ead03a08d8a907cdd0e6910c436",
                "snapshot_hash": "01c9f0803e665b63b025bc555628a0c5a8c8d9c06439fd1ddf214ea2e8fd1f21",
                "snapshot_ordinal": 1487440,
                "transaction_original": {
                    "value": {
                        "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                        "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                        "amount": 1300000000,
                        "fee": 0,
                        "parent": {
                            "ordinal": 68,
                            "hash": "72f0d835343f4b28c5c3439b6e064f8a5ad175c59252fdd91ac09d515b337a6c",
                        },
                        "salt": 8770718881675292,
                        "encoded": "240DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY40DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK84d7c6d006472f0d835343f4b28c5c3439b6e064f8a5ad175c59252fdd91ac09d515b337a6c26810141f28ec1f5df81c",
                    },
                    "proofs": [
                        {
                            "id": "82cba6939d21f2009d7f13fe685f8096c51b8d53446ceac502c8979450efb0d5aec35b315c38464d96cac3a5b4c69181fe00292a5b940c78b1111aee6f58ada4",
                            "signature": "3044022056a0d2200dfbaa2cbf8f32cd6593333f68560c134e512f7bd37cdb64f2990ece02207e0674636688cc30620dda27fec422d19e029ee82665a86a04e4c3f197869ae0",
                        }
                    ],
                },
                "timestamp": datetime(
                    2025, 6, 6, 2, 42, 39, 224000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_currency_transactions_by_snapshot(
        self, network, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/snapshots/952394/transactions?limit=3",
            json=mock_block_explorer_responses["paca_snapshot_by_ordinal"],
        )
        results = await network.be_api.get_currency_transactions_by_snapshot(
            metagraph_id=el_paca_metagraph_id, hash_or_ordinal=952394, limit=3
        )
        assert [r.model_dump() for r in results] == [
            {
                "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                "amount": 1300000000,
                "fee": 0,
                "hash": "121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
                "parent": {
                    "ordinal": 19,
                    "hash": "d29fdbc9b560f49387d0d8539ecdeca12314c6c5829919a0cdac0e6ab24d1f7a",
                },
                "salt": 8896174606352968,
                "block_hash": "3f78913ae81bb1a288fa859c2901c00587960c8555e40978ae1b4dbcbf9c4478",
                "snapshot_hash": "c1c9215f51e8016e7fcf3714b6118bda8349348207fb40f7e6fb6ec27cfc2b33",
                "snapshot_ordinal": 952394,
                "transaction_original": None,
                "timestamp": datetime(
                    2025, 2, 13, 1, 10, 5, 98000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            }
        ]


@pytest.mark.integration
class TestIntegrationBlockExplorerAPI:
    """Test Block Explorer API endpoints integration responses"""

    @pytest.mark.asyncio
    async def test_get_latest_snapshot(self, network):
        result = await network.be_api.get_latest_snapshot()
        assert isinstance(result.hash, str)

    @pytest.mark.asyncio
    async def test_get_snapshot_by_id(self, network):
        network.config("integrationnet")
        result = await network.be_api.get_snapshot("2404170")
        assert result.model_dump() == {
            "hash": "23d0204c004668ddbe15d9bbaa6fe67b152531f1e2762cb88d63242f870355ca",
            "ordinal": 2404170,
            "height": 259,
            "sub_height": 33123,
            "last_snapshot_hash": "81f3f251c0d91841492d1b79f1080921323453dcf62a75cd38b402102b99aade",
            "blocks": [],
            "timestamp": datetime(2024, 11, 22, 19, 23, 47, 35000, tzinfo=timezone.utc),
        }

    @pytest.mark.asyncio
    async def test_get_transactions_by_snapshot(self, network):
        results = await network.be_api.get_transactions_by_snapshot("2404170")
        assert [r.model_dump() for r in results] == [
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG29HwuP2PKU8SBj38x5qq2Z4JcgvKkXA7QS71F",
                "amount": 100000000,
                "fee": 1,
                "hash": "cc448d16e75393b6f0d4399f838e143024218ca9dabfd2c854cd20379433d3d6",
                "parent": {
                    "ordinal": 33486,
                    "hash": "870a9121c99007d00246a06ebee7d0828ed7cd5cd1ad845fdd5879d55af79535",
                },
                "salt": 8954232736330903,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG29GCbirutbQT6gZiqH4rCzyZaGMvq37ziffz9",
                "amount": 100000000,
                "fee": 1,
                "hash": "870a9121c99007d00246a06ebee7d0828ed7cd5cd1ad845fdd5879d55af79535",
                "parent": {
                    "ordinal": 33485,
                    "hash": "d893e16bcae22cf88218292f38c155c6a40f854fea582a49a908dab026c8af90",
                },
                "salt": 8886846019806075,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG29Eozyb6hvzyzQ4WCEG75j93E7kRoDFTn6vii",
                "amount": 100000000,
                "fee": 1,
                "hash": "d893e16bcae22cf88218292f38c155c6a40f854fea582a49a908dab026c8af90",
                "parent": {
                    "ordinal": 33484,
                    "hash": "6be0e59ce98905e5ebe1dbd2cc1992bd52d8dde716d2e007d3e93cf0a35a08c9",
                },
                "salt": 8840318903816347,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG29By3VV7NLNTcNSkCMpZGhJrSbbD1VAvEofeW",
                "amount": 100000000,
                "fee": 1,
                "hash": "6be0e59ce98905e5ebe1dbd2cc1992bd52d8dde716d2e007d3e93cf0a35a08c9",
                "parent": {
                    "ordinal": 33483,
                    "hash": "bbf2ffb06913369826495790abf244d72c3778cba7ebce9201789993d6e80dea",
                },
                "salt": 8969132073928850,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG29Au5yB4VdDYHah2cXNfkowdC7qW5cAT5P1AC",
                "amount": 100000000,
                "fee": 1,
                "hash": "bbf2ffb06913369826495790abf244d72c3778cba7ebce9201789993d6e80dea",
                "parent": {
                    "ordinal": 33482,
                    "hash": "5732d34f8e1b7f76bd4ec68322d92c1788363efda31a388f7a78ebe5e7e8fc59",
                },
                "salt": 8934505058177616,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG29A55UY5RdeNgW8qmEMFrQvEN3KGNv57EEsBW",
                "amount": 100000000,
                "fee": 1,
                "hash": "5732d34f8e1b7f76bd4ec68322d92c1788363efda31a388f7a78ebe5e7e8fc59",
                "parent": {
                    "ordinal": 33481,
                    "hash": "50e911286d58e834b88c229dc80a60fff470920830f320c03261f21f3f103a4f",
                },
                "salt": 8886284664860962,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG299TNGcth4gyJeqDNoc9VSoNYtLpMuJQ7LVTy",
                "amount": 100000000,
                "fee": 1,
                "hash": "50e911286d58e834b88c229dc80a60fff470920830f320c03261f21f3f103a4f",
                "parent": {
                    "ordinal": 33480,
                    "hash": "7d09d5a8e48dbc7be7c6e3b61a56bb8441b600f9c249c4bcec7c0fdcda0ac3e3",
                },
                "salt": 8955042557014797,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG298vcvHStuUCRJHrL1VWdpeuJuqYhPj2QBaBC",
                "amount": 100000000,
                "fee": 1,
                "hash": "7d09d5a8e48dbc7be7c6e3b61a56bb8441b600f9c249c4bcec7c0fdcda0ac3e3",
                "parent": {
                    "ordinal": 33479,
                    "hash": "b8f5aab2fc41ceffaa9c7fbf9b6fe76884e757f494db1551b0076ab51706e8d5",
                },
                "salt": 8910301828550029,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG298grkE5rszp6y7Jnu3iy9x4toSRrWUrHP5KW",
                "amount": 100000000,
                "fee": 1,
                "hash": "b8f5aab2fc41ceffaa9c7fbf9b6fe76884e757f494db1551b0076ab51706e8d5",
                "parent": {
                    "ordinal": 33478,
                    "hash": "4505c835532dfaf44d399ae1e3dbb744bcd420733f2dc467e4f6aac4687fa020",
                },
                "salt": 8907089777099447,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG298BQeq7E69YqkfGHVxugCvRKdwXm8yGNM9TJ",
                "amount": 100000000,
                "fee": 1,
                "hash": "4505c835532dfaf44d399ae1e3dbb744bcd420733f2dc467e4f6aac4687fa020",
                "parent": {
                    "ordinal": 33477,
                    "hash": "36cf170f91e6822d80f349c00ac5405e0b882ecef0ba62ffd2c82b664ced3f20",
                },
                "salt": 9005846514073260,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG296FkyZx9QNuYHiQ5bqsxvnktiiZphCYr9cRt",
                "amount": 100000000,
                "fee": 1,
                "hash": "36cf170f91e6822d80f349c00ac5405e0b882ecef0ba62ffd2c82b664ced3f20",
                "parent": {
                    "ordinal": 33476,
                    "hash": "7c182096fec6b2c06c8b4e9ff64b66c40b06383d23d5a51239d77730ac827b72",
                },
                "salt": 8942145206465409,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG294QWUEhyFoVpvWosFdt9QLJHYTPcVQ2LvR5J",
                "amount": 100000000,
                "fee": 1,
                "hash": "7c182096fec6b2c06c8b4e9ff64b66c40b06383d23d5a51239d77730ac827b72",
                "parent": {
                    "ordinal": 33475,
                    "hash": "7ca2c5c88ffd53a25e11d431bf3c102d05b37c2fcf0d290e3963c0c7fbc200c7",
                },
                "salt": 8875187811397639,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG294NQLanMrpuDT2Rkv5fwZiRc5R58WYakyQvp",
                "amount": 100000000,
                "fee": 1,
                "hash": "7ca2c5c88ffd53a25e11d431bf3c102d05b37c2fcf0d290e3963c0c7fbc200c7",
                "parent": {
                    "ordinal": 33474,
                    "hash": "4aba4310243dc7bd5c3105a3d851649f6f494d01cce801bc9724ce46fc1c5588",
                },
                "salt": 8816459062332295,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG2941AvQynHPPcLUJPfSGTn3hz849TCCnGokTN",
                "amount": 100000000,
                "fee": 1,
                "hash": "4aba4310243dc7bd5c3105a3d851649f6f494d01cce801bc9724ce46fc1c5588",
                "parent": {
                    "ordinal": 33473,
                    "hash": "6b588e3025e5abc9ff1a10ad38e3cf9922617729aeb12ee7f6ed6cf13a729f8f",
                },
                "salt": 8910931956240443,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG293ufhpa4Tu11eWAsjwxbyx49ePR16bFetHyi",
                "amount": 100000000,
                "fee": 1,
                "hash": "6b588e3025e5abc9ff1a10ad38e3cf9922617729aeb12ee7f6ed6cf13a729f8f",
                "parent": {
                    "ordinal": 33472,
                    "hash": "e32967d59f2df811856e5711eb563a38d968b90bc208c5ad06208b22cd996979",
                },
                "salt": 8750434624047889,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG291vgnGv8F1dbe1pkidcWSnnDMi8r5cg77esW",
                "amount": 100000000,
                "fee": 1,
                "hash": "e32967d59f2df811856e5711eb563a38d968b90bc208c5ad06208b22cd996979",
                "parent": {
                    "ordinal": 33471,
                    "hash": "9f0d9264d8b296e5a93132a0e4c918f0b777e4de60909db20b6c4e4d231489e9",
                },
                "salt": 8729735318881061,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG291ot64cGojrckD2EbpbvkPCv9jXykL7AFgBt",
                "amount": 100000000,
                "fee": 1,
                "hash": "9f0d9264d8b296e5a93132a0e4c918f0b777e4de60909db20b6c4e4d231489e9",
                "parent": {
                    "ordinal": 33470,
                    "hash": "8cb4fb9c29e6ef8dade10a9eb6e2674997c599653a39b7ee65f3657ca60c4086",
                },
                "salt": 8967912568565078,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28ycDPYTECvwEbWfoJmoT8dMunpNhD4zYRLii",
                "amount": 100000000,
                "fee": 1,
                "hash": "8cb4fb9c29e6ef8dade10a9eb6e2674997c599653a39b7ee65f3657ca60c4086",
                "parent": {
                    "ordinal": 33469,
                    "hash": "9cd2e3f9425064778ca313552cbcb43289350eeef6d0e54c89ab7addead9f41c",
                },
                "salt": 8868644248316460,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28xwYsxLDLkvMWJTviNMyvGoJpannrV3PZjNK",
                "amount": 100000000,
                "fee": 1,
                "hash": "9cd2e3f9425064778ca313552cbcb43289350eeef6d0e54c89ab7addead9f41c",
                "parent": {
                    "ordinal": 33468,
                    "hash": "021c8d748f505f5e4eda889a105acf9245625f6cf0ad3237c4e84af415ca67ad",
                },
                "salt": 8819003936336068,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28wzrsBJTzkkV6vJiZ3Re9wVyByCb2Zg883BD",
                "amount": 100000000,
                "fee": 1,
                "hash": "021c8d748f505f5e4eda889a105acf9245625f6cf0ad3237c4e84af415ca67ad",
                "parent": {
                    "ordinal": 33467,
                    "hash": "ea532794e49210afd57c583072c2c30b11c179a5b96568e5a79f58c8810dc441",
                },
                "salt": 8846674598933268,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28rPqcmKYwna77rtYGrVxrR1MRiC23aG3v7Mu",
                "amount": 100000000,
                "fee": 1,
                "hash": "ea532794e49210afd57c583072c2c30b11c179a5b96568e5a79f58c8810dc441",
                "parent": {
                    "ordinal": 33466,
                    "hash": "aaac135350fc8131ab798631db166c2069ceaf548c67ccd87c999798e8cdf179",
                },
                "salt": 8727457203810866,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28q8MfvEnUShHYseorJKFzLEgkYwwozkEy4xr",
                "amount": 100000000,
                "fee": 1,
                "hash": "aaac135350fc8131ab798631db166c2069ceaf548c67ccd87c999798e8cdf179",
                "parent": {
                    "ordinal": 33465,
                    "hash": "5a03bd51988b25a5c7afab5e9397e2cc6684786c75d79f9d9d2a5c57977338a9",
                },
                "salt": 8874690037468310,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28q5BLAykkrivTnq5XDH5sb2mfuM4cDDnTkUq",
                "amount": 100000000,
                "fee": 1,
                "hash": "5a03bd51988b25a5c7afab5e9397e2cc6684786c75d79f9d9d2a5c57977338a9",
                "parent": {
                    "ordinal": 33464,
                    "hash": "50c5047ded402ae8ab6f8ea1cd5241a4d72ac6375c9e65f7e0f1210e04e8ee9b",
                },
                "salt": 8880854065520484,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28pv6VyRkZGRV22YMrzvVBpBeW9vfmg2FFEJW",
                "amount": 100000000,
                "fee": 1,
                "hash": "50c5047ded402ae8ab6f8ea1cd5241a4d72ac6375c9e65f7e0f1210e04e8ee9b",
                "parent": {
                    "ordinal": 33463,
                    "hash": "1707a2f370990b597fa8ff9b10b24c2324fc58d2f6bb8d0c45fecf49014ca46b",
                },
                "salt": 8839032480196073,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28opEQSQvm6nKuZdJsZbDHVaXRdeVRDA85zy2",
                "amount": 100000000,
                "fee": 1,
                "hash": "1707a2f370990b597fa8ff9b10b24c2324fc58d2f6bb8d0c45fecf49014ca46b",
                "parent": {
                    "ordinal": 33462,
                    "hash": "703df06603961af3161376f566185997cede428970a9442d77aabab85af82e00",
                },
                "salt": 8987316793702932,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28ni8y7j1CaneqCVPwsiYP8nPZMhhz69tRyue",
                "amount": 100000000,
                "fee": 1,
                "hash": "703df06603961af3161376f566185997cede428970a9442d77aabab85af82e00",
                "parent": {
                    "ordinal": 33461,
                    "hash": "3c9bc6729eb54e2d439570fc88397edd8b342109c4133f58b40ba105c950d65a",
                },
                "salt": 8741522601707402,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28mM1eZaetz63b2zVCzE9RLkvrTttGfJwryTw",
                "amount": 100000000,
                "fee": 1,
                "hash": "3c9bc6729eb54e2d439570fc88397edd8b342109c4133f58b40ba105c950d65a",
                "parent": {
                    "ordinal": 33460,
                    "hash": "368f50696429a41e1ddb6bb82e1a4955d4784556e9208a54562595bb3fa66158",
                },
                "salt": 8988180152249531,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28m5ajTpsxtz1uykrwjKTzGsicm3wZGG3owJm",
                "amount": 100000000,
                "fee": 1,
                "hash": "368f50696429a41e1ddb6bb82e1a4955d4784556e9208a54562595bb3fa66158",
                "parent": {
                    "ordinal": 33459,
                    "hash": "241e5d5aaf4481590468f806110fe656b2d921224a86d1bf052838ef938e96fb",
                },
                "salt": 8932170899940070,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28kmd8wtDD2rHaMPRZTvUz8k21UFZNDWyunAC",
                "amount": 100000000,
                "fee": 1,
                "hash": "241e5d5aaf4481590468f806110fe656b2d921224a86d1bf052838ef938e96fb",
                "parent": {
                    "ordinal": 33458,
                    "hash": "f52f13487f891eca3495687d0c11ea15c724097d315db10ce6b9f2b6f0b11b2a",
                },
                "salt": 8924787322188376,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28jjWihVpiLRh6dbWmKX4fbR5cNadDQJy6tpi",
                "amount": 100000000,
                "fee": 1,
                "hash": "f52f13487f891eca3495687d0c11ea15c724097d315db10ce6b9f2b6f0b11b2a",
                "parent": {
                    "ordinal": 33457,
                    "hash": "06368d410e8e884f283ec7d4fd71a22fa1f8ae229b417d4d602c6a5b754fed3d",
                },
                "salt": 8827451505406628,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28jPvh8Remp4UtEQNiHtaFHf6UumM9rfaExQ3",
                "amount": 100000000,
                "fee": 1,
                "hash": "06368d410e8e884f283ec7d4fd71a22fa1f8ae229b417d4d602c6a5b754fed3d",
                "parent": {
                    "ordinal": 33456,
                    "hash": "da0434e608230df667961599c0e3fbe4dda332001899db65a3426b0cee4d3817",
                },
                "salt": 8925548712851375,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28iiXnSAHmJp1rqxVPJNrELSVF3QnwycpX26Y",
                "amount": 100000000,
                "fee": 1,
                "hash": "da0434e608230df667961599c0e3fbe4dda332001899db65a3426b0cee4d3817",
                "parent": {
                    "ordinal": 33455,
                    "hash": "11e4c326e89a9ca9b3c80e0f84e572561e24626295b0c460ee782030a7de5617",
                },
                "salt": 8880436496140764,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28gKC9r9b3U6avHcpZ3px6FeoKzULKbBeH3jX",
                "amount": 100000000,
                "fee": 1,
                "hash": "11e4c326e89a9ca9b3c80e0f84e572561e24626295b0c460ee782030a7de5617",
                "parent": {
                    "ordinal": 33454,
                    "hash": "e0bb23b06bc3be7c019c30eb0f6e97ac6c9ef21200c3b035f37a68a2101354eb",
                },
                "salt": 8774194606664021,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28gJSg3Cw2HPL3y24UA4rUwAWo34p5Uy9zMxp",
                "amount": 100000000,
                "fee": 1,
                "hash": "e0bb23b06bc3be7c019c30eb0f6e97ac6c9ef21200c3b035f37a68a2101354eb",
                "parent": {
                    "ordinal": 33453,
                    "hash": "5d2d1c1bbf535e80f14de1cb748ac044ce397a46002531145a01f69c14bd7e04",
                },
                "salt": 8930260520058133,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28eorec2SbKgEBsuuhLihvgwT86zHmo5qddDF",
                "amount": 100000000,
                "fee": 1,
                "hash": "5d2d1c1bbf535e80f14de1cb748ac044ce397a46002531145a01f69c14bd7e04",
                "parent": {
                    "ordinal": 33452,
                    "hash": "92e827cad7d3bc4b50d8837cb8f6f608f064798ca636ea90f84818f317d9f687",
                },
                "salt": 8821017741325223,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28eitC3R46zcwjZttDyE8phmio72kXgiWekmM",
                "amount": 100000000,
                "fee": 1,
                "hash": "92e827cad7d3bc4b50d8837cb8f6f608f064798ca636ea90f84818f317d9f687",
                "parent": {
                    "ordinal": 33451,
                    "hash": "d3226c871b06f0eb2829687d2a243c838c89565ee9099c47d9f10e7e1501f14b",
                },
                "salt": 8885737531200025,
                "block_hash": "8983a66675c4787e56f3e5356211ed0e8b9405d3a783dd48a1ffcd24beec2fe3",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28dm26cg24TmSoRF2uEKN6U29cc3PXDnqsL3M",
                "amount": 100000000,
                "fee": 1,
                "hash": "d3226c871b06f0eb2829687d2a243c838c89565ee9099c47d9f10e7e1501f14b",
                "parent": {
                    "ordinal": 33450,
                    "hash": "34afb366131b764a7314e3dd897293053690990676204f7639d51f2c79497a82",
                },
                "salt": 8989170849613013,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28cbUrFxoKcECP3jqCzufLcUEugULRKjkwfvN",
                "amount": 100000000,
                "fee": 1,
                "hash": "34afb366131b764a7314e3dd897293053690990676204f7639d51f2c79497a82",
                "parent": {
                    "ordinal": 33449,
                    "hash": "7ec6a38c171c390ec5bef5adcaf28d2be7506f531912a319ac0099c044bbe56d",
                },
                "salt": 8883407348819404,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28bDqQu4dDRucaZXcaKF3XXvfgptDL5PmjVED",
                "amount": 100000000,
                "fee": 1,
                "hash": "7ec6a38c171c390ec5bef5adcaf28d2be7506f531912a319ac0099c044bbe56d",
                "parent": {
                    "ordinal": 33448,
                    "hash": "7f07b2c1a00ba296deb615fbefa3d4549f4b76c4f773c0e85dbdc629fdd365d0",
                },
                "salt": 8841826312902561,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28aSfoq67JZwqmjwqQWH6sih6VHK3c97f4wnx",
                "amount": 100000000,
                "fee": 1,
                "hash": "7f07b2c1a00ba296deb615fbefa3d4549f4b76c4f773c0e85dbdc629fdd365d0",
                "parent": {
                    "ordinal": 33447,
                    "hash": "818babd1ffb6ce7420a11d9eb9efc8824e3783c78bde69e7ee61ba0da07586af",
                },
                "salt": 8945175599350690,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28ZjNygUTDxtn86ThLt1DTfRKZqFSVZJaL6zo",
                "amount": 100000000,
                "fee": 1,
                "hash": "818babd1ffb6ce7420a11d9eb9efc8824e3783c78bde69e7ee61ba0da07586af",
                "parent": {
                    "ordinal": 33446,
                    "hash": "32f5946e8546e9185153a5447577a0b7e48b62b8813d4fa75671f19866ecc7ee",
                },
                "salt": 8941551130063554,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28YhxGyt6Kkd56ba355PiN6AuhzH3jhyyezUH",
                "amount": 100000000,
                "fee": 1,
                "hash": "32f5946e8546e9185153a5447577a0b7e48b62b8813d4fa75671f19866ecc7ee",
                "parent": {
                    "ordinal": 33445,
                    "hash": "213f963bbd944f34278fbfb4b9d26f603abba4a9ecdd235e2ff4f64931df0862",
                },
                "salt": 8812895484355888,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28UELeziBsn4rME4kF6dikiFJW18mxZdhH7Dt",
                "amount": 100000000,
                "fee": 1,
                "hash": "213f963bbd944f34278fbfb4b9d26f603abba4a9ecdd235e2ff4f64931df0862",
                "parent": {
                    "ordinal": 33444,
                    "hash": "c4b138fc4f474122c50a83c26c612cda4b65a9d3cec4dd8d1ce1344060c3e360",
                },
                "salt": 8813877890677857,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28S8zcpXxB2F7wqRNKpw8DzydtPj2bgzCT3sX",
                "amount": 100000000,
                "fee": 1,
                "hash": "c4b138fc4f474122c50a83c26c612cda4b65a9d3cec4dd8d1ce1344060c3e360",
                "parent": {
                    "ordinal": 33443,
                    "hash": "cb6441c607867166ea6a6f73bf0d95562f8355f95ae8642eb8417f47f1deadc0",
                },
                "salt": 8777612449721884,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28S4gG98qp5Tt73eYkqwxzhpiWeHdzWeamH66",
                "amount": 100000000,
                "fee": 1,
                "hash": "cb6441c607867166ea6a6f73bf0d95562f8355f95ae8642eb8417f47f1deadc0",
                "parent": {
                    "ordinal": 33442,
                    "hash": "af4abea6cb5fb929662bc7c6797681cc95e7306e3cad8bc2448d2c629c0c0ce3",
                },
                "salt": 8958033201906322,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28RBrVRWd3jdtsrYYYmo2jYsoPQ23DyJMcbr2",
                "amount": 100000000,
                "fee": 1,
                "hash": "af4abea6cb5fb929662bc7c6797681cc95e7306e3cad8bc2448d2c629c0c0ce3",
                "parent": {
                    "ordinal": 33441,
                    "hash": "fedfdb4caef0614ef881c3e9f2a87ffc61fd1b6b35ce0abb703e68b5b85d6cbc",
                },
                "salt": 8737635324133332,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28QfMcNQ7EZyRme5BRGWcozsXtyxFtFiqBEqz",
                "amount": 100000000,
                "fee": 1,
                "hash": "fedfdb4caef0614ef881c3e9f2a87ffc61fd1b6b35ce0abb703e68b5b85d6cbc",
                "parent": {
                    "ordinal": 33440,
                    "hash": "db4d58c3228ed51696cf8f956c713504ad5836adefe375c981501af73ce70df8",
                },
                "salt": 8894089811347772,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28PjUR82mykyNSsb1G56d4ssT82tsq8r13QNm",
                "amount": 100000000,
                "fee": 1,
                "hash": "db4d58c3228ed51696cf8f956c713504ad5836adefe375c981501af73ce70df8",
                "parent": {
                    "ordinal": 33439,
                    "hash": "7fd2e2dbceae2a801163786b58c3e12bb3fde4ae24959fac685f216cc129d77f",
                },
                "salt": 8829871514693996,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28PYKTX3Wsrum13m1NPasPfD4D8b3K9CNbx7z",
                "amount": 100000000,
                "fee": 1,
                "hash": "7fd2e2dbceae2a801163786b58c3e12bb3fde4ae24959fac685f216cc129d77f",
                "parent": {
                    "ordinal": 33438,
                    "hash": "1bbffca79091dd7222989ba488ae25942acf1c38b1d7aa6d3ce4a76533707ae3",
                },
                "salt": 8803717295041152,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28KxBi1bUY3vuCEwiL4NTm3eihnyzvt4a5U1f",
                "amount": 100000000,
                "fee": 1,
                "hash": "1bbffca79091dd7222989ba488ae25942acf1c38b1d7aa6d3ce4a76533707ae3",
                "parent": {
                    "ordinal": 33437,
                    "hash": "e0dfe7764ffecf8577b7dbc23bb687314892083fd40bf7078d6abc8908a29380",
                },
                "salt": 8984844940732779,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28KkpG1zuzHfYyRoJZPBvx9oPed7uvXhaHwz4",
                "amount": 100000000,
                "fee": 1,
                "hash": "e0dfe7764ffecf8577b7dbc23bb687314892083fd40bf7078d6abc8908a29380",
                "parent": {
                    "ordinal": 33436,
                    "hash": "7926f5ff060d93289845ef9a769ac97fbc3dbc508fbd1bbc04f5c1c0c47d72c3",
                },
                "salt": 8958073636092191,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28K5BVAme9nRysQbkmeZY1hpk9x66wWCEJ3NJ",
                "amount": 100000000,
                "fee": 1,
                "hash": "7926f5ff060d93289845ef9a769ac97fbc3dbc508fbd1bbc04f5c1c0c47d72c3",
                "parent": {
                    "ordinal": 33435,
                    "hash": "f6a94dc8e059c00f03203bc09177bd8ca8ae098d6b8ae7b29417956f44bd6639",
                },
                "salt": 8783337646949655,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28JpakAAXSm71B4yBz9nb1rux7CNvqC1yoGWa",
                "amount": 100000000,
                "fee": 1,
                "hash": "f6a94dc8e059c00f03203bc09177bd8ca8ae098d6b8ae7b29417956f44bd6639",
                "parent": {
                    "ordinal": 33434,
                    "hash": "ae437a4fbcae867d2db7d86fb254bfb10a64f6b8f82a27bc157833739f515cef",
                },
                "salt": 8868982516407145,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28GFhMaiB7DnzRXQtnCpGk6VZeJtu6NQft3g8",
                "amount": 100000000,
                "fee": 1,
                "hash": "ae437a4fbcae867d2db7d86fb254bfb10a64f6b8f82a27bc157833739f515cef",
                "parent": {
                    "ordinal": 33433,
                    "hash": "48e6c5f33fa779d717d04b75e7b99f1e196ed95e2f9ecbde29ae56d01d54df23",
                },
                "salt": 8730447477139871,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28G7mCUKAFoc2JSYw8ZEz8LvjxnU5yDDjRTvR",
                "amount": 100000000,
                "fee": 1,
                "hash": "48e6c5f33fa779d717d04b75e7b99f1e196ed95e2f9ecbde29ae56d01d54df23",
                "parent": {
                    "ordinal": 33432,
                    "hash": "c08dc04d477c6d3f671d6ae5d695633bc4a61f31378052e960b041aea89d7dc6",
                },
                "salt": 8810330735987241,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28CikeQhfCZb1ZrwH6E7Lg6ph7SnEge9rwyB3",
                "amount": 100000000,
                "fee": 1,
                "hash": "c08dc04d477c6d3f671d6ae5d695633bc4a61f31378052e960b041aea89d7dc6",
                "parent": {
                    "ordinal": 33431,
                    "hash": "d4b58e96cbb40f1579589eec066e564097abe0d9141fcbcf11ae38030d4fd162",
                },
                "salt": 8727430911797334,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28CgCS5d2FjhcwpQLiPoFzsWETRyFW5SAWFmJ",
                "amount": 100000000,
                "fee": 1,
                "hash": "d4b58e96cbb40f1579589eec066e564097abe0d9141fcbcf11ae38030d4fd162",
                "parent": {
                    "ordinal": 33430,
                    "hash": "29fcb034ba6ebb62948f58389c3b7e4c9d5f49693bcfd16fb5ed04bb029d4720",
                },
                "salt": 8812777172239093,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28BY85abizT9aj47zPjjwF9pNsH19ui8W6uYd",
                "amount": 100000000,
                "fee": 1,
                "hash": "29fcb034ba6ebb62948f58389c3b7e4c9d5f49693bcfd16fb5ed04bb029d4720",
                "parent": {
                    "ordinal": 33429,
                    "hash": "426bcb4feb75c3121a600334075cf2e1f72f9f2c9fa73cf3e104c838a8dbecab",
                },
                "salt": 8855126228375996,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG28B6d8be7q3hGPCH4Y7DjV1kp5L1knYjTWe6F",
                "amount": 100000000,
                "fee": 1,
                "hash": "426bcb4feb75c3121a600334075cf2e1f72f9f2c9fa73cf3e104c838a8dbecab",
                "parent": {
                    "ordinal": 33428,
                    "hash": "4f752067dca8c1f394c540bd3df3cbe52a8ce48c54558283589bff2d0356164f",
                },
                "salt": 8782371290628505,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG2899CFW9hCYg27vtZ7dYLPsTzKiBvNCMVV5SJ",
                "amount": 100000000,
                "fee": 1,
                "hash": "4f752067dca8c1f394c540bd3df3cbe52a8ce48c54558283589bff2d0356164f",
                "parent": {
                    "ordinal": 33427,
                    "hash": "75d1333931dbe0c2abe17b231ab918b248281dc3ee462cc8583808b0a17b2246",
                },
                "salt": 8744427966381731,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG2891AWH9k7uQARYVFW3yhcGfG1puPdCGpciCi",
                "amount": 100000000,
                "fee": 1,
                "hash": "75d1333931dbe0c2abe17b231ab918b248281dc3ee462cc8583808b0a17b2246",
                "parent": {
                    "ordinal": 33426,
                    "hash": "f9546bcf81b63ff23a9fa8dfcf66478cd5e4c5d51fd608f27ddf99f35ff16f05",
                },
                "salt": 8869369119858981,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG284VwJYA1V2yWdH29KrqQD4n8MCCnaWrxgEHW",
                "amount": 100000000,
                "fee": 1,
                "hash": "f9546bcf81b63ff23a9fa8dfcf66478cd5e4c5d51fd608f27ddf99f35ff16f05",
                "parent": {
                    "ordinal": 33425,
                    "hash": "adf76cc1a8e00db02c4d4f0f350d4fee5d9f364d2291fc8aa63a48871b2e9578",
                },
                "salt": 8887060956180073,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG284PdrZDDwvhwzGkLHx1a4GZBJYQL7mU8T87H",
                "amount": 100000000,
                "fee": 1,
                "hash": "adf76cc1a8e00db02c4d4f0f350d4fee5d9f364d2291fc8aa63a48871b2e9578",
                "parent": {
                    "ordinal": 33424,
                    "hash": "3b5ab77b67f1b83bed0d2c0b6c4efb6eda3306018f3a18a16b505a2378690a03",
                },
                "salt": 8841847194535041,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG283D9BfjRVTMk7Exffq7osvqeioPTT4bMGJaS",
                "amount": 100000000,
                "fee": 1,
                "hash": "3b5ab77b67f1b83bed0d2c0b6c4efb6eda3306018f3a18a16b505a2378690a03",
                "parent": {
                    "ordinal": 33423,
                    "hash": "b48113046958aba9ee45fc40d40117a5a95e8e2ae01edb2c9ead37a55383dcab",
                },
                "salt": 8862083536416101,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG282GKnpQBDQujTeBv8dqS1bmvXXqEZdSXs1vz",
                "amount": 100000000,
                "fee": 1,
                "hash": "b48113046958aba9ee45fc40d40117a5a95e8e2ae01edb2c9ead37a55383dcab",
                "parent": {
                    "ordinal": 33422,
                    "hash": "a80a2de24e7e9f559b360651fecc73a048b4957f009f8ba5e4fcd9eb213beaa7",
                },
                "salt": 8886555738762677,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG282EuHq37QHeTLq2icsWJTyZ4N9uYE8KYDw4h",
                "amount": 100000000,
                "fee": 1,
                "hash": "a80a2de24e7e9f559b360651fecc73a048b4957f009f8ba5e4fcd9eb213beaa7",
                "parent": {
                    "ordinal": 33421,
                    "hash": "32b2f500bb47502e5e592534cdd47cc3a02b459b7a43c8bc67cb69a0b44e836e",
                },
                "salt": 8958704510624218,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG281Vaf6BxaKZ5UoGnJaHSxEjeYxfdBDnQ9uiq",
                "amount": 100000000,
                "fee": 1,
                "hash": "32b2f500bb47502e5e592534cdd47cc3a02b459b7a43c8bc67cb69a0b44e836e",
                "parent": {
                    "ordinal": 33420,
                    "hash": "97ab72ff598fcca071a7641408d298d6b2c33ee31ce1841361d32733ff19ff0e",
                },
                "salt": 8934141234210650,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27zi3SmjW3G2zTnzKMoyULTQShViM5ePpRSes",
                "amount": 100000000,
                "fee": 1,
                "hash": "97ab72ff598fcca071a7641408d298d6b2c33ee31ce1841361d32733ff19ff0e",
                "parent": {
                    "ordinal": 33419,
                    "hash": "d9b7c1bb0e729643576d16128984268cc695c18d6cc8e8ac9d634d01cab0c484",
                },
                "salt": 8758410050324820,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27yvjRxxWBUUkj3ozs7uYjoGAUxzDRDfPfSH3",
                "amount": 100000000,
                "fee": 1,
                "hash": "d9b7c1bb0e729643576d16128984268cc695c18d6cc8e8ac9d634d01cab0c484",
                "parent": {
                    "ordinal": 33418,
                    "hash": "144d791bd596b357bce4a890ae539c1667b2b662b54a756069d1f2ee3a460446",
                },
                "salt": 8796067920244547,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27vLHmxcHaDtBjcHQA6p6wmAyYZhfecwqLW1E",
                "amount": 100000000,
                "fee": 1,
                "hash": "144d791bd596b357bce4a890ae539c1667b2b662b54a756069d1f2ee3a460446",
                "parent": {
                    "ordinal": 33417,
                    "hash": "cf4a0a4cb3e3867b8e3de55db96ccbb932b8d93450c4fad016c8931d8f63cf23",
                },
                "salt": 8867218360426638,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27uZHD7GuQjcDgkroJaym25mLmvwSh3ia5FQg",
                "amount": 100000000,
                "fee": 1,
                "hash": "cf4a0a4cb3e3867b8e3de55db96ccbb932b8d93450c4fad016c8931d8f63cf23",
                "parent": {
                    "ordinal": 33416,
                    "hash": "a923d6acc45bce7aa5d6790e97c17e39df2166a9f0c9d389f35a56fa9100fbd2",
                },
                "salt": 8755671139294592,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27siUmmZ82yvBzhZxP7iygQKGycF1mtENv4Dz",
                "amount": 100000000,
                "fee": 1,
                "hash": "a923d6acc45bce7aa5d6790e97c17e39df2166a9f0c9d389f35a56fa9100fbd2",
                "parent": {
                    "ordinal": 33415,
                    "hash": "ddcbec6baddc89c8dc9a9369ae4592d66fbe4e7c32c617c92592d35751231799",
                },
                "salt": 8817405294856169,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27ofTv4Y2is6Q2yNw4zX5JaWP8FkzrKEU9Ups",
                "amount": 100000000,
                "fee": 1,
                "hash": "ddcbec6baddc89c8dc9a9369ae4592d66fbe4e7c32c617c92592d35751231799",
                "parent": {
                    "ordinal": 33414,
                    "hash": "ee7bc22867151ca993d14e6d35eb89cb1df2469e8495f39d5736168f47570e41",
                },
                "salt": 8934491000970388,
                "block_hash": "0703e08fc288e4847a18bc755452ed372297da150802d70ef753b2f434d8019a",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27nqH8Nud8NBEN2oVmKYEX7Mxy78nbGtFVzRM",
                "amount": 100000000,
                "fee": 1,
                "hash": "ee7bc22867151ca993d14e6d35eb89cb1df2469e8495f39d5736168f47570e41",
                "parent": {
                    "ordinal": 33413,
                    "hash": "af1dc9effb4ffb972b6315c5ccf0210f759c259ff42cccb83fe3934747a33b72",
                },
                "salt": 8789993744464740,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27ndhaiUhN9vfy4ti64TaGMC8gvRkLwaqxdKu",
                "amount": 100000000,
                "fee": 1,
                "hash": "af1dc9effb4ffb972b6315c5ccf0210f759c259ff42cccb83fe3934747a33b72",
                "parent": {
                    "ordinal": 33412,
                    "hash": "8ed868b55039cb437a6caf31fc391a4b2dbaba73406ebd1eecb9ac9dec93965d",
                },
                "salt": 8927489499849351,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27n2udkQyhjsy9dpGPRfKeqqE8dBxhaPjMw3q",
                "amount": 100000000,
                "fee": 1,
                "hash": "8ed868b55039cb437a6caf31fc391a4b2dbaba73406ebd1eecb9ac9dec93965d",
                "parent": {
                    "ordinal": 33411,
                    "hash": "261470a987d6dc844028ec530dfdc8409c8c313581778221cb9e592336c585f9",
                },
                "salt": 8945413209725154,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27mbFEsYQmVVkp4SBPPQThYZePnckyRUYEcNM",
                "amount": 100000000,
                "fee": 1,
                "hash": "261470a987d6dc844028ec530dfdc8409c8c313581778221cb9e592336c585f9",
                "parent": {
                    "ordinal": 33410,
                    "hash": "5eb56081f53218296d82e8402408ec9e60bade886dab1e5e7af7ddc64999b553",
                },
                "salt": 8922294941523742,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27m3RWErGQyE18hZhtdqsGNWgUMc6j4aWxGsJ",
                "amount": 100000000,
                "fee": 1,
                "hash": "5eb56081f53218296d82e8402408ec9e60bade886dab1e5e7af7ddc64999b553",
                "parent": {
                    "ordinal": 33409,
                    "hash": "9bd4d1db3977be4b3056084937d87c58abafdbb82ef28e4284199d1581517d4f",
                },
                "salt": 8847997796053068,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27jpfRT6PakwLuYrNcPEwyeZSXH1E9spBmUv6",
                "amount": 100000000,
                "fee": 1,
                "hash": "9bd4d1db3977be4b3056084937d87c58abafdbb82ef28e4284199d1581517d4f",
                "parent": {
                    "ordinal": 33408,
                    "hash": "3e61ce6c624673267d3de1ab1587dd3a29571b88f6630aec40fb7cb159aff3bc",
                },
                "salt": 8985842168289848,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27i4K44LWUDVuoVXonhs2dtyW7DuFLD8XuGc2",
                "amount": 100000000,
                "fee": 1,
                "hash": "3e61ce6c624673267d3de1ab1587dd3a29571b88f6630aec40fb7cb159aff3bc",
                "parent": {
                    "ordinal": 33407,
                    "hash": "6d47712dd45bd53af854280a322dd0871d6ccdce96094a876423fcb290de4499",
                },
                "salt": 8978717164451980,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27i2brcFxc1JRFNySp21SMUc1R9hggS51xcgg",
                "amount": 100000000,
                "fee": 1,
                "hash": "6d47712dd45bd53af854280a322dd0871d6ccdce96094a876423fcb290de4499",
                "parent": {
                    "ordinal": 33406,
                    "hash": "c8f76c64844bdf710031adfbbfac899ed4171db4f24167195edadb3e5d06cf47",
                },
                "salt": 8915752233340226,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27fopFHKXmtijNgH57DFJ9476Czb2xdcGRAMC",
                "amount": 100000000,
                "fee": 1,
                "hash": "c8f76c64844bdf710031adfbbfac899ed4171db4f24167195edadb3e5d06cf47",
                "parent": {
                    "ordinal": 33405,
                    "hash": "21df5a47f0e98e592e85089c946b449136895dab62b7cc88347f300cdd777a13",
                },
                "salt": 8734100165219902,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27fSeDzduh6Zk2A7po3Duw1AE7dktN86LsSWL",
                "amount": 100000000,
                "fee": 1,
                "hash": "21df5a47f0e98e592e85089c946b449136895dab62b7cc88347f300cdd777a13",
                "parent": {
                    "ordinal": 33404,
                    "hash": "547f9805e9719dca9234f5d35333839599a539ffa4d0d5a537a755877f4f49e3",
                },
                "salt": 8904131102063956,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27fMZ5reZgsnwvHWpEsz9v47euCKMwHwF6Cvn",
                "amount": 100000000,
                "fee": 1,
                "hash": "547f9805e9719dca9234f5d35333839599a539ffa4d0d5a537a755877f4f49e3",
                "parent": {
                    "ordinal": 33403,
                    "hash": "be697aa499ea646482e0c5bb9db3146863600c39cc7ad08f59b02709afa8fca8",
                },
                "salt": 8948629402692807,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27eXyp9nZxLamKoSrgTPURMdVncrjXYuY4ZVU",
                "amount": 100000000,
                "fee": 1,
                "hash": "be697aa499ea646482e0c5bb9db3146863600c39cc7ad08f59b02709afa8fca8",
                "parent": {
                    "ordinal": 33402,
                    "hash": "e850cc4956487c951309fd3904fa08ede108792d5f5bb31d6fbd3ce1b715e3e3",
                },
                "salt": 8820338923473056,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27eLPspxZq43FSLEeS6FcPUBZFWLbJkVUBjSz",
                "amount": 100000000,
                "fee": 1,
                "hash": "e850cc4956487c951309fd3904fa08ede108792d5f5bb31d6fbd3ce1b715e3e3",
                "parent": {
                    "ordinal": 33401,
                    "hash": "6b1daa4a954cace3efd517e61a03970750ccdced73ea91bec8927e694628295e",
                },
                "salt": 8967794715079645,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27bcCyZseJbrdRXAVhtJStz4AWeYqR9UeVgtF",
                "amount": 100000000,
                "fee": 1,
                "hash": "6b1daa4a954cace3efd517e61a03970750ccdced73ea91bec8927e694628295e",
                "parent": {
                    "ordinal": 33400,
                    "hash": "797980c8e0ee4bbf47b2fb3bb8658e8eb4e395e8e4040d233b26f87340164851",
                },
                "salt": 8980621309048597,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27YpfWuDzWyzwmWsjtv9W78LyFXV63N77qA2b",
                "amount": 100000000,
                "fee": 1,
                "hash": "797980c8e0ee4bbf47b2fb3bb8658e8eb4e395e8e4040d233b26f87340164851",
                "parent": {
                    "ordinal": 33399,
                    "hash": "786a198e6e7181a5add1f52aa4b6e565711a7855e377557272caa06445b533de",
                },
                "salt": 8924984977173992,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27Vph52tNmgh2vfoWEonqtDeVKvJD4VZMdVri",
                "amount": 100000000,
                "fee": 1,
                "hash": "786a198e6e7181a5add1f52aa4b6e565711a7855e377557272caa06445b533de",
                "parent": {
                    "ordinal": 33398,
                    "hash": "de584a41c968bf8a5085288603d8d70f5b4d738a86495bee88071bde63dbb9ee",
                },
                "salt": 8989415856577059,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27VAkStefBECu8Rne5KK9jV9dMMLn3iM6QXvY",
                "amount": 100000000,
                "fee": 1,
                "hash": "de584a41c968bf8a5085288603d8d70f5b4d738a86495bee88071bde63dbb9ee",
                "parent": {
                    "ordinal": 33397,
                    "hash": "2ae2027afffac0369a4e0bbe04a66bf4b7a0f6fc1e4876e3c5a27e9f60ec90c2",
                },
                "salt": 8869578238043367,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27Tgxx8eQhE2y8WYpnZt742uHMEKwKbFWDFSk",
                "amount": 100000000,
                "fee": 1,
                "hash": "2ae2027afffac0369a4e0bbe04a66bf4b7a0f6fc1e4876e3c5a27e9f60ec90c2",
                "parent": {
                    "ordinal": 33396,
                    "hash": "e08a06983e6f8de032de90e370397ebc95aa07c13c35864de571d9f65c6636cd",
                },
                "salt": 8798491864338190,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27TFBK87jU1fokCmkci3BV6wS7vNQVsvvxc8j",
                "amount": 100000000,
                "fee": 1,
                "hash": "e08a06983e6f8de032de90e370397ebc95aa07c13c35864de571d9f65c6636cd",
                "parent": {
                    "ordinal": 33395,
                    "hash": "deccdc9a3e7720c2cfc9070f4418ff42961efc8141566c305451ee044437cc22",
                },
                "salt": 8771405645526666,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27T4KYDeVQzhHzicecBVRVuKf1ARtf17Yq9ue",
                "amount": 100000000,
                "fee": 1,
                "hash": "deccdc9a3e7720c2cfc9070f4418ff42961efc8141566c305451ee044437cc22",
                "parent": {
                    "ordinal": 33394,
                    "hash": "87e5554540b31a618a873ccb485e4b7c03777e654542675987ddf911f3086f5b",
                },
                "salt": 8831052809443472,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27S44HbCAHFbrB8oS5pmiRVZJ1QZuuQPYjWJz",
                "amount": 100000000,
                "fee": 1,
                "hash": "87e5554540b31a618a873ccb485e4b7c03777e654542675987ddf911f3086f5b",
                "parent": {
                    "ordinal": 33393,
                    "hash": "3af25d3b42610056bb88670bb111f1e523016d77131bd44beafefb0dc91dccbc",
                },
                "salt": 8982473152350769,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27Rt8tPKcdUyF2VLrpLUiu8bLMkC6o2hD95YY",
                "amount": 100000000,
                "fee": 1,
                "hash": "3af25d3b42610056bb88670bb111f1e523016d77131bd44beafefb0dc91dccbc",
                "parent": {
                    "ordinal": 33392,
                    "hash": "47232411e71be94758def53eaa316fee48b2f2f36a731fed1acf7fc1fa127843",
                },
                "salt": 8874858234016594,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27QfQDvjEzMNYChnnsCjSJhw5F8cpCHMouibQ",
                "amount": 100000000,
                "fee": 1,
                "hash": "47232411e71be94758def53eaa316fee48b2f2f36a731fed1acf7fc1fa127843",
                "parent": {
                    "ordinal": 33391,
                    "hash": "4b4ecb4d7bb81590a66ac08266f7fcb3930b984b2bd97ce91c3a4ccf5cced189",
                },
                "salt": 8910781261250690,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27PA5bDAgPmSvh8J14g4e6Y8nkWSKydqXt4dJ",
                "amount": 100000000,
                "fee": 1,
                "hash": "4b4ecb4d7bb81590a66ac08266f7fcb3930b984b2bd97ce91c3a4ccf5cced189",
                "parent": {
                    "ordinal": 33390,
                    "hash": "82528adfe40a1bb3fc281a2a726f1cf7b23d93b95d72c7187dc343c5d53cc2c7",
                },
                "salt": 8957741477249166,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27NyLedbDV2fvDkfZYzQaex8RRHcFKTD3BnCM",
                "amount": 100000000,
                "fee": 1,
                "hash": "82528adfe40a1bb3fc281a2a726f1cf7b23d93b95d72c7187dc343c5d53cc2c7",
                "parent": {
                    "ordinal": 33389,
                    "hash": "e17d4a748c6a98f1a00df3095c417e3194ba57a520fdf46d984997aa4ed21399",
                },
                "salt": 8744864859432907,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27Mpp1N8UD7qtJKeYizDv4QggCckNDuZS2jKE",
                "amount": 100000000,
                "fee": 1,
                "hash": "e17d4a748c6a98f1a00df3095c417e3194ba57a520fdf46d984997aa4ed21399",
                "parent": {
                    "ordinal": 33388,
                    "hash": "13975e2c6e264c34dcd0e17e405858a6b42b94890264517548210d2269d08c11",
                },
                "salt": 8732735795450885,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
            {
                "source": "DAG5KmHp9gFS723uN6uukwRqCTwvrddaW5QuKKKz",
                "destination": "DAG27M67xRGog7Sktk8CFoJ5K4R2de1t7bQ9x2Lo",
                "amount": 100000000,
                "fee": 1,
                "hash": "13975e2c6e264c34dcd0e17e405858a6b42b94890264517548210d2269d08c11",
                "parent": {
                    "ordinal": 33387,
                    "hash": "20a3ed206f940dc3cf50bfbe8ace94ec3d320cd9943ca38fdf2b10a7b0c31399",
                },
                "salt": 8780003328586561,
                "block_hash": "6846023a1a4fb6a88953fc5ae31e3d9eee2034d27e78efe690f3e19ff88d0063",
                "snapshot_hash": "3e34c85769f1dbd886dbb6b17c042ce55a4e715ccd867098b3bb57d580ab3708",
                "snapshot_ordinal": 2404170,
                "transaction_original": None,
                "timestamp": datetime(
                    2024, 7, 16, 22, 37, 37, 697000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": {
                    "next": "eyJoYXNoIjoiMjBhM2VkMjA2Zjk0MGRjM2NmNTBiZmJlOGFjZTk0ZWMzZDMyMGNkOTk0M2NhMzhmZGYyYjEwYTdiMGMzMTM5OSJ9"
                },
            },
        ]

    @pytest.mark.asyncio
    async def test_get_rewards_by_snapshot(self, network):
        network.config("integrationnet")
        results = await network.be_api.get_rewards_by_snapshot(2504170)
        print([r.model_dump() for r in results])
        assert [r.model_dump() for r in results] == [
            {
                "destination": "DAGSTARDUSTCOLLECTIVEHZOIPHXZUBFGNXWJETZVSPAPAHMLXS",
                "amount": 3292181069,
            },
            {
                "destination": "DAG8zJDJnxRfhYX2uoCb3rTVPUYeSmyo1UEXez2n",
                "amount": 13168724,
            },
            {
                "destination": "DAG8YjP3K7WCgUxsJtoKtb2ri5cLRERMPGvLwgcr",
                "amount": 13168724,
            },
            {
                "destination": "DAG8Wu5QFCqEzT8L12Fcyq5eGHNdxdw9KL5GPafz",
                "amount": 13168724,
            },
            {
                "destination": "DAG8VWWrxvFtH6f5VAMU7QQ3ScDJ43UHcXqcP61Z",
                "amount": 13168724,
            },
            {
                "destination": "DAG8VT7bxjs1XXBAzJGYJDaeyNxuThikHeUTp9XY",
                "amount": 3292181069,
            },
            {
                "destination": "DAG8QgoD39o5hKJ6564rco74Trx163nYZ94QM8uW",
                "amount": 13168724,
            },
            {
                "destination": "DAG8mz1jFPRHRV1EWPX5g7TMeKACxFV3nvXwBgCm",
                "amount": 13168725,
            },
            {
                "destination": "DAG8MmAVxrNFZSWRshH7bmf1AXsgkEeyoSbEJkkZ",
                "amount": 13168724,
            },
            {
                "destination": "DAG8JZJGGrFQs2SvLbYWP5HZ7gJHtDUszEgf3Xxx",
                "amount": 13168724,
            },
            {
                "destination": "DAG8HK2o1SCTUP6NZuW8ton1euZyht8VYacEenap",
                "amount": 13168724,
            },
            {
                "destination": "DAG8HaRvrtKyAkhy9rNHJCsrYcaVndMGwJx8kyHN",
                "amount": 13168724,
            },
            {
                "destination": "DAG8drf58PfFEHzkNpcdg4cVKLdELxH1q8qytayB",
                "amount": 13168724,
            },
            {
                "destination": "DAG8djGkp4a9gQyVzpfwiePr5Laba5eorr9kwF12",
                "amount": 13168724,
            },
            {
                "destination": "DAG8bxrEjLbqPeMsN233MGFGqrLcpgbdXwQzYrYv",
                "amount": 13168724,
            },
            {
                "destination": "DAG8Asd2jLRfy5pA6hTmxJ8Yn1wChSFSbdpn4WRq",
                "amount": 13168724,
            },
            {
                "destination": "DAG89CVPVLwMpDVN7snKGcBL54sB4e3Y56k5S5xi",
                "amount": 13168724,
            },
            {
                "destination": "DAG87Q35NsAFSw1kG8B1JSQCGmTqDz1JpiDvQYgd",
                "amount": 13168725,
            },
            {
                "destination": "DAG811pBdd5HGTVni44iUMtiUuj2HzPdsBTNCuUi",
                "amount": 13168724,
            },
            {
                "destination": "DAG7zzgDp5i7Y5YqSFhpBZ6TkYHaK93JDt8dZdTf",
                "amount": 13168724,
            },
            {
                "destination": "DAG7YCtZJzd3WNV2SsXj1Jo7qXw4HvTGhMnthpt8",
                "amount": 13168724,
            },
            {
                "destination": "DAG7wWEfUbnWNFri8SQt26SBVEUVrwdmRwUVHYXF",
                "amount": 13168725,
            },
            {
                "destination": "DAG7Wfhp55yk6f5AUDc8a2D8WxnVZqjGmHt3YGy1",
                "amount": 13168724,
            },
            {
                "destination": "DAG7vXeZTnFDm37HWGCWRtBjaVJJSqZvneADo33A",
                "amount": 13168724,
            },
            {
                "destination": "DAG7SCMNpqcqHYZkWxZw4wSojKv6MvWmcg8RiZW7",
                "amount": 13168725,
            },
            {
                "destination": "DAG7NNrJK2kmNnGcBwAmqxrp1iioRKG5uE4H2f2b",
                "amount": 13168725,
            },
            {
                "destination": "DAG7n8ZpxSBTFGzPyEpHWUV377ExST2FVu2HJ5NP",
                "amount": 13168724,
            },
            {
                "destination": "DAG7mZfUDiRyWZGDjEEf5espBYdB9ajMtMXCm2er",
                "amount": 13168725,
            },
            {
                "destination": "DAG7JGReB7SQDThBt5xkRzFSLBuRpPAr8wnXBq5i",
                "amount": 13168724,
            },
            {
                "destination": "DAG7ijtUZRLQjp72uCSpLoQutM7CrLhharUwZYxT",
                "amount": 13168724,
            },
            {
                "destination": "DAG7gqUoqdmmTYLb8AV7uoQcB2Wvasstzux98YhD",
                "amount": 13168725,
            },
            {
                "destination": "DAG7FSV5RGXNPUKcFZLJLqz5NPspgpa6ZWvuNbPd",
                "amount": 13168724,
            },
            {
                "destination": "DAG7fdF6mUCBukPH9d38oCy5QG9rFiYLCfMBky3h",
                "amount": 13168724,
            },
            {
                "destination": "DAG7dHS4QTnBvNi914N6RtYxb8XoourQJoYbfvz2",
                "amount": 13168725,
            },
            {
                "destination": "DAG7CzDn4BgQu8RPDpW3TkDVCkMSdVL19yryFZ9C",
                "amount": 13168724,
            },
            {
                "destination": "DAG77VVVRvdZiYxZ2hCtkHz68h85ApT5b2xzdTkn",
                "amount": 13168724277,
            },
            {
                "destination": "DAG77DM3gLBuZfJ72w1RHXDtWGN8CeQ6PgYPaYsX",
                "amount": 13168725,
            },
            {
                "destination": "DAG76M3oSbstSwANBz88DBDHrGgtAuaBEATuVBpL",
                "amount": 13168724,
            },
            {
                "destination": "DAG73UNhPD2H6M6vs3WoEDgzvb5mLTq1auQT8gfK",
                "amount": 13168724,
            },
            {
                "destination": "DAG73r6tddpCtswC4L16vFg5kAejKYMW1PV2PM6x",
                "amount": 13168724,
            },
            {
                "destination": "DAG716ALSFmeM1PZLyZ65q4DGn9J3WbSVpy9ETg8",
                "amount": 13168724,
            },
            {
                "destination": "DAG6ypoT1X1ZpGKumy4SeVftDECKZD18KCsRHhwL",
                "amount": 13168724,
            },
            {
                "destination": "DAG6yjC48183uuLGBGMiPkmcsRM78LsEreoPv3SL",
                "amount": 13168724,
            },
            {
                "destination": "DAG6Y5tGkKn5v7wN158Cr55MnWc91ku9UcAYUEaP",
                "amount": 13168724,
            },
            {
                "destination": "DAG6xHpnRH4QJGqTecpFtfQUFX1MxGxHZ1cagoXi",
                "amount": 13168725,
            },
            {
                "destination": "DAG6txgy7uqgdKZmHPQTJv29YcsiV4ntQ6gSbbL5",
                "amount": 13168725,
            },
            {
                "destination": "DAG6qTJ4CdNmHs8NosUkS2nMKCC95D5iavpYZaZY",
                "amount": 13168724,
            },
            {
                "destination": "DAG6o95gCq5dS4o7U7Am6v8BkhbnuwsdiZQRwqJE",
                "amount": 13168724,
            },
            {
                "destination": "DAG6LYwRx44stSmYmn24ZudQmEEt4GRxAekxjS33",
                "amount": 13168724,
            },
            {
                "destination": "DAG6LiKykvLkdHhEqaiYrAWy639jmfYZ17oLYdu7",
                "amount": 13168724,
            },
            {
                "destination": "DAG6KXuPGu2HB7tdkrCssaeutSN5ioeVeB7p7U5h",
                "amount": 13168724,
            },
            {
                "destination": "DAG6iXXxC1PUZFVoeB9yf6AFMBDMQT5AGDyaoJ3o",
                "amount": 13168725,
            },
            {
                "destination": "DAG6foKfPYqKMEyLccPi9jJEZNw2RsUFWEHB4NrA",
                "amount": 13168724,
            },
            {
                "destination": "DAG6dbSaWW7vU4DZNeHTjsWKj6b8723Dmq5nhmJm",
                "amount": 13168725,
            },
            {
                "destination": "DAG6Cio3hYk5Ujh6J9rhZCWTd62GYAyzBU2vhcXH",
                "amount": 13168725,
            },
            {
                "destination": "DAG6BtaaJgswcSiaugcWmhyRUEtD6tooMFohT27f",
                "amount": 13168724,
            },
            {
                "destination": "DAG6bbSWaBRQ5Zq38yavBqojdWnTus53FGMGKoRp",
                "amount": 13168724,
            },
            {
                "destination": "DAG6BBJzxbHBPEocRiLJaFTy3WHm3dtegjEiqggJ",
                "amount": 13168725,
            },
            {
                "destination": "DAG69r4PW83zAxeNC7erpUCYUG6qcE6zPAHe71xz",
                "amount": 13168724,
            },
            {
                "destination": "DAG68P9rxLprNauRgRNgP2Ff9h1euV2ixFCF2nSn",
                "amount": 13168725,
            },
            {
                "destination": "DAG63Eddem5U5N62yMWe2sk3Gmc9T4rJ3orwrsSe",
                "amount": 13168724,
            },
            {
                "destination": "DAG5za7kj1H7aoq1EdzuMB8ymNu62FXMikfTwLwU",
                "amount": 13168725,
            },
            {
                "destination": "DAG5YYawX1nJmG7pKCmTdLhtrhTpvZDJfV6rVDSk",
                "amount": 13168724,
            },
            {
                "destination": "DAG5XZs5aF6myfgNjLKrWzE3JT1om3vQ2z9CtGR3",
                "amount": 13168724,
            },
            {
                "destination": "DAG5XGYSdAtr6NijwnqxzyZaUbPc8QQEcELYkLgZ",
                "amount": 13168724,
            },
            {
                "destination": "DAG5vbqJ4VXWRpqfcRLgiQ35HE3vYJXYHfbWv53B",
                "amount": 13168724,
            },
            {
                "destination": "DAG5UQTCbBx4C2oLttMue8xsEdymtAbUCcxBsYeN",
                "amount": 13168725,
            },
            {
                "destination": "DAG5teGVRQC8LEAcZwtnG2wwyDmBNcAc6BgiEy7h",
                "amount": 13168724,
            },
            {
                "destination": "DAG5t6kbeBPQoGnpN1P662JmN4hjbbZPFFTRzQ7J",
                "amount": 13168725,
            },
            {
                "destination": "DAG5soH85JdGw2mB6TUwpovmmJncKqG2eGqWvfXa",
                "amount": 13168725,
            },
            {
                "destination": "DAG5r4jGLpruFjRiGDQVyUZwqHy2GpkcSthWS116",
                "amount": 13168725,
            },
            {
                "destination": "DAG5oK1LzLWSmPKi5rJL1GP7NCbzkjstVyTnQePf",
                "amount": 13168724,
            },
            {
                "destination": "DAG5oALC6HkEWSFTbSaY7XfLbEiS1PLhUueyuuNq",
                "amount": 13168724,
            },
            {
                "destination": "DAG5NQ2p3bYtXZFB3gcJyWise6qfxohPjYTkgtPo",
                "amount": 13168724,
            },
            {
                "destination": "DAG5nGsdmrV5EQGh9KrR6uiey4YER83mqqo4xwn2",
                "amount": 13168724,
            },
            {
                "destination": "DAG5mTwh2KvkTFbJEWveTb92cAneciP64dURSWDG",
                "amount": 13168724,
            },
            {
                "destination": "DAG5MmRunS6DCD6owJVcou1BHPYS2ZPLbD9y8j9G",
                "amount": 13168724,
            },
            {
                "destination": "DAG5M9TU8f9XZrGEi9BxWC19iXHJQmpPG5WsCYjZ",
                "amount": 13168724,
            },
            {
                "destination": "DAG5kkRSktD7mfeiaE2dPPt7yWek2Pritxq5qmFc",
                "amount": 13168724,
            },
            {
                "destination": "DAG5kFWqLX9nCMEv6sHcSTaGDFrrETKFRt5rV3LS",
                "amount": 13168724,
            },
            {
                "destination": "DAG5k7PkcDHrPxMorUdZ2fodnc5ggwWQjzfnyZs9",
                "amount": 13168724,
            },
            {
                "destination": "DAG5jPRqjXvUnVYBc3nWreAeaeNnoJ2bCgQbmphA",
                "amount": 13168725,
            },
            {
                "destination": "DAG5HU65RV1KJMH9LYGiBuB8BZZfJ4FZgyA7g1vt",
                "amount": 13168725,
            },
            {
                "destination": "DAG5HHwHL2YmjJLThUWck59uDG7QrxShcUkUVnGp",
                "amount": 13168725,
            },
            {
                "destination": "DAG5h3ovBqMkC1tfxwhsavLCn3Lc3Z4LzkGDGLNe",
                "amount": 13168724,
            },
            {
                "destination": "DAG5gauM9AfbVHRiA9oVNoo4QmEeBn1vzAZKSKYG",
                "amount": 13168725,
            },
            {
                "destination": "DAG5FNpeDLgh4ZFnYgUr7c64cngg8QycrmffuGW3",
                "amount": 13168724,
            },
            {
                "destination": "DAG5eJaVkCqsyXN8DurEKeZ8jC7aztEgrpgBZSGQ",
                "amount": 13168724,
            },
            {
                "destination": "DAG5AmgDqthym43A7GXBSVYWv9Lj9QHXGUyQbgBG",
                "amount": 13168725,
            },
            {
                "destination": "DAG58VfzPeABVR7bDw9JMHf1GgaakBfDY7jwDQz9",
                "amount": 13168724,
            },
            {
                "destination": "DAG55N9AuWkYaBCEUKkQo435Tq3Hpxi3Pwsv8LG1",
                "amount": 13168724,
            },
            {
                "destination": "DAG54ztnw9rSv8SjPZYPbaqUZsoCm4QFCLDPdF43",
                "amount": 13168724,
            },
            {
                "destination": "DAG53qe3Vr2frts9o2Y9LzXtS92Qji1y1SfatoEs",
                "amount": 13168724,
            },
            {
                "destination": "DAG4yMYC8u6pGBJBnkxd24KEiRvFJg2cCyAWyBAZ",
                "amount": 13168725,
            },
            {
                "destination": "DAG4v8H4pDWtp6EqL6kSnEq2hQp3HnjDNHX2LFwV",
                "amount": 13168725,
            },
            {
                "destination": "DAG4UGS3z9vMAo6pxRPLK9U9Cyy4XASAoYhXbyNV",
                "amount": 13168724,
            },
            {
                "destination": "DAG4SMNaVHuLp3Dgd1xeEfrY4Aa6K1P97XySyLDB",
                "amount": 13168725,
            },
            {
                "destination": "DAG4RC8Tn1F5Vx2N26HNkh8j6yLUpb2e274BW5fT",
                "amount": 13168724,
            },
            {
                "destination": "DAG4q72D71W4UFDbGnG2kRPFxd86WCvbyoe2WN1A",
                "amount": 13168724,
            },
            {
                "destination": "DAG4Q6tNFweUvhqDbZM9zcf6TP2vogNLPSz8aBNR",
                "amount": 13168725,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_latest_snapshot_transactions(self, network):
        network.config("integrationnet")
        results = await network.be_api.get_latest_snapshot_transactions()
        assert isinstance(results, list), (
            f"Snapshot data should be a list, got {type(results)}"
        )

    @pytest.mark.asyncio
    async def test_get_latest_snapshot_rewards(self, network):
        network.config("integrationnet")
        results = await network.be_api.get_latest_snapshot_rewards()
        assert isinstance(results, list), "Snapshot data should be a list"

    @pytest.mark.asyncio
    async def test_get_transactions(self, network):
        network.config("integrationnet")
        num_of_snapshots = 12
        results = await network.be_api.get_transactions(limit=num_of_snapshots)
        assert len(results) == num_of_snapshots, "Snapshot data should be a list"

    @pytest.mark.asyncio
    async def test_get_transaction(self, network):
        result = await network.be_api.get_transaction(
            "dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e"
        )
        assert result.model_dump() == {
            "source": "DAG2AhT8r7JoQb8fJNEKFLNEkaRSxjNmZ6Bbnqmb",
            "destination": "DAG7b166Y3dzREaLxfTsrFdbwzScxHZSdVrQaQUA",
            "amount": 25000110000000,
            "fee": 0,
            "hash": "dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e",
            "parent": {
                "ordinal": 77,
                "hash": "ff765b26b12e2f63fbda7d33efb6728be3dec86856fb85922c8fa2d8d7062555",
            },
            "salt": 8940539553876237,
            "block_hash": "85f034cf2df202ced872da05ef3eaf00cd1117e0f8deef9d56022505457072e9",
            "snapshot_hash": "baa81574222c46c9ac37baa9eeea97b83f4f02aa46e187b19064a64188f5132f",
            "snapshot_ordinal": 2829094,
            "transaction_original": None,
            "timestamp": datetime(2024, 9, 15, 18, 47, 33, 82000, tzinfo=timezone.utc),
            "proofs": [],
            "meta": None,
        }

    @pytest.mark.asyncio
    async def test_get_latest_currency_snapshot(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        result = await network.be_api.get_latest_currency_snapshot(el_paca_metagraph_id)
        assert isinstance(result.hash, str)

    @pytest.mark.asyncio
    async def test_get_currency_snapshot(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        result = await network.be_api.get_currency_snapshot(
            el_paca_metagraph_id, 1488009
        )
        assert result.model_dump() == {
            "hash": "0eefc8e08edf7a0933a546103c22cbfb090bfc54264977bba0240684150de5f9",
            "ordinal": 1488009,
            "height": 1119,
            "sub_height": 3450,
            "last_snapshot_hash": "c3c7eef84d57df264faff5a0589b6f7049170408131514c1a81db0b6be08ecb2",
            "blocks": [],
            "timestamp": datetime(2025, 6, 6, 5, 19, 13, 917000, tzinfo=timezone.utc),
            "fee": 400000,
            "owner_address": "DAG5VxUBiDx24wZgBwjJ1FeuVP1HHVjz6EzXa3z6",
            "staking_address": None,
            "size_in_kb": 4,
            "meta": None,
        }

    @pytest.mark.asyncio
    async def test_get_latest_currency_snapshot_rewards(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        results = await network.be_api.get_latest_currency_snapshot_rewards(
            el_paca_metagraph_id
        )
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_get_currency_snapshot_rewards(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        results = await network.be_api.get_currency_snapshot_rewards(
            el_paca_metagraph_id, 950075
        )
        assert [r.model_dump() for r in results] == [
            {
                "destination": "DAG4eVyr7kUzr7r2oPoxnUfLDgugdXYXLDh6gxZS",
                "amount": 200000000,
            },
            {
                "destination": "DAG3dQwyG69DmcXxqAQzfPEp39FEfepc3iaGGQVg",
                "amount": 200000000,
            },
            {
                "destination": "DAG2YaNbtUv35YVjJ5U6PR9r8obVunEky2RDdGJb",
                "amount": 100000000,
            },
            {
                "destination": "DAG2ACig4MuEPit149J1mEjhYqwn8SBvXgVuy2aX",
                "amount": 300000000,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_currency_address_balance(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        try:
            result = await network.be_api.get_currency_address_balance(
                metagraph_id=el_paca_metagraph_id,
                hash="b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364",
            )
        except httpx.ConnectError:
            pytest.skip("Connection Error")
        else:
            result = result.model_dump()
            result.pop("ordinal")
            assert result == {
                "balance": 0,
                "address": "b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364",
                "meta": None,
            }

    @pytest.mark.asyncio
    async def test_get_currency_transaction(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        result = await network.be_api.get_currency_transaction(
            metagraph_id=el_paca_metagraph_id,
            hash="121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
        )
        assert result.model_dump() == {
            "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
            "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
            "amount": 1300000000,
            "fee": 0,
            "hash": "121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
            "parent": {
                "ordinal": 19,
                "hash": "d29fdbc9b560f49387d0d8539ecdeca12314c6c5829919a0cdac0e6ab24d1f7a",
            },
            "salt": 8896174606352968,
            "block_hash": "3f78913ae81bb1a288fa859c2901c00587960c8555e40978ae1b4dbcbf9c4478",
            "snapshot_hash": "c1c9215f51e8016e7fcf3714b6118bda8349348207fb40f7e6fb6ec27cfc2b33",
            "snapshot_ordinal": 952394,
            "transaction_original": None,
            "timestamp": datetime(2025, 2, 13, 1, 10, 5, 98000, tzinfo=timezone.utc),
            "proofs": [],
            "meta": None,
        }

    @pytest.mark.asyncio
    async def test_get_currency_transactions(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        results = await network.be_api.get_currency_transactions(
            metagraph_id=el_paca_metagraph_id, limit=3
        )
        assert len([r.model_dump() for r in results]) == 3

    @pytest.mark.asyncio
    async def test_get_currency_transactions_by_address(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        results = await network.be_api.get_currency_transactions_by_address(
            metagraph_id=el_paca_metagraph_id,
            address="DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
            limit=3,
        )
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_currency_transactions_by_snapshot(self, network):
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
        results = await network.be_api.get_currency_transactions_by_snapshot(
            metagraph_id=el_paca_metagraph_id, hash_or_ordinal=952394, limit=3
        )
        assert [r.model_dump() for r in results] == [
            {
                "source": "DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY",
                "destination": "DAG0fNmxAvUJh5133TttDC9tm1Lx4bdY1GuuPZCK",
                "amount": 1300000000,
                "fee": 0,
                "hash": "121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
                "parent": {
                    "ordinal": 19,
                    "hash": "d29fdbc9b560f49387d0d8539ecdeca12314c6c5829919a0cdac0e6ab24d1f7a",
                },
                "salt": 8896174606352968,
                "block_hash": "3f78913ae81bb1a288fa859c2901c00587960c8555e40978ae1b4dbcbf9c4478",
                "snapshot_hash": "c1c9215f51e8016e7fcf3714b6118bda8349348207fb40f7e6fb6ec27cfc2b33",
                "snapshot_ordinal": 952394,
                "transaction_original": None,
                "timestamp": datetime(
                    2025, 2, 13, 1, 10, 5, 98000, tzinfo=timezone.utc
                ),
                "proofs": [],
                "meta": None,
            }
        ]
