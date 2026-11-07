"""The pytest wiring of const-locations' fixtures: the shared hooks, the subject of the shared items,
and the scope every test runs in."""

from collections.abc import Iterator
from dataclasses import replace

import pytest
from constitution_layer_kit import identity
from constitution_layer_kit.testing import acceptance
from constitution_layer_kit.testing.items import Subject
from locations_gate import start

# The test file builds its expected messages as it is imported, by the functions the gate uses, so it is
# imported inside a scope of the gate's identity. The fixture below opens the scope that the tests run in.
with identity.declared(start.GENERATOR):
    import test_locations


def pytest_configure(config: pytest.Config) -> None:
    acceptance.configure(config)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    acceptance.collected(items)


@pytest.fixture
def subject(request: pytest.FixtureRequest) -> Subject:
    """The module's subject. The shared item about a log record the transcript does not confirm writes a
    run of the harness's own script into its transcript; this module's hook script is the grant's, not the
    generator's, so that item is run with the grant's harness."""
    if request.node.name == "test_effect_disagree":
        return replace(test_locations.SUBJECT, harness=test_locations.G)
    return test_locations.SUBJECT


@pytest.fixture(scope="session", autouse=True)
def gate_declared() -> Iterator[None]:
    """The one scope of the module's identity, no mode, that every test of the session runs in; an item that
    needs another declaration opens its own inside it, and one that needs none runs in a fresh context."""
    with identity.declared(test_locations.IDENTITY):
        yield
