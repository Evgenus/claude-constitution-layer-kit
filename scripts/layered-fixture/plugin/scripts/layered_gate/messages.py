"""The texts of this gate's own findings, skips, notes and dial failures, as functions with typed
parameters; the texts every gate shares live in the shared package's messages module.

A finding states what failed, why the rule exists (one clause) and the exact fix; a configuration failure is
one self-sufficient line. The name of a dials file is never written here: it is asked from the identity in
force, so that a text names the file the run is reading.
"""

from __future__ import annotations

from constitution_layer_kit import identity
from constitution_layer_kit.messages import echoed, escaped
from constitution_layer_kit.model import Broken, Defect, Finding

from .model import FORBIDDEN_LABEL, LAYER_DIALECT, LAYER_DIALECT_KEY, Key


def _ns() -> str:
    return identity.current().namespace


def _file() -> str:
    return identity.dials_file()


# ---------------------------------------------------------------- configuration failures


def l1_dialect(value: str) -> Broken:
    return Broken(
        Key.L1,
        f"{_file()}: {LAYER_DIALECT_KEY} is '{echoed(value)}', and this layer knows only '{LAYER_DIALECT}'",
        f"{_ns()} reads documents in one dialect, and a dialect it does not know would be judged by rules"
        f" written for another: set {LAYER_DIALECT_KEY}: {LAYER_DIALECT} in {_file()}, or remove the line",
    )


def l2_policy_namespace(name: str) -> Broken:
    return Broken(
        Key.L2,
        f"{_file()}: {echoed(name)} is a policy's namespace, and the policies stand in another file",
        f"a policy declared in two files would have two territories, and {_ns()} reads it from one only:"
        f" move the '{echoed(name)}' key, with its territory, to the file of the constitution's policies,"
        " and remove it from this file",
    )


# ---------------------------------------------------------------- findings


def l3_forbidden(rel: str, policy: str, phrase: str) -> Finding:
    return Finding(
        Key.L3,
        f"{escaped(rel)}: holds '{echoed(phrase)}', which its policy '{echoed(policy)}' forbids",
        "a policy lists what its documents must not say, and a document that says it breaks the rule it is"
        " governed by",
        f"remove '{echoed(phrase)}' from the document, or remove the line"
        f" '{FORBIDDEN_LABEL} {echoed(phrase)}' from the policy '{echoed(policy)}'",
    )


def l4_unresolved(rel: str, defect: Defect) -> Finding:
    return Finding(
        Key.L4,
        f"{escaped(rel)}: no one policy governs it ({defect.value})",
        "a document is judged by exactly one policy, or its rules are undefined",
        "place the file in the territory of one policy, or declare the id of one policy in its envelope",
    )


# ---------------------------------------------------------------- skips and the scan's tail


def g1_skip_outside_territory(rel: str) -> str:
    return f"{escaped(rel)} is outside claimed territory"


def f9_scan_tail(examined: int, scanned: int, policies: int) -> str:
    return (
        f"{examined} governed document(s) examined, {scanned} Markdown file(s) scanned, {policies} policies"
    )
