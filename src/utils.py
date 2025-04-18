import logging
import sys

from nier_editora.core.constants import PC_SAVE_SIZE, CONSOLE_SAVE_SIZE, CONSOLE_HEADER_SIZE
from nier_editora.core.exceptions import SaveFormatError

logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO") -> None:
    fmt = "%(asctime)s %(levelname)-6s %(name)-8s: %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            # logging.FileHandler("save_editor.log")
        ],
    )
    logging.captureWarnings(True)

def console_to_pc(ps4_data: bytes) -> bytes:
    """
    Adjust a decrypted PS4 Nier:Automata save file so that it matches the PC layout.
    https://www.reddit.com/r/nier/comments/8w5fcp/comment/irq9swi

      1. Insert zero bytes at the beginning of the file.
      2. Duplicate a “line” of data (assumed to be 16 bytes) at offset 235568.
      3. If the resulting file is shorter than 235980 bytes, pad zeros at the end until it reaches that length.
    """

    if len(ps4_data) not in (PC_SAVE_SIZE, CONSOLE_SAVE_SIZE):
        raise SaveFormatError(f"Unexpected save file length: {hex(len(ps4_data))}")

    # 1. Insert zero bytes at the beginning
    logger.debug("Inserting header of %d bytes", CONSOLE_HEADER_SIZE)
    adjusted = bytearray(b'\x00' * CONSOLE_HEADER_SIZE + ps4_data)

    # 2. Duplicate one “line” at offset 235568.
    duplicate_offset = 0x39830
    duplicate_line_length = 0x10
    logger.debug("Duplicating %d-byte block at offset %#x", duplicate_line_length, duplicate_offset)
    # Ensure we have enough data to duplicate
    if len(adjusted) >= duplicate_offset + duplicate_line_length:
        line_data = adjusted[duplicate_offset:duplicate_offset + duplicate_line_length]
        # Insert (duplicate) the line data exactly at that offset; the original remains.
        adjusted[duplicate_offset:duplicate_offset] = line_data
    else:
        raise SaveFormatError("The adjusted file is too short, possibly due to corrupted save.")

    # 3. Pad with zeros at the end if necessary (or trim if too long)
    cur_length = len(adjusted)
    if cur_length < PC_SAVE_SIZE:
        pad_length = PC_SAVE_SIZE - cur_length
        adjusted.extend(b'\x00' * pad_length)
    elif cur_length > PC_SAVE_SIZE:
        adjusted = adjusted[:PC_SAVE_SIZE]

    logger.debug("console_to_pc: output size=%d", len(adjusted))
    return bytes(adjusted)

def pc_to_console(pc_data: bytes) -> bytes:
    """
    Reverts adjustments made by adjust_ps4_save, returning the original console save file.

    The reversion steps are:
      1. Remove the first CONSOLE_HEADER_SIZE bytes.
      2. Remove the duplicated 16-byte block that was inserted.
      3. Remove the trailing padding so that the size becomes CONSOLE_SAVE_SIZE.

    """
    if len(pc_data) != PC_SAVE_SIZE:
        raise SaveFormatError(f"PC save file must be exactly {PC_SAVE_SIZE} bytes, got {len(pc_data)}.")

    # 1. Remove the inserted header.
    data = bytearray(pc_data[CONSOLE_HEADER_SIZE:])

    # 2. Remove the duplicated block.
    duplicate_offset = 0x39830 - CONSOLE_HEADER_SIZE
    if len(data) < duplicate_offset + 0x10:
        raise SaveFormatError("The PC save is too short to remove the duplicate block as expected.")
    del data[duplicate_offset:duplicate_offset + 0x10]

    # 3. Remove trailing padding.
    current_length = len(data)
    if current_length < CONSOLE_SAVE_SIZE:
        raise SaveFormatError("Data is too short after reversion.")
    # Remove extra bytes at the end.
    data = data[:CONSOLE_SAVE_SIZE]

    return bytes(data)
