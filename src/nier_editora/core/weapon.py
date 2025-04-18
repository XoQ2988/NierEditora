import io
import struct
from dataclasses import dataclass
from typing import ClassVar, Optional

from nier_editora.core.constants import WEAPON_SIZE, ITEM_LIST, INVENTORY_WEAPON_COUNT
from nier_editora.core.exceptions import SerializationError
from nier_editora.core.i18n import translate_item
from nier_editora.core.inventory import SlotManager


@dataclass
class Weapon:
    index: int
    ID: int
    level: int
    is_new_item: bool
    is_new_story: bool
    enemies_defeated: int

    # class constants
    COUNT: ClassVar[int] = WEAPON_SIZE // 4
    _STRUCT: ClassVar[struct.Struct] = struct.Struct(f"<{COUNT}i")

    @classmethod
    def read(cls, stream: io.BytesIO, index: int):
        raw = stream.read(WEAPON_SIZE)
        if len(raw) != WEAPON_SIZE:
            raise SerializationError(f"Expected {WEAPON_SIZE} bytes, got {len(raw)}")

        ID, level, newItemFlag, newStoryFlag, enemiesDefeated = cls._STRUCT.unpack(raw)
        isNewItem = bool(newItemFlag)
        isNewStory = bool(newStoryFlag)

        return cls(
            index=index,
            ID=ID,
            level=level,
            is_new_item=isNewItem,
            is_new_story=isNewStory,
            enemies_defeated=enemiesDefeated,
        )

    def to_bytes(self) -> bytes:
        return self._STRUCT.pack(
            self.ID,
            self.level,
            1 if self.is_new_item else 0,
            1 if self.is_new_story else 0,
            self.enemies_defeated
        )


    def write(self, stream: io.BytesIO) -> None:
        stream.write(self.to_bytes())

    @property
    def name(self) -> Optional[str]:
        name = translate_item(self.ID)
        if not name:
            name = ITEM_LIST.get(self.ID, "Unknown")
        return name

    def __str__(self):
        return f"Lvl. {self.level} {self.name} ({self.enemies_defeated} Kills)"


class WeaponInventory(SlotManager[Weapon]):
    SLOT_COUNT = INVENTORY_WEAPON_COUNT

    def is_slot_active(self, slot: Weapon) -> bool:
        return slot.ID != -1
