"""The mover's three acts. Each rewrites files and then hands over to the scan: the rewrite is
an assist, and the proof that no reference is left broken is the gate's own check of the
whole tree, whose verdict is the act's exit code."""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from const_gate.dials import load_dials
from const_gate.errors import ConfigurationFailure
from const_gate.output import Output
from const_gate.pipeline import ScanTarget
from const_gate.repository import first_line, git, list_markdown, read_text, repo_root
from const_gate.territory import Matcher

from . import dials as own_dials
from . import messages, modes, repair
from .mentions import other_files
from .model import Ids
from .repair import Rewritten


@dataclass(frozen=True, slots=True)
class Request:
    """What the command line asked for: `ids`, or a move from `old` to `new` — made now, or
    `by_hand` already."""

    ids: bool
    by_hand: bool
    old: str
    new: str


def act(output: Output, request: Request) -> int:
    root = repo_root(Path.cwd())
    if root is None:
        raise ConfigurationFailure(messages.v5_outside(str(Path.cwd())))
    shared_dials = load_dials(root)
    if shared_dials is None:
        raise ConfigurationFailure(messages.v5_no_dials(str(root)))
    dials = own_dials.parse(shared_dials.own)
    if request.ids:
        old = new = ""
    else:
        old, new = _within(root, request.old), _within(root, request.new)
        _refuse_what_cannot_move(root, old, new, request.by_hand)
        if not request.by_hand:
            (root / new).parent.mkdir(parents=True, exist_ok=True)
            moved = git(["mv", "--", old, new], cwd=root)
            if moved.returncode != 0:
                raise ConfigurationFailure(messages.v5_git_mv(first_line(moved.stderr)))
        output.out(messages.v1_moved(old, new))
    with Matcher() as matcher:  # the documents the gate covers are the documents a move repairs
        target = ScanTarget(root, shared_dials)
        covered = modes.covered_documents(matcher, dials, target, list_markdown(root)) or []
    texts = {rel: text for rel in covered if (text := read_text(root, rel)) is not None}
    files = links = 0
    ids = modes.ids_of(texts) if request.ids else None
    for rel, text in texts.items():
        done = _repair(rel, text, old, new, ids)
        if done.links:
            (root / rel).write_text(done.text, encoding="utf-8")
            output.out(messages.v2_rewrote(rel, done.links))
            files, links = files + 1, links + done.links
    listed = 0 if request.ids else _list_mentions(output, root, covered, old, new)
    output.out(messages.v4_count(files, links, listed))
    return modes.scan_mode(output, root)


def _repair(rel: str, text: str, old: str, new: str, ids: Ids | None) -> Rewritten:
    if ids is not None:
        return repair.id_links(rel, text, ids)
    if rel == new:  # the moved document: its links were written where it lay before
        return repair.own_links(old, new, text)
    return repair.inbound(rel, text, old, new)


def _list_mentions(output: Output, root: Path, covered: Sequence[str], old: str, new: str) -> int:
    listed = 0
    for rel in [*covered, *other_files(root)]:
        if rel == new:
            continue
        text = read_text(root, rel)
        for mention in repair.mentions(text or "", repair.names_of(rel, old)):
            output.out(messages.v3_mention(rel, mention.line, mention.text))
            listed += 1
    return listed


def _within(root: Path, given: str) -> str:
    path = Path(os.path.abspath(given))
    parent = (
        Path(os.path.realpath(path.parent)) / path.name
    )  # the file itself may be a link, or not there yet
    try:
        return parent.relative_to(Path(os.path.realpath(root))).as_posix()
    except ValueError as outside:
        raise ConfigurationFailure(messages.v5_outside(given)) from outside


def _refuse_what_cannot_move(root: Path, old: str, new: str, by_hand: bool) -> None:
    if old == new:
        raise ConfigurationFailure(messages.v5_same(old))
    if by_hand:
        if (root / old).exists() or not (root / new).is_file():
            raise ConfigurationFailure(messages.v5_not_moved(old, new))
        return
    listed = git(["ls-files", "--error-unmatch", "--", old], cwd=root)
    if listed.returncode != 0 or not (root / old).is_file():
        raise ConfigurationFailure(messages.v5_not_listed(old))
    if (root / new).exists():
        raise ConfigurationFailure(messages.v5_target_exists(new))
