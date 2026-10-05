"""The two checks, each a function of typed inputs: does a subcommand match an entry, and does
every item of a list open with a handle."""

from __future__ import annotations

import re
from collections.abc import Sequence

from .model import Entry, Hit, ListHit, Subcommand

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
ITEM = re.compile(r"^[-*+] (.*)$")
# An item's text may open with an anchor, and a bold marker, before its handle; a handle form
# that is itself bold is matched on the text with the anchor alone removed.
ANCHOR = re.compile(r'^(?:<a id="[^"]*"></a>\s*)?')
BOLD = re.compile(r"^\*\*")


def match(entries: Sequence[Entry], subcommands: Sequence[Subcommand]) -> list[Hit]:
    """At most one hit per subcommand: the first entry it matches. An entry's first word is the
    program; each later word follows it with only options, and one value after an option given
    without `=`, between them. A flag matches by equality when long, inside a cluster when
    short; the scan of flags stops at `--`."""
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
    if not words or words[0] != entry.command[0]:
        return None
    after = 1
    for wanted in entry.command[1:]:
        found = _next_word(words, after, wanted)
        if found is None:
            return None
        after = found + 1
    if not entry.flags:
        return ""
    for word in words[after:]:
        if word == "--":
            break
        for flag in entry.flags:
            if flag.startswith("--"):
                if word == flag:
                    return flag
            elif (
                len(flag) == 2 and word.startswith("-") and not word.startswith("--") and flag[1] in word[1:]
            ):
                return flag
    return None


def _next_word(words: Sequence[str], start: int, wanted: str) -> int | None:
    """The index of the wanted word at or after `start`, where every word before it is an option
    (starts with `-`, and is not `-` alone) or the one value right after an option given without
    `=`; None where any other word stands first, or at `--`. A word equal to the wanted one is
    read as it, even where it could be an option's value: the walk errs toward examining more."""
    value_may_follow = False
    for index in range(start, len(words)):
        word = words[index]
        if word == wanted:
            return index
        if word == "--":
            return None
        if word.startswith("-") and word != "-":
            value_may_follow = "=" not in word
        elif value_may_follow:
            value_may_follow = False
        else:
            return None
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
                unanchored = ANCHOR.sub("", item, count=1)
                candidates = (unanchored, BOLD.sub("", unanchored, count=1))
                if not any(p.match(c) for p in patterns for c in candidates):
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
