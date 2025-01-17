import asyncio
from time import sleep

from dag_wallet import Wallet
from os import getenv

WORDS = getenv("WORDS")
TO_ADDR = getenv("TO_ADDR")


async def main():
    """Testing stuff here"""
    # print("Step 1: Create new wallet")
    # wallet = Wallet.new()
    print("Step 1: Import wallet:")
    wallet = Wallet.from_mnemonic(WORDS)
    # TODO: Add sign data and dL1_host
    wallet = wallet.set_network(network="integrationnet", l1_host="http://dormintnet-cl1-1183959999.us-west-2.elb.amazonaws.com:8000")
    balance = await wallet.get_address_balance()
    print("Balance: ", balance, "$iDAG")
    print("Done!")
    print("Step 2: Build Transaction")
    tx = await wallet.transaction(to_address=TO_ADDR, amount=1.0, fee=0.002)
    print("Done!")
    print("Step 3: Post Transaction")
    tx_hash = await wallet.send(tx)
    print(f"Sending Transaction ({tx_hash})...")
    while True:
        t = 1
        pending = await wallet.get_pending_transaction(
            transaction_hash=tx_hash)
        if not pending:
            break
        print(f"Transaction is currently \"{pending.status.lower()}\". Checking in {t}...")
        await asyncio.sleep(t)
    print("Transaction Sent!")

if __name__ == "__main__":
    asyncio.run(main())



