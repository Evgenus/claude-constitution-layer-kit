#!/usr/bin/env python3
"""Kit check: constitution.yaml is written in block style — one key per line, one "- " item per
line — and flow style, {...} or [...], stands only where a list or a mapping is empty.

The dials file is read by people line by line and reviewed by diff: a collection written on one
line hides its items where a diff cannot name the one that changed, and a pair of the coverage
map or a catalog entry written as {a: 1, b: 2} is read twice before it is read right. A style a
gate holds does not drift; one a comment asks for does.

Modes:  [PATH]              check the file (default: the kit's constitution.yaml);
        --fix [PATH]        rewrite every non-empty flow collection into block style, keeping every
                            comment, anchor, alias and quote as written, then check the result —
                            a flow collection spanning several lines is left to the hand, and said;
        --self-test         prove each finding red, the empty forms green, the rewrite equal in data
                            and whole in comments, and idempotent, on throwaway files.
Exit:   0 green; 2 a finding; 1 the check could not run.

The rewrite works on the parser's event stream: each flow collection's span is known to the
byte from its marks, the block form is rendered from the events inside it with each scalar's
original text, and the text outside the spans is not touched. A comment after the collection on
the same line moves to the end of that line's first part.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    print("BROKEN: PyYAML is not installed — fix: python3 -m pip install pyyaml", file=sys.stderr)
    print("BROKEN: the check could not run — 0 collections examined", file=sys.stderr)
    sys.exit(1)

KIT = Path(__file__).resolve().parent.parent
DEFAULT = KIT / "constitution.yaml"
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
STEP = 2  # the indent of a block collection under its key or its dash


# ---------------------------------------------------------------- the tree of a flow collection


@dataclass
class Scalar:
    text: str  # as written, quotes included
    anchor: str | None = None


@dataclass
class Alias:
    name: str


@dataclass
class Seq:
    items: list[Node] = field(default_factory=list)
    anchor: str | None = None


@dataclass
class Map:
    pairs: list[tuple[Node, Node]] = field(default_factory=list)
    anchor: str | None = None


Node = Scalar | Alias | Seq | Map


@dataclass(frozen=True)
class Span:
    """One outermost non-empty flow collection: where it stands in the text, and what it holds."""

    start: int  # index of its first character, the anchor included
    end: int  # index after its closing bracket
    line: int  # 1-based
    kind: str  # "list" or "mapping"
    node: Node


def parse_events(text: str) -> list[yaml.Event]:
    return list(yaml.parse(text))


def scalar_text(text: str, event: yaml.ScalarEvent) -> Scalar:
    raw = text[event.start_mark.index : event.end_mark.index]
    anchor = event.anchor
    if anchor and raw.startswith("&"):
        raw = raw[len(anchor) + 1 :].lstrip()
    return Scalar(raw, anchor)


def build(text: str, events: list[yaml.Event], at: int) -> tuple[Node, int]:
    """The node starting at events[at], and the index after its last event."""
    event = events[at]
    if isinstance(event, yaml.ScalarEvent):
        return scalar_text(text, event), at + 1
    if isinstance(event, yaml.AliasEvent):
        return Alias(event.anchor), at + 1
    if isinstance(event, yaml.SequenceStartEvent):
        seq = Seq(anchor=event.anchor)
        at += 1
        while not isinstance(events[at], yaml.SequenceEndEvent):
            item, at = build(text, events, at)
            seq.items.append(item)
        return seq, at + 1
    if isinstance(event, yaml.MappingStartEvent):
        mapping = Map(anchor=event.anchor)
        at += 1
        while not isinstance(events[at], yaml.MappingEndEvent):
            key, at = build(text, events, at)
            value, at = build(text, events, at)
            mapping.pairs.append((key, value))
        return mapping, at + 1
    raise ValueError(f"unexpected event {type(event).__name__}")


def flow_spans(text: str, events: list[yaml.Event]) -> list[Span]:
    """Every non-empty flow collection, outermost only, in text order."""
    spans: list[Span] = []
    at = 0
    while at < len(events):
        event = events[at]
        if isinstance(event, yaml.SequenceStartEvent | yaml.MappingStartEvent) and event.flow_style:
            node, after = build(text, events, at)
            empty = (isinstance(node, Seq) and not node.items) or (isinstance(node, Map) and not node.pairs)
            if not empty:
                kind = "list" if isinstance(node, Seq) else "mapping"
                end = events[after - 1].end_mark.index
                spans.append(Span(event.start_mark.index, end, event.start_mark.line + 1, kind, node))
            at = after
            continue
        at += 1
    return spans


# ---------------------------------------------------------------- rendering block style


def inline(node: Node) -> str | None:
    """What stands on the key's or the dash's own line: a scalar, an alias, an anchor, an empty form."""
    if isinstance(node, Scalar):
        return f"&{node.anchor} {node.text}" if node.anchor else node.text
    if isinstance(node, Alias):
        return f"*{node.name}"
    anchor = f"&{node.anchor}" if node.anchor else ""
    if isinstance(node, Seq) and not node.items:
        return f"{anchor} []".strip()
    if isinstance(node, Map) and not node.pairs:
        return f"{anchor} {{}}".strip()
    return anchor or None


def render(node: Node, indent: int) -> list[str]:
    """The block lines of a non-empty collection at this indent; nothing for anything else."""
    lines: list[str] = []
    pad = " " * indent
    if isinstance(node, Seq):
        for item in node.items:
            if isinstance(item, Map) and item.pairs:
                first, rest = item.pairs[0], item.pairs[1:]
                lines.extend(pair_lines(first, indent + STEP, prefix=pad + "- "))
                for pair in rest:
                    lines.extend(pair_lines(pair, indent + STEP))
            else:
                head = inline(item)
                lines.append((pad + "- " + head).rstrip() if head is not None else pad + "-")
                lines.extend(render(item, indent + STEP))
    elif isinstance(node, Map):
        for pair in node.pairs:
            lines.extend(pair_lines(pair, indent))
    return lines


def pair_lines(pair: tuple[Node, Node], indent: int, prefix: str | None = None) -> list[str]:
    key, value = pair
    head = inline(value)
    first = (prefix if prefix is not None else " " * indent) + key_text(key) + ":"
    if head is not None:
        first += " " + head
    return [first, *render(value, indent + STEP)]


def key_text(key: Node) -> str:
    if isinstance(key, Scalar):
        return key.text
    raise ValueError("a complex key cannot be rewritten")


def rewrite(text: str, spans: list[Span]) -> str:
    """The text with each span replaced by its block form, last span first so indices hold."""
    for span in reversed(spans):
        line_start = text.rfind("\n", 0, span.start) + 1
        line_end = text.find("\n", span.end)
        line_end = len(text) if line_end == -1 else line_end
        before = text[line_start : span.start]
        after = text[span.end : line_end]  # a trailing comment, or nothing
        if "\n" in text[span.start : span.end]:
            raise ValueError(span.line)
        if before.rstrip().endswith("-") and before.strip() == "-":
            block = item_block(span.node, before, after)
        elif before.rstrip().endswith(":"):
            block = value_block(span.node, before, after)
        else:
            raise ValueError(span.line)
        text = text[:line_start] + block + text[line_end:]
    return text


def value_block(node: Node, before: str, after: str) -> str:
    """`key: [..]` — the items go under the key, indented one step past it."""
    key_indent = len(before) - len(before.lstrip(" "))
    head = inline(node)
    first = before.rstrip() + (" " + head if head else "")
    if after.strip():
        first += "   " + after.strip()
    return "\n".join([first, *render(node, key_indent + STEP)])


def item_block(node: Node, before: str, after: str) -> str:
    """`- {..}` — the first pair stays on the dash's line, the rest align under it."""
    dash_indent = before.index("-")
    if isinstance(node, Map):
        first, rest = node.pairs[0], node.pairs[1:]
        lines = pair_lines(first, dash_indent + STEP, prefix=before.rstrip() + " ")
        for pair in rest:
            lines.extend(pair_lines(pair, dash_indent + STEP))
    else:
        head = inline(node)
        lines = [(before.rstrip() + (" " + head if head else "")), *render(node, dash_indent + STEP)]
    if after.strip():
        lines[0] += "   " + after.strip()
    return "\n".join(lines)


# ---------------------------------------------------------------- the check


def finding(path: Path, span: Span, text: str) -> str:
    shown = text[span.start : span.end]
    shown = shown if len(shown) <= 60 else shown[:60] + "…"
    return (
        f"RED: {path.name}:{span.line}: a {span.kind} written in flow style: {shown}\n"
        "  why: the dials file is read line by line and reviewed by diff, and a collection on one line"
        " hides its items where a diff cannot name the one that changed\n"
        '  fix: write it in block style — one "- " item or one key per line; only an empty list or'
        f" mapping stays [] or {{}}; python3 scripts/check-yaml-style.py --fix {path} rewrites the file"
    )


class Broken(Exception):
    """The check could not run: one self-sufficient line."""


def load(path: Path) -> tuple[str, list[yaml.Event]]:
    if not path.is_file():
        raise Broken(
            f"BROKEN: {path} does not exist — fix: run the check on the kit's constitution.yaml, or name"
            " a file"
        )
    text = path.read_text(encoding="utf-8")
    try:
        return text, parse_events(text)
    except yaml.YAMLError as exc:
        detail = " ".join(str(exc).split())
        raise Broken(f"BROKEN: {path} is not valid YAML ({detail}) — fix: repair the YAML first") from exc


def count(events: list[yaml.Event]) -> int:
    return sum(1 for e in events if isinstance(e, yaml.SequenceStartEvent | yaml.MappingStartEvent))


def check(path: Path) -> int:
    text, events = load(path)
    spans = flow_spans(text, events)
    examined = count(events)
    for span in spans:
        print(finding(path, span, text))
    if spans:
        print(f"RED: {len(spans)} finding(s) — {examined} collection(s) examined")
        return EXIT_RED
    print(f"GREEN: {path.name} is in block style — {examined} collection(s) examined")
    return EXIT_GREEN


def fix(path: Path) -> int:
    text, events = load(path)
    spans = flow_spans(text, events)
    if not spans:
        print(f"nothing to rewrite in {path.name}")
        return check(path)
    try:
        rewritten = rewrite(text, spans)
    except ValueError as exc:
        print(
            f"BROKEN: {path.name}:{exc.args[0]}: this collection cannot be rewritten by the script — a flow"
            " collection spanning several lines, a complex key, or one standing where neither a key nor"
            " a dash precedes it — fix: write it in block style by hand, then run the check",
            file=sys.stderr,
        )
        return EXIT_BROKEN
    if yaml.safe_load(rewritten) != yaml.safe_load(text):
        print(
            f"BROKEN: the rewrite of {path.name} would change what the file says; nothing was written"
            " — fix: this is a defect of the script; rewrite by hand and report it",
            file=sys.stderr,
        )
        return EXIT_BROKEN
    path.write_text(rewritten, encoding="utf-8")
    print(f"REWROTE: {path.name}: {len(spans)} collection(s) to block style")
    return check(path)


# ---------------------------------------------------------------- self-test

SAMPLE = """# header
root_policy: docs/policies/root.md   # where
a-policy:
  territory: &pol ["docs/**", 'x y']   # anchored: the catalog numbers exactly this
b-policy:
  territory: []
const-x:
  catalogs:
    - {prefix: dec, width: 4, territory: *pol}   # id and stem
    - {prefix: plc, territory: ["docs/policies/**"]}
  pairs:
    - {name: one, code: ["src/**", "!src/v/**"], docs: ["d/one.md"], extra: {}}
  lanes:
    - pattern: '\\bM[0-9]+\\b'
      home: ["/docs/requirements.md"]
  nested: {k: [1, 2], m: {p: q}}
empty: {}
"""


def self_test() -> int:
    ok = 0
    total = 0

    def case(title: str, passed: bool, evidence: str) -> None:
        nonlocal ok, total
        total += 1
        ok += 1 if passed else 0
        print(f"[{'ok' if passed else 'FAIL'}] {title}\n        {evidence}")

    with tempfile.TemporaryDirectory(prefix="yaml-style-") as scratch:
        directory = Path(scratch)
        sample = directory / "constitution.yaml"
        sample.write_text(SAMPLE, encoding="utf-8")
        text, events = load(sample)
        spans = flow_spans(text, events)
        case(
            "every non-empty flow collection is a finding, outermost once; empty ones are not",
            [s.line for s in spans] == [4, 9, 10, 12, 15, 16],
            f"lines {[s.line for s in spans]}",
        )
        rewritten = rewrite(text, spans)
        after = directory / "after.yaml"
        after.write_text(rewritten, encoding="utf-8")
        case(
            "the rewrite says what the file said",
            yaml.safe_load(rewritten) == yaml.safe_load(text),
            "safe_load equal",
        )
        comments = [
            line.split("#", 1)[1]
            for line in SAMPLE.splitlines()
            if "#" in line and not line.strip().startswith("'")
        ]
        kept = all(c in rewritten for c in comments)
        case(
            "every comment survives the rewrite, the header and the trailing ones",
            kept,
            f"{len(comments)} comments",
        )
        case(
            "anchors, aliases and quotes survive as written",
            "&pol" in rewritten and "*pol" in rewritten and "'x y'" in rewritten and '"docs/**"' in rewritten,
            "&pol, *pol, 'x y', \"docs/**\"",
        )
        case(
            "the rewritten file is green, and empty forms stay",
            not flow_spans(rewritten, parse_events(rewritten)) and "[]" in rewritten and "{}" in rewritten,
            "no flow span left; [] and {} kept",
        )
        case(
            "the rewrite is idempotent",
            rewrite(rewritten, flow_spans(rewritten, parse_events(rewritten))) == rewritten,
            "a second pass changes nothing",
        )
        expected = "    - prefix: dec   # id and stem\n      width: 4\n      territory: *pol\n"
        case(
            "a mapping item keeps its first pair on the dash's line, the comment beside it",
            expected in rewritten,
            expected.strip().splitlines()[0],
        )
        expected = "  territory: &pol   # anchored: the catalog numbers exactly this\n    - \"docs/**\"\n    - 'x y'\n"
        case(
            "an anchored list keeps its anchor on the key's line",
            expected in rewritten,
            expected.splitlines()[0].strip(),
        )
        multi = directory / "multi.yaml"
        multi.write_text("a: [1,\n  2]\n", encoding="utf-8")
        text2, events2 = load(multi)
        try:
            rewrite(text2, flow_spans(text2, events2))
            refused = False
        except ValueError:
            refused = True
        case(
            "a flow collection over several lines is refused, never rewritten",
            refused,
            "ValueError at its line",
        )
        broken = directory / "broken.yaml"
        broken.write_text("a: [\n", encoding="utf-8")
        try:
            load(broken)
            refused = False
        except Broken:
            refused = True
        case("a file that is not YAML is a configuration failure", refused, "Broken raised")
    print(f"{ok}/{total} self-test cases green")
    return EXIT_GREEN if ok == total else EXIT_RED


# ---------------------------------------------------------------- entry


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-yaml-style", add_help=False, allow_abbrev=False)
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("path", nargs="?", default=str(DEFAULT))
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print(
            "BROKEN: misinvocation — fix: run with no arguments, with --fix, with --self-test, or with a"
            " file's path",
            file=sys.stderr,
        )
        return EXIT_BROKEN
    try:
        if args.self_test:
            return self_test()
        if args.fix:
            return fix(Path(args.path))
        return check(Path(args.path))
    except Broken as failure:
        print(str(failure), file=sys.stderr)
        print("BROKEN: the check could not run — 0 collections examined", file=sys.stderr)
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
