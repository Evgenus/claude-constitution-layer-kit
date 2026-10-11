"""The two modes. Each wires the shared pipeline to this module's checks and returns an exit
code. No policy is resolved: the covered documents are the Markdown files git lists that the
module's own territories hold. Both modes run the same examination — the documents prepared,
copied into a temporary tree beside a configuration generated from the dials, and handed to Vale
in one run."""

from __future__ import annotations

import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from const_gate import identity, pipeline
from const_gate import messages as shared
from const_gate.errors import ConfigurationFailure
from const_gate.model import POST_WRITE, PRE_WRITE, Finding
from const_gate.output import Output
from const_gate.pipeline import Skip
from const_gate.repository import list_markdown, read_text
from const_gate.territory import Matcher

from . import dials as own_dials
from . import messages, rules, vale
from .model import Hit, LanguageDials, Level, Rule
from .prepare import prepare


@dataclass(frozen=True, slots=True)
class Verdict:
    """What the examination of one or more documents produced, in document and line order."""

    findings: list[Finding]
    notes: list[str]


def hook_mode(output: Output, stdin: TextIO) -> int:
    target = pipeline.locate_write(output, stdin)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    if target.event_name not in (PRE_WRITE, POST_WRITE):
        raise ConfigurationFailure(messages.c12_event(target.event_name))
    dials = own_dials.parse(target.dials.own)
    rel = target.rel
    with Matcher() as matcher:
        covered = rel in matcher.match(dials.territories, [rel])
        allowed = _allowed(matcher, dials, [rel])
    if not covered:
        return pipeline.skip(output, messages.g1_skip_not_covered(rel))
    verdict = examine({rel: target.text}, dials, allowed, _hook_waits())
    if not verdict.findings:
        return pipeline.green_hook(output, messages.g1_covered(), verdict.notes, target.event_name)
    shown = pipeline.within_the_cap(verdict.findings)
    count = (
        messages.f9_cut(len(verdict.findings), len(shown), rel)
        if len(shown) < len(verdict.findings)
        else None
    )
    return pipeline.report_hook(
        output, shown, verdict.notes, rel, target.dials.severity, target.event_name, count
    )


def _hook_waits() -> vale.Waits:
    """The hook's waits: each takes the smaller of its cap and what is left of the hook's one deadline,
    asked as the wait begins; a spent deadline is the shared configuration failure, C12.14."""
    return vale.Waits(
        probe=lambda: identity.remaining(vale.VERSION_SECONDS, "vale reported its version"),
        run=lambda: identity.remaining(vale.HOOK_SECONDS, "vale finished its run"),
    )


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    paths = list_markdown(target.root)
    with Matcher() as matcher:
        covered = sorted(matcher.match(dials.territories, paths))
        allowed = _allowed(matcher, dials, covered)
        matched = [set(matcher.match(d.paths, covered)) for d in dials.departures]
    notes = [
        messages.n3_stale_departure(index, departure)
        for index, (departure, files) in enumerate(zip(dials.departures, matched, strict=True), 1)
        if not files
    ]
    texts: dict[str, str] = {}
    for rel in covered:
        text = read_text(target.root, rel)
        if text is None:  # a file git lists and nobody can read: a count that skipped it would lie
            raise ConfigurationFailure(shared.c12_unreadable(rel))
        texts[rel] = text
    verdict = examine(texts, dials, allowed, vale.Waits(lambda: vale.VERSION_SECONDS, lambda: None))
    tail = messages.f9_tail(
        len(covered), dials.grade_ceiling, dials.sentence_words, len(dials.departures), len(paths)
    )
    return pipeline.report_scan(output, verdict.findings, [*notes, *verdict.notes], tail)


def _allowed(matcher: Matcher, dials: LanguageDials, rels: Sequence[str]) -> dict[str, set[Rule]]:
    """The rules each document's departures allow: {rel: rules}, empty where none applies."""
    allowed: dict[str, set[Rule]] = {rel: set() for rel in rels}
    for departure in dials.departures:
        for rel in matcher.match(departure.paths, rels):
            allowed[rel].update(departure.allow)
    return allowed


def examine(
    texts: dict[str, str], dials: LanguageDials, allowed: dict[str, set[Rule]], waits: vale.Waits
) -> Verdict:
    """Every document prepared and checked in one Vale run; the findings and notes in document
    and line order, a Vale comment outside a fence or a code span a finding wherever it stands; a
    hit of a rule that a departure allows for its document is neither. `waits` says how long the version
    probe and each Vale run may take, asked as each begins: the hook's are capped by what its deadline has
    left, the scan's probe has its cap and its runs none, and there is no default."""
    binary = vale.preflight(waits.probe())
    findings: list[Finding] = []
    notes: list[str] = []
    if not texts:
        return Verdict(findings, notes)
    with tempfile.TemporaryDirectory(prefix="const-language-") as scratch:
        directory = Path(scratch)
        config = rules.write_style(directory, dials)
        tree = directory / "tree"
        prepared = {rel: prepare(text) for rel, text in texts.items()}
        # Flat numbered names: Vale picks the format from the ending, and the one section the
        # configuration holds is `[*.md]`, so a covered X.MD under its own name would be read as no
        # Markdown at all; no ending, no collision of X.MD with X.md, no odd path (a line break, a dash)
        named = {f"{index:06d}.md": rel for index, rel in enumerate(prepared)}
        tree.mkdir()
        for name, rel in named.items():
            (tree / name).write_text(prepared[rel].text, encoding="utf-8")
        ran = vale.run(binary, config, tree, list(named), waits.run)
        hits = {named[name]: found for name, found in ran.items()}
    for rel in sorted(prepared):
        lines = prepared[rel].text.split("\n")
        placed: list[tuple[int, int, Finding | str]] = []
        for line, comment in prepared[rel].comments:
            placed.append((line, 0, messages.l6_vale_comment(rel, line, comment.replace("\n", " "))))
        for hit in hits.get(rel, []):
            if hit.rule in allowed.get(rel, set()):
                continue
            placed.append((hit.line, 1, _judge(rel, hit, lines, dials)))
        for _, _, item in sorted(placed, key=lambda p: (p[0], p[1])):
            if isinstance(item, Finding):
                findings.append(item)
            else:
                notes.append(item)
    return Verdict(findings, notes)


def _judge(rel: str, hit: Hit, lines: Sequence[str], dials: LanguageDials) -> Finding | str:
    """A hit as its rule's level says: a finding at error, a note at warning."""
    if hit.rule is Rule.SENTENCE:  # Vale names where the sentence starts and not its words: echo them
        line = lines[hit.line - 1] if 0 < hit.line <= len(lines) else ""
        hit = Hit(hit.rule, hit.line, hit.column, line[max(hit.column - 1, 0) :].strip(), hit.message)
    found = messages.finding(rel, hit, dials.grade_ceiling, dials.sentence_words)
    if dials.levels[hit.rule] is Level.WARNING:
        return messages.n2_warning(rel, hit.rule, found)
    return found
