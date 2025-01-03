import asyncio
from asyncio import create_task

from dag_wallet import Wallet


async def main():
    """Test stuff"""
    print("Step 1: Create new wallet")
    wallet = Wallet.new()
    wallet = Wallet(address=wallet.address, public_key=wallet.public_key, private_key=wallet.private_key, words=wallet.words)
    wallet = Wallet.from_mnemonic(wallet.words)
    wallet = Wallet.from_private_key(wallet.private_key)
    print("Done!")
    print("Step 2: Build Transaction")
    tx = await wallet.build_transaction(to_address='DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', amount=1.0, fee=0.0002)
    print(tx.get_post_transaction())
    print("Done!")
    print("Step 3: Post Transaction")
    resp = await tx.send()
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())



