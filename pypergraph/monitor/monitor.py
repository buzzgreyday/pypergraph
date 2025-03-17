# MONITOR
import asyncio
from typing import Optional

from rx import operators as ops, empty, of
from rx.scheduler.eventloop import AsyncIOScheduler

from pypergraph.keyring import KeyringManager


class KeyringMonitor:
    def __init__(self, keyring_manager: Optional[KeyringManager] = None):
        self._scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        self._keyring_manager = keyring_manager or KeyringManager()

        def event_handler(event):
            """Handles incoming keyring events."""
            if not isinstance(event, dict):
                print(f"⚠️ Unexpected event format: {event}")
                return

            event_type = event.get("type")
            if event_type == "lock":
                print("🔒 Vault locked!")
            elif event_type == "unlock":
                print("🔓 Vault unlocked!")
            elif event_type == "account_update":
                print("🔄 Account updated:", event["data"])
            elif event_type == "removed_account":
                print("❌ Account removed:", event["data"])
            elif event_type == "state_update":
                print("⚡ State updated:", event["data"])
            else:
                print(f"⚠️ Unknown event type: {event_type}")

        def state_handler(state):
            """Handles state changes."""
            print(f"Wallet {'unlocked' if state['is_unlocked'] else 'locked'}: {len(state['wallets'])} wallets present")

        def error_handler(event, e):
            """Handles errors per event, ensuring processing continues."""
            print(f"🚨 Error processing event {event}: {e}")
            return empty(scheduler=self._scheduler)  # Ensures the stream continues

        def safe_event_processing(event):
            """Processes an event safely, catching errors per event."""
            try:
                event_handler(event)
                return of(event)  # Ensures an observable is returned
            except Exception as e:
                return error_handler(event, e)

        # Subscribing to state updates
        self._keyring_manager._state_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.distinct_until_changed(),
            ops.catch(lambda e, src: of(None)),  # Keep state stream alive
        ).subscribe(
            on_next=state_handler,
        )

        # Subscribing to events safely
        self._keyring_manager._event_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.flat_map(safe_event_processing)  # Ensures event processing continues
        ).subscribe()


# Running the setup
async def main():
    keyring = KeyringManager()
    monitor = KeyringMonitor(keyring)

    await keyring.login("super_S3cretP_Asswo0rd")
    await keyring.logout()
    await asyncio.sleep(2)
    keyring._event_subject.on_next({"invalid": "error"})
    try:
        await keyring.login("fail")  # Should trigger an error safely
    except Exception as e:
        print(f"Login failed, continuing...")
    await asyncio.sleep(2)
    await keyring.login("super_S3cretP_Asswo0rd")
    await keyring.logout()
    await asyncio.sleep(2)
    try:
        await keyring.set_password("fail")
    except Exception as e:
        print(f"Password invalid, continuing...")

asyncio.run(main())

