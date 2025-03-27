# TESTING MONITOR STUFF HERE
#
#
#

import asyncio
import logging
from typing import Optional

from rx import operators as ops, of, empty
from rx.scheduler.eventloop import AsyncIOScheduler

from pypergraph.keyring import KeyringManager

logging.basicConfig(level=logging.ERROR)

class KeyringMonitor:
    def __init__(self, keyring_manager: Optional[KeyringManager] = None):
        self._scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        self._keyring_manager = keyring_manager or KeyringManager()

        def event_handler(event):
            """Handles incoming keyring events."""
            if not isinstance(event, dict):
                logging.warning(f"⚠️ Unexpected event format: {event}")
                return

            event_type = event.get("type")
            if event_type == "lock":
                logging.debug("🔒 Vault locked!")
            elif event_type == "unlock":
                logging.debug("🔓 Vault unlocked!")
            elif event_type == "account_update":
                logging.info("🔄 Account updated:", event["data"])
            elif event_type == "removed_account":
                logging.info("❌ Account removed:", event["data"])
            elif event_type == "state_update":
                logging.debug(f"⚡ State updated, has {len(event['data']['wallets'])} wallet(s): {event['data']}")
            else:
                logging.warning(f"⚠️ Unknown event type: {event_type}")

        def state_handler(state):
            """Handles state changes."""
            #print(f"Wallet {'unlocked' if state['is_unlocked'] else 'locked'}: {len(state['wallets'])} wallets present")
            pass

        def safe_event_processing(event):
            """Processes an event safely, catching errors per event."""
            try:
                event_handler(event)
                return of(event)  # Ensure an observable is returned
            except Exception as e:
                logging.error(f"🚨 Error processing event {event}: {e}", exc_info=True)
                #return of(None)  # Send placeholder down the line
                return empty() # End the current stream entirely

        # Subscribing to state updates
        self._keyring_manager._state_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.distinct_until_changed(),
            ops.retry(3),  # Retry on transient errors
            ops.catch(lambda e, src: of(None)),  # Keep the stream alive after retries fail
        ).subscribe(on_next=state_handler)

        # Subscribing to events safely
        self._keyring_manager._event_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.flat_map(safe_event_processing)  # Ensures event processing continues
        ).subscribe()


# Running the setup
async def main():
    keyring = KeyringManager(storage_file_path="key_storage.json")
    monitor = KeyringMonitor(keyring)

    keyring._event_subject.on_next({"invalid": "error"})  # Logs warning but doesn't crash
    await keyring.login("super_S3cretP_Asswo0rd")
    await keyring.logout()

asyncio.run(main())


