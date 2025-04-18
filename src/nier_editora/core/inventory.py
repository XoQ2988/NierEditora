import io
import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Iterator

from nier_editora.core.exceptions import SlotIndexError

T = TypeVar("T")

logger = logging.getLogger(__name__)

class SlotManager(Generic[T], ABC):
    """
    Base class for managing a fixed number of slots of type T.

    Subclasses must define SLOT_COUNT and implement is_slot_active().
    """
    SLOT_COUNT: int

    def __init__(self, raw_slots: List[T]) -> None:
        """
        Initialize the SlotManager with a list of raw slot objects.

        Args:
            raw_slots: List of slots to manage. Length must equal SLOT_COUNT.

        Raises:
            NotImplementedError: If subclass does not define SLOT_COUNT.
            SlotIndexError: If raw_slots length != SLOT_COUNT.
        """
        logger.debug(f"Initializing {self.__class__.__name__} with {len(raw_slots)} slots")
        if not hasattr(self, "SLOT_COUNT"):
            logger.error("Subclasses must define SLOT_COUNT")
            raise NotImplementedError("Subclasses must define SLOT_COUNT")
        if len(raw_slots) != self.SLOT_COUNT:
            logger.error(f"Expected {self.SLOT_COUNT} slots, got {len(raw_slots)}")
            raise SlotIndexError(f"Expected {self.SLOT_COUNT} slots, got {len(raw_slots)}")
        self._slots = list(raw_slots)

    @property
    def raw(self) -> List[T]:
        """
        All slots, including inactive ones.

        Returns:
            List of all slots.
        """
        return self._slots

    @abstractmethod
    def is_slot_active(self, slot: T) -> bool:
        """
        Determine if a given slot is active.

        Args:
            slot: The slot object to check.

        Returns:
            True if the slot is active; False otherwise.
        """
        ...

    @property
    def active(self) -> List[T]:
        """
        List of currently active slots.

        Returns:
            List of slots where is_slot_active(slot) is True.
        """
        active_slots = [slot for slot in self._slots if self.is_slot_active(slot)]
        logger.debug(f"Computed active slots: {len(active_slots)} of {self.SLOT_COUNT}")
        return active_slots

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over active slots.

        Yields:
            Active slot objects one by one.
        """
        return iter(self.active)

    def add(self, item: T) -> bool:
        """
        Add an item to the first available inactive slot.

        Args:
            item: The slot object to add.

        Returns:
            True if the item was added; False if no inactive slots were available.
        """
        for idx, slot in enumerate(self._slots):
            if not self.is_slot_active(slot):
                self._slots[idx] = item
                logger.info(f"Added item to slot index {idx}")
                return True
        logger.warning(f"No inactive slot available to add item: {item}")
        return False

    def write(self, buf: io.BytesIO) -> None:
        """
        Serialize all slots to the given buffer.

        Args:
            buf: A BytesIO buffer to write each slot into.
        """
        logger.debug("Writing all slots to buffer")
        for slot in self._slots:
            slot.write(buf)
        logger.info(f"Wrote {len(self._slots)} slots to buffer")
