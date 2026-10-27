"""This gate's own closed vocabulary: the stable handles of its texts, and the names it reads."""

from __future__ import annotations

from enum import StrEnum

CONSTITUTION_FILE = "constitution.yaml"  # where the policies stand: the file of the constitution
LAYER_DIALECT_KEY = "layer_dialect"  # the layer's own kernel key, in its own file
LAYER_DIALECT = "plain"  # the one value it takes
FORBIDDEN_LABEL = "FORBIDDEN:"  # a line of a policy that names a phrase its documents must not hold


class Key(StrEnum):
    L1 = "L1"  # the layer's dialect is not the one it knows
    L2 = "L2"  # a policy namespace in the layer's own file
    L3 = "L3"  # a document that holds a phrase its governing policy forbids
    L4 = "L4"  # a document that no one policy governs
