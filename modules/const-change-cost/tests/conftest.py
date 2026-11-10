"""The pytest wiring of const-change-cost's fixtures: the shared hooks and the scope every test runs in."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from change_cost_gate import start
from constitution_layer_kit import identity
from constitution_layer_kit.testing import acceptance
from constitution_layer_kit.testing.items import Subject

# The test file builds its expected messages as it is imported, by the functions the module uses, so it is
# imported inside a scope of the module's identity. The fixture below opens the scope that the tests run in.
with identity.declared(start.COUNT):
    import test_change_cost

# the session's install of the pinned ccusage, a fixture of the test file, is the shared items' too
installed = test_change_cost.installed


def pytest_configure(config: pytest.Config) -> None:
    acceptance.configure(config)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    acceptance.collected(items)


@pytest.fixture
def subject(installed: Path) -> Iterator[Subject]:
    """The subject of the shared items. Every run of the count looks for the pinned ccusage first, even one
    with nothing to count, so for as long as a shared item runs, the plugin root holds a link to the copy
    installed for the session; the link is removed after the item, so that the module's own items about
    finding and installing ccusage meet a plugin root that holds none."""
    link = test_change_cost.PLUGIN / "node_modules"
    if link.exists() or link.is_symlink():
        pytest.fail(f"{link} stands already: remove it, so that the items about finding ccusage meet none")
    link.symlink_to(installed / "node_modules")
    try:
        yield test_change_cost.SUBJECT
    finally:
        link.unlink()


@pytest.fixture(scope="session", autouse=True)
def gate_declared() -> Iterator[None]:
    """The one scope of the module's identity, no mode, that every test of the session runs in; an item that
    needs another declaration opens its own inside it, and one that needs none runs in a fresh context."""
    with identity.declared(test_change_cost.IDENTITY):
        yield
