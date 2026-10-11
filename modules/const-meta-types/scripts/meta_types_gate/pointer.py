"""The pointer to the governing policy: on a green write in claimed territory, one advisory line
that names the policy's document and, where it has a rule named Enforcement, that rule's anchor,
so that the session opens the policy's rules before it edits further. Advisory: it shapes what
the session reads next and checks nothing.

Said once per session, per repository and policy, since the same line on every write would cost
every write its characters and teach the reader to skip it. What was said is remembered in a
memo beside the module's output log — under `log_dir` when set, else under the platform's
per-plugin data directory — one line per pointer: the session, the repository root and the
policy's path, tab-separated. Where neither place exists the memo has no home and nothing is
pointed: a session the platform runs has the data directory. A memo that cannot be read or
written is treated as holding nothing, so the line is said again rather than lost; nothing here
changes a verdict. The two `OSError`s swallowed here, the memo's read and its write, are each said
so at their place: beside the output log's own, they are the module's departure from the rule that
a gate swallows one error, declared in its document.
"""

from __future__ import annotations

import re
from pathlib import Path

from const_gate import identity
from const_gate.output import Output

from . import messages

# A rule named Enforcement in a policy's body, in the one form this module reads: its explicit anchor,
# then the bold name, with or without a full stop inside the bold; the first such rule is the one named.
# The id's shape is fixed by the pattern, so the message takes it as it stands.
ENFORCEMENT_RE = re.compile(r'<a id="([A-Za-z0-9_-]+)"></a>\s*\*\*Enforcement\.?\*\*')
MEMO_SUFFIX = ".pointed"
MEMO_LINES = 200  # the memo keeps its last lines: a session points at few policies, and old sessions go


def enforcement_anchor(policy_text: str) -> str | None:
    found = ENFORCEMENT_RE.search(policy_text)
    return found.group(1) if found else None


def memo_path(output: Output) -> Path | None:
    """Beside the output log, under the same name as the log with another suffix; None where the
    log goes nowhere."""
    if output.log_file is None:
        return None
    return output.log_file.parent / (identity.current().namespace + MEMO_SUFFIX)


def _memo_key(session: str, root: Path, policy_path: str) -> str:
    return "\t".join((session, str(root), policy_path))


def _remember(memo: Path, key: str) -> bool:
    """True when the key was not in the memo and is now; False when it was. A memo that cannot be
    read or written counts as holding nothing: the line is said again, never lost."""
    try:
        held = memo.read_text(encoding="utf-8").splitlines() if memo.is_file() else []
    except OSError:
        held = []  # deliberate: a memo nobody can read holds nothing; the line is said again, never lost
    if key in held:
        return False
    held = [*held[-(MEMO_LINES - 1) :], key]
    try:
        memo.parent.mkdir(parents=True, exist_ok=True)
        memo.write_text("".join(line + "\n" for line in held), encoding="utf-8")
    except OSError:
        pass  # deliberate: the memo is advice's bookkeeping, and a verdict never waits on it
    return True


def policy_pointer(
    output: Output, session: str, root: Path, policy_path: str, policy_text: str | None
) -> str | None:
    """The line to add to a green write's context, or None: said already in this session for this
    repository and policy, no session named by the event, or no home for the memo."""
    memo = memo_path(output)
    if memo is None or not session:
        return None
    if not _remember(memo, _memo_key(session, root, policy_path)):
        return None
    anchor = enforcement_anchor(policy_text) if policy_text is not None else None
    return messages.n3_policy_pointer(policy_path, anchor)
