"""This module's own structures: the lines of its three logs, a commit's window, a count, a ccusage report,
the reasons a commit is not counted, and the keys of its configuration failures.

The three logs stand in the folder FOLDER of git's common directory, each line one compact JSON object:
the start log (a session's id, its start in milliseconds, its source and its transcript's path), the commit
log (a commit's SHA, the time in milliseconds, the session that made it, the event that logged it) and the
file of counts (one kept line per counted commit)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

PIN = (
    "20.0.48"  # the ccusage the module counts with, exactly; package.json and package-lock.json say the same
)
FOLDER = "const-change-cost"  # the folder of the logs in git's common directory
STARTS = "starts.jsonl"
COMMITS = "commits.jsonl"
COUNTS = "counts.jsonl"
LOCK = "counts.lock"
COMPACTION = "compact_boundary"  # the type, or the subtype, of the record a compaction writes
LOCK_SECONDS = 120.0  # how long a count waits for the lock on the file of counts
CCUSAGE_SECONDS = 60.0  # how long one ccusage run may take
NPM_SECONDS = 120.0  # how long `npm ci` may take
GIT_MINIMUM = (2, 54)  # the first git that runs hooks set in its configuration, hook.<name>.command
HOOK_COMMIT = "hook.const-change-cost-commit"  # the key of the hook on post-commit, as MODULE.md names it
HOOK_MERGE = "hook.const-change-cost-merge"  # the key of the hook on post-merge
SHA_SHOWN = 12  # how many characters of a commit's SHA a line shows

# a reply, as ccusage keys it: its message id and its request id
ReplyKey = tuple[str, str | None]


class Key(StrEnum):
    """Stable handles of this module's own configuration failures (J6) and notes."""

    J6_1 = "J6.1"  # node is not on PATH
    J6_2 = "J6.2"  # npm is not on PATH, and the pinned ccusage must be installed
    J6_3 = "J6.3"  # no ccusage stands under the plugin root or in the data folder
    J6_4 = "J6.4"  # a ccusage of another version stands there
    J6_5 = "J6.5"  # npm could not install the pinned ccusage
    J6_6 = "J6.6"  # ccusage gave no count
    J6_7 = "J6.7"  # not inside a git repository
    J6_8 = "J6.8"  # --session without CLAUDE_CODE_SESSION_ID
    J6_9 = "J6.9"  # the throwaway folder could not be made
    J6_10 = "J6.10"  # git older than the setup needs
    J6_11 = "J6.11"  # misinvocation
    J6_15 = "J6.15"  # git could not write a key into its configuration


@dataclass(frozen=True, slots=True)
class StartLine:
    """One line of the start log."""

    session: str
    ms: int
    source: str
    transcript_path: str


@dataclass(frozen=True, slots=True)
class CommitLine:
    """One line of the commit log; an empty session is a commit made outside Claude Code."""

    sha: str
    ms: int
    session: str
    event: str


@dataclass(frozen=True, slots=True)
class ModelTokens:
    """The tokens of one model in a window: the four counts added."""

    model: str
    tokens: int


@dataclass(frozen=True, slots=True)
class Kept:
    """One line of the file of counts: what a commit's window spent, written once and never again."""

    sha: str
    session: str
    input: int
    output: int
    cache_write: int
    cache_read: int
    total: int
    cost: float  # ccusage's list price for the window as a whole; a lower bound where `unpriced` is not empty
    replies: int
    models: tuple[ModelTokens, ...]
    compactions: int  # the compactions named in the window, never counted
    unpriced: tuple[str, ...]  # the models ccusage's table lacks
    ccusage: str  # the version that counted it
    counted_ms: int


@dataclass(frozen=True, slots=True)
class Entry:
    """One reply, or one advisor iteration, in ccusage's output: its model and its four counts."""

    model: str
    input: int
    output: int
    cache_write: int
    cache_read: int


@dataclass(frozen=True, slots=True)
class Report:
    """What `ccusage claude session --id <session> --json` says of a window; no entry for a null."""

    entries: tuple[Entry, ...]
    total_tokens: int
    total_cost: float


@dataclass(frozen=True, slots=True)
class Counted:
    """A window's report with the models ccusage marks as having no price."""

    report: Report
    unpriced: tuple[str, ...]


class Reason(StrEnum):
    """Why a commit has no kept line: J11.1 to J11.5."""

    NO_LOG = "J11.1"  # the report's: a commit of a range that the commit log does not hold
    NO_SESSION = "J11.2"
    NO_START = "J11.3"
    WAITING = "J11.4"
    NO_TRANSCRIPT = "J11.5"


@dataclass(frozen=True, slots=True)
class NotCounted:
    """A logged commit that has no kept line, and the reason with the facts its line names."""

    sha: str
    reason: Reason
    session: str = ""
    path: str = ""  # the transcript's path, for NO_TRANSCRIPT
