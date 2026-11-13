"""The mover's three acts. Each rewrites files and then hands over to the scan: the rewrite is
an assist, and the proof that no reference is left broken is the gate's own check of the
whole tree, whose verdict is the act's exit code."""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from constitution_layer_kit import messages as shared_messages
from constitution_layer_kit import pipeline
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.envelope import id_of_text
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.index import build_index
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
    """Everything that can refuse is asked first — the repository, the dials and where the log
    goes, what is covered, the link checker the closing scan needs, the two paths, and whether every
    document the act reads can be read and every one it rewrites can be written — so that a refusal
    finds the tree as it was. Only then is anything moved or written."""
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
    if not request.ids:
        if request.new.endswith(("/", os.sep)):
            raise ConfigurationFailure(messages.v5_names_a_directory(request.new))
        old, new = _within(root, request.old), _within(root, request.new)
        _refuse_what_cannot_move(root, old, new, request.by_hand)
    planned = _planned(root, dials, target, before, old, new, request)
    _refuse_what_cannot_be_rewritten(root, planned, old, new, request.ids)
    if not request.ids:
        if not request.by_hand:
            _move(root, old, new, closing)
        output.out(messages.v1_moved(old, new))
    with Matcher() as matcher:  # asked again: the moved document lies elsewhere now
        covered = modes.covered_documents(matcher, dials, target, list_markdown(root)) or []
    # the moved document's own links are repaired wherever it went, covered there or not
    repaired = [*covered, *([new] if is_markdown(new) and new not in covered else [])]
    texts = {rel: text for rel in repaired if (text := _read(root, rel, output)) is not None}
    files = links = 0
    ids = modes.ids_of(texts) if request.ids else None
    for rel, text in texts.items():
        done = _repair(rel, text, old, new, ids)
        if done.links:
            closing.changed = True
            with (root / rel).open("w", encoding="utf-8", newline="") as handle:  # line endings as they were
                handle.write(done.text)
            output.out(messages.v2_rewrote(rel, done.links))
            files, links = files + 1, links + done.links
    listed = 0 if request.ids else _list_mentions(output, root, covered, old, new)
    output.out(messages.v4_count(files, links, listed))
    return modes.scan_mode(output, root)


def _planned(
    root: Path,
    dials: ReferencingDials,
    target: ScanTarget,
    covered: Sequence[str],
    old: str,
    new: str,
    request: Request,
) -> list[tuple[str, str]]:
    """The documents the act will read and may rewrite, each as the pair (where it lies now, where it
    will lie when it is read). For --ids and --moved nothing moves before the rewrites, so the pairs are
    the covered documents as they stand. For a move they are the documents covered in the tree as it will
    stand after the move, worked out before it. The moved document is read whenever its new path is
    Markdown, covered there or not — as the act reads it."""
    if request.ids or request.by_hand:
        after = list(covered)
        source = {rel: rel for rel in after}
    else:
        source = _paths_after(root, old, new)
        predicted = _covered_after(root, dials, target, source, old)
        if predicted is None:  # the root policy itself moves: no coverage can be read after it
            after = [new if rel == old else rel for rel in covered]
            source = {**{rel: rel for rel in covered}, new: old}
        else:
            after = predicted
    if is_markdown(new) and new not in after:
        after = [*after, new]
    return [(source.get(rel, old if rel == new else rel), rel) for rel in after]


def _paths_after(root: Path, old: str, new: str) -> dict[str, str]:
    """The Markdown paths the shared listing will give once the file has moved, each with the path that
    holds its text now. The listing keeps a path git lists that is a file, through any link: so the
    moved file goes from its old path to its new one, a link to the moved file drops out, since it will
    lead nowhere, and a link to the new path comes in, since it will lead to the moved file."""
    listed = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    if listed.returncode != 0:
        raise ConfigurationFailure(shared_messages.c12_ls_files(str(root), first_line(listed.stderr)))
    gone, coming = os.path.realpath(root / old), os.path.realpath(root / new)
    paths: dict[str, str] = {}
    for rel in os.fsdecode(listed.stdout).split("\0"):
        if not rel or not is_markdown(rel) or rel == old:
            continue
        real = os.path.realpath(root / rel)
        if real == gone:
            continue
        if real == coming:
            paths[rel] = old
        elif (root / rel).is_file():
            paths[rel] = rel
    if is_markdown(new):
        paths[new] = old
    return paths


def _covered_after(
    root: Path, dials: ReferencingDials, target: ScanTarget, paths: dict[str, str], old: str
) -> list[str] | None:
    """The covered documents of the tree after the move, by the rules the gate covers them by:
    the territories; under governed_only, also a policy's territory or the root policy's. A policy is a
    document in the root policy's territory that carries an id, the first by path for an id two carry,
    as the shared index finds them. None when the root policy itself is among the paths that move."""
    names = sorted(paths)
    with Matcher() as matcher:
        in_territory = sorted(matcher.match(dials.territories, names))
        if not dials.governed_only:
            return in_territory
        root_policy = target.dials.root_policy
        if root_policy is None or root_policy == old:
            return None
        index = build_index(root, target.dials, root_policy, matcher)  # the root as it stands, unmoved
        considered = sorted({*names, root_policy})
        in_root = matcher.match(index.root_territory, considered)
        claimed: set[str] = set()
        seen: set[str] = set()
        for path in sorted(in_root):
            text = read_text(root, paths.get(path, path))
            policy_id = id_of_text(text) if text is not None else None
            if policy_id is None or policy_id in seen:
                continue
            seen.add(policy_id)
            claimed.update(matcher.match(target.dials.territory_of(policy_id), considered))
    return [rel for rel in in_territory if rel in in_root or rel in claimed]


def _refuse_what_cannot_be_rewritten(
    root: Path, planned: Sequence[tuple[str, str]], old: str, new: str, ids: bool
) -> None:
    """Before anything moves or is written: a document the act must read cannot be read, or one it would
    rewrite cannot be written. Either would stop the act midway, with the tree half changed — the closing
    scan cannot read the first, and the rewrite fails on the second. A file that is not UTF-8 is no
    refusal: the act leaves it alone and says so."""
    texts: dict[tuple[str, str], str] = {}
    for now, after in planned:
        try:
            with (root / now).open(encoding="utf-8", newline="") as handle:
                texts[(now, after)] = handle.read()
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            raise ConfigurationFailure(messages.v5_unreadable(now, _reason(exc))) from exc
    known = modes.ids_of({after: text for (_, after), text in texts.items()}) if ids else None
    for (now, after), text in texts.items():
        if not _repair(after, text, old, new, known).links:
            continue
        try:  # opened for writing and closed again: nothing is written, the content and its time stay
            os.close(os.open(root / now, os.O_WRONLY | os.O_NONBLOCK))
        except OSError as exc:
            raise ConfigurationFailure(messages.v5_unwritable(now, _reason(exc))) from exc


def _reason(exc: OSError) -> str:
    return exc.strerror or type(exc).__name__


def _move(root: Path, old: str, new: str, closing: Closing) -> None:
    """git mv, into a directory made for it where none exists — and unmade again when git refuses."""
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


def _read(root: Path, rel: str, output: Output) -> str | None:
    """A document exactly as it is on disk: line endings kept, and no character replaced — a
    file that is not UTF-8 is left alone and said to be, since writing it back would damage it."""
    try:
        with (root / rel).open(encoding="utf-8", newline="") as handle:
            return handle.read()
    except UnicodeDecodeError:
        output.out(messages.v2_left_alone(rel))
    except OSError:
        pass
    return None


def _repair(rel: str, text: str, old: str, new: str, ids: Ids | None) -> Rewritten:
    if ids is not None:
        return repair.id_links(rel, text, ids)
    if rel == new:  # the moved document: its links were written where it lay before
        return repair.own_links(old, new, text)
    return repair.inbound(rel, text, old, new)


def _list_mentions(output: Output, root: Path, covered: Sequence[str], old: str, new: str) -> int:
    """Every text file git lists is read for the old path: the covered documents, the Markdown
    files outside coverage, and the other files. A symbolic link outside coverage is not read."""
    known = set(covered)
    uncovered = [rel for rel in list_markdown(root) if rel not in known and not (root / rel).is_symlink()]
    listed = 0
    for rel in [*covered, *uncovered, *other_files(root)]:
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
