"""The pytest wiring of const-referencing's fixtures: the shared hooks, the subject of the shared items,
and the scope every test runs in."""

from collections.abc import Iterator

import acceptance
import pytest
from constitution_layer_kit import identity
from referencing_gate import start
from test_shared_items import Subject

# The test file builds its expected messages as it is imported, by the functions the gate uses, so it is
# imported inside a scope of the gate's identity. The fixture below opens the scope that the tests run in.
with identity.declared(start.GATE):
    import test_referencing


def pytest_configure(config: pytest.Config) -> None:
    acceptance.configure(config)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    acceptance.collected(items)


@pytest.fixture(scope="session")
def subject() -> Subject:
    return test_referencing.SUBJECT


@pytest.fixture(scope="session", autouse=True)
def gate_declared() -> Iterator[None]:
    """The one scope of the module's identity, no mode, that every test of the session runs in; an item that
    needs another declaration opens its own inside it, and one that needs none runs in a fresh context."""
    with identity.declared(test_referencing.IDENTITY):
        yield
