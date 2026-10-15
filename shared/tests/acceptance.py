"""The pytest side of the fixtures every module shares: the item marker, the rule that every test is
one numbered acceptance item, and the checks that assert.

A module's tests/conftest.py calls `configure` from its own `pytest_configure` and `collected` from its
own `pytest_collection_modifyitems`. `collected` stops the run before any test runs when a test
carries no `item(<number>, <title>)` or when two tests carry one number, one line per fault, the
numbers in order; and it hands each test's number to pytest's JUnit report as the property `item`.
One module's folder is one run: the shared items carry the same numbers in every module, and each
module's test file declares its own gate.

The checks assert in place of returning a pair: `check_case` both halves of a red→green case,
`expect` an exit and a text, `broken_first_line` a configuration failure. Until the old runners go,
each calls the harness's function that returns the pair, so the logic has one home. `failure_of` turns a
check that fails into its message, for an item that gathers several and reports every failure.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from harness import Case, Harness, Result, number_collisions
from harness import broken_first_line as broken_first_line_pair
from harness import expect as expect_pair

MARKER = "item"


def item(number: int, title: str) -> pytest.MarkDecorator:
    """The acceptance item a test is: its number, kept in every run and never reissued, and its title."""
    return pytest.mark.item(number, title)


def check_case(harness: Harness, case: Case) -> None:
    ok, evidence = harness.run_case(case)
    assert ok, evidence


def expect(result: Result, code: int, text: str, where: str = "both", label: str = "") -> None:
    """`label`, when given, opens the message: which case of a gathering failed."""
    ok, evidence = expect_pair(result, code, text, where)
    assert ok, f"{label}: {evidence}" if label else evidence


def broken_first_line(result: Result, first_line: str, label: str = "") -> None:
    ok, evidence = broken_first_line_pair(result, first_line)
    assert ok, f"{label}: {evidence}" if label else evidence


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
        lines += number_collisions(held, runner=own_test_file(items[0]), selection="a node id")  # type: ignore[arg-type]
    if lines:
        raise pytest.UsageError("\n".join(lines))
