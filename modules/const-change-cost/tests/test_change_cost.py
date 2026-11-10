"""Fixtures of const-change-cost: `python3 -m pytest tests` from the module's folder.

Needs git, Python 3.12+, pytest, the libraries in the plugin's requirements file, and Node with npm: the
items that count run the pinned ccusage, installed once per test session from the plugin's lockfile by
`npm ci --ignore-scripts` into a scratch folder. Without Node, npm or the network the session stops with the
install command and those items fail, never pass. Every item has a stable number: this module's own items
from 1, the items every gate shares from 101.

The transcripts are the comparison's synthetic fixture (res-0015, E3): a parent session `S1` with a
subagent and a workflow agent, and its fork `S2`, fixed ids, round counts, no personal data. Each test
builds its own clone: a git repository with the three logs written by hand, and a copy of the transcripts.
The count is driven through its real entry, `count-costs.sh`, with a plugin data folder that holds the
installed ccusage and the same lockfile, so that nothing is installed during a test unless it is the point.
The independent count of the items about windows is made apart from ccusage, in this file, from the
fixture's own usage fields.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import sys
from bisect import bisect_left
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from change_cost_gate import counter as counters
from change_cost_gate import counting, logs, messages, start, windows
from change_cost_gate.model import PIN, CommitLine, NotCounted, Reason, StartLine
from constitution_layer_kit.testing.acceptance import item
from constitution_layer_kit.testing.harness import Harness, Result, fake_program

SCRIPTS = Path(__file__).resolve().parent.parent / "plugin" / "scripts"
PLUGIN = SCRIPTS.parent
FIXTURE = Path(__file__).resolve().parent / "fixture" / "projects" / "p"

IDENTITY = start.COUNT  # declared for the whole session by conftest; the expected messages read it
NS = IDENTITY.namespace
H = Harness(SCRIPTS, "count-costs.sh", "count-costs.py", NS)
HS = Harness(SCRIPTS, "session-start.sh", "session-start.py", NS)  # the start hook
HU = Harness(SCRIPTS, "setup-commit-log.sh", "setup-commit-log.py", NS)  # the setup a person runs
HR = Harness(SCRIPTS, "cost-report.sh", "cost-report.py", NS)  # the report a person runs

S1 = "11111111-1111-4111-8111-111111111111"
S2 = "22222222-2222-4222-8222-222222222222"
S3 = "33333333-3333-4333-8333-333333333333"
S4 = "44444444-4444-4444-8444-444444444444"
SONNET = "claude-sonnet-4-5-20250929"
OPUS = "claude-opus-4-5-20251101"
BASE = datetime(2026, 11, 1, 10, 0, 0, tzinfo=UTC)
CLAUSE = "until then no commit is counted"
CLOSING = "BROKEN: the count could not run — no commit was counted"
START_CLAUSE = "until then no session's start is logged, and its commits get no count"
START_CLOSING = "BROKEN: const-change-cost could not log this session's start — its commits will get no count"
SETUP_C2_CLAUSE = "until then no hook of the commit log is written"
SETUP_CLOSING = "BROKEN: the setup could not run — setup-commit-log.sh --check shows what stands"
REPORT_C2_CLAUSE = "until then no report or export is made"
REPORT_CLOSING = "BROKEN: the report could not run — nothing was shown or written"
HOOK_COMMIT = "hook.const-change-cost-commit"
HOOK_MERGE = "hook.const-change-cost-merge"
NPM_HINT = (
    "install Node.js, which brings npm (https://nodejs.org/en/download), and run: npm ci --ignore-scripts"
)
GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull, "LC_ALL": "C"}
KEPT_KEYS = {
    "sha",
    "session",
    "input",
    "output",
    "cache_write",
    "cache_read",
    "total",
    "cost",
    "replies",
    "models",
    "compactions",
    "unpriced",
    "ccusage",
    "counted_ms",
}


# ------------------------------------------------------------------ time, records, and the independent count


def at(seconds: float) -> int:
    """Milliseconds since the epoch of 10:00:00 on 2026-11-01 UTC plus `seconds`, the fixture's own day."""
    return int(BASE.timestamp() * 1000) + round(seconds * 1000)


def stamp(seconds: float) -> str:
    moment = BASE + timedelta(seconds=seconds)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def line_of(record: Mapping[str, object]) -> str:
    return json.dumps(record, separators=(",", ":")) + "\n"


def user_record(session: str, seconds: float) -> str:
    return line_of(
        {
            "type": "user",
            "timestamp": stamp(seconds),
            "sessionId": session,
            "message": {"role": "user", "content": "x"},
        }
    )


USAGE_FIELDS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def usage_sum(usage: object) -> int:
    if not isinstance(usage, dict):
        return 0
    return sum(usage.get(name, 0) for name in USAGE_FIELDS)


def apart(files: Sequence[Path], session: str, start_s: float, cuts_s: Sequence[float]) -> list[int]:
    """The tokens of each window, counted here from the fixture's usage fields, apart from ccusage: a reply is
    its message id and request id, the record with the larger total stands for it, its advisor iterations
    add, and it belongs to the window of its first record at or after the start. One more window holds what
    follows the last cut."""
    first: dict[tuple[str, str], float] = {}
    best: dict[tuple[str, str], int] = {}
    for path in files:
        for raw in path.read_text(encoding="utf-8").splitlines():
            record = json.loads(raw)
            message = record.get("message")
            if not isinstance(message, dict) or "id" not in message or "usage" not in message:
                continue
            when = (datetime.fromisoformat(record["timestamp"]) - BASE).total_seconds()
            if when < start_s or record.get("sessionId") != session:
                continue
            key = (message["id"], record["requestId"])
            usage = message["usage"]
            total = usage_sum(usage) + sum(usage_sum(part) for part in usage.get("iterations", []))
            first[key] = min(first.get(key, when), when)
            best[key] = max(best.get(key, 0), total)
    held = [0] * (len(cuts_s) + 1)
    for key, when in first.items():
        held[bisect_left(list(cuts_s), when)] += best[key]
    return held


# ------------------------------------------------------------------ a clone with its logs and transcripts


def install_script(root: Path, version: str, body: str) -> None:
    """A fake ccusage package under `root`: its package.json and a launcher that runs `body`."""
    (root / "node_modules" / "ccusage").mkdir(parents=True)
    (root / "node_modules" / "ccusage" / "package.json").write_text(
        json.dumps({"name": "ccusage", "version": version}), encoding="utf-8"
    )
    (root / "node_modules" / ".bin").mkdir()
    fake_program(root / "node_modules" / ".bin" / "ccusage", body)


FAKE_REPORT = (
    'case "$*" in\n'
    '  *"--id"*) echo \'{"entries":[{"model":"m","inputTokens":1,"outputTokens":2,'
    '"cacheCreationTokens":3,"cacheReadTokens":4}],"totalTokens":10,"totalCost":0.5}\' ;;\n'
    "  *) echo '{\"sessions\":[]}' ;;\n"
    "esac\n"
)


@dataclass
class Clone:
    """A git repository with its logs, a copy of the fixture's transcripts, a plugin data folder that holds
    the installed ccusage and a lockfile equal to the plugin's, and a folder for the system's temp files."""

    root: Path
    folder: Path  # the folder of the logs in git's common directory
    projects: Path  # `projects/p` of the fake configuration folder
    data: Path
    tmp: Path

    @classmethod
    def make(cls, parent: Path, installed: Path | None) -> Clone:
        parent.mkdir(parents=True, exist_ok=True)
        root = parent / "repo"
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True, env={**os.environ, **GIT_ENV})
        projects = parent / "claude" / "projects" / "p"
        shutil.copytree(FIXTURE, projects)
        data = parent / "data"
        data.mkdir()
        if installed is not None:
            for name in ("package.json", "package-lock.json"):
                shutil.copyfile(PLUGIN / name, data / name)
            os.symlink(installed / "node_modules", data / "node_modules")
        tmp = parent / "tmp"
        tmp.mkdir()
        real = Path(os.path.realpath(root))
        return cls(real, real / ".git" / "const-change-cost", projects, data, tmp)

    def transcript(self, session: str) -> Path:
        return self.projects / f"{session}.jsonl"

    def append_line(self, name: str, record: Mapping[str, object]) -> None:
        logs.append_line(self.folder / name, record)

    def start(self, session: str, seconds: float, source: str = "startup", path: Path | None = None) -> None:
        shown = path if path is not None else self.transcript(session)
        self.append_line(
            "starts.jsonl",
            {"session": session, "ms": at(seconds), "source": source, "transcript_path": str(shown)},
        )

    def commit(self, sha: str, seconds: float, session: str) -> None:
        self.append_line(
            "commits.jsonl", {"sha": sha, "ms": at(seconds), "session": session, "event": "commit"}
        )

    def append_record(self, session: str, seconds: float) -> None:
        with self.transcript(session).open("a", encoding="utf-8") as handle:
            handle.write(user_record(session, seconds))

    def environment(self, extra: Mapping[str, str] | None = None) -> dict[str, str]:
        return {
            "CLAUDE_PLUGIN_DATA": str(self.data),
            "TMPDIR": str(self.tmp),
            "CLAUDE_CODE_SESSION_ID": "",
            **GIT_ENV,
            **(extra or {}),
        }

    def count(
        self, *args: str, env: Mapping[str, str] | None = None, harness: Harness = H, cwd: Path | None = None
    ) -> Result:
        return harness.run_gate("", args=list(args), env=self.environment(env), cwd=cwd or self.root)

    def kept(self) -> list[dict[str, object]]:
        path = self.folder / "counts.jsonl"
        return (
            [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines()]
            if path.exists()
            else []
        )


@pytest.fixture(scope="session")
def installed(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The pinned ccusage, installed once per test session from the plugin's lockfile; a missing npm or a
    failed install fails the run with the install command, never skips what needs it."""
    folder = tmp_path_factory.mktemp("ccusage-installed")
    for name in ("package.json", "package-lock.json"):
        shutil.copyfile(PLUGIN / name, folder / name)
    npm = shutil.which("npm")
    if npm is None:
        pytest.fail(f"npm is not on PATH, and the items that count need the pinned ccusage — {NPM_HINT}")
    done = subprocess.run(
        [npm, "ci", "--ignore-scripts"], cwd=folder, capture_output=True, text=True, check=False
    )
    if done.returncode != 0:
        pytest.fail(f"npm ci --ignore-scripts failed in the scratch folder: {done.stderr.strip()[:300]}")
    return folder


@pytest.fixture
def clone(tmp_path: Path, installed: Path) -> Clone:
    return Clone.make(tmp_path, installed)


def bare_clone(tmp_path: Path) -> Clone:
    """A clone whose data folder holds nothing: for the items about finding and installing ccusage."""
    return Clone.make(tmp_path, None)


def ccusage_of(installed: Path) -> counters.Ccusage:
    return counters.Ccusage(counters.launcher_of(installed), PIN, PLUGIN)


def closing(result: Result) -> str:
    return result.stdout.splitlines()[-1]


def counted_line(counted: int, before: int, waiting: int, never: int) -> str:
    return (
        f"COUNTED: {counted} commit(s) counted now, {before} counted before, {waiting} waiting for a later"
        f" record, {never} never to be counted — cost-report.sh shows them"
    )


def totals(clone: Clone) -> list[int]:
    return [int(str(held["total"])) for held in clone.kept()]


def first_line(result: Result) -> str:
    return result.stderr.splitlines()[0] if result.stderr else ""


# ------------------------------------------------------------------ T5 to T11: the count


@item(5, "the known count at the pin: the parent session's four counts, total and list cost")
def test_known_count_at_the_pin(tmp_path: Path, installed: Path) -> None:
    """The fixture's parent session through the cutter and the pinned ccusage: 1,551 input, 186 output, 1,000
    cache write and 3,000 cache read, 5,737 in all, and the cost equal to the price page's by hand (res-0015,
    E3). The rates are the page's, per million tokens: Sonnet 4.5 $3 input, $15 output, $3.75 cache write and
    $0.30 cache read, Opus 4.5 $5 input and $25 output."""
    files = windows.transcripts_of(FIXTURE / f"{S1}.jsonl")
    found = windows.survey(files, S1, at(0))
    folders = windows.cut(files, S1, at(0), found, [at(60)], {0}, tmp_path)
    counted = counters.count(ccusage_of(installed), folders[0], S1)
    report = counted.report
    assert [sum(getattr(held, name) for held in report.entries) for name in ("input", "output")] == [
        1551,
        186,
    ]
    assert sum(held.cache_write for held in report.entries) == 1000
    assert sum(held.cache_read for held in report.entries) == 3000
    assert report.total_tokens == 5737
    by_hand = {SONNET: (3.0, 15.0, 3.75, 0.30), OPUS: (5.0, 25.0, 6.25, 0.50)}
    price = sum(
        (
            held.input * by_hand[held.model][0]
            + held.output * by_hand[held.model][1]
            + held.cache_write * by_hand[held.model][2]
            + held.cache_read * by_hand[held.model][3]
        )
        / 1_000_000
        for held in report.entries
    )
    assert round(report.total_cost, 6) == 0.012213 == round(price, 6)
    assert counted.unpriced == ()


@item(
    6,
    "windows: a commit's window runs from the previous commit, a reply counted once in its first record's"
    " window",
)
def test_windows(clone: Clone) -> None:
    """Commits of S1 at 10:00:05.500 and 10:00:10.500 give 2,360 and 3,375, the 2 tokens after them waiting
    for a third commit that a later record completes. The reply written twice across the first commit is in
    the first window, once. Each window equals a count made apart from ccusage in this file."""
    clone.start(S1, 0)
    clone.commit("a" * 40, 5.5, S1)
    clone.commit("b" * 40, 10.5, S1)
    clone.commit("c" * 40, 13, S1)
    done = clone.count("--all")
    assert (done.code, closing(done)) == (0, counted_line(2, 0, 1, 0)), done.stderr
    assert totals(clone) == [2360, 3375]
    files = [path for path in (FIXTURE / S1).rglob("*.jsonl")] + [FIXTURE / f"{S1}.jsonl"]
    assert apart(files, S1, 0, [5.5, 10.5, 13]) == [2360, 3375, 2, 0]
    clone.append_record(S1, 14)
    later = clone.count("--all")
    assert (later.code, closing(later)) == (0, counted_line(1, 2, 0, 0)), later.stderr
    assert totals(clone) == [2360, 3375, 2]


@item(7, "a fork's two sessions: the fork cut at its start gives 8,430 and the parent 5,737, in either order")
def test_fork(tmp_path: Path, installed: Path) -> None:
    """The fork copies its parent's records with their ids and times. Cut at the fork's own start, 10:00:20,
    it gives its own two replies, 8,430; the parent gives 5,737; with the commits logged in either order, the
    same (res-0015, E4)."""
    results: list[dict[str, int]] = []
    for order in ((S1, S2), (S2, S1)):
        clone = Clone.make(tmp_path / "-".join(order[:1]), installed)
        clone.start(S1, 0)
        clone.start(S2, 20)
        clone.append_record(S1, 14)
        clone.append_record(S2, 30)
        for session in order:
            clone.commit(session[0] * 40, 13 if session == S1 else 25, session)
        done = clone.count("--all")
        assert (done.code, closing(done)) == (0, counted_line(2, 0, 0, 0)), done.stderr
        results.append({str(held["session"]): int(str(held["total"])) for held in clone.kept()})
    assert results[0] == results[1] == {S1: 5737, S2: 8430}


@item(8, "the earliest start owns: a start log with startup, resume and compact for one id cuts at the first")
def test_earliest_start(clone: Clone, tmp_path: Path, installed: Path) -> None:
    clone.start(S1, 11, "compact")
    clone.start(S1, 0, "startup")
    clone.start(S1, 8, "resume")
    clone.append_record(S1, 14)
    clone.commit("a" * 40, 13, S1)
    done = clone.count("--all")
    assert (done.code, closing(done)) == (0, counted_line(1, 0, 0, 0)), done.stderr
    assert totals(clone) == [5737]
    # what stands before the earliest start is no part of the session: a compaction there is named in no
    # window, and a reply that began there does not move a later record of it into an earlier window
    cut = Clone.make(tmp_path / "cut", installed)
    with cut.transcript(S2).open("a", encoding="utf-8") as handle:
        handle.write(assistant_record(S2, 15, "msg_x", 100))
        handle.write(assistant_record(S2, 22.5, "msg_x", 110))
        handle.write(
            line_of(
                {"type": "system", "subtype": "compact_boundary", "timestamp": stamp(18), "sessionId": S2}
            )
        )
        handle.write(user_record(S2, 30))
    cut.start(S2, 20)
    cut.commit("a" * 40, 21.5, S2)
    cut.commit("b" * 40, 25, S2)
    again = cut.count("--all")
    assert (again.code, closing(again)) == (0, counted_line(2, 0, 0, 0)), again.stderr
    assert totals(cut) == [3660, 4880]
    assert [held["compactions"] for held in cut.kept()] == [0, 0]


def assistant_record(session: str, seconds: float, message: str, tokens: int) -> str:
    usage = {"input_tokens": tokens, "output_tokens": 0}
    body = {"id": message, "model": SONNET, "role": "assistant", "usage": usage}
    return line_of(
        {
            "type": "assistant",
            "timestamp": stamp(seconds),
            "sessionId": session,
            "requestId": "req_" + message,
            "message": body,
        }
    )


@item(9, "the copy: plain files, the agents' included, lines byte for byte; --config keeps the count")
def test_copy_and_config(tmp_path: Path, installed: Path) -> None:
    """The copy holds plain files in the layout under `projects/`, the subagent's and the workflow agent's
    included, each line as it stood. A `.ccusage/ccusage.json` in the working folder and a `ccusage.json` in
    the configuration folder that set the cost to 0 change a run without `--config` and leave the counter's
    (res-0015, E7)."""
    files = windows.transcripts_of(FIXTURE / f"{S1}.jsonl")
    found = windows.survey(files, S1, at(0))
    folders = windows.cut(files, S1, at(0), found, [at(60)], {0}, tmp_path)
    copied = sorted(path for path in folders[0].rglob("*") if path.is_file() or path.is_symlink())
    shown = [str(path.relative_to(folders[0])) for path in copied]
    assert sorted(shown) == sorted(
        [
            f"projects/p/{S1}.jsonl",
            f"projects/p/{S1}/subagents/agent-a1.jsonl",
            f"projects/p/{S1}/subagents/workflows/wf_1/agent-w1.jsonl",
        ]
    )
    assert not any(path.is_symlink() for path in copied)
    for path in copied:
        source = FIXTURE / path.relative_to(folders[0] / "projects" / "p")
        assert path.read_bytes() == source.read_bytes()
    # what is no regular file is left out: a link to a .jsonl, a dangling link, a folder named .jsonl, and a
    # session's own transcript given as a link; the copy and the count stay as they were
    hostile = tmp_path / "hostile" / "projects" / "p"
    shutil.copytree(FIXTURE, hostile)
    own = hostile / S1
    os.symlink(hostile / f"{S2}.jsonl", own / "subagents" / "link.jsonl")
    os.symlink(hostile / "nowhere.jsonl", own / "dangling.jsonl")
    (own / "folder.jsonl").mkdir()
    plain_names = sorted(held.destination.name for held in files)
    assert (
        sorted(held.destination.name for held in windows.transcripts_of(hostile / f"{S1}.jsonl"))
        == plain_names
    )
    linked = tmp_path / "linked" / "projects" / "p"
    linked.mkdir(parents=True)
    os.symlink(FIXTURE / f"{S1}.jsonl", linked / f"{S1}.jsonl")
    assert windows.transcripts_of(linked / f"{S1}.jsonl") == []
    hostile_files = windows.transcripts_of(hostile / f"{S1}.jsonl")
    hostile_found = windows.survey(hostile_files, S1, at(0))
    hostile_cut = windows.cut(hostile_files, S1, at(0), hostile_found, [at(60)], {0}, tmp_path / "cut")
    assert sorted(p.name for p in hostile_cut[0].rglob("*.jsonl")) == plain_names
    assert counters.count(ccusage_of(installed), hostile_cut[0], S1).report.total_tokens == 5737
    plan = '{"claude":{"commands":{"session":{"mode":"display"}}}}'
    (folders[0] / ".ccusage").mkdir()
    (folders[0] / ".ccusage" / "ccusage.json").write_text(plan, encoding="utf-8")
    (folders[0] / "ccusage.json").write_text(plan, encoding="utf-8")
    plain = subprocess.run(
        [str(counters.launcher_of(installed)), "claude", "session", "--id", S1, "--json", "--offline"],
        cwd=folders[0],
        env={**os.environ, "CLAUDE_CONFIG_DIR": str(folders[0])},
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(plain.stdout)["totalCost"] == 0
    kept = counters.count(ccusage_of(installed), folders[0], S1)
    assert round(kept.report.total_cost, 6) == 0.012213
    assert kept.report.total_tokens == 5737


@item(10, "an unpriced model keeps its tokens, and the kept line names it")
def test_unpriced_model(clone: Clone) -> None:
    """A reply renamed to a model the table lacks: the tokens stay, the cost falls by that reply's price, and
    the kept line names the model (res-0015, E8)."""
    path = clone.transcript(S1)
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(raw)
        if record.get("message", {}).get("id") == "msg_a":
            record["message"]["model"] = "claude-imaginary-9"
        lines.append(line_of(record))
    path.write_text("".join(lines), encoding="utf-8")
    clone.start(S1, 0)
    clone.append_record(S1, 14)
    clone.commit("a" * 40, 13, S1)
    done = clone.count("--all")
    assert (done.code, closing(done)) == (0, counted_line(1, 0, 0, 0)), done.stderr
    held = clone.kept()[0]
    assert (held["total"], held["unpriced"]) == (5737, ["claude-imaginary-9"])
    assert held["models"] == {SONNET: 4583, OPUS: 44, "claude-imaginary-9": 1110}
    assert round(float(str(held["cost"])), 6) == 0.008013


@item(11, "a compaction is named in the window it falls in and never counted")
def test_compaction(clone: Clone) -> None:
    boundary = {
        "type": "system",
        "subtype": "compact_boundary",
        "content": "Conversation compacted",
        "timestamp": stamp(8),
        "sessionId": S1,
    }
    with clone.transcript(S1).open("a", encoding="utf-8") as handle:
        handle.write(line_of(boundary))
    clone.start(S1, 0)
    clone.commit("a" * 40, 5.5, S1)
    clone.commit("b" * 40, 10.5, S1)
    clone.commit("c" * 40, 13, S1)
    clone.append_record(S1, 14)
    done = clone.count("--all")
    assert (done.code, closing(done)) == (0, counted_line(3, 0, 0, 0)), done.stderr
    assert [held["compactions"] for held in clone.kept()] == [0, 1, 0]
    assert totals(clone) == [2360, 3375, 2]


# ------------------------------------------------------------------ T12 to T14: completeness, the kept line


@item(
    12,
    "completeness and once: a commit with no later record waits; a second pass changes nothing; a killed"
    " count leaves no line",
)
def test_waits_and_once(tmp_path: Path, installed: Path) -> None:
    clone = Clone.make(tmp_path / "once", installed)
    clone.start(S1, 0)
    clone.commit("a" * 40, 13, S1)
    waiting = clone.count("--all")
    assert (waiting.code, closing(waiting)) == (0, counted_line(0, 0, 1, 0)), waiting.stderr
    assert clone.kept() == []
    clone.append_record(S1, 14)
    counted = clone.count("--all")
    assert (counted.code, closing(counted)) == (0, counted_line(1, 0, 0, 0)), counted.stderr
    before = (clone.folder / "counts.jsonl").read_bytes()
    again = clone.count("--all")
    assert (again.code, closing(again)) == (0, counted_line(0, 1, 0, 0)), again.stderr
    assert (clone.folder / "counts.jsonl").read_bytes() == before
    # a count killed inside ccusage leaves no line, and a later pass counts the window
    killed = Clone.make(tmp_path / "killed", installed)
    killed.start(S1, 0)
    killed.append_record(S1, 14)
    killed.commit("b" * 40, 13, S1)
    root = tmp_path / "killer"
    shutil.copytree(PLUGIN, root, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
    install_script(root, PIN, "kill -9 $PPID\n")
    harness = Harness(root / "scripts", "count-costs.sh", "count-costs.py", NS)
    dead = killed.count("--all", harness=harness, env={"CLAUDE_PLUGIN_DATA": str(tmp_path / "nowhere")})
    assert dead.code == -9, dead.stderr
    assert killed.kept() == []
    recovered = killed.count("--all")
    assert (recovered.code, closing(recovered)) == (0, counted_line(1, 0, 0, 0)), recovered.stderr
    assert totals(killed) == [5737]


@item(
    13,
    "the kept line's fields, the ccusage version among them, no throwaway folder left, an unreadable log"
    " line named",
)
def test_kept_line_and_unreadable_lines(clone: Clone) -> None:
    clone.start(S1, 0)
    clone.append_record(S1, 14)
    clone.commit("a" * 40, 13, S1)
    done = clone.count("--all")
    assert (done.code, closing(done)) == (0, counted_line(1, 0, 0, 0)), done.stderr
    held = clone.kept()[0]
    assert set(held) == KEPT_KEYS
    assert (held["sha"], held["session"], held["ccusage"]) == ("a" * 40, S1, "20.0.48")
    assert [held[name] for name in ("input", "output", "cache_write", "cache_read", "total", "replies")] == [
        1551,
        186,
        1000,
        3000,
        5737,
        8,
    ]
    assert held["models"] == {SONNET: 5693, OPUS: 44}
    assert (held["compactions"], held["unpriced"]) == (0, [])
    assert round(float(str(held["cost"])), 6) == 0.012213
    assert abs(int(str(held["counted_ms"])) - int(datetime.now(UTC).timestamp() * 1000)) < 120_000
    assert list(clone.tmp.iterdir()) == []
    # lines that cannot be read, in each of the three logs, are left out with their note
    for name, text in (
        ("starts.jsonl", "this is not JSON\n"),
        ("commits.jsonl", "[1, 2]\n"),
        ("counts.jsonl", '{"sha": "x"}\n'),
    ):
        with (clone.folder / name).open("a", encoding="utf-8") as handle:
            handle.write(text)
    after = clone.count("--all")
    shown = f"note: a log line cannot be read and is left out: {clone.folder}"
    assert after.stdout.splitlines() == [
        f"{shown}/starts.jsonl line 2: it is not JSON",
        f"{shown}/commits.jsonl line 2: it is not a JSON object",
        f"{shown}/counts.jsonl line 2: the field session is missing or has the wrong type",
        counted_line(0, 1, 0, 0),
    ]


@item(14, "the commits not counted, each named: no session, no start, no transcript, a window not complete")
def test_commits_not_counted(clone: Clone) -> None:
    """The reasons, as the model finds them and as the lines J11.1 to J11.5 are worded, typed by hand."""
    clone.start(S1, 0)
    clone.start(S4, 0, path=clone.projects / "gone.jsonl")
    clone.commit("1" * 40, 13, "")
    clone.commit("2" * 40, 13, S3)
    clone.commit("3" * 40, 13, S4)
    clone.commit("4" * 40, 13, S1)
    done = clone.count("--all")
    assert (done.code, closing(done)) == (0, counted_line(0, 0, 1, 3)), done.stderr
    starts, _ = logs.read_starts(clone.folder)
    commits, _ = logs.read_commits(clone.folder)
    tally = counting.Tally()
    for session, held in counting.commits_of(commits).items():
        own = [line for line in starts if line.session == session]
        counting.count_session(session, held, own, set(), None, clone.folder, tally)
    gone = str(clone.projects / "gone.jsonl")
    assert tally.not_counted == [
        NotCounted("1" * 40, Reason.NO_SESSION),
        NotCounted("2" * 40, Reason.NO_START, S3),
        NotCounted("3" * 40, Reason.NO_TRANSCRIPT, S4, gone),
        NotCounted("4" * 40, Reason.WAITING, S1),
    ]
    sha = "abcdef012345"
    assert [
        messages.j11_not_counted(NotCounted(sha + "6789", reason, S1, "/x/s.jsonl")) for reason in Reason
    ] == [
        f"{sha}: not counted — no line in the commit log: made before setup-commit-log.sh ran, by a tool that"
        " runs no git hook, or on a forge",
        f"{sha}: not counted — the commit log names no session: made outside Claude Code",
        f"{sha}: not counted — session {S1} has no start in the start log: it started before the plugin was"
        " enabled, or in another folder",
        f"{sha}: not counted — its window is not complete: no record of session {S1} is dated after the"
        " commit"
        " yet; a later pass counts it",
        f"{sha}: not counted — no transcript of session {S1} stands at /x/s.jsonl: swept by Claude Code's"
        " cleanup, or never kept",
    ]


# ------------------------------------------------------------------ T19, T20: where ccusage stands, the pin


@dataclass
class Rig:
    """A plugin copied to a folder with no ccusage, a clone with nothing installed, and a PATH of tools that
    the test chooses: `sh`, `dirname`, `git` and `python3` always, `node` and `npm` when it adds them."""

    clone: Clone
    root: Path
    harness: Harness
    bin: Path
    npm_log: Path

    @classmethod
    def make(cls, parent: Path, node: bool = True, npm: str | None = None) -> Rig:
        clone = bare_clone(parent / "clone")
        root = parent / "plugin"
        shutil.copytree(PLUGIN, root, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
        folder = parent / "bin"
        folder.mkdir()
        for tool in ("sh", "dirname", "git"):
            found = shutil.which(tool)
            assert found, tool
            os.symlink(found, folder / tool)
        os.symlink(os.path.realpath(sys.executable), folder / "python3")
        if node:
            fake_program(folder / "node", "exit 0\n")
        log = parent / "npm.log"
        if npm is not None:
            fake_program(folder / "npm", npm)
        harness = Harness(root / "scripts", "count-costs.sh", "count-costs.py", NS)
        clone.start(S1, 0)
        clone.append_record(S1, 14)
        clone.commit("a" * 40, 13, S1)
        return cls(clone, root, harness, folder, log)

    def run(self, data: bool = True, env: Mapping[str, str] | None = None) -> Result:
        extra = {"PATH": str(self.bin), "NPM_LOG": str(self.npm_log), **(env or {})}
        if not data:
            self.clone.data.rmdir()
            extra["CLAUDE_PLUGIN_DATA"] = ""
        return self.clone.count("--all", env=extra, harness=self.harness)


FAKE_NPM = (
    'echo "$PWD $*" >> "$NPM_LOG"\n'
    "/bin/mkdir -p node_modules/ccusage node_modules/.bin\n"
    'echo \'{"version":"20.0.48"}\' > node_modules/ccusage/package.json\n'
    '/bin/cp "$FAKE_CCUSAGE" node_modules/.bin/ccusage\n'
)


@item(
    19,
    "ccusage under the plugin root, else the data folder, installed there when the lockfile copy differs;"
    " J5.3 and J6.1 to J6.6",
)
def test_finding_ccusage(tmp_path: Path) -> None:
    fake = tmp_path / "fake-ccusage"
    fake_program(fake, FAKE_REPORT)
    # under the plugin root: used, no npm call
    rig = Rig.make(tmp_path / "root", npm=FAKE_NPM)
    install_script(rig.root, PIN, FAKE_REPORT)
    done = rig.run()
    assert (done.code, closing(done)) == (0, counted_line(1, 0, 0, 0)), done.stderr
    assert not rig.npm_log.exists()
    assert totals(rig.clone) == [10]
    # no ccusage anywhere, the data folder without a lockfile: installed there, once, by npm ci
    rig = Rig.make(tmp_path / "data", npm=FAKE_NPM)
    first = rig.run(env={"FAKE_CCUSAGE": str(fake)})
    note = f"note: the pinned ccusage {PIN} was installed into {rig.clone.data}"
    assert first.code == 0 and first.stdout.splitlines() == [note, counted_line(1, 0, 0, 0)], first.stderr
    assert rig.npm_log.read_text(encoding="utf-8").splitlines() == [f"{rig.clone.data} ci --ignore-scripts"]
    # the lockfile copy is the plugin's now: a pass installs nothing more
    rig.clone.commit("b" * 40, 14.5, S1)
    rig.clone.append_record(S1, 16)
    second = rig.run(env={"FAKE_CCUSAGE": str(fake)})
    assert (second.code, second.stdout.splitlines()) == (0, [counted_line(1, 1, 0, 0)]), second.stderr
    assert len(rig.npm_log.read_text(encoding="utf-8").splitlines()) == 1
    # a lockfile copy that differs: installed again
    (rig.clone.data / "package-lock.json").write_text("{}\n", encoding="utf-8")
    third = rig.run(env={"FAKE_CCUSAGE": str(fake)})
    assert third.code == 0 and third.stdout.splitlines()[0] == note, third.stderr
    assert len(rig.npm_log.read_text(encoding="utf-8").splitlines()) == 2
    assert ccusage_failures(tmp_path / "failures") == []


@item(
    20,
    "the pin: package.json and the lockfile name ccusage 20.0.48 exactly, every package an https address"
    " and a hash, none a script",
)
def test_the_pin() -> None:
    manifest = json.loads((PLUGIN / "package.json").read_text(encoding="utf-8"))
    assert manifest["dependencies"] == {"ccusage": "20.0.48"}
    lock = json.loads((PLUGIN / "package-lock.json").read_text(encoding="utf-8"))
    assert lock["lockfileVersion"] == 3
    packages = {name: held for name, held in lock["packages"].items() if name}
    assert packages["node_modules/ccusage"]["version"] == "20.0.48"
    platforms = sorted(name for name in packages if name.startswith("node_modules/@ccusage/ccusage-"))
    assert [name.rpartition("ccusage-")[2] for name in platforms] == [
        "darwin-arm64",
        "darwin-x64",
        "linux-arm64",
        "linux-x64",
        "win32-arm64",
        "win32-x64",
    ]
    for name, held in packages.items():
        assert held["version"] == "20.0.48", name
        assert held["resolved"].startswith("https://registry.npmjs.org/"), name
        assert held["integrity"].startswith("sha512-"), name
        assert "hasInstallScript" not in held and "scripts" not in held, name
    assert json.loads((PLUGIN / "ccusage.json").read_text(encoding="utf-8")) == {}
    assert (PLUGIN / "requirements.txt").read_text(encoding="utf-8") == "PyYAML>=6.0\n"


# ------------------------------------------------------------------ T19 and T23: the configuration failures


def broken_line(what: str, fix: str) -> str:
    return f"BROKEN: {what} — fix: {fix} — {CLAUSE}"


@item(21, "the lock: two passes at once count each commit once; a lock held past 120 s gives J5.2")
def test_lock(clone: Clone) -> None:
    clone.start(S1, 0)
    clone.append_record(S1, 14)
    for index, seconds in enumerate((5.5, 10.5, 13)):
        clone.commit(str(index) * 40, seconds, S1)
    passes = [
        subprocess.Popen(
            [H.sh, str(H.wrapper), "--all"],
            cwd=clone.root,
            env=H.environment(clone.environment()),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(2)
    ]
    outputs = [(held.communicate(), held.returncode) for held in passes]
    assert [code for _, code in outputs] == [0, 0], outputs
    assert sorted(str(held["sha"]) for held in clone.kept()) == ["0" * 40, "1" * 40, "2" * 40]
    closings = sorted(out.splitlines()[-1] for (out, _), _ in outputs)
    assert closings == [counted_line(0, 3, 0, 0), counted_line(3, 0, 0, 0)]
    # a lock another count keeps past its seconds: the pass counts nothing and says so
    held_clone = Clone.make(clone.root.parent / "held", clone.data)
    held_clone.start(S1, 0)
    held_clone.append_record(S1, 14)
    held_clone.commit("a" * 40, 13, S1)
    held_clone.folder.mkdir(exist_ok=True)
    sitecustomize = held_clone.tmp / "sitecustomize.py"
    sitecustomize.write_text(
        "import time\nreal = time.monotonic\ntime.monotonic = lambda: real() * 1000.0\n", encoding="utf-8"
    )
    descriptor = os.open(held_clone.folder / "counts.lock", os.O_RDWR | os.O_CREAT)
    fcntl.flock(descriptor, fcntl.LOCK_EX)
    try:
        done = held_clone.count("--all", env={"PYTHONPATH": str(held_clone.tmp)})
    finally:
        os.close(descriptor)
    assert done.code == 0, done.stderr
    assert done.stdout.splitlines() == [
        "note: another count kept the lock on the file of counts for 120 s — this pass counts nothing, and"
        " the"
        " next pass counts what is left",
        counted_line(0, 0, 1, 0),
    ]
    assert held_clone.kept() == []


@item(
    22,
    "--session counts only the session CLAUDE_CODE_SESSION_ID names, J6.8 without it; --all covers every"
    " session",
)
def test_session_and_all(clone: Clone) -> None:
    clone.start(S1, 0)
    clone.start(S2, 20)
    clone.append_record(S1, 14)
    clone.append_record(S2, 30)
    clone.commit("a" * 40, 13, S1)
    clone.commit("b" * 40, 25, S2)
    lacking = clone.count("--session")
    assert lacking.code == 1 and lacking.stdout == ""
    assert lacking.stderr.splitlines() == [
        "BROKEN: --session needs CLAUDE_CODE_SESSION_ID, which Claude Code sets in its hooks and its shell"
        f" tool — fix: run it in a Claude Code session, or run count-costs.sh --all — {CLAUSE}",
        CLOSING,
    ]
    own = clone.count("--session", env={"CLAUDE_CODE_SESSION_ID": S2})
    assert (own.code, closing(own)) == (0, counted_line(1, 0, 0, 0)), own.stderr
    assert [held["session"] for held in clone.kept()] == [S2]
    everything = clone.count("--all")
    assert (everything.code, closing(everything)) == (0, counted_line(1, 1, 0, 0)), everything.stderr
    assert sorted(str(held["session"]) for held in clone.kept()) == [S1, S2]


@item(
    23, "the exit-code split of the count: 0 with its closing line, 1 with its line first on stderr, never 2"
)
def test_exit_codes(tmp_path: Path, clone: Clone) -> None:
    clone.start(S1, 0)
    assert clone.count("--all").code == 0
    outside = tmp_path / "outside"
    outside.mkdir()
    not_git = clone.count("--all", cwd=outside, env={"GIT_CEILING_DIRECTORIES": str(tmp_path)})
    assert not_git.code == 1 and not_git.stdout == ""
    assert not_git.stderr.splitlines() == [
        broken_line(
            f"{outside} is not inside a git repository", "run it inside the clone whose commits it counts"
        ),
        CLOSING,
    ]
    for args, detail in (
        ((), "one of the arguments --all --session is required"),
        (("--all", "--session"), "argument --session: not allowed with argument --all"),
        (("--bogus",), "one of the arguments --all --session is required"),
        (("--all", "x"), "unrecognized arguments: x"),
    ):
        misuse = clone.count(*args)
        assert misuse.code == 1, args
        assert misuse.stderr.splitlines() == [
            broken_line(f"misinvocation: {detail}", "run it as count-costs.sh [--all | --session]"),
            CLOSING,
        ], args
    # the throwaway folder cannot be made
    clone.append_record(S1, 14)
    clone.commit("a" * 40, 13, S1)
    sitecustomize = clone.tmp / "sitecustomize.py"
    sitecustomize.write_text(
        "import tempfile\n\n\ndef refuse(*args, **kwargs):\n    raise PermissionError(13, 'Permission"
        " denied')\n\n\n"
        "tempfile.mkdtemp = refuse\n",
        encoding="utf-8",
    )
    refused = clone.count("--all", env={"PYTHONPATH": str(clone.tmp)})
    assert refused.code == 1 and refused.stdout == ""
    assert refused.stderr.splitlines() == [
        f"BROKEN: the throwaway folder for session {S1} could not be made: [Errno 13] Permission denied —"
        " fix:"
        f" free or repair the system's temporary directory, which TMPDIR names, then count again — {CLAUSE}",
        CLOSING,
    ]
    assert clone.kept() == []
    exit_codes_of_start_and_setup(tmp_path, clone)
    exit_codes_of_report(tmp_path / "report-codes")


def exit_codes_of_start_and_setup(tmp_path: Path, clone: Clone) -> None:
    """The start hook's and the setup's parts of the exit-code split: 0 with their lines, 1 with the line
    first on stderr and their own closing line, never 2; J6.7, J6.11 and J6.15 typed by hand."""
    logged_before = len(log_lines(clone, "starts.jsonl"))
    fix_input = (
        "as a hook this script reads one tool event, a JSON object, on stdin; to check a repository by hand"
        " run it with --scan [<dir>]"
    )
    for stdin, detail in (
        ("{", "it is not JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"),
        ("[]", "it is JSON, but the top level is not an object"),
        (
            '{"session_id": "x", "transcript_path": "/t", "cwd": "/"}',
            "a SessionStart event must carry a string source",
        ),
    ):
        bad = start_hook(clone, stdin)
        assert bad.code == 1 and bad.stdout == "", stdin
        assert bad.stderr.splitlines() == [
            f"BROKEN: hook input cannot be used ({detail}) — fix: {fix_input}",
            START_CLOSING,
        ], stdin
    misuse = HS.run_gate(payload(S1, clone.root), args=["x"], env=clone.environment(), cwd=clone.root)
    assert misuse.code == 1 and misuse.stdout == ""
    assert misuse.stderr.splitlines() == [
        "BROKEN: misinvocation: unexpected argument x — fix: run it as session-start.sh with no argument and"
        f" one SessionStart event on its standard input — {START_CLAUSE}",
        START_CLOSING,
    ]
    assert len(log_lines(clone, "starts.jsonl")) == logged_before, "a start that cannot be read logs nothing"
    outside = tmp_path / "outside-setup"
    outside.mkdir()
    nowhere = clone.count(harness=HU, cwd=outside, env={"GIT_CEILING_DIRECTORIES": str(tmp_path)})
    assert nowhere.code == 1 and nowhere.stdout == ""
    assert nowhere.stderr.splitlines() == [
        f"BROKEN: {outside} is not inside a git repository — fix: run it inside the clone whose commits it"
        " counts",
        SETUP_CLOSING,
    ]
    for args, detail in (
        (("--bogus",), "unrecognized arguments: --bogus"),
        (("--remove", "--check"), "argument --check: not allowed with argument --remove"),
        (("x",), "unrecognized arguments: x"),
    ):
        wrong = setup_run(clone, *args)
        assert wrong.code == 1 and wrong.stdout == "", args
        assert wrong.stderr.splitlines() == [
            f"BROKEN: misinvocation: {detail} — fix: run it as setup-commit-log.sh [--remove | --check]",
            SETUP_CLOSING,
        ], args
    git_dir = clone.root / ".git"
    git_dir.chmod(0o555)  # git cannot lock the configuration file
    try:
        locked = setup_run(clone)
    finally:
        git_dir.chmod(0o755)
    assert locked.code == 1 and locked.stdout == ""
    first, closing_line = locked.stderr.splitlines()
    assert closing_line == SETUP_CLOSING
    assert first.startswith(
        f"BROKEN: git could not write {HOOK_COMMIT}.command into {git_dir}/config: error: could not lock"
    )
    assert first.endswith(
        " — fix: repair what git names, such as the file's rights, then run setup-commit-log.sh --check"
    )
    assert HOOK_COMMIT not in git_in(clone.root, "config", "--local", "--list", session=None)


def exit_codes_of_report(parent: Path) -> None:
    """The report's part of the exit-code split: 0 with its head line, 1 with the line first on stderr and the
    report's closing line, never 2; J6.7, J6.11, J6.12 and J6.14 typed by hand."""
    clone, shas = report_rig(parent / "rig")
    assert run_report(clone).code == 0
    outside = parent / "outside"
    outside.mkdir()
    for args in ((), ("base..HEAD",), ("--trailer", "base..HEAD")):
        nowhere = clone.count(*args, harness=HR, cwd=outside, env={"GIT_CEILING_DIRECTORIES": str(parent)})
        assert nowhere.code == 1 and nowhere.stdout == "", args
        assert nowhere.stderr.splitlines() == [
            f"BROKEN: {outside} is not inside a git repository — fix: run it inside the clone whose commits"
            " it counts",
            REPORT_CLOSING,
        ], args
    usage = "cost-report.sh [<range>] | --trailer <range> | --pr <range> | --notes <range>"
    for args, detail in (
        (("--bogus",), "unrecognized arguments: --bogus"),
        (("--trailer",), "argument --trailer: expected one argument"),
        (("--trailer", "a..b", "--pr", "c..d"), "argument --pr: not allowed with argument --trailer"),
        (("a..b", "c..d"), "unrecognized arguments: c..d"),
        (("--pr", "a..b", "c"), "unexpected argument c"),
    ):
        misuse = run_report(clone, *args)
        assert misuse.code == 1 and misuse.stdout == "", args
        assert misuse.stderr.splitlines() == [
            f"BROKEN: misinvocation: {detail} — fix: run it as {usage}",
            REPORT_CLOSING,
        ], args
    for flag in ("", "--trailer", "--pr", "--notes"):
        args = (flag, "nowhere..HEAD") if flag else ("nowhere..HEAD",)
        unreadable = run_report(clone, *args)
        assert unreadable.code == 1 and unreadable.stdout == "", args
        first, closing_line = unreadable.stderr.splitlines()
        assert closing_line == REPORT_CLOSING
        assert first.startswith(f"BROKEN: git cannot read the range nowhere..HEAD in {clone.root}: fatal: ")
        assert first.endswith(
            " — fix: name commits this clone has, such as main..HEAD; a shallow clone may need git fetch"
            " --unshallow"
        )
    (clone.root / ".git" / "refs" / "notes").write_text("a file where git wants a folder\n", encoding="utf-8")
    refused = run_report(clone, "--notes", "base..HEAD", env=AUTHOR)
    assert refused.code == 1 and refused.stdout == ""
    first, closing_line = refused.stderr.splitlines()
    assert closing_line == REPORT_CLOSING
    assert first.startswith(f"BROKEN: git could not write the note on {short(shas, 'counted')}: ")
    assert first.endswith(
        " — fix: repair what git names, then run cost-report.sh --notes again; the notes already written"
        " stand"
    )


@dataclass(frozen=True)
class Entry:
    """One entry of the module under test: its harness, the arguments and input of a plain run, the clause it
    closes its failures with (none for a generator's) and its closing line."""

    harness: Harness
    script: str
    args: tuple[str, ...]
    stdin: str
    clause: str
    closing: str
    c2_clause: str  # the identity's clause, which closes the shared C2 alone for a generator

    def tail(self) -> str:
        return f" — {self.clause}" if self.clause else ""


def entries(clone: Clone) -> list[Entry]:
    return [
        Entry(H, "count-costs.py", ("--all",), "", CLAUSE, CLOSING, CLAUSE),
        Entry(HS, "session-start.py", (), payload(S1, clone.root), START_CLAUSE, START_CLOSING, START_CLAUSE),
        Entry(HU, "setup-commit-log.py", (), "", "", SETUP_CLOSING, SETUP_C2_CLAUSE),
        Entry(HR, "cost-report.py", (), "", "", REPORT_CLOSING, REPORT_C2_CLAUSE),
    ]


@item(
    25, "each entry's install-failure lines, C1, C2, C14 and C15, close with its own clause, then its J line"
)
def test_install_failures(tmp_path: Path, clone: Clone) -> None:
    clone.start(S1, 0)
    tools = tmp_path / "tools"  # a PATH holding only sh, dirname and git: no python3
    tools.mkdir()
    for tool in ("sh", "dirname", "git"):
        found = shutil.which(tool)
        assert found, tool
        os.symlink(found, tools / tool)
    shadow = tmp_path / "shadow"  # PyYAML hidden: the shared C2, its clause this entry's
    shadow.mkdir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    lowered = (
        "import sys; sys.version_info = (3, 11, 0); path = sys.argv[1]; "
        "exec(compile(open(path).read(), path, 'exec'), {'__name__': '__main__', '__file__': path})"
    )
    for entry in entries(clone):
        env = clone.environment()
        no_python = entry.harness.run_gate(
            entry.stdin, args=list(entry.args), env={**env, "PATH": str(tools)}, cwd=clone.root
        )
        assert no_python.code == 1, entry.script
        assert no_python.stderr.splitlines() == [
            "BROKEN: const-change-cost needs python3 — fix: install Python 3.12 or newer"
            f" (https://www.python.org/downloads/){entry.tail()}",
            entry.closing,
        ], entry.script
        no_yaml = entry.harness.run_gate(
            entry.stdin, args=list(entry.args), env={**env, "PYTHONPATH": str(shadow)}, cwd=clone.root
        )
        assert no_yaml.code == 1, entry.script
        assert no_yaml.stderr.splitlines() == [
            "BROKEN: const-change-cost needs PyYAML — fix: run: python3 -m pip install -r"
            f" '{PLUGIN}/requirements.txt' — {entry.c2_clause}",
            entry.closing,
        ], entry.script
        path = SCRIPTS / entry.script  # the entry file run as an interpreter of 3.11 would run it
        old = entry.harness.run_gate(
            entry.stdin, command=[sys.executable, "-c", lowered, str(path)], env=env, cwd=clone.root
        )
        assert old.code == 1, entry.script
        assert old.stderr.splitlines() == [
            "BROKEN: const-change-cost needs Python 3.12 or newer, found 3.11 — fix: install a current"
            f" Python 3 (https://www.python.org/downloads/) and put it first on PATH{entry.tail()}",
            entry.closing,
        ], entry.script
        no_package = entry.harness.run_gate(  # the harness's shared folder left out, and no site-packages
            entry.stdin,
            args=list(entry.args),
            env={**env, "PYTHONPATH": ""},
            command=[sys.executable, "-S", str(path)],
            shared=False,
            cwd=clone.root,
        )
        assert no_package.code == 1, entry.script
        assert no_package.stderr.splitlines() == [
            "BROKEN: const-change-cost needs the Python package constitution-layer-kit 2.0.0 or a later 2.x"
            " release,"
            f" and python3 cannot import it — fix: install it for python3 as {PLUGIN}/INSTALL.md says"
            f"{entry.tail()}",
            entry.closing,
        ], entry.script


# ------------------------------------------------------------------ T1 to T4, T24: start hook, setup

AUTHOR = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
}
J1_HEAD = (
    "const-change-cost (advisory): this clone logs no commit, so none of its commits is counted — git's"
    " configuration lacks "
)
J1_TAIL = (
    ". Load the skill const-change-cost:share-costs, tell the person, and run sh"
    ' "{root}/scripts/setup-commit-log.sh" only when they ask.'
)


def payload(session: str, cwd: Path, source: str = "startup", transcript: str = "/t/s.jsonl") -> str:
    """A real SessionStart event, as Claude Code writes it to a hook's standard input."""
    return json.dumps(
        {
            "session_id": session,
            "transcript_path": transcript,
            "cwd": str(cwd),
            "hook_event_name": "SessionStart",
            "source": source,
        }
    )


def git_in(cwd: Path, *args: str, session: str | None = S1, check: bool = True) -> str:
    """The real git, in `cwd`, as a session would run it: the variable of the session named, or unset."""
    env = {key: value for key, value in os.environ.items() if key != "CLAUDE_CODE_SESSION_ID"}
    env.update({**GIT_ENV, **AUTHOR})
    if session is not None:
        env["CLAUDE_CODE_SESSION_ID"] = session
    done = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=False)
    if check:
        assert done.returncode == 0, f"git {' '.join(args)}: {done.stderr.strip()}"
    return done.stdout.strip()


def start_hook(clone: Clone, stdin: str, cwd: Path | None = None) -> Result:
    return HS.run_gate(stdin, env=clone.environment(), cwd=cwd or clone.root)


def setup_run(clone: Clone, *args: str, cwd: Path | None = None) -> Result:
    return clone.count(*args, harness=HU, cwd=cwd)


def local_config(root: Path) -> list[str]:
    return git_in(root, "config", "--local", "--list", session=None).splitlines()


def set_hook(root: Path, key: str, event: str) -> None:
    git_in(root, "config", "--local", f"{key}.command", "true", session=None)
    git_in(root, "config", "--local", f"{key}.event", event, session=None)


def log_lines(clone: Clone, name: str) -> list[dict[str, object]]:
    path = clone.folder / name
    return [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


@item(1, "the start record: one compact JSON line in the common directory, from the checkout and a worktree")
def test_start_record(tmp_path: Path, clone: Clone) -> None:
    git_in(clone.root, "commit", "--allow-empty", "-q", "-m", "a")
    worktree = tmp_path / "wt"
    git_in(clone.root, "worktree", "add", "-q", str(worktree), "-b", "other")
    before = int(datetime.now(UTC).timestamp() * 1000)
    main = start_hook(clone, payload(S1, clone.root, "startup", "/t/one.jsonl"))
    linked = start_hook(clone, payload(S2, worktree, "resume", "/t/two.jsonl"), cwd=worktree)
    after = int(datetime.now(UTC).timestamp() * 1000)
    for done in (main, linked):
        assert (done.code, done.stdout.count("\n")) == (0, 1), done.stderr  # the start line J1 alone
    raw = (clone.folder / "starts.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(raw) == 2
    for text, session, source, transcript in (
        (raw[0], S1, "startup", "/t/one.jsonl"),
        (raw[1], S2, "resume", "/t/two.jsonl"),
    ):
        record = json.loads(text)
        assert list(record) == ["session", "ms", "source", "transcript_path"]
        assert (record["session"], record["source"], record["transcript_path"]) == (
            session,
            source,
            transcript,
        )
        assert isinstance(record["ms"], int) and before <= record["ms"] <= after
        assert text == json.dumps(record, separators=(",", ":"))  # compact
    assert not (worktree / ".git").is_dir() and not (worktree / "const-change-cost").exists()


@item(2, "J1 with both hooks and with one missing; nothing printed when both stand or outside a repository")
def test_start_line(tmp_path: Path, clone: Clone) -> None:
    root = str(PLUGIN)
    both = start_hook(clone, payload(S1, clone.root))
    assert both.code == 0 and both.stderr == ""
    assert both.stdout.splitlines() == [
        J1_HEAD + f"{HOOK_COMMIT} and {HOOK_MERGE}" + J1_TAIL.format(root=root)
    ]
    set_hook(clone.root, HOOK_COMMIT, "post-commit")
    only_merge_missing = start_hook(clone, payload(S1, clone.root))
    assert only_merge_missing.stdout.splitlines() == [J1_HEAD + HOOK_MERGE + J1_TAIL.format(root=root)]
    git_in(clone.root, "config", "--local", "--remove-section", HOOK_COMMIT, session=None)
    set_hook(clone.root, HOOK_MERGE, "post-merge")
    only_commit_missing = start_hook(clone, payload(S1, clone.root))
    assert only_commit_missing.stdout.splitlines() == [J1_HEAD + HOOK_COMMIT + J1_TAIL.format(root=root)]
    set_hook(clone.root, HOOK_COMMIT, "post-merge")  # a hook on the wrong event is no hook of the log
    wrong_event = start_hook(clone, payload(S1, clone.root))
    assert wrong_event.stdout.splitlines() == [J1_HEAD + HOOK_COMMIT + J1_TAIL.format(root=root)]
    set_hook(clone.root, HOOK_COMMIT, "post-commit")
    git_in(clone.root, "config", "--local", "--unset-all", f"{HOOK_COMMIT}.event", session=None)
    git_in(clone.root, "config", "--local", "--add", f"{HOOK_COMMIT}.event", "post-merge", session=None)
    git_in(clone.root, "config", "--local", "--add", f"{HOOK_COMMIT}.event", "post-commit", session=None)
    standing = start_hook(clone, payload(S1, clone.root))  # both stand, one on two events
    assert (standing.code, standing.stdout, standing.stderr) == (0, "", "")
    assert len(log_lines(clone, "starts.jsonl")) == 5  # every start is logged, the line or not
    outside = tmp_path / "outside"
    outside.mkdir()
    env = {"GIT_CEILING_DIRECTORIES": str(tmp_path)}
    nowhere = HS.run_gate(payload(S1, outside), env=clone.environment(env), cwd=outside)
    assert (nowhere.code, nowhere.stdout, nowhere.stderr) == (0, "", "")
    assert list(outside.iterdir()) == []
    assert len(log_lines(clone, "starts.jsonl")) == 5


@item(
    3, "the setup: J17 with both hooks and nothing else written; J19 both ways; J18 keeping the logs; old git"
)
def test_setup(tmp_path: Path, clone: Clone) -> None:
    config = clone.root / ".git" / "config"
    before = local_config(clone.root)
    checked = setup_run(clone, "--check")
    assert (checked.code, checked.stdout.splitlines(), checked.stderr) == (
        0,
        [
            f"CHECK: git's configuration lacks {HOOK_COMMIT} and {HOOK_MERGE}"
            " — setup-commit-log.sh writes them"
        ],
        "",
    )
    done = setup_run(clone)
    assert (done.code, done.stderr) == (0, "")
    assert done.stdout.splitlines() == [
        f"SET: {HOOK_COMMIT} on post-commit and {HOOK_MERGE} on post-merge written into {config}"
        " — every commit of this clone is logged from now on"
    ]
    after = local_config(clone.root)
    added = [line for line in after if line not in before]
    assert sorted(line.split("=", 1)[0] for line in added) == [
        f"{HOOK_COMMIT}.command",
        f"{HOOK_COMMIT}.event",
        f"{HOOK_MERGE}.command",
        f"{HOOK_MERGE}.event",
    ]
    assert [line for line in before if line not in after] == [], "nothing that stood was changed"
    assert f"{HOOK_COMMIT}.event=post-commit" in after and f"{HOOK_MERGE}.event=post-merge" in after
    for key in (HOOK_COMMIT, HOOK_MERGE):
        value = git_in(clone.root, "config", "--local", "--get", f"{key}.command", session=None)
        assert value.startswith("python3 -c '") and value.endswith("'") and "\n" not in value
    again = setup_run(clone)  # a second run writes the same, and adds nothing
    assert again.code == 0 and sorted(local_config(clone.root)) == sorted(after)
    both = setup_run(clone, "--check")
    assert (both.code, both.stdout.splitlines()) == (
        0,
        ["CHECK: both hooks of the commit log stand in git's configuration"],
    )
    git_in(clone.root, "config", "--local", "--remove-section", HOOK_MERGE, session=None)
    one = setup_run(clone, "--check")
    assert (one.code, one.stdout.splitlines()) == (
        0,
        [f"CHECK: git's configuration lacks {HOOK_MERGE} — setup-commit-log.sh writes them"],
    )
    setup_run(clone)
    clone.start(S1, 0)  # a log the removal must keep
    clone.commit("a" * 40, 1, S1)
    removed = setup_run(clone, "--remove")
    assert (removed.code, removed.stderr) == (0, "")
    assert removed.stdout.splitlines() == [
        f"REMOVED: {HOOK_COMMIT} and {HOOK_MERGE} removed from {config} — the logs and the counts stay in"
        f" {clone.folder}"
    ]
    assert local_config(clone.root) == before
    assert len(log_lines(clone, "starts.jsonl")) == 1 and len(log_lines(clone, "commits.jsonl")) == 1
    assert setup_run(clone, "--remove").code == 0  # nothing to remove is done
    # a git older than 2.54 is refused, and nothing is written
    real = shutil.which("git")
    assert real
    fake = tmp_path / "fakegit"
    fake.mkdir()
    fake_program(
        fake / "git",
        f'[ "$1" = "--version" ] && {{ echo "git version 2.53.1"; exit 0; }}\nexec {real} "$@"\n',
    )
    old = clone.count(harness=HU, env={"PATH": f"{fake}{os.pathsep}{os.environ['PATH']}"})
    assert old.code == 1 and old.stdout == ""
    assert old.stderr.splitlines() == [
        "BROKEN: const-change-cost needs git 2.54 or newer, which runs hooks set in its configuration, and"
        " found 2.53.1 — fix: install a newer git (https://git-scm.com/downloads), then run"
        " setup-commit-log.sh again",
        SETUP_CLOSING,
    ]
    assert local_config(clone.root) == before


@item(
    4,
    "the commit log by a real git: commit, amend, cherry-pick, rebase, a merge's commit and merge --no-ff"
    " once each; a fast-forward not; no variable an empty session; a worktree into the same file",
)
def test_commit_log(tmp_path: Path, clone: Clone) -> None:
    root = clone.root
    assert setup_run(clone).code == 0
    seen = {"count": 0}

    def logged(label: str, *, wanted: int, session: str = S1, event: str = "commit") -> None:
        lines = log_lines(clone, "commits.jsonl")
        assert len(lines) == seen["count"] + wanted, f"{label}: {lines[seen['count'] :]}"
        for line in lines[seen["count"] :]:
            assert list(line) == ["sha", "ms", "session", "event"], label
            assert line["session"] == session and line["event"] == event, f"{label}: {line}"
            assert line["sha"] == git_in(root, "rev-parse", "HEAD", session=None), label
        seen["count"] = len(lines)

    started = int(datetime.now(UTC).timestamp() * 1000)
    git_in(root, "branch", "-M", "main", check=False)
    git_in(root, "commit", "--allow-empty", "-q", "-m", "a")
    logged("commit", wanted=1)
    git_in(root, "commit", "--amend", "--allow-empty", "-q", "-m", "a2")
    logged("amend", wanted=1)
    git_in(root, "checkout", "-q", "-b", "side")
    (root / "f").write_text("x\n", encoding="utf-8")
    git_in(root, "add", "f")
    git_in(root, "commit", "-q", "-m", "b")
    logged("a commit on a branch", wanted=1)
    git_in(root, "checkout", "-q", "main")
    git_in(root, "commit", "--allow-empty", "-q", "-m", "m1")
    logged("a commit on main", wanted=1)
    git_in(root, "cherry-pick", "side")
    logged("cherry-pick", wanted=1)
    git_in(root, "checkout", "-q", "-b", "replay", "side")
    (root / "h").write_text("y\n", encoding="utf-8")
    git_in(root, "add", "h")
    git_in(root, "commit", "-q", "-m", "replayed")
    logged("a commit to replay", wanted=1)
    git_in(root, "rebase", "-q", "main")
    logged("rebase", wanted=1)
    git_in(root, "checkout", "-q", "main")
    # a merge that stops on a conflict and is concluded by a commit
    for branch, text in (("one", "1\n"), ("two", "2\n")):
        git_in(root, "checkout", "-q", "-b", branch, "main")
        (root / "g").write_text(text, encoding="utf-8")
        git_in(root, "add", "g")
        git_in(root, "commit", "-q", "-m", branch)
        logged(f"commit {branch}", wanted=1)
    git_in(root, "merge", "one", check=False)  # stops on the conflict, makes no commit
    assert git_in(root, "ls-files", "--unmerged", session=None) != ""
    logged("a merge that stops on a conflict", wanted=0)
    (root / "g").write_text("both\n", encoding="utf-8")
    git_in(root, "add", "g")
    git_in(root, "commit", "-q", "--no-edit")
    logged("the commit that concludes a merge", wanted=1)
    git_in(root, "checkout", "-q", "main")
    git_in(root, "checkout", "-q", "-b", "n1")
    git_in(root, "commit", "--allow-empty", "-q", "-m", "n1")
    logged("a commit to merge", wanted=1)
    git_in(root, "checkout", "-q", "main")
    git_in(root, "commit", "--allow-empty", "-q", "-m", "m2")
    logged("a commit on main again", wanted=1)
    git_in(root, "merge", "--no-ff", "-q", "-m", "merged", "n1")
    logged("merge --no-ff", wanted=1, event="merge")
    # a fast-forward fires post-merge and makes no commit
    git_in(root, "checkout", "-q", "-b", "ahead")
    git_in(root, "commit", "--allow-empty", "-q", "-m", "ahead")
    logged("a commit before a fast-forward", wanted=1)
    git_in(root, "checkout", "-q", "main")
    git_in(root, "merge", "--ff-only", "-q", "ahead")
    logged("merge --ff-only", wanted=0)
    upstream = tmp_path / "upstream"
    git_in(tmp_path, "clone", "-q", str(root), str(upstream))
    git_in(upstream, "commit", "--allow-empty", "-q", "-m", "upstream", session=None)
    git_in(root, "pull", "-q", "--ff-only", str(upstream), "main")
    logged("pull --ff-only", wanted=0)
    # a fast-forward onto a branch whose tip is a merge commit: HEAD has a second parent, so only the
    # reflog's word "Fast-forward" keeps it out of the log
    far = tmp_path / "far"
    git_in(tmp_path, "clone", "-q", str(root), str(far))
    for base, name in ((root, "mb"), (far, "fb")):
        who = S1 if base == root else None
        git_in(base, "checkout", "-q", "-b", name, "main", session=who)
        git_in(base, "commit", "--allow-empty", "-q", "-m", f"{name}1", session=who)
        git_in(base, "checkout", "-q", "-b", f"{name}2", "main", session=who)
        git_in(base, "commit", "--allow-empty", "-q", "-m", f"{name}2", session=who)
        git_in(base, "checkout", "-q", name, session=who)
        git_in(base, "merge", "--no-ff", "-q", "-m", f"{name} merged", f"{name}2", session=who)
    assert len(log_lines(clone, "commits.jsonl")) == seen["count"] + 3  # two commits and the merge, logged
    seen["count"] += 3
    git_in(root, "checkout", "-q", "main")
    old_main = git_in(root, "rev-parse", "main", session=None)
    git_in(root, "merge", "--ff-only", "-q", "mb")
    assert git_in(root, "rev-parse", "HEAD^2", session=None)  # the tip is a merge commit
    logged("merge --ff-only onto a merge commit", wanted=0)
    git_in(far, "checkout", "-q", "main", session=None)
    git_in(far, "merge", "--ff-only", "-q", "fb", session=None)
    git_in(root, "checkout", "-q", "-b", "behind", old_main)
    git_in(root, "pull", "-q", "--ff-only", str(far), "fb")
    assert git_in(root, "rev-parse", "HEAD^2", session=None)
    logged("pull --ff-only onto a merge commit", wanted=0)
    git_in(root, "checkout", "-q", "main")
    # no variable: the commit is logged, with an empty session
    git_in(root, "commit", "--allow-empty", "-q", "-m", "by hand", session=None)
    logged("no variable", wanted=1, session="")
    # a linked worktree logs into the clone's own file
    worktree = tmp_path / "wt"
    git_in(root, "worktree", "add", "-q", str(worktree), "-b", "wtb")
    git_in(worktree, "commit", "--allow-empty", "-q", "-m", "in the worktree", session=S2)
    lines = log_lines(clone, "commits.jsonl")
    assert len(lines) == seen["count"] + 1
    assert lines[-1]["session"] == S2 and lines[-1]["sha"] == git_in(worktree, "rev-parse", "HEAD")
    assert not (worktree / ".git").is_dir() and not (worktree / "const-change-cost").exists()
    stamps = [int(str(line["ms"])) for line in lines]
    assert stamps == sorted(stamps) and started <= stamps[0] <= stamps[-1] <= int(
        datetime.now(UTC).timestamp() * 1000
    )


@item(
    24,
    "the hooks file: three handlers in exec form, integer timeouts, async on two, no matcher, no other event",
)
def test_hooks_file() -> None:
    text = (PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8")
    hooks = json.loads(text)
    start_handler = {
        "type": "command",
        "command": "sh",
        "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh"],
        "timeout": 30,
    }
    count_all = {
        "type": "command",
        "command": "sh",
        "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/count-costs.sh", "--all"],
        "async": True,
        "timeout": 600,
    }
    count_session = {
        "type": "command",
        "command": "sh",
        "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/count-costs.sh", "--session"],
        "async": True,
        "timeout": 600,
    }
    assert hooks == {
        "hooks": {
            "SessionStart": [{"hooks": [start_handler, count_all]}],
            "Stop": [{"hooks": [count_session]}],
        }
    }
    handlers = [h for groups in hooks["hooks"].values() for group in groups for h in group["hooks"]]
    assert len(handlers) == 3 and "matcher" not in text
    for handler in handlers:
        assert type(handler["timeout"]) is int and handler["command"] == "sh"
        assert (PLUGIN / handler["args"][0].replace("${CLAUDE_PLUGIN_ROOT}/", "")).is_file()
    assert [h for h in handlers if h.get("async")] == [count_all, count_session]


@item(
    31,
    "a commit whose session has no logged start gets no count, even where another session's transcript"
    " holds its records",
)
def test_no_start_is_made_up(clone: Clone) -> None:
    """S3 committed, but its start was never logged. Its records stand inside the parent's transcript, as a
    fork's copies do. No start is made up from them: the commit is never counted."""
    with clone.transcript(S1).open("a", encoding="utf-8") as handle:
        handle.write(user_record(S3, 6))
        handle.write(user_record(S3, 14))
    clone.start(S1, 0)
    clone.commit("a" * 40, 13, S3)
    done = clone.count("--all")
    assert (done.code, closing(done)) == (0, counted_line(0, 0, 0, 1)), done.stderr
    assert clone.kept() == []
    commits, _ = logs.read_commits(clone.folder)
    starts, _ = logs.read_starts(clone.folder)
    tally = counting.Tally()
    counting.count_session(
        S3, commits, [line for line in starts if line.session == S3], set(), None, clone.folder, tally
    )
    assert tally.not_counted == [NotCounted("a" * 40, Reason.NO_START, S3)]


# ------------------------------------------------------------------ T15 to T18: the report and its exports

NOT_COUNTED = {
    "nolog": "no line in the commit log: made before setup-commit-log.sh ran, by a tool that runs no git"
    " hook, or on a forge",
    "nosession": "the commit log names no session: made outside Claude Code",
    "nostart": f"session {S3} has no start in the start log: it started before the plugin was enabled, or in"
    " another folder",
    "notranscript": f"no transcript of session {S4} stands at {{gone}}: swept by Claude Code's cleanup, or"
    " never kept",
    "waiting": f"its window is not complete: no record of session {S1} is dated after the commit yet; a later"
    " pass counts it",
}
F1 = (
    "input 1,000, output 200, cache write 300, cache read 4,500, total 6,000 tokens; $0.01 at list price;"
    f" 3 replies; models: {SONNET} 5,000, {OPUS} 1,000; compactions: 0; unpriced: none"
)
F3 = (
    "input 123,456, output 2,000, cache write 0, cache read 0, total 125,456 tokens; at least $0.40 at list"
    " price; 2 replies; models: claude-imaginary-9 125,456; compactions: 1; unpriced: claude-imaginary-9"
)
FT = (
    "input 124,456, output 2,200, cache write 300, cache read 4,500, total 131,456 tokens; at least $0.42 at"
    f" list price; 5 replies; models: claude-imaginary-9 125,456, {SONNET} 5,000, {OPUS} 1,000;"
    " compactions: 1; unpriced: claude-imaginary-9"
)
LIST_PRICE = "tokens counted by ccusage 20.0.48, cost at its list price"


def kept_line(sha: str, session: str, figures: Mapping[str, object]) -> dict[str, object]:
    return {"sha": sha, "session": session, **figures, "ccusage": PIN, "counted_ms": at(20)}


COUNTS_OF_ONE: dict[str, object] = {
    "input": 1000,
    "output": 200,
    "cache_write": 300,
    "cache_read": 4500,
    "total": 6000,
    "cost": 0.012213,
    "replies": 3,
    "models": {SONNET: 5000, OPUS: 1000},
    "compactions": 0,
    "unpriced": [],
}
COUNTS_OF_THREE: dict[str, object] = {
    "input": 123456,
    "output": 2000,
    "cache_write": 0,
    "cache_read": 0,
    "total": 125456,
    "cost": 0.404,
    "replies": 2,
    "models": {"claude-imaginary-9": 125456},
    "compactions": 1,
    "unpriced": ["claude-imaginary-9"],
}


def report_rig(parent: Path) -> tuple[Clone, dict[str, str]]:
    """A clone of eight real commits: a base, two counted by hand-written kept lines, and one for each reason
    a commit has none. The report reads the file of counts, so nothing is counted here and no ccusage runs."""
    clone = bare_clone(parent)
    shas: dict[str, str] = {}
    for name in ("base", "counted", "nolog", "unpriced", "nosession", "nostart", "notranscript", "waiting"):
        git_in(clone.root, "commit", "--allow-empty", "-m", name, session=None)
        shas[name] = git_in(clone.root, "rev-parse", "HEAD", session=None)
    git_in(clone.root, "tag", "base", shas["base"], session=None)
    clone.start(S1, 0)
    clone.start(S4, 0, path=clone.projects / "gone.jsonl")
    for name, session in (
        ("counted", S1),
        ("unpriced", S1),
        ("nosession", ""),
        ("nostart", S3),
        ("notranscript", S4),
        ("waiting", S1),
    ):
        clone.commit(shas[name], 13, session)
    clone.append_line("counts.jsonl", kept_line(shas["counted"], S1, COUNTS_OF_ONE))
    clone.append_line("counts.jsonl", kept_line(shas["unpriced"], S1, COUNTS_OF_THREE))
    return clone, shas


def short(shas: Mapping[str, str], name: str) -> str:
    return shas[name][:12]


def reason_lines(clone: Clone, shas: Mapping[str, str], names: Sequence[str]) -> list[str]:
    gone = str(clone.projects / "gone.jsonl")
    return [
        f"{short(shas, name)}: not counted — {NOT_COUNTED[name].replace('{gone}', gone)}" for name in names
    ]


UNCOUNTED = ("nolog", "nosession", "nostart", "notranscript", "waiting")


def run_report(
    clone: Clone, *args: str, path: Path | None = None, env: Mapping[str, str] | None = None
) -> Result:
    extra = {"PATH": str(path)} if path is not None else {}
    return clone.count(*args, harness=HR, env={**extra, **(env or {})})


@item(15, "the report with no range and with one: J9, J10 and J12, the list price named")
def test_report(tmp_path: Path) -> None:
    clone, shas = report_rig(tmp_path)
    one, three = short(shas, "counted"), short(shas, "unpriced")
    everything = run_report(clone)
    assert everything.code == 0 and everything.stderr == "", everything.stderr
    assert everything.stdout.splitlines() == [
        f"CHANGE-COST: 2 commit(s) counted in this clone — {LIST_PRICE}",
        f"{one}: {F1}",
        f"{three}: {F3}",
    ]
    ranged = run_report(clone, "base..HEAD")
    assert ranged.code == 0 and ranged.stderr == "", ranged.stderr
    assert ranged.stdout.splitlines() == [
        f"CHANGE-COST: 7 commit(s) of base..HEAD, 2 counted, 5 not counted — {LIST_PRICE}",
        f"{one}: {F1}",
        *reason_lines(clone, shas, ["nolog"]),
        f"{three}: {F3}",
        *reason_lines(clone, shas, UNCOUNTED[1:]),
        f"total, 2 counted commit(s): {FT}",
    ]
    only = run_report(clone, f"{shas['base']}..{shas['counted']}")
    assert only.stdout.splitlines() == [
        f"CHANGE-COST: 1 commit(s) of {shas['base']}..{shas['counted']}, 1 counted, 0 not counted —"
        f" {LIST_PRICE}",
        f"{one}: {F1}",
        f"total, 1 counted commit(s): "
        "input 1,000, output 200, cache write 300, cache read 4,500, total 6,000 tokens; $0.01 at list price;"
        f" 3 replies; models: {SONNET} 5,000, {OPUS} 1,000; compactions: 0; unpriced: none",
    ]
    nothing = run_report(clone, f"{shas['counted']}..{shas['counted']}")
    assert nothing.stdout.splitlines() == [
        f"CHANGE-COST: 0 commit(s) of {shas['counted']}..{shas['counted']}, 0 counted, 0 not counted —"
        f" {LIST_PRICE}",
        "total, 0 counted commit(s): input 0, output 0, cache write 0, cache read 0, total 0 tokens; $0.00 at"
        " list price; 0 replies; models: none; compactions: 0; unpriced: none",
    ]
    with (clone.folder / "counts.jsonl").open("a", encoding="utf-8") as handle:
        handle.write("{\n")
    unreadable = run_report(clone)
    assert unreadable.code == 0 and unreadable.stdout == everything.stdout
    assert unreadable.stderr.splitlines() == [
        f"note: a log line cannot be read and is left out: {clone.folder}/counts.jsonl line 3: it is not JSON"
    ]


def trailer_lines(shas: Mapping[str, str]) -> list[str]:
    return [
        f"Change-Cost-Commit: {short(shas, 'counted')} {F1}",
        f"Change-Cost-Commit: {short(shas, 'unpriced')} {F3}",
        f"Change-Cost: 2 of 7 commit(s) counted; {FT}",
    ]


@item(16, "--trailer: J13 in the range's order with the total; git interpret-trailers reads every line")
def test_trailer(tmp_path: Path) -> None:
    clone, shas = report_rig(tmp_path)
    done = run_report(clone, "--trailer", "base..HEAD")
    assert done.code == 0 and done.stderr == "", done.stderr
    assert done.stdout.splitlines() == trailer_lines(shas)
    parsed = subprocess.run(
        ["git", "interpret-trailers", "--parse"],
        input=f"Merge branch 'work'\n\n{done.stdout}",
        cwd=clone.root,
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, **GIT_ENV},
    )
    assert parsed.stdout.splitlines() == trailer_lines(shas)
    half = run_report(clone, "--trailer", f"{shas['base']}..{shas['nolog']}")
    assert half.stdout.splitlines() == [
        f"Change-Cost-Commit: {short(shas, 'counted')} {F1}",
        "Change-Cost: 1 of 2 commit(s) counted; "
        "input 1,000, output 200, cache write 300, cache read 4,500, total 6,000 tokens; $0.01 at list price;"
        f" 3 replies; models: {SONNET} 5,000, {OPUS} 1,000; compactions: 0; unpriced: none",
    ]


FAKE_GH = (
    'echo "$*" >> "$GH_LOG"\n'
    'case "$1 $2" in\n'
    '  "pr view")\n'
    '    if [ -n "$GH_NO_PR" ]; then echo "no pull requests found for branch" >&2; exit 1; fi\n'
    '    /bin/cat "$GH_VIEW" ;;\n'
    '  "pr edit")\n'
    '    /bin/cat > "$GH_BODY"\n'
    '    if [ -n "$GH_FAIL" ]; then echo "$GH_FAIL" >&2; exit 1; fi ;;\n'
    "esac\n"
)


def tool_folder(parent: Path, gh: str | None = None) -> Path:
    """A PATH of `sh`, `dirname`, `git` and `python3`, and a fake `gh` when the test gives one."""
    folder = parent / "bin"
    folder.mkdir(parents=True)
    for tool in ("sh", "dirname", "git"):
        found = shutil.which(tool)
        assert found, tool
        os.symlink(found, folder / tool)
    os.symlink(os.path.realpath(sys.executable), folder / "python3")
    if gh is not None:
        fake_program(folder / "gh", gh)
    return folder


def block_of_the_rig(clone: Clone, shas: Mapping[str, str], upto: str | None = None) -> list[str]:
    one, three = short(shas, "counted"), short(shas, "unpriced")
    if upto == "nolog":
        return [
            "<!-- const-change-cost -->",
            f"**Change cost** — {LIST_PRICE}",
            "",
            "| commit | input | output | cache write | cache read | total | cost | replies | models |"
            " compactions | unpriced |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
            f"| `{one}` | 1,000 | 200 | 300 | 4,500 | 6,000 | $0.01 | 3 | {SONNET} 5,000, {OPUS} 1,000 | 0 |"
            " none |",
            f"| total, 1 of 2 | 1,000 | 200 | 300 | 4,500 | 6,000 | $0.01 | 3 | {SONNET} 5,000, {OPUS}"
            " 1,000 | 0 | none |",
            "",
            *(f"- {line}" for line in reason_lines(clone, shas, ["nolog"])),
            "<!-- /const-change-cost -->",
        ]
    return [
        "<!-- const-change-cost -->",
        f"**Change cost** — {LIST_PRICE}",
        "",
        "| commit | input | output | cache write | cache read | total | cost | replies | models |"
        " compactions | unpriced |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
        f"| `{one}` | 1,000 | 200 | 300 | 4,500 | 6,000 | $0.01 | 3 | {SONNET} 5,000, {OPUS} 1,000 | 0 |"
        " none |",
        f"| `{three}` | 123,456 | 2,000 | 0 | 0 | 125,456 | at least $0.40 | 2 | claude-imaginary-9"
        " 125,456 | 1 | claude-imaginary-9 |",
        f"| total, 2 of 7 | 124,456 | 2,200 | 300 | 4,500 | 131,456 | at least $0.42 | 5 | claude-imaginary-9"
        f" 125,456, {SONNET} 5,000, {OPUS} 1,000 | 1 | claude-imaginary-9 |",
        "",
        *(f"- {line}" for line in reason_lines(clone, shas, UNCOUNTED)),
        "<!-- /const-change-cost -->",
    ]


@item(
    17,
    "--pr: no gh prints the block and J15.2; a fake gh gets it between its markers, J15.1, a rerun replaces"
    " it; a failing gh is J6.13",
)
def test_pr(tmp_path: Path) -> None:
    clone, shas = report_rig(tmp_path / "rig")
    block = block_of_the_rig(clone, shas)
    j15_2 = "note: gh found no pull request of this branch — the block above is printed for a person to paste"
    # no gh on PATH: the block is printed, nothing is changed
    without = run_report(clone, "--pr", "base..HEAD", path=tool_folder(tmp_path / "none"))
    assert without.code == 0 and without.stderr == "", without.stderr
    assert without.stdout.splitlines() == [*block, j15_2]
    # a gh that finds no pull request: asked once, nothing written
    log, body, view = tmp_path / "gh.log", tmp_path / "body.txt", tmp_path / "view.json"
    env = {"GH_LOG": str(log), "GH_BODY": str(body), "GH_VIEW": str(view)}
    view.write_text(json.dumps({"number": 7, "body": "Description.\n"}), encoding="utf-8")
    tools = tool_folder(tmp_path / "fake", FAKE_GH)
    absent = run_report(clone, "--pr", "base..HEAD", path=tools, env={**env, "GH_NO_PR": "1"})
    assert absent.code == 0 and absent.stdout.splitlines() == [*block, j15_2], absent.stderr
    assert log.read_text(encoding="utf-8").splitlines() == ["pr view --json number,body"]
    assert not body.exists()
    # a gh that finds the pull request: the block is added after the description
    log.unlink()
    written = run_report(clone, "--pr", "base..HEAD", path=tools, env=env)
    assert written.code == 0 and written.stderr == "", written.stderr
    assert written.stdout.splitlines() == [
        "PR: the block was written into the description of pull request #7 through gh"
    ]
    assert log.read_text(encoding="utf-8").splitlines() == [
        "pr view --json number,body",
        "pr edit 7 --body-file -",
    ]
    first = "Description.\n\n" + "\n".join(block) + "\n"
    assert body.read_text(encoding="utf-8") == first
    # a rerun replaces the block between its markers and keeps the rest of the description
    view.write_text(json.dumps({"number": 7, "body": first + "\nFooter.\n"}), encoding="utf-8")
    again = run_report(clone, "--pr", f"{shas['base']}..{shas['nolog']}", path=tools, env=env)
    assert again.code == 0, again.stderr
    assert body.read_text(encoding="utf-8") == (
        "Description.\n\n" + "\n".join(block_of_the_rig(clone, shas, "nolog")) + "\n\nFooter.\n"
    )
    assert body.read_text(encoding="utf-8").count("<!-- const-change-cost -->") == 1
    # a gh that fails to write: the block is printed above J6.13, and exit 1
    failed = run_report(
        clone, "--pr", "base..HEAD", path=tools, env={**env, "GH_FAIL": "HTTP 401: Bad credentials"}
    )
    assert failed.code == 1 and failed.stdout.splitlines() == block
    assert failed.stderr.splitlines() == [
        "BROKEN: gh could not write the description of pull request #7: HTTP 401: Bad credentials — fix:"
        " repair what gh names, such as its login, or paste the block printed above into the description",
        REPORT_CLOSING,
    ]


@item(18, "--notes: one note per counted commit under refs/notes/change-cost, the same figures, J16, no push")
def test_notes(tmp_path: Path) -> None:
    clone, shas = report_rig(tmp_path / "rig")
    bare = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, env={**os.environ, **GIT_ENV})
    git_in(clone.root, "remote", "add", "origin", str(bare), session=None)
    git_in(clone.root, "config", "push.default", "matching", session=None)
    done = run_report(clone, "--notes", "base..HEAD", env=AUTHOR)
    assert done.code == 0 and done.stderr == "", done.stderr
    assert done.stdout.splitlines() == [
        "NOTES: 2 note(s) written under refs/notes/change-cost — nothing is pushed; push them with git push"
        " <remote> refs/notes/change-cost"
    ]
    ref = "refs/notes/change-cost"
    noted = git_in(clone.root, "notes", "--ref", ref, "list", session=None).splitlines()
    assert sorted(line.split()[1] for line in noted) == sorted([shas["counted"], shas["unpriced"]])
    assert git_in(clone.root, "notes", "--ref", ref, "show", shas["counted"], session=None) == (
        f"{short(shas, 'counted')}: {F1}"
    )
    assert git_in(clone.root, "notes", "--ref", ref, "show", shas["unpriced"], session=None) == (
        f"{short(shas, 'unpriced')}: {F3}"
    )
    # run again: the notes are replaced, not doubled
    again = run_report(clone, "--notes", "base..HEAD", env=AUTHOR)
    assert again.code == 0 and again.stdout == done.stdout
    assert len(git_in(clone.root, "notes", "--ref", ref, "list", session=None).splitlines()) == 2
    # nothing reached the bare remote, whose refs stay empty
    assert git_in(clone.root, "ls-remote", "origin", session=None) == ""
    refs = subprocess.run(
        ["git", "--git-dir", str(bare), "for-each-ref"], capture_output=True, text=True, check=True
    )
    assert refs.stdout == ""


# ------------------------------------------------------------------ T19, T23: failures typed by hand


def ccusage_failures(tmp_path: Path) -> list[str]:
    """J6.1 to J6.6 of the count, each typed by hand: the failures of finding, installing and running"
    " ccusage."""
    failures: list[str] = []

    def check(label: str, result: Result, first: str) -> None:
        if result.code != 1 or result.stderr.splitlines() != [first, CLOSING]:
            failures.append(f"{label}: exit {result.code}: {result.stderr.strip()[:500]}")

    rig = Rig.make(tmp_path / "no-node", node=False, npm=FAKE_NPM)
    check(
        "J6.1",
        rig.run(),
        broken_line(
            "const-change-cost needs node on PATH, which runs ccusage",
            "install Node.js (https://nodejs.org/en/download)",
        ),
    )
    rig = Rig.make(tmp_path / "no-npm")
    data = rig.clone.data
    check(
        "J6.2",
        rig.run(),
        broken_line(
            f"const-change-cost needs npm on PATH to install the pinned ccusage into {data}",
            "install Node.js, which brings npm (https://nodejs.org/en/download), then start a session again",
        ),
    )
    rig = Rig.make(tmp_path / "none")
    check(
        "J6.3",
        rig.run(data=False),
        broken_line(
            "const-change-cost needs ccusage 20.0.48, which its package-lock.json pins, and found none"
            f" under {rig.root}"
            " or in the plugin's data folder",
            "start a Claude Code session in this project, whose start installs it, or run npm ci"
            " --ignore-scripts"
            f" in {rig.root}",
        ),
    )
    rig = Rig.make(tmp_path / "other")
    install_script(rig.root, "20.0.47", FAKE_REPORT)
    check(
        "J6.4",
        rig.run(data=False),
        broken_line(
            f"const-change-cost needs ccusage 20.0.48 and found 20.0.47 under {rig.root}",
            "start a Claude Code session in this project, whose start installs the pinned one, or run npm ci"
            f" --ignore-scripts in {rig.root}",
        ),
    )
    rig = Rig.make(tmp_path / "npm-fails", npm='echo "npm error network down" >&2\nexit 1\n')
    check(
        "J6.5",
        rig.run(),
        broken_line(
            f"npm could not install the pinned ccusage into {rig.clone.data}: npm error network down",
            "repair what npm names — the network, the registry, the folder's rights — then start a session"
            " again",
        ),
    )
    assert not (rig.clone.data / "package-lock.json").exists(), "a failed install keeps no lockfile copy"
    where = "this is a defect of the count or of the installed ccusage, not of the repository; run"
    for label, body, what in (
        ("J6.6 exit", 'echo "boom" >&2\nexit 3\n', "exit 3: boom"),
        ("J6.6 output", "echo 'not json'\n", "output that is no session report: it is not JSON"),
        (
            "J6.6 shape",
            "echo '{\"entries\": 1}'\n",
            "output that is no session report: it has no entries list",
        ),
    ):
        rig = Rig.make(tmp_path / label.replace(" ", "-"))
        install_script(rig.root, PIN, body)
        launcher = rig.root / "node_modules" / ".bin" / "ccusage"
        check(
            label,
            rig.run(data=False),
            broken_line(
                f"ccusage gave no count for session {S1}: {what}",
                f"{where} {launcher} --version and report both to whoever maintains the plugin",
            ),
        )
    assert messages.j6_5_npm_failed("/d", messages.detail_npm_silent()).render() == (
        "BROKEN: npm could not install the pinned ccusage into /d: no answer in 120 s — fix: repair what"
        " npm names"
        f" — the network, the registry, the folder's rights — then start a session again — {CLAUSE}"
    )
    assert messages.detail_ccusage_silent() == "no answer in 60 s"
    assert CommitLine("a", 1, "s", "commit") == logs.parse_commit(
        {"sha": "a", "ms": 1, "session": "s", "event": "commit"}
    )
    assert StartLine("s", 1, "startup", "/t") == logs.parse_start(
        {"session": "s", "ms": 1, "source": "startup", "transcript_path": "/t"}
    )
    return failures
