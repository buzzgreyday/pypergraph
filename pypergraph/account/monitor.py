import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Union, List, Optional

from rx import operators as ops, of, empty
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.subject import Subject

from pypergraph.account import DagAccount
from pypergraph.account.tests import secret
from pypergraph.keyring.storage import StateStorageDb
from pypergraph.network import DagTokenNetwork
from pypergraph.network.models import PendingTransaction

TWELVE_MINUTES = 12 * 60 * 1000

@dataclass
class WaitFor:
    future: asyncio.Future
    resolve: callable

@dataclass
class DagWalletMonitorUpdate:
    pending_has_confirmed: bool
    pending_txs: List[PendingTransaction]
    tx_changed: bool
    pool_count: int  # Needed for `poll_pending_txs


class Monitor:

    def __init__(self, account: DagAccount):
        self.account: DagAccount = account
        self._scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        self.mem_pool_change = Subject()
        self.last_timer = 0.0
        self.pending_timer = 0.0
        self.wait_for_map: Dict[str, WaitFor] = {}
        self.cache_utils = StateStorageDb()
        self.cache_utils.set_prefix('pypergraph-')

        # Subscribing to events safely
        self.mem_pool_change.pipe(
            ops.observe_on(self._scheduler),
            ops.flat_map(self._safe_event_processing)  # Ensures event processing continues
        ).subscribe()

        self.account._session_change.pipe(
            ops.observe_on(self._scheduler),
            ops.flat_map(self._safe_event_processing)  # Ensures event processing continues
        ).subscribe()

        self.account.network._network_change.pipe(
            ops.observe_on(self._scheduler),
            ops.flat_map(self._safe_event_processing)  # Ensures event processing continues
        ).subscribe()

    def _safe_account_process_event(self, event):
        try:
            if event == "logout":
                print(f"Logged Out!")
            elif event == "login":
                print(f"Logged In!")
            else:
                print(f"Unknown event: {event}")
            return of(event)
        except Exception as e:
            print(f"🚨 Error processing event: {e}")
            return empty()  # Skip this event and continue the stream

    def _safe_mem_store_process_event(self, event: dict):
        """Process an event safely, catching errors."""
        try:
            # Simulate event processing (replace with your logic)
            if event:
                print(f"Transaction changed: {event}")
            return of(event)  # Emit the event downstream
        except Exception as e:
            print(f"🚨 Error processing event: {e}")
            return empty()  # Skip this event and continue the stream

    def _safe_network_process_event(self, event: dict):
        """Process an event safely, catching errors."""
        try:
            # Simulate event processing (replace with your logic)
            print(f"Network changed: {event}")
            return of(event)  # Emit the event downstream
        except Exception as e:
            print(f"🚨 Error processing event: {e}")
            return empty()  # Skip this event and continue the stream

    def _safe_event_processing(self, observable: dict):
        if isinstance(observable, dict):
            event_type = observable["type"]
            event = observable["event"]
            try:
                if event_type == "mem_store":
                    self._safe_mem_store_process_event(event)
                elif event_type == "account":
                    self._safe_account_process_event(event)
                elif event_type == "network":
                    self._safe_network_process_event(event)
                return of(observable)  # Ensure an observable is returned
            except Exception as e:
                logging.error(f"🚨 Error processing event {event}: {e}", exc_info=True)
                #return of(None)  # Send placeholder down the line
                return empty() # End the current stream entirely
        else:
            print(observable)

    async def set_to_mem_pool_monitor(self, pool: List[PendingTransaction]):
        network_info = self.account.network.get_network()
        key = f"network-{network_info['network_id'].lower()}-mempool"
        await self.cache_utils.set(key, [tx.model_dump() for tx in pool])

    async def get_mem_pool_from_monitor(self, address: Optional[str] = None) -> List[PendingTransaction]:
        address = address or self.account.address
        network_info = self.account.network.get_network()

        try:
            txs: List[PendingTransaction] = [PendingTransaction(**tx) for tx in await self.cache_utils.get(f"network-{network_info['network_id'].lower()}-mempool")] or []
        except Exception as e:
            print(f'get_mem_pool_from_monitor warning: {e}, will return empty list.')
            return []

        return [tx for tx in txs if not address or not tx.receiver or tx.receiver == address or tx.sender == address]

    async def schedule_polling(self):
        await asyncio.sleep(1)  # Wait 1 second
        await self.poll_pending_txs()  # Call the function asynchronously

    async def add_to_mem_pool_monitor(self, value: Union[PendingTransaction, str]) -> Dict: # Dict PendingTx and Transaction models might go in Core
        network_info = self.account.network.get_network()
        key = f"network-{network_info['network_id'].lower()}-mempool"
        payload: List[PendingTransaction] = await self.cache_utils.get(key) or []

        tx = value if isinstance(value, PendingTransaction) else PendingTransaction(hash=value, timestamp=int(datetime.now().timestamp()*1000))

        if not any(p['hash'] == tx.hash for p in payload):
            payload.append(tx)
            await self.cache_utils.set(key, payload)
            self.last_timer = datetime.now().timestamp()
            self.pending_timer = 1000

        asyncio.create_task(self.schedule_polling())

        return self.transform_pending_to_transaction(tx)

    async def poll_pending_txs(self):
        try:
            current_time = datetime.now().timestamp() * 1000
            if current_time - self.last_timer + 1000 < self.pending_timer:
                print('Canceling extra timer')
                return

            pending_result = await self.process_pending_txs()
            pending_txs = pending_result.pending_txs

            if pending_txs:
                await self.set_to_mem_pool_monitor(pending_txs)
                self.pending_timer = 10000
                self.last_timer = current_time
                asyncio.create_task(self.schedule_polling())
            elif pending_result.pool_count > 0:
                await self.set_to_mem_pool_monitor([])

            self.mem_pool_change.on_next({"type": "mem_store", "event": pending_result})
        except Exception as e:
            print(f"🚨 Error in poll_pending_txs: {e}")

    async def process_pending_txs(self) -> DagWalletMonitorUpdate:
        try:
            pool = await self.get_mem_pool_from_monitor()
            pending_txs = []
            next_pool = []
            pending_has_confirmed = False
            tx_changed = False

            for pending_tx in pool:
                try:
                    tx_hash = pending_tx.hash
                    cb_tx = None

                    if cb_tx:
                        # Process cb_tx and update pending_tx
                        # ... (similar logic to TypeScript version)
                        next_pool.append(pending_tx)
                    else:
                        try:
                            be_tx = await self.account.network.get_transaction(tx_hash)
                            if be_tx:
                                pending_has_confirmed = True
                                tx_changed = True
                                if tx_hash in self.wait_for_map:
                                    self.wait_for_map[tx_hash].resolve(True)
                                    del self.wait_for_map[tx_hash]
                        except Exception as e:
                            print(f'Error processing transaction: {e}')

                    pending_txs.append(pending_tx)
                except Exception as e:
                    print(f"🚨 Error processing pending transaction: {e}")

            return DagWalletMonitorUpdate(
                pending_has_confirmed=pending_has_confirmed,
                pending_txs=pending_txs,
                tx_changed=tx_changed,
                pool_count=len(next_pool)  # Fix: Add pool count here
            )
        except Exception as e:
            print(f"🚨 Error in process_pending_txs: {e}")
            return DagWalletMonitorUpdate(
                pending_has_confirmed=False,
                pending_txs=[],
                tx_changed=False,
                pool_count=0  # Fix: Add pool count here
            )

    def transform_pending_to_transaction(self, pending: PendingTransaction) -> Dict:

        return {
    "hash": pending.hash,
    "source": pending.sender,
    "destination": pending.receiver,
    "amount": pending.amount,
    "fee": pending.fee,
    "parent": {
        "ordinal": pending.ordinal,
        "hash": ""
    },
    "snapshot_hash": "",
    "block_hash": "",
    "timestamp": datetime.fromtimestamp(pending.timestamp / 1000).isoformat(),
    "transaction_original": {
        "ordinal": pending.ordinal,
        "hash": pending.hash
        }
    }

    async def wait_for_transaction(self, hash: str) -> asyncio.Future:
        if hash not in self.wait_for_map:
            loop = asyncio.get_event_loop()
            future = loop.create_future()
            self.wait_for_map[hash] = WaitFor(
                future=future,
                resolve=lambda result: future.set_result(result)
            )
        return self.wait_for_map[hash].future

    def start_monitor(self):
        asyncio.create_task(self.poll_pending_txs())

    async def get_latest_transactions(self, address: str, limit: Optional[int] = None, search_after: Optional[str] = None) -> List[dict]:
        c_txs = await self.account.network.get_transactions_by_address(address, limit, search_after)
        pending_result = await self.process_pending_txs()
        pending_transactions = [self.transform_pending_to_transaction(p) for p in pending_result.pending_txs]

        return pending_transactions + (c_txs if c_txs else [])

async def main():
    account = DagAccount()
    monitor = Monitor(account)
    monitor.start_monitor()
    account.connect('testnet')
    account.login_with_seed_phrase(secret.mnemo)
    await asyncio.sleep(10)
    await account.transfer(secret.to_address, 50000, 200000)
    account.logout()
    await asyncio.sleep(25)


if __name__ == "__main__":

    asyncio.run(main())
