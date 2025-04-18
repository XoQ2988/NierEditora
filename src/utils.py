"""
utils.py

Conversion utilities for Nier:Automata save files between console and PC layouts.
"""

import logging

from nier_editora.core.constants import (
    PC_SAVE_SIZE,
    CONSOLE_SAVE_SIZE,
    CONSOLE_HEADER_SIZE, DUPLICATION_OFFSET, DUPLICATION_LENGTH,
)
from nier_editora.core.exceptions import SaveFormatError

logger = logging.getLogger(__name__)


def console_to_pc(ps4_data: bytes) -> bytes:
    """
    Convert a decrypted console save to PC format.

    Steps:
      1. Prepend CONSOLE_HEADER_SIZE zero bytes.
      2. Duplicate a block of length _DUPLICATION_LENGTH at _DUPLICATION_OFFSET.
      3. Pad with zeros or trim so final size == PC_SAVE_SIZE.

    Args:
        ps4_data (bytes): Raw console save bytes.

    Returns:
        bytes: PC-formatted save of exactly PC_SAVE_SIZE length.

    Raises:
        SaveFormatError: If input length is unexpected or data is too short.
    """
    length = len(ps4_data)
    if length not in (CONSOLE_SAVE_SIZE, PC_SAVE_SIZE):
        logger.error(f"Unexpected input size: {length}")
        raise SaveFormatError(f"Unexpected save file length: {hex(length)}")

    logger.debug(f"console_to_pc: starting with input size={length}")

    # 1) Prepend header
    data = bytearray(b"\x00" * CONSOLE_HEADER_SIZE + ps4_data)
    logger.debug(f"Prepended {CONSOLE_HEADER_SIZE}-byte header; size={len(data)}")

    # 2) Duplicate block
    end = DUPLICATION_OFFSET + DUPLICATION_LENGTH
    if len(data) < end:
        logger.error(
            f"Data too short for duplication at offset {DUPLICATION_OFFSET:#x} "
            f"(need up to {end:#x}, got {len(data)})"
        )
        raise SaveFormatError("Corrupted save: insufficient data for duplication.")
    block = data[DUPLICATION_OFFSET:end]
    data[DUPLICATION_OFFSET:DUPLICATION_OFFSET] = block
    logger.debug(
        f"Duplicated {DUPLICATION_LENGTH}-byte block at {DUPLICATION_OFFSET:#x}; size now={len(data)}"
    )

    # 3) Pad or trim
    if len(data) < PC_SAVE_SIZE:
        pad = PC_SAVE_SIZE - len(data)
        data.extend(b"\x00" * pad)
        logger.debug(f"Padded {pad} bytes; final size={len(data)}")
    elif len(data) > PC_SAVE_SIZE:
        del data[PC_SAVE_SIZE:]
        logger.debug(f"Trimmed to {PC_SAVE_SIZE} bytes")

    logger.info(f"console_to_pc: completed (output size={len(data)})")
    return bytes(data)


def pc_to_console(pc_data: bytes) -> bytes:
    """
    Revert a PC-formatted save back to console format.

    Steps:
      1. Strip the first CONSOLE_HEADER_SIZE bytes.
      2. Remove the duplicated block of _DUPLICATION_LENGTH at adjusted offset.
      3. Trim to CONSOLE_SAVE_SIZE.

    Args:
        pc_data (bytes): PC-formatted save exactly PC_SAVE_SIZE long.

    Returns:
        bytes: Console-formatted save of CONSOLE_SAVE_SIZE length.

    Raises:
        SaveFormatError: If input isn't PC_SAVE_SIZE or data is too short.
    """
    length = len(pc_data)
    if length != PC_SAVE_SIZE:
        logger.error(f"Invalid PC save size: {length} bytes")
        raise SaveFormatError(f"PC save must be {PC_SAVE_SIZE} bytes (got {length}).")

    logger.debug(f"pc_to_console: starting with input size={length}")

    # 1) Remove header
    data = bytearray(pc_data[CONSOLE_HEADER_SIZE:])
    logger.debug(f"Removed {CONSOLE_HEADER_SIZE}-byte header; size={len(data)}")

    # 2) Remove duplicated block
    dup_off = DUPLICATION_OFFSET - CONSOLE_HEADER_SIZE
    end_dup = dup_off + DUPLICATION_LENGTH
    if len(data) < end_dup:
        logger.error(
            f"Cannot remove duplicate block: need up to index {end_dup}, got {len(data)}"
        )
        raise SaveFormatError("Corrupted PC save: insufficient data to undo duplication.")
    del data[dup_off:end_dup]
    logger.debug(
        f"Removed duplicated block ({DUPLICATION_LENGTH} bytes) at {dup_off}; size now={len(data)}"
    )

    # 3) Trim to console size
    if len(data) < CONSOLE_SAVE_SIZE:
        logger.error(f"Data too short after trimming: {len(data)} bytes (expected {CONSOLE_SAVE_SIZE})")
        raise SaveFormatError("Corrupted PC save: data too short after reversion.")
    del data[CONSOLE_SAVE_SIZE:]
    logger.info(f"pc_to_console: completed (output size={CONSOLE_SAVE_SIZE})")

    return bytes(data)
