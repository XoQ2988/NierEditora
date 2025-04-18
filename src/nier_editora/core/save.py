import io
import logging
from pathlib import Path
from typing import Optional

from nier_editora.core.exceptions import UnsupportedSaveSizeError
from nier_editora.core import (
    Item,
    ItemInventory,
    Weapon,
    WeaponInventory,
    Chip,
    ChipInventory,
    constants,
)
from nier_editora.logging_config import setup_logging
from utils import console_to_pc, pc_to_console

logger = logging.getLogger(__name__)


class SaveFile:
    """
    Represents a Nier:Automata save file.

    Can load from PC or console formats, expose metadata and inventories,
    and write changes back in the original format.
    """

    def __init__(self) -> None:
        """
        Initialize an empty SaveFile instance.

        Attributes:
            self._raw: Raw PC-format save bytes.
            self._is_console: Whether the original save was in console format.
            self.header_id: Raw header identifier bytes.
            self.play_time: Total play time in seconds.
            self.chapter: Current chapter number.
            self.player_name: Unicode player name.
            self.xp: Experience points.
            self.money: In-game currency.
            self.inventory: Main item inventory.
            self.corpse_inventory: Corpses inventory.
            self.weapons: Weapon inventory.
            self.chips: Chip inventory.
        """
        self._raw: bytes = b""
        self._is_console: bool = False

        self.header_id: bytes = b""
        self.play_time: int = 0
        self.chapter: int = 0
        self.player_name: str = ""
        self.xp: int = 0
        self.money: int = 0

        self.inventory: Optional[ItemInventory] = None
        self.corpse_inventory: Optional[ItemInventory] = None
        self.weapons: Optional[WeaponInventory] = None
        self.chips: Optional[ChipInventory] = None

    @classmethod
    def load_from_file(cls, path: Path) -> "SaveFile":
        """
        Load a save file from disk.

        Args:
            path: Path to the save file.

        Returns:
            An instance of SaveFile with parsed data.
        """
        logger.debug(f"Loading save file from {path}")
        data = path.read_bytes()
        inst = cls()
        inst.load(data)
        return inst

    def load(self, save_data: bytes) -> None:
        """
        Parse save data bytes into object fields.

        Detects console format and normalizes to PC format.

        Args:
            save_data: Raw bytes of the save file.

        Raises:
            UnsupportedSaveSizeError: If data length is neither console nor PC size.
        """
        length = len(save_data)
        logger.debug(f"Loading save, raw size={length}")

        if length == constants.CONSOLE_SAVE_SIZE:
            self._is_console = True
            logger.info("Detected console-format save; converting to PC format")
            save_data = console_to_pc(save_data)
        elif length != constants.PC_SAVE_SIZE:
            logger.error(f"Unexpected save size: {hex(length)}")
            raise UnsupportedSaveSizeError(f"Unexpected save size: {hex(length)}")

        self._raw = save_data
        buf = io.BytesIO(self._raw)

        # Header ID
        buf.seek(constants.OFF_HEADER_ID)
        self.header_id = buf.read(constants.LEN_HEADER_ID)

        # Play time
        buf.seek(constants.OFF_PLAYTIME)
        self.play_time = int.from_bytes(buf.read(4), "little", signed=True)

        # Chapter
        buf.seek(constants.OFF_CHAPTER)
        self.chapter = int.from_bytes(buf.read(4), "little", signed=True)

        # Player name (UTF-16-LE)
        buf.seek(constants.OFF_PLAYER_NAME)
        raw_name = buf.read(constants.LEN_PLAYER_NAME)
        self.player_name = raw_name.decode("utf-16-le").rstrip("\x00")

        logger.info(
            f"Parsed save: header_id={self.header_id!r}, player='{self.player_name}', "
            f"play_time={self.play_time}s, chapter={self.chapter}"
        )

        # Currency and XP
        buf.seek(constants.OFF_MONEY)
        self.money = int.from_bytes(buf.read(4), "little", signed=True)
        buf.seek(constants.OFF_EXPERIENCE)
        self.xp = int.from_bytes(buf.read(4), "little", signed=True)

        # Inventories
        buf.seek(constants.OFF_INVENTORY)
        items = [Item.read(buf, i) for i in range(constants.INVENTORY_ITEM_COUNT)]
        self.inventory = ItemInventory(items)
        logger.debug(
            f"Loaded inventory: total={len(self.inventory.raw)}, "
            f"active={len(self.inventory.active)}"
        )

        buf.seek(constants.OFF_CORPSE_INV)
        corpses = [Item.read(buf, i) for i in range(constants.CORPSE_INVENTORY_ITEM_COUNT)]
        self.corpse_inventory = ItemInventory(corpses)
        logger.debug(
            f"Loaded corpse inventory: total={len(self.corpse_inventory.raw)}, "
            f"active={len(self.corpse_inventory.active)}"
        )

        buf.seek(constants.OFF_WEAPONS)
        weapons = [Weapon.read(buf, i) for i in range(constants.INVENTORY_WEAPON_COUNT)]
        self.weapons = WeaponInventory(weapons)
        logger.debug(
            f"Loaded weapons: total={len(self.weapons.raw)}, "
            f"active={len(self.weapons.active)}"
        )

        buf.seek(constants.OFF_CHIPS)
        chips = [Chip.read(buf, i) for i in range(constants.INVENTORY_CHIPS_COUNT)]
        self.chips = ChipInventory(chips)
        logger.debug(
            f"Loaded chips: total={len(self.chips.raw)}, active={len(self.chips.active)}"
        )

    def write(self) -> bytes:
        """
        Serialize current state back to save bytes.

        Preserves PC format, then reverts to console if necessary.

        Returns:
            Bytes of the updated save file.

        Raises:
            ValueError: If called before loading.
        """
        if not self._raw:
            logger.error("Write called before a save was loaded")
            raise ValueError("No save data to write from")

        logger.debug("Writing save data to bytes buffer")
        base = bytearray(self._raw)
        buf = io.BytesIO(base)

        # Header ID
        buf.seek(constants.OFF_HEADER_ID)
        buf.write(self.header_id)

        # Play time, chapter, name
        buf.seek(constants.OFF_PLAYTIME)
        buf.write(self.play_time.to_bytes(4, "little", signed=True))
        buf.seek(constants.OFF_CHAPTER)
        buf.write(self.chapter.to_bytes(4, "little", signed=True))

        buf.seek(constants.OFF_PLAYER_NAME)
        name_bytes = self.player_name.encode("utf-16-le")
        buf.write(name_bytes + b"\x00\x00")

        # Money and XP
        buf.seek(constants.OFF_MONEY)
        buf.write(self.money.to_bytes(4, "little", signed=True))
        buf.seek(constants.OFF_EXPERIENCE)
        buf.write(self.xp.to_bytes(4, "little", signed=True))

        # Write inventories
        buf.seek(constants.OFF_INVENTORY)
        self.inventory.write(buf)
        buf.seek(constants.OFF_CORPSE_INV)
        self.corpse_inventory.write(buf)
        buf.seek(constants.OFF_WEAPONS)
        self.weapons.write(buf)
        buf.seek(constants.OFF_CHIPS)
        self.chips.write(buf)

        result = buf.getvalue()
        if self._is_console:
            logger.info("Converting PC data back to console format")
            result = pc_to_console(result)

        logger.info(f"Write complete: output size={len(result)} bytes")
        return result

    def save_to_file(self, path: Path) -> None:
        """
        Write the serialized save bytes to disk.

        Args:
            path: Destination path for the save file.
        """
        logger.debug(f"Saving save file to {path}")
        path.write_bytes(self.write())
        logger.info(f"Save written to {path}")

    def __str__(self) -> str:
        """
        Human-readable summary: Player name and play time.
        """
        hours, rem = divmod(self.play_time, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{self.player_name} - {hours:02d}:{minutes:02d}:{seconds:02d}"

if __name__ == '__main__':
    setup_logging(level="DEBUG")
    save = SaveFile.load_from_file(Path(__file__).parent.parent / "data" / "saves" / "SlotData_0.dat")

    for item in save.inventory:
        print(item.name)
