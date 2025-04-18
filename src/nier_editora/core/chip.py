import io
import struct
from dataclasses import dataclass
from typing import ClassVar, Optional

from nier_editora.core.constants import CHIP_SIZE_WITHOUT_PADDING, CHIP_PADDING, INVENTORY_CHIPS_COUNT
from nier_editora.core.exceptions import SerializationError
from nier_editora.core.i18n import translate_item
from nier_editora.core.inventory import SlotManager


@dataclass
class Chip:
    index: int
    base_code: int
    base_id: int
    chip_type: int
    level: int
    weight: int
    slot_a: int
    slot_b: int
    slot_c: int

    # class constants
    COUNT: ClassVar[int] = CHIP_SIZE_WITHOUT_PADDING // 4
    _STRUCT: ClassVar[struct.Struct] = struct.Struct(f"<{COUNT}i")

    @classmethod
    def read(cls, stream: io.BytesIO, index: int):
        raw = stream.read(CHIP_SIZE_WITHOUT_PADDING)
        if len(raw) != CHIP_SIZE_WITHOUT_PADDING:
            raise SerializationError(f"Expected {CHIP_SIZE_WITHOUT_PADDING} bytes, got {len(raw)}")

        values = cls._STRUCT.unpack(raw)
        baseCode, baseID, chipType, level, weight, slotA, slotB, slotC = values

        # skip padding
        pad = stream.read(len(CHIP_PADDING))
        if len(pad) != len(CHIP_PADDING):
            raise SerializationError(f"Expected {len(CHIP_PADDING)} padding bytes, got {len(pad)}")

        return cls(
            index=index,
            base_code=baseCode,
            base_id=baseID,
            chip_type=chipType,
            level=level,
            weight=weight,
            slot_a=slotA,
            slot_b=slotB,
            slot_c=slotC,
        )

    def to_bytes(self) -> bytes:
        data = self._STRUCT.pack(
            self.base_code,
            self.base_id,
            self.chip_type,
            self.level,
            self.weight,
            self.slot_a,
            self.slot_b,
            self.slot_c
        )
        return data + CHIP_PADDING

    def write(self, stream: io.BytesIO):
        stream.write(self.to_bytes())

    @property
    def name(self) -> Optional[str]:
        return translate_item(self.base_id)

class ChipInventory(SlotManager[Chip]):
    SLOT_COUNT = INVENTORY_CHIPS_COUNT

    def is_slot_active(self, slot: Chip) -> bool:
        return slot.base_id != -1
