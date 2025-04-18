from enum import Enum


class ItemStatus(Enum):
    """
    Enumeration of possible item slot statuses.

    Attributes:
        ACTIVE: The slot is occupied by an active item.
        INACTIVE: The slot is empty or inactive.
    """
    ACTIVE = 0x00070000
    INACTIVE = -1

    def __str__(self) -> str:
        """
        Return a lowercase string representation of the status name.

        Returns:
            A human-readable string like 'active' or 'inactive'.
        """
        return self.name.lower()
