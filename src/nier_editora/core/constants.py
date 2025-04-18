# =============================================================================
# Save file Sizes and Layout Adjustments
# =============================================================================
import json
from pathlib import Path

PC_SAVE_SIZE = 0x399CC
CONSOLE_SAVE_SIZE = 0x39990
CONSOLE_HEADER_SIZE = 12

# =============================================================================
# Offsets (Pc Layout)
# =============================================================================
# Header
OFF_HEADER_ID   = 0x00004
LEN_HEADER_ID   = 12

# Player stats
OFF_PLAYTIME    = 0x00024
OFF_CHAPTER     = 0x0002C
OFF_PLAYER_NAME = 0x00034
LEN_PLAYER_NAME = 70
OFF_GAMEWORLD_STATE = 0x0007C

# Currency & XP
OFF_MONEY       = 0x3056C
OFF_EXPERIENCE  = 0x3871C

# Inventory regions
OFF_INVENTORY   = 0x30570
OFF_CORPSE_INV  = 0x31170
OFF_WEAPONS     = 0x31D70
OFF_CHIPS       = 0x324BC

# Block duplication details
DUPLICATION_OFFSET = 0x39830
DUPLICATION_LENGTH = 0x10

# =============================================================================
# Counts & Record Sizes
# =============================================================================
# Number of slots per category
INVENTORY_ITEM_COUNT = 256
CORPSE_INVENTORY_ITEM_COUNT = 256
INVENTORY_WEAPON_COUNT = 39
INVENTORY_CHIPS_COUNT = 256

# Bytes per record (int32 = 4bytes)
CHIP_PADDING = bytes([
    0xFF, 0xFF, 0xFF, 0xFF,     0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF,     0x00, 0x00, 0x00, 0x00,
])
CHIP_SIZE = 12 * 0x4      # baseCode, baseID, chipType, level, weight, slotA, slotB, slotC
CHIP_SIZE_WITHOUT_PADDING = CHIP_SIZE - len(CHIP_PADDING)
ITEM_SIZE = 3 * 0x4       # ID, status, quantity
WEAPON_SIZE = 5 * 0x4     # ID level, newItem, newStory, enemiesDefeated

# =============================================================================
# XP Table (https://nierautomata.wiki.fextralife.com/EXP)
# =============================================================================
_DATA_DIR: Path = Path(__file__).parent.parent / "data" / "constants"
_EXPERIENCE_FILE: Path = _DATA_DIR / "experience_table.json"

def _load_experience_table() -> dict[int, int]:
    """
    Load the experience table from a JSON file.

    Returns:
        A mapping from level to cumulative XP.
    """
    try:
        with open(_EXPERIENCE_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Experience table JSON not found: {_EXPERIENCE_FILE}") from e

EXPERIENCE_TABLE: dict[int, int] = _load_experience_table()

# =============================================================================
# Item List (https://bitbucket.org/Xutax_Kamay/nierautomata/src/da5adadd9f0f0637a7969ba3ea354f7cbdce17e2/ItemList.txt)
# =============================================================================
_ITEM_LIST_FILE: Path = _DATA_DIR / "item_list.json"

def _load_item_list() -> dict[int, str]:
    """
    Load the item list mapping from a JSON file.

    Returns:
        A mapping from item ID to code string.
    """
    try:
        with open(_ITEM_LIST_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Item list JSON not found: {_ITEM_LIST_FILE}") from e

ITEM_LIST: dict[int, str] = _load_item_list()
