"""The pytest wiring of const-language's fixtures: the shared hooks, and the subject of the shared items."""

import acceptance
import pytest
import test_language
from test_shared_items import Subject


def pytest_configure(config: pytest.Config) -> None:
    acceptance.configure(config)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    acceptance.collected(items)


@pytest.fixture(scope="session")
def subject() -> Subject:
    return test_language.SUBJECT
