"""The pytest side of the fixtures every module shares: the item marker, the rule that every test is
one numbered acceptance item, and the checks that assert.

A module's tests/conftest.py calls `configure` from its own `pytest_configure` and `collected` from its
own `pytest_collection_modifyitems`, and names no plugin in `pytest_plugins`: it imports the module's test
file for its `subject` fixture, and a file imported before pytest registers it as a plugin keeps plain
asserts, a warning that `-W error` makes fatal. `collected` stops the run before any test runs when a test
carries no `item(<number>, <title>)` or when two tests carry one number, one line per fault, the
numbers in order; and it hands each test's number to pytest's JUnit report as the property `item`.
One module's folder is one run: the shared items carry the same numbers in every module, and each
module's test file declares its own gate.

The checks assert: `check_case` both halves of a red→green case, through the harness's two-half check,
`expect` an exit and a text, `broken_first_line` a configuration failure. `failure_of` turns a check that
fails into its message, for an item that gathers several and reports every failure.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import pytest
from harness import Case, Harness, Result

MARKER = "item"
FIRST_SHARED = 101  # the number of the first shared item; the shared numbers are never moved or reissued


def item(number: int, title: str) -> pytest.MarkDecorator:
    """The acceptance item a test is: its number, kept in every run and never reissued, and its title."""
    return pytest.mark.item(number, title)


def check_case(harness: Harness, case: Case) -> None:
    ok, evidence = harness.run_case(case)
    assert ok, evidence


def expect(result: Result, code: int, text: str, where: str = "both", label: str = "") -> None:
    """The run exited `code` and printed `text` on `where`: "stdout", "stderr" or "both". `label`, when
    given, opens the message: which case of a gathering failed."""
    haystack = {"stdout": result.stdout, "stderr": result.stderr, "both": result.stdout + result.stderr}[
        where
    ]
    said = f"wanted exit {code} teaching {text!r}; got exit {result.code}: {haystack.strip()}"
    assert result.code == code and text in haystack, f"{label}: {said}" if label else said


def broken_first_line(result: Result, first_line: str, label: str = "") -> None:
    """A configuration failure: exit 1 — never 2, never 0 — and its line is the FIRST stderr line."""
    first = result.stderr.splitlines()[0] if result.stderr else ""
    said = f"wanted exit 1 with first line {first_line!r}; got exit {result.code}: {result.stderr.strip()}"
    assert result.code == 1 and first == first_line, f"{label}: {said}" if label else said


def failure_of(check: Callable[[], object]) -> str | None:
    """The message of `check` when it fails — an assertion or a `pytest.fail` — or None: for an item that
    gathers several checks and reports every failure, where one failing check must hide no other."""
    try:
        check()
    except (AssertionError, pytest.fail.Exception) as error:
        return str(error)
    return None


def configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", f"{MARKER}(number, title): the acceptance item a test is")


@dataclass(frozen=True)
class Numbered:
    number: int
    title: str


def numbered(test: pytest.Item) -> Numbered | None:
    mark = test.get_closest_marker(MARKER)
    if mark is None or len(mark.args) != 2:
        return None
    number, title = mark.args
    return Numbered(number, title) if isinstance(number, int) and isinstance(title, str) else None


def own_test_file(test: pytest.Item) -> str:
    """The module's own test file, as the fix of a doubled number names it: tests/test_<name>.py, the name
    its folder's without `const-`, hyphens made underscores."""
    module = Path(str(test.path)).parent.parent.name
    return f"tests/test_{module.removeprefix('const-').replace('-', '_')}.py"


def number_collisions(items: Sequence[Numbered], test_file: str) -> list[str]:
    """One message for each number that two or more of `items` carry, in number order — what failed,
    why, and the exact fix. Nothing here knows which item is a shared one, so a number from the first
    shared one up is worded conditionally. The fix names the free numbers below the first shared one —
    those above the highest number the items hold there, since a number an item left free is never
    reissued — as many as the items that must move need; the items left without one are counted, and
    that is a decision to raise, since the shared numbers never move. `test_file` is the file the fix
    names."""
    titles: dict[int, list[str]] = {}
    for item in items:
        titles.setdefault(item.number, []).append(item.title)
    free = list(range(max((n for n in titles if n < FIRST_SHARED), default=0) + 1, FIRST_SHARED))
    lines: list[str] = []
    for number in sorted(n for n, held in titles.items() if len(held) > 1):
        held = titles[number]
        named = ", ".join(repr(title) for title in held)
        moving = len(held) - 1
        given, free = free[:moving], free[moving:]
        left = moving - len(given)
        keep = f"keep one of them at {number}"
        if number >= FIRST_SHARED:
            keep += " — the shared one, if one is shared, since a shared number is never moved or reissued"
        others = "the other one" if moving == 1 else f"each of the other {moving}"
        decision = "raise it as a decision, since the shared numbers are never moved"
        if not given:
            fix = f"{keep}; but no number is free below {FIRST_SHARED} for {others} — {decision}"
        else:
            noun, other = ("number", "a number") if len(given) == 1 else ("numbers", "numbers")
            who = others if not left else f"{len(given)} of the other {moving}"
            fix = (
                f"{keep}, and in the module's own {test_file} give {who} the {noun}"
                f" {', '.join(map(str, given))} — {other} no other item holds, below {FIRST_SHARED}"
            )
            if left:
                are = "item is" if left == 1 else "items are"
                fix += f"; {left} {are} then left with no free number — {decision}"
        lines.append(
            f"item number {number} is carried by {len(held)} items, {named} — why: one number, one"
            f" item, or a result and a node id cannot say which item they mean — fix: {fix}"
        )
    return lines


def collected(items: list[pytest.Item]) -> None:
    held: list[Numbered] = []
    lines = []
    for test in items:
        found = numbered(test)
        if found is None:
            lines.append(
                f"{test.nodeid} carries no item(<number>, <title>) — why: a test outside the acceptance"
                " table is examined by no row — fix: give it @item(<number>, <title>) from acceptance"
            )
            continue
        held.append(found)
        test.user_properties.append((MARKER, str(found.number)))
    if items:
        lines += number_collisions(held, own_test_file(items[0]))
    if lines:
        raise pytest.UsageError("\n".join(lines))
