# nier_editora/core/experience.py

import bisect
from typing import Dict, List, Tuple

from nier_editora.core.constants import EXPERIENCE_TABLE  # type: Dict[int, int]


class Experience:
    """
    Compute player level from total XP, based on the game's XP table.
    """

    # Precompute a sorted list of (level, xp_threshold) tuples
    _LEVELS_AND_THRESHOLDS: List[Tuple[int, int]] = sorted(
        EXPERIENCE_TABLE.items(), key=lambda lt: lt[0]
    )
    # Split into parallel lists for fast lookup
    _LEVELS: List[int] = [lvl for lvl, _ in _LEVELS_AND_THRESHOLDS]
    _THRESHOLDS: List[int] = [xp for _, xp in _LEVELS_AND_THRESHOLDS]

    @classmethod
    def get_level_from_experience(cls, experience: int) -> int:
        if experience < 0:
            raise ValueError("Experience cannot be negative")

        idx = bisect.bisect_right(cls._THRESHOLDS, experience)

        if idx == 0:
            return cls._LEVELS[0]
        if idx >= len(cls._LEVELS):
            return cls._LEVELS[-1]
        return cls._LEVELS[idx - 1]


    @classmethod
    def get_experience_for_level(cls, level: int) -> int:
        """
        Return the minimum total XP required to reach the given level.

        Raises ValueError if the level is not in the table.
        """
        try:
            return EXPERIENCE_TABLE[level]
        except KeyError:
            raise ValueError(f"Level {level!r} is not a valid level")


    @classmethod
    def get_experience_range_for_level(cls, level: int) -> Tuple[int, int]:
        """
        Return (min_xp, max_xp) such that any XP in this half‑open
        interval [min_xp, max_xp) will map back to exactly `level`.

        For the highest level, max_xp will be the same as min_xp.
        """
        min_xp = cls.get_experience_for_level(level)
        # find next level’s threshold, if any
        levels = cls._LEVELS
        if level not in levels:
            raise ValueError(f"Level {level!r} is not a valid level")
        idx = levels.index(level)
        if idx + 1 < len(levels):
            max_xp = cls._THRESHOLDS[idx + 1]
        else:
            max_xp = min_xp
        return min_xp, max_xp


    @staticmethod
    def is_valid_level(level: int) -> bool:
        return level in EXPERIENCE_TABLE
