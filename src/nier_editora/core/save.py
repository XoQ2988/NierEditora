import io
import logging
from pathlib import Path

from nier_editora.core.exceptions import UnsupportedSaveSizeError
from nier_editora.core import Item, ItemInventory, Weapon, WeaponInventory, Chip, ChipInventory, constants
from utils import console_to_pc, pc_to_console

logger = logging.getLogger(__name__)


class SaveFile:
    def __init__(self):
        self._raw: bytes = b''
        self._is_console: bool = False

        self.header_id: bytes = b''
        self.play_time: int = 0
        self.chapter: int = 0
        self.player_name: str = ''
        self.xp: int = 0
        self.money: int = 0

        # will be initialized in load()
        self.inventory: ItemInventory = None  # type: ignore
        self.corpse_inventory: ItemInventory = None  # type: ignore
        self.weapons: WeaponInventory = None  # type: ignore
        self.chips: ChipInventory = None  # type: ignore

    @classmethod
    def load_from_file(cls, path: Path) -> "SaveFile":
        data = path.read_bytes()
        inst = cls()
        inst.load(data)
        return inst

    def load(self, save_data: bytes):
        logger.debug("Loading save, raw size=%d", len(save_data))

        # store raw and normalize console format
        if len(save_data) == constants.CONSOLE_SAVE_SIZE:
            self._is_console = True
            save_data = console_to_pc(save_data)
        elif len(save_data) != constants.PC_SAVE_SIZE:
            raise UnsupportedSaveSizeError(f"Unexpected save size: {hex(len(save_data))}")

        self._raw = save_data
        buf = io.BytesIO(self._raw)

        buf.seek(constants.OFF_HEADER_ID)
        self.header_id = buf.read(constants.LEN_HEADER_ID)

        buf.seek(constants.OFF_PLAYTIME)
        self.play_time = int.from_bytes(buf.read(4), "little", signed=True)

        buf.seek(constants.OFF_CHAPTER)
        self.chapter = int.from_bytes(buf.read(4), "little", signed=True)

        buf.seek(constants.OFF_PLAYER_NAME)
        name_bytes = buf.read(constants.LEN_PLAYER_NAME)
        self.player_name = name_bytes.decode("utf-16-le").rstrip("\x00")

        logger.info("Parsed headerID=%r, player='%s', play_time=%d",
                    self.header_id, self.player_name, self.play_time)

        buf.seek(constants.OFF_GAMEWORLD_STATE)

        buf.seek(constants.OFF_MONEY)
        self.money = int.from_bytes(buf.read(4), "little", signed=True)

        buf.seek(constants.OFF_EXPERIENCE)
        self.xp = int.from_bytes(buf.read(4), "little", signed=True)

        buf.seek(constants.OFF_INVENTORY)
        self.inventory = ItemInventory([Item.read(buf, i) for i in range(constants.INVENTORY_ITEM_COUNT)])
        logger.debug(f"Loaded {len(self.inventory.raw)} inventory slots ({len(self.inventory.active)} active)")

        buf.seek(constants.OFF_CORPSE_INV)
        self.corpse_inventory = ItemInventory([Item.read(buf, i) for i in range(constants.CORPSE_INVENTORY_ITEM_COUNT)])
        logger.debug(f"Loaded {len(self.corpse_inventory.raw)} corpse inventory slots"
                     f" ({len(self.corpse_inventory.active)} active)")

        buf.seek(constants.OFF_WEAPONS)
        self.weapons = WeaponInventory([Weapon.read(buf, i) for i in range(constants.INVENTORY_WEAPON_COUNT)])
        logger.debug(f"Loaded {len(self.weapons.raw)} weapon slots ({len(self.weapons.active)} active)")

        buf.seek(constants.OFF_CHIPS)
        self.chips = ChipInventory([Chip.read(buf, i) for i in range(constants.INVENTORY_CHIPS_COUNT)])
        logger.debug(f"Loaded {len(self.chips.raw)} chip slots ({len(self.chips.active)} active)")

    def write(self) -> bytes:
        if self._raw is None:
            raise ValueError("No save loaded to write from")

        # start from the PC-format raw bytes
        base = bytearray(self._raw)
        buf = io.BytesIO(base)

        buf.seek(constants.OFF_HEADER_ID)
        buf.write(self.header_id)

        buf.seek(constants.OFF_PLAYTIME)
        buf.write(self.play_time.to_bytes(4, "little", signed=True))

        buf.seek(constants.OFF_CHAPTER)
        buf.write(self.chapter.to_bytes(4, "little", signed=True))

        buf.seek(constants.OFF_PLAYER_NAME)
        name_bytes = self.player_name.encode("utf-16-le")
        buf.write(name_bytes)
        # null-terminate (2 bytes); do NOT pad further
        buf.write(b"\x00\x00")

        buf.seek(constants.OFF_MONEY)
        buf.write(self.money.to_bytes(4, "little", signed=True))

        buf.seek(constants.OFF_EXPERIENCE)
        buf.write(self.xp.to_bytes(4, "little", signed=True))

        # --- inventories write back in full slot order ---
        buf.seek(constants.OFF_INVENTORY)
        self.inventory.write(buf)

        buf.seek(constants.OFF_CORPSE_INV)
        self.corpse_inventory.write(buf)

        buf.seek(constants.OFF_WEAPONS)
        self.weapons.write(buf)

        buf.seek(constants.OFF_CHIPS)
        self.chips.write(buf)

        result = buf.getvalue()
        # if it was originally a console save, convert back
        if self._is_console:
            result = pc_to_console(result)

        return result

    def save_to_file(self, path: Path) -> None:
        path.write_bytes(self.write())

    def __str__(self) -> str:
        hours, rem = divmod(self.play_time, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{self.player_name} - {hours:02d}:{minutes:02d}:{seconds:02d}"
