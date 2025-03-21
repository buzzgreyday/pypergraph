import asyncio
import logging
import traceback
from dataclasses import dataclass
from datetime import datetime
import time
from typing import Dict, Union, List, Optional

from rx import operators as ops, of, empty
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.subject import Subject

from pypergraph.account import DagAccount
from pypergraph.account.tests import secret
from pypergraph.keyring.storage import StateStorageDb
import json

from pypergraph.network.models import PendingTransaction, NetworkInfo, BlockExplorerTransaction

TWELVE_MINUTES = 12 * 60 * 1000

@dataclass
class WaitFor:
    future: asyncio.Future
    resolve: callable

@dataclass
class DagWalletMonitorUpdate:
    pending_has_confirmed: bool
    pending_txs: List[json]
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

    def _safe_account_process_event(self, observable):
        try:
            if observable["event"] == "logout":
                print(f"Logged Out!")
            elif observable["event"] == "login":
                print(f"Logged In!")
            elif observable["type"] == "add_transaction":
                asyncio.create_task(self.add_to_mem_pool_monitor(observable["event"]))
            else:
                print(f"Unknown event: {observable['event']}")
            return of(observable)
        except Exception as e:
            print(f"🚨 Error processing event: {e}")
            return empty()  # Skip this event and continue the stream

    def _safe_mem_store_process_event(self, observable: dict):
        """Process an event safely, catching errors."""
        try:
            # Simulate event processing (replace with your logic)
            if observable:
                print(f"Transaction changed: {observable['event']}")
            return of(observable)  # Emit the event downstream
        except Exception as e:
            print(f"🚨 Error processing event: {e}")
            return empty()  # Skip this event and continue the stream

    def _safe_network_process_event(self, observable: dict):
        """Process an event safely, catching errors."""
        try:
            # Simulate event processing (replace with your logic)
            print(f"Network changed: {observable['event']}")
            return of(observable)  # Emit the event downstream
        except Exception as e:
            print(f"🚨 Error processing event: {e}")
            return empty()  # Skip this event and continue the stream

    def _safe_event_processing(self, observable: dict):
        if isinstance(observable, dict):
            type: Optional[str] = observable.get("type", None)
            event: Optional[str, dict] = observable.get("event", None)
            module: Optional[str] = observable.get("module", None)
            try:
                if type == "mem_store":
                    self._safe_mem_store_process_event(observable)
                elif module == "account":
                    self._safe_account_process_event(observable)
                elif type == "network":
                    self._safe_network_process_event(observable)
                return of(observable)  # Ensure an observable is returned
            except Exception as e:
                logging.error(f"🚨 Error processing event {event}: {e}", exc_info=True)
                #return of(None)  # Send placeholder down the line
                return empty() # End the current stream entirely
        else:
            print(f"Not a dict:", observable)

    async def set_to_mem_pool_monitor(self, pool: List[dict]):
        network_info = self.account.network.get_network()
        key = f"network-{network_info['network_id'].lower()}-mempool"
        await self.cache_utils.set(key, [tx for tx in pool])

    async def get_mem_pool_from_monitor(self, address: Optional[str] = None) -> List[dict]:
        address = address or self.account.address
        network_info = self.account.network.get_network()

        try:
            txs: List[json] = await self.cache_utils.get(f"network-{network_info['network_id'].lower()}-mempool") or []
            txs = [json.loads(tx) if not isinstance(tx, dict) else tx for tx in txs] if txs else []
        except Exception as e:
            print(f'get_mem_pool_from_monitor warning: {traceback.format_exc()}, will return empty list.')
            return []
        return [tx for tx in txs if not address or not tx["receiver"] or tx["receiver"] == address or tx["sender"] == address]

    async def add_to_mem_pool_monitor(self, value: PendingTransaction):  # 'value' can be a dict or string
        network_info = NetworkInfo(**self.account.network.get_network())
        key = f"network-{network_info.network_id}-mempool"

        # Get cached payload or initialize empty list
        cached = await self.cache_utils.get(key)
        payload = cached if isinstance(cached, list) else []
        payload = [PendingTransaction(**p) for p in payload]

        # Create transaction object
        if isinstance(value, str):
            tx = PendingTransaction(**{"hash": value, "timestamp": int(time.time() * 1000)})
        elif isinstance(value, PendingTransaction):
            tx = value
        else:
            raise ValueError("Monitor :: Must be PendingTransaction.")

        # Check for existing transaction
        if not any(p.hash == tx.hash for p in payload):
            payload.append(tx)
            payload = [tx.model_dump_json()]
            await self.cache_utils.set(key, payload)
            self.last_timer = int(time.time() * 1000)
            self.pending_timer = 1000

        # Schedule polling after 1 second
        asyncio.create_task(self._schedule_poll())
        return self.transform_pending_to_transaction(tx)

    async def _schedule_poll(self):
        await asyncio.sleep(1)  # 1 second delay
        await self.poll_pending_txs()

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
                self.pending_timer = 1000
                self.last_timer = current_time
                #asyncio.create_task(self.poll_pending_txs())
            elif pending_result.pool_count > 0:
                await self.set_to_mem_pool_monitor([])

            self.mem_pool_change.on_next({"module": "monitor", "type": "mem_store", "event": pending_result})
        except Exception as e:
            print(f"🚨 Error in poll_pending_txs: {traceback.format_exc()}")

    async def process_pending_txs(self) -> DagWalletMonitorUpdate:
        try:
            pool = await self.get_mem_pool_from_monitor()
            pending_txs = []
            next_pool = []
            pending_has_confirmed = False
            tx_changed = False
            for pending_tx in pool:
                try:
                    tx_hash = pending_tx["hash"]
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
                pool_count=len(next_pool)
            )
        except Exception as e:
            print(f"🚨 Error in process_pending_txs: {traceback.format_exc()}")
            return DagWalletMonitorUpdate(
                pending_has_confirmed=False,
                pending_txs=[],
                tx_changed=False,
                pool_count=0
            )

    def transform_pending_to_transaction(self, pending: PendingTransaction) -> Dict:
        print(BlockExplorerTransaction(PendingTransaction))
        exit(0)
        return {
            "hash": pending["hash"],
            "source": pending["sender"],
            "destination": pending["receiver"],
            "amount": pending["amount"],
            "fee": pending["fee"],
            "parent": {
                "ordinal": pending["ordinal"],
                "hash": ""
            },
            "snapshot_hash": "",
            "block_hash": "",
            "timestamp": datetime.fromtimestamp(pending["timestamp"] / 1000).isoformat(),
            "transaction_original": {
                "ordinal": pending["ordinal"],
                "hash": pending["hash"]
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

    async def monitor_loop(self):
        while True:
            await self.poll_pending_txs()
            await asyncio.sleep(10)

    def start_monitor(self):
        asyncio.create_task(self.poll_pending_txs())
        asyncio.create_task(self.monitor_loop())

    async def get_latest_transactions(self, address: str, limit: Optional[int] = None, search_after: Optional[str] = None) -> List[dict]:
        c_txs = await self.account.network.get_transactions_by_address(address, limit, search_after)
        pending_result = await self.process_pending_txs()
        pending_transactions = [self.transform_pending_to_transaction(p) for p in pending_result.pending_txs]

        return pending_transactions + (c_txs if c_txs else [])

async def main():
    account = DagAccount()
    monitor = Monitor(account)
    # monitor.start_monitor()
    account.connect('testnet')
    account.login_with_seed_phrase(secret.mnemo)
    pending_tx = await account.transfer(secret.to_address, 50000, 200000)
    await monitor.add_to_mem_pool_monitor(pending_tx)
    await asyncio.sleep(60)
    account.logout()



if __name__ == "__main__":

    asyncio.run(main())
