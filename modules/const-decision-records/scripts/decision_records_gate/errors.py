"""One exception with one job: keeping exit 1 (the checker could not run) distinct from
exit 2 (the repository is wrong)."""

from __future__ import annotations

from .model import Broken


class ConfigurationFailure(Exception):
    def __init__(self, broken: Broken) -> None:
        super().__init__(broken.headline)
        self.broken = broken
