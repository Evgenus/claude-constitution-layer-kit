#!/usr/bin/env python3
"""Kit check: a kit document outside module prose cites a module by a link to its specification.

Module prose says "module `const-x`"; every other kit document writes the same words as a link,
module [`const-x`](<path to>/docs/requirements.md#const-x) — rule 4 of plc-0007-requirements. The
link lint of const-referencing cannot hold this: it matches its lanes on text whose code spans are
blanked, and the module's name stands in one. So the kit checks it here, over the Markdown files
git lists, the names being the directories under modules/.

Not read: module prose (modules/, module-template/), where the plain form is the rule; frozen
comparisons (docs/research/), which keep the form they were frozen with (rule 7 of
plc-0005-research); the kit's templates (templates/), whose text is copied into another folder,
so that a relative link cannot be right in both — a template gives the path from the copy's folder
in a code span instead; fenced code; a mention inside a link's text or inside a longer code span; a
name that is no module's directory, such as the placeholder `const-x`.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway repository: red for the plain form in a
                       document, green for the link and for every place not read.
Exit:   0 green; 2 a plain mention; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2

SPEC = "docs/requirements.md"
NOT_READ = ("modules/", "module-template/", "docs/research/", "templates/")
MENTION = re.compile(r"module `(const-[a-z0-9-]+)`")
TICKS = re.compile(r"`+")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
WHY = (
    "a kit document cites a module by a link to its specification, so a reader reaches it in one"
    " click (rule 4 of plc-0007-requirements)"
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    name: str

    def render(self) -> str:
        spec = os.path.relpath(SPEC, os.path.dirname(self.path) or ".")
        return (
            f"RED: {self.path}:{self.line}: module `{self.name}` is written plain, outside module prose\n"
            f"  why: {WHY}\n"
            f"  fix: write module [`{self.name}`]({spec}#{self.name})"
        )


def listed_markdown(root: Path) -> list[str]:
    try:
        done = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "*.md"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as missing:
        raise Broken("git is not on PATH — fix: install git, then run the check again") from missing
    if done.returncode != 0:
        first = (done.stderr.splitlines() or ["no message"])[0]
        raise Broken(f"git ls-files failed: {first} — fix: run the check from a checkout of the kit")
    return sorted(p for p in done.stdout.split("\0") if p and (root / p).is_file())


def module_names(root: Path) -> frozenset[str]:
    modules = root / "modules"
    if not modules.is_dir():
        raise Broken(f"{root} has no modules/ directory — fix: run the script from a checkout of the kit")
    return frozenset(m.name for m in modules.iterdir() if m.is_dir() and m.name.startswith("const-"))


def inside_link_text(before: str) -> bool:
    return before.count("[") > before.count("]")


def code_spans(line: str) -> list[tuple[int, int]]:
    """Where the code spans of one line stand: a run of backticks closed by the next run of the
    same length, as CommonMark reads them."""
    spans: list[tuple[int, int]] = []
    runs = list(TICKS.finditer(line))
    i = 0
    while i < len(runs):
        close = next((j for j in range(i + 1, len(runs)) if len(runs[j][0]) == len(runs[i][0])), None)
        if close is None:
            i += 1
            continue
        spans.append((runs[i].start(), runs[close].end()))
        i = close + 1
    return spans


def inside_code_span(line: str, position: int) -> bool:
    return any(start <= position < end for start, end in code_spans(line))


def check_document(path: str, text: str, names: frozenset[str]) -> list[Finding]:
    findings: list[Finding] = []
    fence: str | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        opener = FENCE.match(line)
        if fence is not None:
            if opener and opener[1][0] == fence[0] and len(opener[1]) >= len(fence):
                fence = None
            continue
        if opener:
            fence = opener[1]
            continue
        for mention in MENTION.finditer(line):
            before = line[: mention.start()]
            if (
                mention[1] in names
                and not inside_link_text(before)
                and not inside_code_span(line, mention.start())
            ):
                findings.append(Finding(path, number, mention[1]))
    return findings


def check_kit(root: Path) -> tuple[list[Finding], int, int]:
    names = module_names(root)
    documents = [p for p in listed_markdown(root) if not p.startswith(NOT_READ)]
    findings = [
        finding
        for path in documents
        for finding in check_document(path, (root / path).read_text(encoding="utf-8"), names)
    ]
    return findings, len(documents), len(names)


def report(findings: list[Finding], documents: int, names: int) -> int:
    counts = f"{documents} document(s) examined outside module prose, {names} module name(s) known"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every module named outside module prose is a link to its specification — {counts}")
    return EXIT_GREEN


def self_test() -> int:
    """Red→green on a throwaway repository: the plain form is red where the check reads, and the
    link is green; every place the check does not read stays green with the plain form."""
    linked = "See module [`const-sample`](../requirements.md#const-sample).\n"
    plain = "See module `const-sample`.\n"
    red: dict[str, tuple[str, str, str]] = {  # case: path, green text, red text
        "a policy": ("docs/policies/p.md", linked, plain),
        "a record, two on one line": (
            "docs/decisions/d.md",
            linked,
            "module `const-sample` and module `const-sample`.\n",
        ),
        "the guide at the root": (
            "GUIDE.md",
            "module [`const-sample`](docs/requirements.md#const-sample)\n",
            plain,
        ),
        "a line after a closed fence": ("docs/f.md", linked, "```\nx\n```\n" + plain),
    }
    green: dict[str, tuple[str, str]] = {  # case: path, text with the plain form not read
        "module prose": ("modules/const-sample/MODULE.md", plain),
        "the module template": ("module-template/MODULE.md", plain),
        "a frozen comparison": ("docs/research/r.md", plain),
        "a template": ("templates/policy.md", plain),
        "a fenced block": ("docs/policies/q.md", "~~~\n" + plain + "~~~\n"),
        "link text": ("docs/policies/s.md", "[the words module `const-sample` here](x.md)\n"),
        "a longer code span": ("docs/policies/t.md", "`` module `const-sample` ``\n"),
        "a code span after another": ("docs/policies/v.md", "`a` then `` module `const-sample` ``\n"),
        "a name that is no module": ("docs/policies/u.md", "module `const-x`\n"),
    }

    def fresh(root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / "modules" / "const-sample").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / SPEC).write_text('<a id="const-sample"></a>\n', encoding="utf-8")

    def write(root: Path, path: str, text: str) -> None:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")

    failed = 0
    for name, (path, good, bad) in red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, good)
            green_before = not check_kit(root)[0]
            write(root, path, bad)
            findings = check_kit(root)[0]
            red_after = len(findings) == bad.count("module `const-sample`") and all(
                f.path == path for f in findings
            )
        ok = green_before and red_after
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the link is green, the plain form in {name} is red")
    for name, (path, text) in green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, text)
            ok = not check_kit(root)[0]
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the plain form in {name} is not read")
    total = len(red) + len(green)
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-module-links", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 documents examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(*check_kit(KIT))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 documents examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
