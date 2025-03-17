# MONITOR
import asyncio
from typing import Optional

from rx import operators as ops, from_future, just, empty
from rx import of
from rx.scheduler.eventloop import AsyncIOScheduler

from pypergraph.keyring import KeyringManager
from pypergraph.keyring.encryptor import SecurityException


class KeyringMonitor:
    def __init__(self, keyring_manager: Optional[KeyringManager] = None):
        self._scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        self._keyring_manager = keyring_manager or KeyringManager(scheduler=self._scheduler)

        def event_handler(event):
            try:
                if event["type"] == "lock":
                    print("🔒 Vault locked!")
                elif event["type"] == "unlock":
                    print("🔓 Vault unlocked!")
                elif event["type"] == "account_update":
                    print("🔄 Account updated:", event["data"])
                elif event["type"] == "removed_account":
                    print("❌ Account removed:", event["data"])
                elif event["type"] == "state_update":
                    print("⚡ State updated:", event["data"])
                elif event["type"] == "error":
                    print("❗ Error:", event["data"])
            except Exception as e:
                print(f"🚨 Error handling event: {e}")

        def state_handler(state):
            if state["is_unlocked"] is False:
                print(f"Wallet is locked: {len(state['wallets'])} wallets present")
            elif state["is_unlocked"] is True:
                print(f"Wallet is unlocked: {len(state['wallets'])} wallets present")

        def error_handler(e):
            print(f"⚠️ Event processing error: {e}")
            return of(None)  # Continue processing other events

        # Catch: handle exceptions that might terminate the stream
        #self._keyring_manager._event_subject.pipe(
        #    ops.observe_on(self._scheduler),
        #    ops.catch(lambda e, src: error_handler(e)),  # Catch errors and continue
        #).subscribe(
        #    on_next=event_handler,
        #    #on_error=lambda e: print(f"🔥 Fatal event error: {e}")
        #)

        # Subscribing to _state_subject safely
        self._keyring_manager._state_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.distinct_until_changed(),
            ops.catch(lambda e, src: error_handler(e)),  # Catch errors and continue
        ).subscribe(
            on_next=state_handler,
            #on_error=lambda e: print(f"🔥 Fatal state error: {e}")
        )

        # Flat mapping: recover from specific events

        def handle_flat_map_error(event: Exception):
            print(f"⚠️ Handling error event: {event}")
            return empty(scheduler=self._scheduler)  # Emits a new observable

        self._keyring_manager._event_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.flat_map(lambda event: event_handler(event)),
        ).subscribe(
            on_next=event_handler,
            on_error=handle_flat_map_error
        )


# Running the setup
async def main():
    keyring = KeyringManager()
    monitor = KeyringMonitor(keyring)
    await keyring.login("fail")  # Should trigger an error safely
    await keyring.login("super_S3cretP_Asswo0rd")

asyncio.run(main())
