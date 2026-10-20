"""Which policy governs a document: by path first; by a declaration in the envelope only
where the path mapping is absent or ambiguous. The result is typed and carries no message:
whether a defect is a finding, and how it is taught, is the module's."""

from __future__ import annotations

from .envelope import declared_policy
from .index import Index
from .model import Defect, Envelope, Resolution


def resolve(index: Index, rel: str, envelope: Envelope) -> Resolution:
    matches = tuple(index.matches(rel))
    declared = declared_policy(envelope)

    def result(policy: str | None, defect: Defect | None) -> Resolution:
        return Resolution(matches, declared, policy, defect)

    if len(matches) == 1:
        only = matches[0].policy_id
        if declared is None or declared == only:
            return result(only, None)
        return result(None, Defect.CONTRADICTION)
    if len(matches) > 1:
        if declared is None:
            return result(None, Defect.MULTI_POLICY)
        if declared in {match.policy_id for match in matches}:
            return result(declared, None)
        return result(None, Defect.CONTRADICTION_IN_OVERLAP)
    if declared is None:
        return result(None, None)  # outside claimed territory: silence
    if declared in index.policies:
        return result(declared, None)
    return result(None, Defect.NO_SUCH_POLICY)
