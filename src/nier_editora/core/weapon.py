import io
import logging
import struct
from dataclasses import dataclass
from typing import ClassVar, Optional

from nier_editora.core.constants import WEAPON_SIZE, ITEM_LIST, INVENTORY_WEAPON_COUNT
from nier_editora.core.exceptions import SerializationError
from nier_editora.core.i18n import translate_item
from nier_editora.core.inventory import SlotManager

logger = logging.getLogger(__name__)


@dataclass
class Weapon:
    """
    Represents a single weapon entry in the save file.

    Attributes:
        index: Zero-based slot index.
        id: Numeric weapon/item identifier for translation lookup.
        level: Upgrade level of the weapon.
        is_new_item: Whether the weapon is flagged as new (item view).
        is_new_story: Whether the weapon is new in story view.
        enemies_defeated: Number of enemies defeated with this weapon.
    """
    index: int
    id: int
    level: int
    is_new_item: bool
    is_new_story: bool
    enemies_defeated: int

    # Serialization constants
    COUNT: ClassVar[int] = WEAPON_SIZE // 4
    _STRUCT: ClassVar[struct.Struct] = struct.Struct(f"<{COUNT}i")

    @classmethod
    def read(cls, stream: io.BytesIO, index: int) -> "Weapon":
        """
        Deserialize a Weapon from the given byte stream.

        Args:
            stream: BytesIO positioned at the start of a weapon record.
            index: Slot index for this weapon.

        Returns:
            A Weapon instance.

        Raises:
            SerializationError: If data size is unexpected.
        """
        raw = stream.read(WEAPON_SIZE)
        if len(raw) != WEAPON_SIZE:
            logger.error(f"Expected {WEAPON_SIZE} bytes for weapon data, got {len(raw)}")
            raise SerializationError(f"Expected {WEAPON_SIZE} bytes, got {len(raw)}")

        values = cls._STRUCT.unpack(raw)
        id_, level, new_item_flag, new_story_flag, enemies_defeated = values
        is_new_item = bool(new_item_flag)
        is_new_story = bool(new_story_flag)

        # logger.debug(f"Read Weapon(index={index}, id={id_}, level={level}, new_item={is_new_item})")
        return cls(
            index=index,
            id=id_,
            level=level,
            is_new_item=is_new_item,
            is_new_story=is_new_story,
            enemies_defeated=enemies_defeated,
        )

    def to_bytes(self) -> bytes:
        """
        Serialize this Weapon to bytes.

        Returns:
            Byte string of length WEAPON_SIZE.
        """
        data = self._STRUCT.pack(
            self.id,
            self.level,
            1 if self.is_new_item else 0,
            1 if self.is_new_story else 0,
            self.enemies_defeated,
        )
        # logger.debug(f"Serialized Weapon(index={self.index}) to {len(data)} bytes")
        return data

    def write(self, stream: io.BytesIO) -> None:
        """
        Write this weapon's bytes into the provided stream.

        Args:
            stream: BytesIO to write into (must be positioned correctly).
        """
        stream.write(self.to_bytes())
        # logger.debug(f"Wrote Weapon(index={self.index}) to stream")

    @property
    def name(self) -> Optional[str]:
        """
        Localized name for this weapon as an item.

        Returns:
            Translated item name or fallback default.
        """
        name = translate_item(self.id)
        if not name:
            name = ITEM_LIST.get(self.id, "Unknown")
        # logger.debug(f"Translated Weapon ID {self.id} to name='{name}'")
        return name

    def __str__(self) -> str:
        """
        Human-readable summary of the weapon.
        """
        return f"Lvl. {self.level} {self.name} ({self.enemies_defeated} Kills)"


class WeaponInventory(SlotManager[Weapon]):
    """
    Manages a fixed-size collection of Weapon slots.

    Inherits from SlotManager; considers a slot active if id != -1.
    """
    SLOT_COUNT = INVENTORY_WEAPON_COUNT

    def is_slot_active(self, slot: Weapon) -> bool:
        """
        Determine if the provided slot contains a valid weapon.

        Args:
            slot: Weapon instance to check.

        Returns:
            True if id is not -1; False otherwise.
        """
        active = slot.id != -1
        # logger.debug(f"Slot index={slot.index} active={active}")
        return active
