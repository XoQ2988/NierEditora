# src/nier_editora/core/item.py
"""
item.py

Defines the Item model and ItemInventory for managing items in a save file.
Handles serialization, deserialization, and translation of item names.
"""

import io
import logging
import struct
from dataclasses import dataclass
from typing import ClassVar, Optional

from nier_editora.core.constants import ITEM_LIST, ITEM_SIZE, INVENTORY_ITEM_COUNT
from nier_editora.core.enums import ItemStatus
from nier_editora.core.exceptions import SerializationError
from nier_editora.core.i18n import translate_item
from nier_editora.core.inventory import SlotManager

logger = logging.getLogger(__name__)


@dataclass
class Item:
    """
    Represents a single inventory item in the save file.

    Attributes:
        index: Zero-based slot index.
        id: Numeric item identifier for lookup.
        status: ItemStatus enum indicating active/inactive.
        quantity: Number of items in this slot.
    """
    index: int
    id: int
    status: ItemStatus
    quantity: int

    # Serialization constants
    COUNT: ClassVar[int] = ITEM_SIZE // 4  # number of ints per record
    _STRUCT: ClassVar[struct.Struct] = struct.Struct(f"<{COUNT}i")

    @classmethod
    def read(cls, stream: io.BytesIO, index: int) -> "Item":
        """
        Deserialize an Item from the given byte stream.

        Args:
            stream: BytesIO positioned at the start of an item record.
            index: Slot index for this item.

        Returns:
            An Item instance.

        Raises:
            SerializationError: If data size is unexpected.
        """
        raw = stream.read(ITEM_SIZE)
        if len(raw) != ITEM_SIZE:
            logger.error(f"Expected {ITEM_SIZE} bytes for item data, got {len(raw)}")
            raise SerializationError(f"Expected {ITEM_SIZE} bytes, got {len(raw)}")

        ID, status_val, quantity = cls._STRUCT.unpack(raw)
        try:
            status = ItemStatus(status_val)
        except ValueError:
            logger.warning(f"Unknown status {status_val} for item ID {ID}; defaulting to INACTIVE")
            status = ItemStatus.INACTIVE

        # logger.debug(f"Read Item(index={index}, id={ID}, status={status}, quantity={quantity})")
        return cls(index=index, id=ID, status=status, quantity=quantity)

    def to_bytes(self) -> bytes:
        """
        Serialize this Item to bytes.

        Returns:
            Byte string of length ITEM_SIZE.
        """
        data = self._STRUCT.pack(self.id, self.status.value, self.quantity)
        # logger.debug(f"Serialized Item(index={self.index}) to {len(data)} bytes")
        return data

    def write(self, stream: io.BytesIO) -> None:
        """
        Write this item's bytes into the provided stream.

        Args:
            stream: BytesIO to write into (must be positioned correctly).
        """
        stream.write(self.to_bytes())
        # logger.debug(f"Wrote Item(index={self.index}) to stream")

    @property
    def name(self) -> Optional[str]:
        """
        Localized name for this item, if available.

        Returns:
            Translated item name or fallback default.
        """
        name = translate_item(self.id)
        if not name:
            name = ITEM_LIST.get(self.id, "Unknown")
        # logger.debug(f"Translated Item ID {self.id} to name='{name}'")
        return name


class ItemInventory(SlotManager[Item]):
    """
    Manages a fixed-size collection of Item slots.

    Inherits from SlotManager; considers a slot active if id != -1.
    """
    SLOT_COUNT = INVENTORY_ITEM_COUNT

    def is_slot_active(self, slot: Item) -> bool:
        """
        Determine if the provided slot contains a valid item.

        Args:
            slot: Item instance to check.

        Returns:
            True if id is not -1; False otherwise.
        """
        active = slot.id != -1
        # logger.debug(f"Slot index={slot.index} active={active}")
        return active