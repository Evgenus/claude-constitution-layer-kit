"""The checks: each pair against the range's paths, each declaration against the pairs, the
working tree's lines. Functions of typed inputs; git is asked elsewhere."""

from __future__ import annotations

from collections.abc import Sequence

from const_gate.model import Finding
from const_gate.territory import Matcher

from . import messages
from .model import Declaration, Pair, PairVerdict, Range


def judge_pairs(matcher: Matcher, pairs: Sequence[Pair], rng: Range) -> list[PairVerdict]:
    verdicts: list[PairVerdict] = []
    for pair in pairs:
        candidates = [path for path in rng.paths if path not in pair.docs]  # a document is no trigger
        touched = tuple(sorted(matcher.match(pair.code, candidates)))
        updated = tuple(doc for doc in pair.docs if doc in rng.paths)
        verdicts.append(PairVerdict(pair, touched, updated))
    return verdicts


def examine(
    verdicts: Sequence[PairVerdict], declarations: Sequence[Declaration], key: str
) -> tuple[list[Finding], list[str]]:
    """The findings and the notes of a range: a covered pair neither updated nor declared; a
    declaration that names no pair or carries no reason; a note for every declaration read."""
    names = [v.pair.name for v in verdicts]
    covered = {v.pair.name for v in verdicts if v.covered}
    declared: set[str] = set()
    findings: list[Finding] = []
    notes: list[str] = []
    for declaration in declarations:
        if declaration.pair not in names:
            findings.append(messages.t3_names_no_pair(declaration, key, names))
            continue
        if not declaration.reason:
            findings.append(messages.t4_no_reason(declaration, key))
            continue
        declared.add(declaration.pair)
        notes.append(messages.n1_declared(declaration, declaration.pair in covered))
    owed = [
        messages.t2_not_updated(v.pair, v.touched, key)
        for v in verdicts
        if v.covered and not v.updated and v.pair.name not in declared
    ]
    return [*owed, *findings], notes


def working_files_note(matcher: Matcher, patterns: Sequence[str], tracked: Sequence[str]) -> list[str]:
    matched = sorted(matcher.match(patterns, tracked))
    return [messages.n2_working_files(matched)] if matched else []


def tree_finding(lines: Sequence[str]) -> Finding:
    return messages.t1_dirty_tree(lines)
