class SaveEditorError(Exception):
    """Base exception for all save-editor errors."""


# Save file format errors
class SaveFormatError(SaveEditorError):
    """
    Raised when a save file fails basic format validation,
    e.g. wrong size
    """

class UnsupportedSaveSizeError(SaveFormatError):
    """
    Raised when the save file is not recognized
    """


# Serialization & I/O errors
class SerializationError(SaveEditorError):
    """
    Raised when packing or unpacking binary data fails unexpectedly
    such as struct errors or insufficient bytes.
    """

# Inventory management errors
class InventoryError(SaveEditorError):
    """Base exception for all inventory-related operations"""

class InventoryFullError(InventoryError):
    """Raised when attempting to add an item to an inventory with no empty slots"""

class SlotIndexError(InventoryError):
    """Raised when a given slot index is out of the valid range"""

# Translation errors
class TranslationError(SaveEditorError):
    """Base exception for all translation-related operations"""
