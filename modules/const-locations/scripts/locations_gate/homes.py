"""Where a new document of a kind goes: derived from the policy's territory and from nothing
else. Three shapes give an answer; everything else is an honest refusal."""

from __future__ import annotations

import re
from collections.abc import Sequence

from const_gate.envelope import ID_RE

from .model import HomeClass, HomeRule

GLOB = re.compile(r"[*?\[\\]")
DIRECTORY = re.compile(r"^(?P<dir>[^*?\[\\]+?)/\*\*(?:/\*\.md)?$")


def rule_of(patterns: Sequence[str]) -> HomeRule:
    """What the territory says. One pattern is read; two or more never give a home."""
    if len(patterns) != 1:
        return HomeRule(HomeClass.NONE, patterns[0] if patterns else "")
    declared = patterns[0]
    pattern = (
        declared[1:] if declared.startswith("/") else declared
    )  # a leading slash anchors, and is no path
    if pattern.startswith("!") or not pattern or pattern.endswith("/"):
        return HomeRule(HomeClass.NONE, declared)
    if GLOB.search(pattern) is None:
        return HomeRule(HomeClass.SINGLE, declared)
    prefix = DIRECTORY.match(pattern)
    if prefix is not None:
        return HomeRule(HomeClass.DIRECTORY, declared, directory=prefix.group("dir"))
    parts = pattern.split("/")
    literal = [part for part in parts if part != "*"]
    if (
        parts.count("*") == 1
        and parts[-1] != "*"
        and parts[-1].lower().endswith(".md")
        and all(part and GLOB.search(part) is None for part in literal)
    ):
        at = parts.index("*")
        return HomeRule(
            HomeClass.SEGMENT,
            declared,
            fixed_name=parts[-1][:-3],
            before="/".join(parts[:at]),
            after="/".join(parts[at + 1 :]),
        )
    return HomeRule(HomeClass.NONE, declared)


def directory_home(rule: HomeRule, stem: str) -> str:
    return f"{rule.directory}/{stem}.md"


def segment_home(rule: HomeRule, segment: str) -> str:
    return "/".join(part for part in (rule.before, segment, rule.after) if part)


def is_kebab(value: str) -> bool:
    return ID_RE.match(value) is not None
