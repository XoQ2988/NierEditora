# src/nier_editora/core/chip.py
"""
chip.py

Defines the Chip model and ChipInventory for managing chips in a save file.
Handles serialization, deserialization, and translation of chip names.
"""

import io
import logging
import struct
from dataclasses import dataclass
from typing import ClassVar, Optional

from nier_editora.core.constants import (
    CHIP_SIZE_WITHOUT_PADDING,
    CHIP_PADDING,
    INVENTORY_CHIPS_COUNT,
)
from nier_editora.core.exceptions import SerializationError
from nier_editora.core.i18n import translate_item
from nier_editora.core.inventory import SlotManager

logger = logging.getLogger(__name__)


@dataclass
class Chip:
    """
    Represents a single chip entry in the save file.

    Attributes:
        index: Zero-based slot index.
        base_code: Internal code for chip logic.
        base_id: Identifier used for translation lookup.
        chip_type: Numeric type/category of the chip.
        level: Upgrade level of the chip.
        weight: Weight value for inventory sorting.
        slot_a: Attachment slot A flag/index.
        slot_b: Attachment slot B flag/index.
        slot_c: Attachment slot C flag/index.
    """
    index: int
    base_code: int
    base_id: int
    chip_type: int
    level: int
    weight: int
    slot_a: int
    slot_b: int
    slot_c: int

    # constants for serialization
    COUNT: ClassVar[int] = CHIP_SIZE_WITHOUT_PADDING // 4  # number of ints
    _STRUCT: ClassVar[struct.Struct] = struct.Struct(f"<{COUNT}i")

    @classmethod
    def empty(cls, index: int) -> "Chip":
        if not (0 <= index < INVENTORY_CHIPS_COUNT):
            raise ValueError(f"Slot index {index} out of range")
        return cls(
            index=index,
            base_code=-1,
            base_id=-1,
            chip_type=-1,
            level=-1,
            weight=-1,
            slot_a=-1,
            slot_b=-1,
            slot_c=-1
        )

    @classmethod
    def read(cls, stream: io.BytesIO, index: int) -> "Chip":
        """
        Deserialize a Chip from the given byte stream.

        Args:
            stream: BytesIO positioned at the start of a chip record.
            index: Slot index for this chip.

        Returns:
            An instance of Chip.

        Raises:
            SerializationError: If data or padding sizes are unexpected.
        """
        raw = stream.read(CHIP_SIZE_WITHOUT_PADDING)
        if len(raw) != CHIP_SIZE_WITHOUT_PADDING:
            logger.error(f"Expected {CHIP_SIZE_WITHOUT_PADDING} bytes for chip data, got {len(raw)}")
            raise SerializationError(f"Expected {CHIP_SIZE_WITHOUT_PADDING} bytes, got {len(raw)}")

        values = cls._STRUCT.unpack(raw)
        base_code, base_id, chip_type, level, weight, slot_a, slot_b, slot_c = values

        pad = stream.read(len(CHIP_PADDING))
        if len(pad) != len(CHIP_PADDING):
            logger.error(f"Expected {len(CHIP_PADDING)} padding bytes, got {len(pad)}")
            raise SerializationError(f"Expected {len(CHIP_PADDING)} padding bytes, got {len(pad)}")

        # logger.debug(f"Read Chip(index={index}, base_id={base_id}, level={level}, type={chip_type})")
        return cls(
            index=index,
            base_code=base_code,
            base_id=base_id,
            chip_type=chip_type,
            level=level,
            weight=weight,
            slot_a=slot_a,
            slot_b=slot_b,
            slot_c=slot_c,
        )

    def to_bytes(self) -> bytes:
        """
        Serialize this Chip to bytes, including padding.

        Returns:
            Byte string of length CHIP_SIZE_WITHOUT_PADDING + len(CHIP_PADDING).
        """
        data = self._STRUCT.pack(
            self.base_code,
            self.base_id,
            self.chip_type,
            self.level,
            self.weight,
            self.slot_a,
            self.slot_b,
            self.slot_c,
        )
        result = data + CHIP_PADDING
        # logger.debug(f"Serialized Chip(index={self.index}) to {len(result)} bytes")
        return result

    def write(self, stream: io.BytesIO) -> None:
        """
        Write this chip's bytes into the provided stream.

        Args:
            stream: BytesIO to write into (must be positioned correctly).
        """
        bytes_out = self.to_bytes()
        stream.write(bytes_out)
        # logger.debug(f"Wrote Chip(index={self.index}) to stream")

    @property
    def name(self) -> Optional[str]:
        """
        Localized name for this chip, if available.

        Returns:
            Translated item name or None if not found.
        """
        name = translate_item(self.base_id)
        # logger.debug(f"Translated Chip base_id={self.base_id} to name='{name}'")
        return name


class ChipInventory(SlotManager[Chip]):
    """
    Manages a fixed-size collection of Chip slots.

    Inherits from SlotManager; considers a slot active if base_id != -1.
    """
    SLOT_COUNT = INVENTORY_CHIPS_COUNT

    def is_slot_active(self, slot: Chip) -> bool:
        """
        Determine if the provided slot contains a valid chip.

        Args:
            slot: Chip instance to check.

        Returns:
            True if base_id is not -1; False otherwise.
        """
        active = slot.base_id != -1
        # logger.debug(f"Slot index={slot.index} active={active}")
        return active
