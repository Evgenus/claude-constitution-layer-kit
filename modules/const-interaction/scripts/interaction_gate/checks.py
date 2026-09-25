"""The two checks, each a function of typed inputs: does a subcommand match an entry, and does
every item of a list open with a handle."""

from __future__ import annotations

import re
from collections.abc import Sequence

from .model import Entry, Hit, ListHit, Subcommand

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
ITEM = re.compile(r"^[-*+] (.*)$")
# An item's text may open with an anchor and a bold marker before its handle.
PREFIX = re.compile(r'^(?:<a id="[^"]*"></a>\s*)?(?:\*\*)?')


def match(entries: Sequence[Entry], subcommands: Sequence[Subcommand]) -> list[Hit]:
    """At most one hit per subcommand: the first entry it matches. A flag matches by equality
    when long, inside a cluster when short; the scan of flags stops at `--`."""
    hits: list[Hit] = []
    for subcommand in subcommands:
        for entry in entries:
            matched = _matches(entry, subcommand)
            if matched is not None:
                hits.append(Hit(entry, subcommand, matched))
                break
    return hits


def _matches(entry: Entry, subcommand: Subcommand) -> str | None:
    words = subcommand.words
    n = len(entry.command)
    if words[:n] != entry.command:
        return None
    if not entry.flags:
        return ""
    for word in words[n:]:
        if word == "--":
            break
        for flag in entry.flags:
            if flag.startswith("--"):
                if word == flag:
                    return flag
            elif len(flag) == 2 and word.startswith("-") and not word.startswith("--") and flag[1] in word[1:]:
                return flag
    return None


def examine_lists(text: str, handles: Sequence[str]) -> list[ListHit]:
    """Every top-level bullet list of two or more items outside a fenced block whose items do
    not all open with a handle: the first such item of each. A blank line or an indented line
    continues the list; any other line ends it."""
    patterns = [re.compile(handle) for handle in handles]
    hits: list[ListHit] = []
    fence: str | None = None
    items: list[tuple[int, str]] = []

    def close() -> None:
        if len(items) >= 2:
            for line, item in items:
                rest = PREFIX.sub("", item, count=1)
                if not any(p.match(rest) for p in patterns):
                    hits.append(ListHit(line, item))
                    break
        items.clear()

    for number, line in enumerate(text.split("\n"), 1):
        opener = FENCE.match(line)
        if fence is not None:
            if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence):
                fence = None
            continue
        if opener and (opener.group(1)[0] == "~" or "`" not in opener.group(2)):
            close()
            fence = opener.group(1)
            continue
        item = ITEM.match(line)
        if item:
            items.append((number, item.group(1).strip()))
            continue
        if line.strip() == "" or line.startswith((" ", "\t")):
            continue
        close()
    close()
    return hits
