import asyncio
from typing import Optional

from rx import operators as ops
from rx import of
from rx.scheduler.eventloop import AsyncIOScheduler

from pypergraph.keyring import KeyringManager


class KeyringMonitor:
    def __init__(self, keyring_manager: Optional[KeyringManager] = None):
        self._scheduler = AsyncIOScheduler(asyncio.get_running_loop())
        self._keyring_manager = keyring_manager or KeyringManager(scheduler=self._scheduler)

        def event_handler(event):
            if event["type"] == "lock":
                print("Vault locked!")
            elif event["type"] == "unlock":
                print("Vault unlocked!")
            elif event["type"] == "account_update":
                print("Account updated:", event["data"])
            elif event["type"] == "removed_account":
                print("Account removed:", event["data"])
            elif event["type"] == "state_update":
                print("State updated:", event["data"])
            elif event["type"] == "error":
                print("error:", event["data"])

        # Subscribing to events with error handling
        self._keyring_manager._event_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.catch(lambda e, src: of(f"Recovered from error: {e}"))
        ).subscribe(
            on_next=event_handler,
            on_error=lambda e: print(f"Error in key_added: {e}")
        )

        # Subscribing to _state_subject
        self._keyring_manager._state_subject.pipe(
            ops.observe_on(self._scheduler),
            ops.distinct_until_changed()  # Only notify when state actually changes
        ).subscribe(
            on_next=lambda state: print(f"State changed: {state}"),
            on_error=lambda e: print(f"Error in state monitoring: {e}")
        )



# Running the setup
async def main():
    keyring = KeyringManager()
    monitor = KeyringMonitor(keyring)

    await keyring.create_or_restore_vault("super_S3cretP_Asswo0rd", seed="multiply angle perfect verify behind sibling skirt attract first lift remove fortune")
    await keyring.login("super_S3cretP_Asswo0rd")
    await keyring.remove_account(address='DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX')
    await keyring.logout()
    await keyring.login("fail")

asyncio.run(main())