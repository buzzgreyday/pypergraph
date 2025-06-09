import httpx
import pytest


""" L1 API """


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
