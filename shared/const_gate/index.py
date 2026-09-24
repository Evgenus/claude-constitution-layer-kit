"""The repository's policies and what each territory claims.

A document is a policy because it lies in the root policy's territory; its namespace in
the dials file is its id. A namespace with no such document behind it is not a policy's
and claims nothing, whatever keys it carries.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from . import messages
from .envelope import id_of_text
from .errors import ConfigurationFailure
from .model import Dials, Match, PendingDocument, Policy
from .repository import list_markdown, read_text
from .territory import Matcher


@dataclass(slots=True)
class Index:
    root: Path
    paths: list[str]  # every Markdown path considered
    pending: PendingDocument | None
    root_id: str = ""
    root_territory: tuple[str, ...] = ()
    in_root: dict[str, str] = field(default_factory=dict)
    policies: dict[str, Policy] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def text(self, rel: str) -> str | None:
        if self.pending is not None and rel == self.pending.rel:
            return self.pending.text
        return read_text(self.root, rel)

    def matches(self, rel: str) -> list[Match]:
        return [Match(p.id, p.claims[rel]) for p in self.policies.values() if rel in p.claims]

    def documents(self) -> Iterator[tuple[str, str]]:
        """Every Markdown path considered, with its text. A file git lists and nobody can read is
        a configuration failure: a scan that skipped it would report a count it did not examine."""
        for rel in self.paths:
            text = self.text(rel)
            if text is None:
                raise ConfigurationFailure(messages.c12_unreadable(rel))
            yield rel, text


def build_index(
    root: Path, dials: Dials, root_policy: str, matcher: Matcher, pending: PendingDocument | None = None
) -> Index:
    paths = set(list_markdown(root))
    paths.add(root_policy)  # even when git ignores it or it is not named *.md
    if pending is not None:
        paths.add(pending.rel)
    index = Index(root=root, paths=sorted(paths), pending=pending)
    _locate_root(index, dials, root_policy, matcher)
    _discover_policies(index, dials, matcher)
    return index


def _locate_root(index: Index, dials: Dials, root_policy: str, matcher: Matcher) -> None:
    text = index.text(root_policy)
    if text is None:
        raise ConfigurationFailure(messages.c6_root_missing(root_policy))
    root_id = id_of_text(text)
    if root_id is None:
        raise ConfigurationFailure(messages.c7_root_without_id(root_policy))
    territory = dials.territory_of(root_id)
    if not territory:
        raise ConfigurationFailure(messages.c8_root_claims_nothing(root_id))
    in_root = matcher.match(territory, index.paths)
    if root_policy not in in_root:
        raise ConfigurationFailure(messages.c9_root_outside_own_territory(root_policy, territory, root_id))
    index.root_id, index.root_territory, index.in_root = root_id, territory, in_root


def _discover_policies(index: Index, dials: Dials, matcher: Matcher) -> None:
    for path in sorted(index.in_root):
        text = index.text(path)
        if text is None:  # a policy by the kernel's rule whose territory nobody can know
            raise ConfigurationFailure(messages.c12_unreadable(path))
        policy_id = id_of_text(text)
        if policy_id is None:
            index.notes.append(messages.n1_note_policy_without_id(path))
        elif policy_id in index.policies:
            index.notes.append(
                messages.n1_note_policy_id_shared(index.policies[policy_id].path, path, policy_id)
            )
        else:
            index.policies[policy_id] = Policy(policy_id, path, dials.territory_of(policy_id))
    for policy in index.policies.values():
        policy.claims = matcher.match(policy.territory, index.paths)
