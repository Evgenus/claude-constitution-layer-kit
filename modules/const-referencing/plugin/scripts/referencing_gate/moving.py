"""The mover's three acts. Each rewrites files and then hands over to the scan: the rewrite is
an assist, and the proof that no reference is left broken is the gate's own check of the
whole tree, whose verdict is the act's exit code."""

from __future__ import annotations

import os
import posixpath
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from constitution_layer_kit import pipeline
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.model import SharedKey
from constitution_layer_kit.output import Output
from constitution_layer_kit.pipeline import ScanTarget
from constitution_layer_kit.repository import (
    first_line,
    git,
    is_markdown,
    list_markdown,
    read_text,
    repo_root,
)
from constitution_layer_kit.territory import Matcher

from . import dials as own_dials
from . import lychee, messages, modes, repair
from .closing import Closing
from .mentions import other_files
from .model import Ids, ReferencingDials
from .repair import Rewritten


@dataclass(frozen=True, slots=True)
class Request:
    """What the command line asked for: `ids`, or a move from `old` to `new` — made now, or
    `by_hand` already."""

    ids: bool
    by_hand: bool
    old: str
    new: str


def act(output: Output, request: Request, closing: Closing) -> int:
    """Everything that can refuse without moving is asked first — the repository, the dials and where
    the log goes, what is covered, the link checker the closing scan needs, the two paths. Then a move is
    made with git, and the act plans on the tree as git lists it after the move: it reads every document
    it reads, works out every rewrite and every mention in memory, and asks whether each document it will
    rewrite can be written. A failure of the plan moves the file back, so that a refusal finds the tree
    as it was. Only then is anything written. --moved and --ids move nothing: they plan on the tree as it
    stands."""
    root = repo_root(Path.cwd())
    if root is None:
        raise ConfigurationFailure(messages.v5_no_repository(str(Path.cwd())))
    shared_dials = load_dials(root)
    if shared_dials is None:
        raise ConfigurationFailure(messages.v5_no_dials(str(root)))
    pipeline.route_log(output, root, shared_dials)  # before any refusal: a refusal belongs in the log too
    dials = own_dials.parse(shared_dials.own)
    lychee.require()
    with Matcher() as matcher:  # the documents the gate covers are the documents a move repairs
        target = ScanTarget(root, shared_dials)
        before = modes.covered_documents(matcher, dials, target, list_markdown(root))
    if before is None:
        raise ConfigurationFailure(messages.v5_no_root_policy())
    old = new = ""
    made: list[Path] | None = None  # the folders the move made; None while nothing moved
    if not request.ids:
        if request.new.endswith(("/", os.sep)):
            raise ConfigurationFailure(messages.v5_names_a_directory(request.new))
        old, new = _within(root, request.old), _within(root, request.new)
        _refuse_what_cannot_move(root, old, new, request.by_hand)
        if not request.by_hand:
            made = _move(root, old, new, closing)
    try:
        plan = _plan(root, dials, target, old, new, request.ids, made)
    except BaseException:  # an interrupt too: the move is undone before anything leaves
        if made is not None:
            _move_back(root, old, new, made, closing)
        raise
    if not request.ids:
        output.out(messages.v1_moved(old, new))
    for rel in plan.left_alone:
        output.out(messages.v2_left_alone(rel))
    links = 0
    for rel, done in plan.rewrites:
        closing.changed = True
        with (root / rel).open("w", encoding="utf-8", newline="") as handle:  # line endings as they were
            handle.write(done.text)
        output.out(messages.v2_rewrote(rel, done.links))
        links += done.links
    for rel, line, text in plan.mentions:
        output.out(messages.v3_mention(rel, line, text))
    output.out(messages.v4_count(len(plan.rewrites), links, len(plan.mentions)))
    return modes.scan_mode(output, root)


@dataclass(frozen=True, slots=True)
class Plan:
    """What the act will write and say, worked out before it writes anything."""

    rewrites: list[tuple[str, Rewritten]]  # each document whose rewrite changes a link, with its new text
    left_alone: list[str]  # the documents that are not UTF-8 text
    mentions: list[tuple[str, int, str]]  # each place that names the old path outside a link


def _plan(
    root: Path,
    dials: ReferencingDials,
    target: ScanTarget,
    old: str,
    new: str,
    ids: bool,
    made: Sequence[Path] | None,
) -> Plan:
    """The act on the tree as it is now — after the move, for a move: the covered documents and the moved
    one, whose own links are repaired wherever it went, covered there or not. A document it cannot read is
    a refusal; a file that is not UTF-8 is left alone. A document whose rewrite changes a link is opened for
    writing and closed again, nothing written, and one the system will not open is a refusal. A refusal
    names the moved document where the move back will leave it."""

    moved = made is not None

    def shown(rel: str) -> str:
        return old if moved and rel == new else rel

    try:
        with Matcher() as matcher:
            covered = modes.covered_documents(matcher, dials, target, list_markdown(root)) or []
    except ConfigurationFailure as failure:
        # the root policy was found by the listing before the move: --moved and --ids meet C6 there, so a
        # root policy missing here can only be the doing of the move just made
        if failure.broken.key is SharedKey.C6:
            folder = _from_here(root, posixpath.dirname(new)) if made else ""  # git mv makes no folder
            route = (old, new, _from_here(root, old), _from_here(root, new), folder)
            raise ConfigurationFailure(messages.v5_takes_the_root_policy(*route)) from failure
        raise
    repaired = [*covered, *([new] if is_markdown(new) and new not in covered else [])]
    texts: dict[str, str] = {}
    left_alone: list[str] = []
    for rel in repaired:
        try:
            with (root / rel).open(encoding="utf-8", newline="") as handle:
                texts[rel] = handle.read()
        except UnicodeDecodeError:
            left_alone.append(rel)
        except OSError as exc:
            raise ConfigurationFailure(messages.v5_unreadable(shown(rel), _reason(exc))) from exc
    known = modes.ids_of(texts) if ids else None
    rewrites: list[tuple[str, Rewritten]] = []
    for rel, text in texts.items():
        done = _repair(rel, text, old, new, known)
        if not done.links:
            continue
        try:  # opened for writing and closed again: nothing is written, the content and its time stay
            os.close(os.open(root / rel, os.O_WRONLY | os.O_NONBLOCK))
        except OSError as exc:
            raise ConfigurationFailure(messages.v5_unwritable(shown(rel), _reason(exc))) from exc
        rewrites.append((rel, done))
    written = {rel: done.text for rel, done in rewrites}
    mentions = [] if ids else _mentions(root, covered, old, new, written)
    return Plan(rewrites, left_alone, mentions)


def _from_here(root: Path, rel: str) -> str:
    """A path from the repository's top as the user types it where they stand: from the working folder."""
    return os.path.relpath(os.path.realpath(root / rel), os.path.realpath(Path.cwd()))


def _reason(exc: OSError) -> str:
    return exc.strerror or type(exc).__name__


def _move(root: Path, old: str, new: str, closing: Closing) -> list[Path]:
    """git mv, into a directory made for it where none exists — and unmade again when git refuses. The
    folders it made are returned, deepest first, for the move back."""
    made: list[Path] = []
    parent = (root / new).parent
    while not parent.exists():
        made.append(parent)
        parent = parent.parent
    for directory in reversed(made):
        directory.mkdir()
    moved = git(["mv", "--", old, new], cwd=root)
    if moved.returncode != 0:
        for directory in made:
            directory.rmdir()
        raise ConfigurationFailure(messages.v5_git_mv(first_line(moved.stderr)))
    closing.changed = True
    return made


def _move_back(root: Path, old: str, new: str, made: Sequence[Path], closing: Closing) -> None:
    """The move undone: the file moved back with git, and the folders the move made removed again. When
    that fails, the closing line says where the file is."""
    back = git(["mv", "--", new, old], cwd=root)
    if back.returncode != 0:
        closing.stranded = messages.v4_move_back_failed(old, new, first_line(back.stderr))
        return
    for directory in made:
        try:
            directory.rmdir()
        except OSError as exc:
            where = directory.relative_to(root).as_posix()
            closing.stranded = messages.v4_folder_left(old, where, _reason(exc))
            return
    closing.changed = False
    closing.moved_back = old


def _repair(rel: str, text: str, old: str, new: str, ids: Ids | None) -> Rewritten:
    if ids is not None:
        return repair.id_links(rel, text, ids)
    if rel == new:  # the moved document: its links were written where it lay before
        return repair.own_links(old, new, text)
    return repair.inbound(rel, text, old, new)


def _mentions(
    root: Path, covered: Sequence[str], old: str, new: str, written: dict[str, str]
) -> list[tuple[str, int, str]]:
    """Every text file git lists is read for the old path: the covered documents, the Markdown
    files outside coverage, and the other files. A symbolic link outside coverage is not read. A document
    the act rewrites is read as it will be written."""
    known = set(covered)
    uncovered = [rel for rel in list_markdown(root) if rel not in known and not (root / rel).is_symlink()]
    found: list[tuple[str, int, str]] = []
    for rel in [*covered, *uncovered, *other_files(root)]:
        if rel == new:
            continue
        text = written[rel] if rel in written else read_text(root, rel)
        for mention in repair.mentions(text or "", repair.names_of(rel, old)):
            found.append((rel, mention.line, mention.text))
    return found


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
    _refuse_unmovable_source(root, old)
    if is_markdown(old) and not is_markdown(new):
        raise ConfigurationFailure(messages.v5_leaves_markdown(old, new))
    _refuse_blocked_target(root, old, new)


def _refuse_unmovable_source(root: Path, old: str) -> None:
    """The file to move is a file git lists, not a link."""
    listed = git(["ls-files", "--error-unmatch", "--", old], cwd=root)
    if listed.returncode != 0 or not (root / old).is_file():
        raise ConfigurationFailure(messages.v5_not_listed(old))
    if (root / old).is_symlink():
        raise ConfigurationFailure(messages.v5_is_a_link(old))


def _refuse_blocked_target(root: Path, old: str, new: str) -> None:
    """The new path is free — save the file itself under a name in another case — and its nearest
    existing ancestor is a directory."""
    # where the file system ignores case, a new name in another case "exists": it is the file itself
    renamed_in_case = (
        old.lower() == new.lower() and (root / new).exists() and (root / new).samefile(root / old)
    )
    if (root / new).exists() and not renamed_in_case:
        raise ConfigurationFailure(messages.v5_target_exists(new))
    for ancestor in (root / new).parents:
        if ancestor.exists():
            if not ancestor.is_dir():
                raise ConfigurationFailure(
                    messages.v5_parent_is_a_file(ancestor.relative_to(root).as_posix())
                )
            break
