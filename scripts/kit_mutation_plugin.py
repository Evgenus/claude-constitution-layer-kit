"""Kit tooling, never shipped in a module: the pytest plugin of the mutation report, passed with
`-p kit_mutation_plugin` by `scripts/kit_mutation.py`, which copies this one file into a folder of its own
on the run's import path. It does three things, each only when asked.

Contexts: while coverage.py measures the pytest process, each test's node id becomes the coverage
context of the lines that process runs during the test; outside a test the context is empty. A child
process takes its context from the environment variable PYTEST_CURRENT_TEST, through the rc file, and
needs nothing from this plugin.

Outcomes: when the environment variable KIT_MUTATION_SEEN names a file, the plugin writes there, as
one JSON object, each test's node id with its `outcome`, `passed` unless a stage of it failed or was
skipped, and its `seconds`, the three stages added. It writes after every test, so that a run stopped
at its limit still leaves the tests it ended.

Selection: when the environment variable KIT_MUTATION_SELECT names a JSON list of node ids, only those
tests run, in the list's order; every other collected test is deselected.
"""

from __future__ import annotations

import json
import os
from collections.abc import Generator

import coverage
import pytest

SELECT_ENV = "KIT_MUTATION_SELECT"
SEEN_ENV = "KIT_MUTATION_SEEN"
SEEN: dict[str, dict[str, object]] = {}


def switch(label: str) -> None:
    measured = coverage.Coverage.current()
    if measured is not None:
        measured.switch_context(label)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item: pytest.Item) -> Generator[None, object, object]:
    switch(item.nodeid)
    try:
        return (yield)
    finally:
        switch("")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    one = SEEN.setdefault(report.nodeid, {"seconds": 0.0, "outcome": "passed"})
    spent = one["seconds"]
    one["seconds"] = round((spent if isinstance(spent, float) else 0.0) + report.duration, 3)
    if report.outcome != "passed":
        one["outcome"] = report.outcome
    target = os.environ.get(SEEN_ENV)
    if target and report.when == "teardown":
        with open(target, "w", encoding="utf-8") as out:
            json.dump(SEEN, out)


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    path = os.environ.get(SELECT_ENV)
    if not path:
        return
    with open(path, encoding="utf-8") as source:
        order = json.load(source)
    by_id = {item.nodeid: item for item in items}
    kept = [by_id[node] for node in order if node in by_id]
    chosen = {id(item) for item in kept}
    dropped = [item for item in items if id(item) not in chosen]
    if dropped:
        config.hook.pytest_deselected(items=dropped)
    items[:] = kept
