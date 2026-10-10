"""This module's own closed vocabulary: the stable handles of its findings."""

from __future__ import annotations

from enum import StrEnum

TITLE_MAX = 200  # characters: the kernel schema's maxLength of title


class Key(StrEnum):
    F1 = "F1"
    F2 = "F2"
    F3 = "F3"
    F4 = "F4"
    F5 = "F5"
    F6 = "F6"
    F7 = "F7"
    F8 = "F8"
    F8B = "F8b"
    F15 = "F15"
    F11 = "F11"
    F12 = "F12"
    F13 = "F13"
    F14 = "F14"
