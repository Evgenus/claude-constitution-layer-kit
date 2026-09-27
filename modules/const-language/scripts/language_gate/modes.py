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

from const_gate import messages as shared
from const_gate import pipeline
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

SHOWN_AFTER_WRITE = 20  # findings printed after one write; the count line carries the total
SHOWN_CHARACTERS = 8000  # and their characters: the platform cuts a hook's text at 10,000


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
    if not covered:
        return pipeline.skip(output, messages.g1_skip_not_covered(rel))
    verdict = examine({rel: target.text}, dials)
    if not verdict.findings:
        return pipeline.green_hook(output, messages.g1_covered(), verdict.notes)
    shown = _within_the_cap(verdict.findings)
    count = (
        messages.f9_cut(len(verdict.findings), len(shown), rel)
        if len(shown) < len(verdict.findings)
        else None
    )
    return pipeline.report_hook(
        output, shown, verdict.notes, rel, target.dials.severity, target.event_name, count
    )


def scan_mode(output: Output, start: Path) -> int:
    target = pipeline.locate_scan(output, start)
    if isinstance(target, Skip):
        return pipeline.skip(output, target.reason)
    dials = own_dials.parse(target.dials.own)
    paths = list_markdown(target.root)
    with Matcher() as matcher:
        covered = sorted(matcher.match(dials.territories, paths))
    texts: dict[str, str] = {}
    for rel in covered:
        text = read_text(target.root, rel)
        if text is None:  # a file git lists and nobody can read: a count that skipped it would lie
            raise ConfigurationFailure(shared.c12_unreadable(rel))
        texts[rel] = text
    verdict = examine(texts, dials)
    tail = messages.f9_tail(len(covered), dials.grade_ceiling, dials.sentence_words, len(paths))
    return pipeline.report_scan(output, verdict.findings, verdict.notes, tail)


def examine(texts: dict[str, str], dials: LanguageDials) -> Verdict:
    """Every document prepared and checked in one Vale run; the findings and notes in document
    and line order, a Vale comment outside a fence or a code span a finding wherever it stands."""
    binary = vale.preflight()
    findings: list[Finding] = []
    notes: list[str] = []
    if not texts:
        return Verdict(findings, notes)
    with tempfile.TemporaryDirectory(prefix="const-language-") as scratch:
        directory = Path(scratch)
        config = rules.write_style(directory, dials)
        tree = directory / "tree"
        prepared = {rel: prepare(text) for rel, text in texts.items()}
        for rel, document in prepared.items():
            path = tree / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(document.text, encoding="utf-8")
        hits = vale.run(binary, config, tree, list(prepared))
    for rel in sorted(prepared):
        lines = prepared[rel].text.split("\n")
        placed: list[tuple[int, int, Finding | str]] = []
        for line, comment in prepared[rel].comments:
            placed.append((line, 0, messages.l6_vale_comment(rel, line, comment.replace("\n", " "))))
        for hit in hits.get(rel, []):
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


def _within_the_cap(findings: Sequence[Finding]) -> Sequence[Finding]:
    """The first findings that fit: at most twenty, and no more characters than leave the count
    line inside what the platform passes on — it cuts a hook's text at 10,000 characters, from
    the end, where the count stands."""
    shown: list[Finding] = []
    size = 0
    for finding in findings[:SHOWN_AFTER_WRITE]:
        size += len(finding.render()) + 1
        if size > SHOWN_CHARACTERS and shown:
            break
        shown.append(finding)
    return shown
