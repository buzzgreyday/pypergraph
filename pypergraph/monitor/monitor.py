# MONITOR
import asyncio
from typing import Optional

from rx import operators as ops
from rx import of
from rx.scheduler.eventloop import AsyncIOScheduler

from pypergraph.keyring import KeyringManager


class KeyringMonitor:
    def __init__(self, keyring_manager: Optional[KeyringManager] = None):
        self._scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        self._keyring_manager = keyring_manager or KeyringManager(scheduler=self._scheduler)

        def event_handler(event):
            try:
                if isinstance(event, dict):  # Handling event_subject
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
                else:  # Handling state_subject
                    print("📢 State changed:", event)
            except Exception as e:
                print(f"🚨 Error handling event: {e}")

        def error_handler(e):
            print(f"⚠️ Event processing error: {e}")
            return of(None)  # Continue processing other events

        # Subscribing to _event_subject safely
        self._keyring_manager._event_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.catch(lambda e, src: error_handler(e)),  # Catch errors and continue
        ).subscribe(
            on_next=event_handler,
            on_error=lambda e: print(f"🔥 Fatal event error: {e}")
        )

        # Subscribing to _state_subject safely
        self._keyring_manager._state_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.distinct_until_changed(),
            ops.catch(lambda e, src: error_handler(e)),  # Catch errors and continue
        ).subscribe(
            on_next=event_handler,
            on_error=lambda e: print(f"🔥 Fatal state error: {e}")
        )


# Running the setup
async def main():
    keyring = KeyringManager()
    monitor = KeyringMonitor(keyring)

    await keyring.login("fail")  # Should trigger an error safely
    await keyring.login("super_S3cretP_Asswo0rd")

asyncio.run(main())
