"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code. The hook answers a Stop: it judges the working tree of the repository the session's
directory lies in, and holds its report while the event lists an agent of the session that still
runs. The scan judges a range of commits against the coverage map."""

from __future__ import annotations

import io
from pathlib import Path
from typing import TextIO

from constitution_layer_kit import cli, pipeline
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.model import STOP
from constitution_layer_kit.output import Output
from constitution_layer_kit.pipeline import ScanTarget, Skip
from constitution_layer_kit.territory import Matcher

from . import checks, history, messages
from . import dials as own_dials
from .model import Declaration, Range, TaskCloseDials

SINCE, CHANGE, BODY_FLAG = "--since", "--change", "--body"


def hook_mode(output: Output, stdin: TextIO) -> int:
    payload = stdin.read()  # read once: the shared reader takes the event, the module its task list
    target = pipeline.locate_event(output, io.StringIO(payload))
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    own_dials.parse(target.dials.own)  # validated at each read, in every mode
    if target.event_name != STOP:
        raise ConfigurationFailure(messages.c12_not_wired(target.event_name))
    lines = history.status_lines(target.root)
    if not lines:
        return pipeline.green_event(output, messages.g1_clean())
    if target.stop_hook_active:
        return pipeline.green_event(output, messages.g1_second_stop(len(lines)))
    running = checks.agents_running(payload)
    if running:  # their files may be among the dirty ones, and they commit their own: the report waits
        return pipeline.green_event(output, messages.g1_held(len(lines), running))
    return pipeline.report_hook(
        output,
        [checks.tree_finding(lines)],
        (),
        "",
        target.dials.severity,
        event_name=STOP,
        count=messages.f9_count_hook(len(lines)),
    )


def scan_mode(output: Output, start: Path) -> int:
    return scan_with(output, start, {SINCE: None, CHANGE: None, BODY_FLAG: None})


def scan_with(output: Output, start: Path, values: cli.Values) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    since, change, body = values.get(SINCE), values.get(CHANGE), values.get(BODY_FLAG)
    if since is not None and change is not None:
        raise ConfigurationFailure(messages.c12_since_and_change())
    body_text = _read_body(body) if body is not None else ""
    with Matcher() as matcher:
        notes = checks.working_files_note(matcher, dials.working_files, history.tracked(target.root))
        if not dials.coverage:
            # zero pairs: no range to examine, so no base to find — the trunk is not looked up, and a
            # repository whose branch is not the trunk is green; a flag's ref is still resolved, an
            # unknown one the configuration failure it is with a map
            if since is not None or change is not None:
                _locate_range(target, dials, since, change)
            return pipeline.report_scan(output, [], notes, messages.f9_scan_tail_empty())
        rng = _locate_range(target, dials, since, change)
        if rng is None:  # no commit yet: nothing landed, nothing to examine
            tail = messages.f9_scan_tail(len(dials.coverage), 0, "HEAD", "HEAD", rooted=True)
            return pipeline.report_scan(output, [], [], tail)
        _documents_exist(target.root, dials, rng)
        verdicts = checks.judge_pairs(matcher, dials.coverage, rng)
    declarations: list[Declaration] = [
        *history.trailers(target.root, rng, dials.declaration_key),
        *history.body_declarations(body_text, dials.declaration_key),
    ]
    findings, declared = checks.examine(verdicts, declarations, dials.declaration_key)
    tail = messages.f9_scan_tail(
        len(dials.coverage), rng.commits, rng.base_short, rng.tip_short, rooted=rng.base is None
    )
    return pipeline.report_scan(output, findings, [*declared, *notes], tail)


def _locate_range(
    target: ScanTarget, dials: TaskCloseDials, since: str | None, change: str | None
) -> Range | None:
    """None when the repository has no commit yet."""
    root = target.root
    if change is not None:
        landed = history.resolve(root, CHANGE, change)
        return history.make_range(root, history.first_parent(root, landed), landed)
    tip = history.head(root)
    if tip is None:
        return None
    if since is not None:
        return history.make_range(
            root, history.merge_base(root, history.resolve(root, SINCE, since), tip), tip
        )
    local, tracked = history.trunk_tips(root, dials.trunk, dials.trunk_remote)
    trunk = history.fresher(root, local, tracked)
    if trunk is None:
        raise ConfigurationFailure(messages.c12_no_trunk(dials.trunk, dials.trunk_remote, str(root)))
    # a detached HEAD at either tip is on the trunk: at a stale local tip it would otherwise be a green
    # over an empty range, the fresher tip being ahead of it
    on_trunk = history.current_branch(root) == dials.trunk or (
        history.current_branch(root) is None and tip in (local, tracked)
    )
    if on_trunk:  # the last landed change, as --change HEAD would examine it
        return history.make_range(root, history.first_parent(root, tip), tip)
    return history.make_range(root, history.merge_base(root, trunk, tip), tip)


def _documents_exist(root: Path, dials: TaskCloseDials, rng: Range) -> None:
    """A document the map names must be a file in the repository's HEAD — the map describes the
    tree as it is, and an older change is judged by today's map — unless the range itself touched
    it: deleted or renamed it, which the diff names. A path that is a directory there can never be
    among a change's paths, so a pair naming one could never be updated: refused, not examined."""
    head = history.head(root) or rng.tip
    for pair in dials.coverage:
        for doc in pair.docs:
            if doc in rng.paths:
                continue
            kind = history.kind_at(root, head, doc)
            if kind == "blob":
                continue
            if kind is None:
                raise ConfigurationFailure(
                    messages.x1_document_missing(pair.name, doc, history.short(root, head))
                )
            raise ConfigurationFailure(
                messages.x2_document_is_directory(pair.name, doc, history.short(root, head))
            )


def _read_body(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ConfigurationFailure(messages.c12_body_unreadable(path, str(exc))) from exc
