from typing import List, Optional

from pydantic import BaseModel, Field


class ObservableStore(BaseModel):
    is_unlocked: bool = Field(default=False)
    wallets: List[dict] = Field(default_factory=list)
    observers: List = Field(default_factory=list)

    def get_state(self):
        return {"is_unlocked": self.is_unlocked, "wallets": self.wallets}

    def update_state(self, is_unlocked: Optional[bool] = None, wallets: Optional[List[dict]] = None):
        if is_unlocked is not None:
            self.is_unlocked = is_unlocked
        if wallets is not None:
            self.wallets = wallets
        self.notify_observers()

    def subscribe(self, callback):
        self.observers.append(callback)

    def notify_observers(self):
        for observer in self.observers:
            observer(self.get_state())