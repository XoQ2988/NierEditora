import io
from typing import TypeVar, Generic, List

from nier_editora.core.exceptions import SlotIndexError

T = TypeVar("T")

class SlotManager(Generic[T]):
    SLOT_COUNT: int

    def __init__(self, raw_slots: List[T]):
        if not hasattr(self, "SLOT_COUNT"):
            raise NotImplementedError("Subclasses must define SLOT_COUNT")
        if len(raw_slots) != self.SLOT_COUNT:
            raise SlotIndexError(f"Expected {self.SLOT_COUNT} slots, got {len(raw_slots)}")
        self._slots = list(raw_slots)

    @property
    def raw(self) -> List[T]:
        return self._slots

    def is_slot_active(self, slot: T) -> bool:
        ...

    @property
    def active(self) -> list[T]:
        return [slot for slot in self._slots if self.is_slot_active(slot)]

    def __iter__(self):
        return iter(self.active)

    def add(self, item: T) -> bool:
        for idx, slot in enumerate(self._slots):
            if not self.is_slot_active(slot):
                self._slots[idx] = item
                return True
        return False

    def write(self, buf: io.BytesIO) -> None:
        for slot in self._slots:
            slot.write(buf)
