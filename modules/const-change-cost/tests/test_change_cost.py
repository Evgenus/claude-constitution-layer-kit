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

S1 = "11111111-1111-4111-8111-111111111111"
S2 = "22222222-2222-4222-8222-222222222222"
S3 = "33333333-3333-4333-8333-333333333333"
S4 = "44444444-4444-4444-8444-444444444444"
SONNET = "claude-sonnet-4-5-20250929"
OPUS = "claude-opus-4-5-20251101"
BASE = datetime(2026, 11, 1, 10, 0, 0, tzinfo=UTC)
CLAUSE = "until then no commit is counted"
CLOSING = "BROKEN: the count could not run — no commit was counted"
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


@item(25, "the count's install-failure lines, C1, C2, C14 and C15, close with its own clause, then J4")
def test_install_failures(tmp_path: Path, clone: Clone) -> None:
    clone.start(S1, 0)
    tools = tmp_path / "tools"  # a PATH holding only sh, dirname and git: no python3
    tools.mkdir()
    for tool in ("sh", "dirname", "git"):
        found = shutil.which(tool)
        assert found, tool
        os.symlink(found, tools / tool)
    no_python = clone.count("--all", env={"PATH": str(tools)})
    assert no_python.code == 1
    assert no_python.stderr.splitlines() == [
        "BROKEN: const-change-cost needs python3 — fix: install Python 3.12 or newer"
        f" (https://www.python.org/downloads/) — {CLAUSE}",
        CLOSING,
    ]
    shadow = tmp_path / "shadow"  # PyYAML hidden: the shared C2, its clause this entry's
    shadow.mkdir()
    (shadow / "yaml.py").write_text("raise ImportError('simulated absence')\n", encoding="utf-8")
    no_yaml = clone.count("--all", env={"PYTHONPATH": str(shadow)})
    assert no_yaml.code == 1
    assert no_yaml.stderr.splitlines() == [
        "BROKEN: const-change-cost needs PyYAML — fix: run: python3 -m pip install -r"
        f" '{PLUGIN}/requirements.txt'"
        f" — {CLAUSE}",
        CLOSING,
    ]
    entry = SCRIPTS / "count-costs.py"  # the entry file run as an interpreter of 3.11 would run it
    lowered = (
        "import sys; sys.version_info = (3, 11, 0); path = sys.argv[1]; "
        "exec(compile(open(path).read(), path, 'exec'), {'__name__': '__main__', '__file__': path})"
    )
    old = H.run_gate("", command=[sys.executable, "-c", lowered, str(entry)], env=clone.environment())
    assert old.code == 1
    assert old.stderr.splitlines() == [
        "BROKEN: const-change-cost needs Python 3.12 or newer, found 3.11 — fix: install a current Python 3"
        f" (https://www.python.org/downloads/) and put it first on PATH — {CLAUSE}",
        CLOSING,
    ]
    no_package = H.run_gate(  # the harness's shared folder left out, and no site-packages
        "",
        args=["--all"],
        env={**clone.environment(), "PYTHONPATH": ""},
        command=[sys.executable, "-S", str(entry)],
        shared=False,
    )
    assert no_package.code == 1
    assert no_package.stderr.splitlines() == [
        "BROKEN: const-change-cost needs the Python package constitution-layer-kit 2.0.0 or a later 2.x"
        " release,"
        f" and python3 cannot import it — fix: install it for python3 as {PLUGIN}/INSTALL.md says — {CLAUSE}",
        CLOSING,
    ]


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
