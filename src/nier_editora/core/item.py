import io
import struct
from dataclasses import dataclass
from typing import ClassVar, Optional

from nier_editora.core.constants import ITEM_LIST, ITEM_SIZE, INVENTORY_ITEM_COUNT
from nier_editora.core.enums import ItemStatus
from nier_editora.core.exceptions import SerializationError
from nier_editora.core.i18n import translate_item
from nier_editora.core.inventory import SlotManager


@dataclass
class Item:
    index:    int
    id:       int
    status:   ItemStatus
    quantity: int

    # class constants
    COUNT: ClassVar[int] = ITEM_SIZE // 4
    _STRUCT:      ClassVar[struct.Struct] = struct.Struct(f"<{COUNT}i")

    @classmethod
    def read(cls, stream: io.BytesIO, index: int) -> "Item":
        raw = stream.read(ITEM_SIZE)
        if len(raw) != ITEM_SIZE:
            raise SerializationError(f"Expected {ITEM_SIZE} bytes, got {len(raw)}")

        ID, statusVal, quantity = cls._STRUCT.unpack(raw)

        # map the raw status integer to our enum, defaulting to INACTIVE
        try:
            status = ItemStatus(statusVal)
        except ValueError:
            status = ItemStatus.INACTIVE

        return cls(index=index, id=ID, status=status, quantity=quantity)

    def to_bytes(self) -> bytes:
        return self._STRUCT.pack(self.id, self.status.value, self.quantity)

    def write(self, stream: io.BytesIO) -> None:
        stream.write(self.to_bytes())

    @property
    def name(self) -> Optional[str]:
        name = translate_item(self.id)
        if not name:
            name = ITEM_LIST.get(self.id, "Unknown")
        return name


class ItemInventory(SlotManager[Item]):
    SLOT_COUNT = INVENTORY_ITEM_COUNT

    def is_slot_active(self, slot: Item) -> bool:
        return slot.id != -1
