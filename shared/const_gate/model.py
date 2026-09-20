"""Enums for the closed vocabularies and dataclasses for every structure that crosses a
function boundary. Untyped data (JSON, YAML) is parsed into these once, at the edge."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

DIALS_FILE = "constitution.yaml"
DECLARATION = "policy"  # the envelope field of the secondary binding
DIALECT = "gitignore"


class MetaType(StrEnum):
    CURRENT_STATE = "current-state"
    TASK_RECORD = "task-record"
    NON_AUTHORITATIVE = "non-authoritative"


class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Severity(StrEnum):
    BLOCK = "block"
    WARN = "warn"


class EnvelopeState(StrEnum):
    NONE = "none"
    UNTERMINATED = "unterminated"
    INVALID = "invalid"
    OK = "ok"


class Mode(StrEnum):
    HOOK = "hook"
    SCAN = "scan"


class Stream(StrEnum):
    STDOUT = "stdout"
    STDERR = "stderr"


class FileTool(StrEnum):
    """The platform tools whose writes this gate judges."""

    WRITE = "Write"
    EDIT = "Edit"


class SharedKey(StrEnum):
    """Stable handles of the configuration failures every gate shares. A module's findings
    carry keys of the module's own enum."""

    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    C4B = "C4b"
    C5 = "C5"
    C6 = "C6"
    C7 = "C7"
    C8 = "C8"
    C9 = "C9"
    C12 = "C12"
    C13 = "C13"


@dataclass(frozen=True, slots=True)
class Finding:
    """The repository is wrong: what failed, why the rule exists, the exact fix."""

    key: StrEnum
    headline: str
    why: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.headline}\n  why: {self.why}\n  fix: {self.fix}"


@dataclass(frozen=True, slots=True)
class Broken:
    """The checker could not run. One self-sufficient line: in hook mode only the first
    stderr line reaches the user."""

    key: StrEnum
    headline: str
    fix: str

    def render(self) -> str:
        return f"BROKEN: {self.headline} — fix: {self.fix}"


@dataclass(frozen=True, slots=True)
class ToolEvent:
    """A PreToolUse event, reduced to the fields this gate reads."""

    tool: FileTool | None  # None: a tool this gate does not judge
    tool_name: str
    file_path: str
    cwd: str
    session_id: str
    content: str | None
    old_string: str | None
    new_string: str | None
    replace_all: bool


@dataclass(frozen=True, slots=True)
class FieldValue:
    """One envelope field as YAML read it: the text when it is a string, and the YAML type."""

    text: str | None
    yaml_type: str
    shown: str


@dataclass(frozen=True, slots=True)
class Envelope:
    """A document's frontmatter as read."""

    state: EnvelopeState
    detail: str = ""
    fields: dict[str, FieldValue] = field(default_factory=dict)

    def text(self, key: str) -> str | None:
        value = self.fields.get(key)
        return value.text if value is not None else None


@dataclass(frozen=True, slots=True)
class Namespace:
    name: str
    territory: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Dials:
    """The keys of the dials file every gate reads, validated, and the module's own
    namespace as YAML read it — untyped on purpose: the module parses its own dials at its
    own edge, once, into its own dataclass."""

    root_policy: str | None
    severity: Severity
    log_dir: str | None
    namespaces: dict[str, Namespace]
    own: Mapping[str, object]

    def territory_of(self, name: str) -> tuple[str, ...]:
        namespace = self.namespaces.get(name)
        return namespace.territory if namespace is not None else ()


@dataclass(frozen=True, slots=True)
class PendingDocument:
    """A document about to be written: judged as it will be, not as it is on disk."""

    rel: str
    text: str


@dataclass(frozen=True, slots=True)
class Match:
    policy_id: str
    pattern: str


@dataclass(slots=True)
class Policy:
    id: str
    path: str
    territory: tuple[str, ...]
    claims: dict[str, str] = field(default_factory=dict)  # path -> deciding pattern


class Defect(StrEnum):
    """The ways a document fails to resolve to exactly one governing policy."""

    NO_SUCH_POLICY = "no-such-policy"  # path maps to none, and the declaration names no policy
    MULTI_POLICY = "multi-policy"  # several territories match, and no declaration picks one
    CONTRADICTION = "contradiction"  # one territory matches, the declaration names another
    CONTRADICTION_IN_OVERLAP = "contradiction-in-overlap"  # several match, it names none of them


@dataclass(frozen=True, slots=True)
class Resolution:
    """Which policy governs a document: path first, a declaration only where the path
    mapping is absent or ambiguous. No policy and no defect: outside claimed territory."""

    matches: tuple[Match, ...]
    declared: str | None
    policy: str | None
    defect: Defect | None

    @property
    def outside(self) -> bool:
        return self.policy is None and self.defect is None


@dataclass(frozen=True, slots=True)
class Examination:
    """One document's verdict. No findings and no policy: the module has nothing to say
    about this document."""

    findings: tuple[Finding, ...]
    policy: str | None

    @property
    def outside(self) -> bool:
        return not self.findings and self.policy is None


# Exit codes, identical in both modes. On the platform, a PreToolUse hook exiting 2 blocks
# the tool call and its stderr reaches the model; any other non-zero exit is non-blocking
# and shows the first stderr line to the user. Exit 1 therefore never blocks.
EXIT_GREEN = 0  # green, or nothing to examine (the count line says which)
EXIT_BROKEN = 1  # configuration failure: the checker could not run
EXIT_RED = 2  # finding: the repository is wrong
