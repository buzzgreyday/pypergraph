import asyncio
from os import getenv

from pypergraph.dag_wallet.account import DagAccount, OldDagAccount

WORDS = getenv("WORDS")

async def main():

    old_wallet = OldDagAccount.from_mnemonic(WORDS)
    print(old_wallet.address)

    network_info = {"network_id": "integrationnet", "be_url": "https://be-integrationnet.constellationnetwork.io", "l0_host": None, "cl1_host": None, "l0_lb_url": "https://l0-lb-integrationnet.constellationnetwork.io", "l1_lb_url": "https://l1-lb-integrationnet.constellationnetwork.io"}
    wallet = DagAccount()
    wallet.login_with_seed_phrase(WORDS)
    wallet = wallet.connect(network_info)
    resp = await wallet.send("DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN", 2)
    print(resp)


if __name__ == "__main__":

    # TODO: Keyring modules needs refactoring, storage needs to be implemented and we also need to think about how to proceed from here.
    asyncio.run(main())
