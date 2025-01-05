import asyncio

from dag_wallet import Wallet


async def main():
    """Test stuff"""
    print("Step 1: Create new wallet")
    wallet = Wallet.new()
    balance = await wallet.get_address_balance()
    print("Done!")
    print("Step 2: Build Transaction")
    tx = await wallet.transaction(to_address='DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', amount=1.0, fee=0.0002)
    print("Done!")
    print("Step 3: Post Transaction")
    resp = await wallet.send(tx)
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())



