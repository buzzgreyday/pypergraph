import asyncio
from os import getenv

from pypergraph.dag_keyring import KeyringManager
from pypergraph.dag_account.account import DagAccount

WORDS = getenv("WORDS")

async def main():

    network_info = {"network_id": "integrationnet", "be_url": "https://be-integrationnet.constellationnetwork.io", "l0_host": None, "cl1_host": None, "l0_lb_url": "https://l0-lb-integrationnet.constellationnetwork.io", "l1_lb_url": "https://l1-lb-integrationnet.constellationnetwork.io"}
    wallet = DagAccount()
    wallet.login_with_seed_phrase(WORDS)
    wallet.connect(network_info)
    network_info = {"network_id": "testnet", "be_url": "https://be-testnet.constellationnetwork.io", "l0_host": None, "cl1_host": None, "l0_lb_url": "https://l0-lb-testnet.constellationnetwork.io", "l1_lb_url": "https://l1-lb-testnet.constellationnetwork.io"}
    wallet.connect(network_info)
    amount = 1 * 10000000
    fee = 2 * 1000000
    resp = await wallet.send("DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN", amount, fee=fee)
    print("Response" , resp)

    controller = KeyringManager()
    await controller.login('password')
    accounts = controller.get_accounts()
    print("Accounts:", accounts)
    vault = await controller.create_or_restore_vault("Test", WORDS, 'password')
    print("Vault:", vault)
    await controller.logout()


if __name__ == "__main__":

    # TODO: Keyring modules needs refactoring, storage needs to be implemented and we also need to think about how to proceed from here.
    asyncio.run(main())
