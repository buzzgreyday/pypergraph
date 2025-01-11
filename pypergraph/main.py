import asyncio
from time import sleep

from dag_wallet import Wallet
from os import getenv

ADDR = getenv("ADDR")
TO_ADDR = getenv("TO_ADDR")


async def main():
    """Testing stuff here"""
    # print("Step 1: Create new wallet")
    # wallet = Wallet.new()
    # print("Step 1: Import wallet:")
    # mnemonic_phrase = Wallet.get_mnemonic_from_input()
    print(ADDR, TO_ADDR)
    wallet = Wallet.from_mnemonic(ADDR)
    balance = await wallet.get_address_balance(metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43")
    print("Balance: ", balance, "$PACA")
    print("Done!")
    print("Step 2: Build Transaction")
    tx = await wallet.transaction(to_address=TO_ADDR, amount=1.0, fee=0.0002)
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
        sleep(t)
    print("Transaction Sent!")

if __name__ == "__main__":
    asyncio.run(main())



