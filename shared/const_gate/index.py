"""The repository's policies and what each territory claims.

A document is a policy because it lies in the root policy's territory; its namespace in
the dials file is its id. A namespace with no such document behind it is not a policy's
and claims nothing, whatever keys it carries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import messages
from .dials import MODULE_PREFIX
from .envelope import declared_policy, document_id, id_of_text, parse_envelope
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
    void: dict[str, dict[str, str]] = field(default_factory=dict)  # namespace -> would-be claims
    notes: list[str] = field(default_factory=list)
    _owners: dict[str, list[str]] | None = None

    def text(self, rel: str) -> str | None:
        if self.pending is not None and rel == self.pending.rel:
            return self.pending.text
        return read_text(self.root, rel)

    def matches(self, rel: str) -> list[Match]:
        return [Match(p.id, p.claims[rel]) for p in self.policies.values() if rel in p.claims]

    def governed(self) -> list[str]:
        claimed: set[str] = set()
        for policy in self.policies.values():
            claimed.update(policy.claims)
        return sorted(claimed)

    def id_owners(self) -> dict[str, list[str]]:
        """id -> the governed documents carrying it (claimed by path, or bound by a declaration
        naming a policy). Built once per run: every Markdown file is read a single time."""
        if self._owners is None:
            claimed = set(self.governed())
            owners: dict[str, list[str]] = {}
            for rel in self.paths:
                envelope = parse_envelope(self.text(rel) or "")
                doc_id = document_id(envelope)
                if doc_id is None:
                    continue
                if rel in claimed or declared_policy(envelope) in self.policies:
                    owners.setdefault(doc_id, []).append(rel)
            self._owners = owners
        return self._owners

    def void_namespaces_claiming(self, rel: str) -> list[str]:
        return [name for name, claims in self.void.items() if rel in claims]


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
        policy_id = id_of_text(index.text(path))
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


def collect_void_namespaces(index: Index, dials: Dials, matcher: Matcher) -> None:
    """What each namespace with a territory and no policy behind it would claim. One git run
    per such namespace, so only a gate that reports them asks for it."""
    for name, namespace in dials.namespaces.items():
        if name in index.policies or name.startswith(MODULE_PREFIX) or not namespace.territory:
            continue
        index.void[name] = matcher.match(namespace.territory, index.paths)
