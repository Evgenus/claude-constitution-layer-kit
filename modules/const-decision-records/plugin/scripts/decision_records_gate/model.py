"""This module's own closed vocabularies and its dials."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

ROUTINE = "routine"  # the one stakes level that never produces a record, so not a member below


class Stakes(StrEnum):
    """The recorded stakes levels."""

    PROCESS = "process"
    PRODUCT = "product"
    ARCHITECTURE = "architecture"


class Key(StrEnum):
    """Stable handles of this module's findings."""

    R1 = "R1"
    R2 = "R2"
    R3 = "R3"


@dataclass(frozen=True, slots=True)
class RecordDials:
    """This module's own dials, validated. The two every gate has are read by the shared code."""

    record_policies: tuple[str, ...]
