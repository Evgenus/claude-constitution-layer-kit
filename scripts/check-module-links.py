#!/usr/bin/env python3
"""Kit check: a kit document outside module prose cites a module by a link to its specification.

Module prose says "module `const-x`"; every other kit document writes the same words as a link,
module [`const-x`](<path to>/docs/requirements.md#const-x) — the reference rule of CLAUDE.md. The
module table of the root README links a module to the module's own README.md instead, as that rule
allows; a link's target is never checked here, so the table needs no exception of its own.
The form read is the word "module" or "modules", with a small or a capital m, a space, and a
module's name in a code span; a name standing alone, or any name after the first of "modules `a` and `b`", is
left to review. The link lint of const-referencing cannot hold this: it matches its lanes on text
whose code spans are blanked, and the module's name stands in one. So the kit checks it here, over
the Markdown files git lists, the names being the module folders of `kit_module_doc.module_folders`,
the kit's one listing: every folder under modules/ whose name opens with neither `.` nor `_`, with
or without `const-`, holding its MODULE.md — a folder without it, and a tree with no modules/, are
BROKEN. A mention is read for `const-` names alone, so a folder named otherwise counts as a name
known and is never matched.

Not read: module prose (modules/, a module's README.md among them, and module-template/), where
the plain form is the rule; every
research comparison (docs/research/), frozen or not: a frozen one keeps the form it was frozen
with (rule 7 of plc-0005-research), and in one not yet frozen review holds the link; the kit's
templates (templates/), whose text is copied into another folder, so that a relative link cannot
be right in both — a template gives the path from the copy's folder in a code span instead;
fenced code; a mention inside a link or inside a longer code span; a name that is no module's
directory, such as the placeholder `const-x`.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway repository: red for the plain form in a
                       document, with the number of findings typed by hand; green for the link
                       and for every place not read; the report of one finding as literal lines
                       with exit 2; the names known over the folders of modules/ (a folder `.x`
                       or `_x` and a plain file not counted, a name without `const-` counted);
                       a module folder without its MODULE.md, a tree with no modules/ and a
                       file that is not UTF-8 as a BROKEN line.
Exit:   0 green; 2 a plain mention; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from kit_module_doc import DocumentError, module_folders

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2

SPEC = "docs/requirements.md"
NOT_READ = ("modules/", "module-template/", "docs/research/", "templates/")
MENTION = re.compile(r"\b([Mm]odules?) `(const-[a-z0-9-]+)`")
LINK = re.compile(  # inline: a destination in <> or with no space, then an optional title; or a reference
    r"\[(?:[^\[\]]|\[[^\[\]]*\])*\]"
    r"(?:\(\s*(?:<[^<>\n]*>|[^()\s]*)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^()]*\)))?\s*\)|\[[^\[\]]*\])"
)
TICKS = re.compile(r"`+")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
WHY = (
    "a kit document cites a module by a link to its specification, so a reader reaches it in one"
    " click (the reference rule of CLAUDE.md)"
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    word: str
    name: str

    def render(self) -> str:
        spec = os.path.relpath(SPEC, os.path.dirname(self.path) or ".")
        return (
            f"RED: {self.path}:{self.line}: {self.word} `{self.name}` is written plain,"
            " outside module prose\n"
            f"  why: {WHY}\n"
            f"  fix: write {self.word} [`{self.name}`]({spec}#{self.name})"
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
    try:
        return frozenset(folder.name for folder in module_folders(root))
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


def inside_link(line: str, position: int) -> bool:
    return any(link.start() <= position < link.end() for link in LINK.finditer(line))


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
        if fence is not None:  # a closing fence carries no info string
            if opener and opener[1][0] == fence[0] and len(opener[1]) >= len(fence) and not opener[2].strip():
                fence = None
            continue
        if opener:
            fence = opener[1]
            continue
        for mention in MENTION.finditer(line):
            if (
                mention[2] in names
                and not inside_link(line, mention.start())
                and not inside_code_span(line, mention.start())
            ):
                findings.append(Finding(path, number, mention[1], mention[2]))
    return findings


def check_kit(root: Path) -> tuple[list[Finding], int, int]:
    names = module_names(root)
    documents = [p for p in listed_markdown(root) if not p.startswith(NOT_READ)]
    findings = [finding for path in documents for finding in check_document(path, read(root, path), names)]
    return findings, len(documents), len(names)


def read(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{path} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}) — fix: make it readable") from bad


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
    """Red→green on a throwaway repository: the plain form is red where the check reads, with
    the number of findings typed by hand, and the link is green; every place the check does not
    read stays green with the plain form; the report of one finding is its literal text with
    exit 2; and a file that is not UTF-8 is a teaching BROKEN line."""
    linked = "See module [`const-sample`](../requirements.md#const-sample).\n"
    plain = "See module `const-sample`.\n"
    red: dict[str, tuple[str, str, str, int]] = {  # case: path, green, red, its findings by hand
        "a policy": ("docs/policies/p.md", linked, plain, 1),
        "a record, two on one line": (
            "docs/decisions/d.md",
            linked,
            "module `const-sample` and module `const-sample`.\n",
            2,
        ),
        "the guide at the root": (
            "GUIDE.md",
            "module [`const-sample`](docs/requirements.md#const-sample)\n",
            plain,
            1,
        ),
        "a line after a closed fence": ("docs/f.md", linked, "```\nx\n```\n" + plain, 1),
        "a capital at a sentence's start": (
            "docs/policies/c.md",
            "Module [`const-sample`](../requirements.md#const-sample) guards it.\n",
            "Module `const-sample` guards it.\n",
            1,
        ),
        "the plural's first name": (
            "docs/policies/m.md",
            "modules [`const-sample`](../requirements.md#const-sample) and more\n",
            "modules `const-sample` and more\n",
            1,
        ),
        "what is no link, its destination holding a space": (
            "docs/policies/n.md",
            linked,
            "[module `const-sample`](b c)\n",
            1,
        ),
        "a line with an unclosed bracket before it": (
            "docs/policies/b.md",
            "a[0 and " + linked,
            "a[0 and " + plain,
            1,
        ),
    }
    green: dict[str, tuple[str, str]] = {  # case: path, text with the plain form not read
        "module prose": ("modules/const-sample/MODULE.md", plain),
        "a module's README": ("modules/const-sample/README.md", plain),
        "the module template": ("module-template/MODULE.md", plain),
        "a research comparison": ("docs/research/r.md", plain),
        "a template": ("templates/policy.md", plain),
        "a fenced block": ("docs/policies/q.md", "~~~\n" + plain + "~~~\n"),
        "a fence whose info-string line closes nothing": (
            "docs/policies/i.md",
            "```\n```python\n" + plain + "```\n",
        ),
        "link text": ("docs/policies/s.md", "[the words module `const-sample` here](x.md)\n"),
        "the text of a link with a title": ("docs/policies/w.md", '[module `const-sample`](x.md "t")\n'),
        "the text of a link whose destination in <> holds a space": (
            "docs/policies/z.md",
            "[module `const-sample`](<a b.md>)\n",
        ),
        "the text of a reference link": ("docs/policies/y.md", "[module `const-sample`][spec]\n"),
        "a longer code span": ("docs/policies/t.md", "`` module `const-sample` ``\n"),
        "a code span after another": ("docs/policies/v.md", "`a` then `` module `const-sample` ``\n"),
        "a name that is no module": ("docs/policies/u.md", "module `const-x`\n"),
    }
    report_lines = [  # the report of the capital case, typed by hand: a message function cannot check itself
        "RED: docs/policies/c.md:1: Module `const-sample` is written plain, outside module prose",
        "  why: a kit document cites a module by a link to its specification, so a reader reaches it in one"
        " click (the reference rule of CLAUDE.md)",
        "  fix: write Module [`const-sample`](../requirements.md#const-sample)",
        "RED: 1 finding(s) — 2 document(s) examined outside module prose, 1 module name(s) known",
    ]

    def fresh(root: Path) -> None:
        try:
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        except OSError as missing:
            raise Broken(
                f"git cannot start ({missing.strerror}) — fix: install git, then run the self-test"
            ) from missing
        except subprocess.CalledProcessError as failed:
            said = (failed.stderr.decode(errors="replace").splitlines() or ["no message"])[0]
            raise Broken(
                f"git init failed in {root}: {said} — fix: repair what git names, then run the self-test"
            ) from failed
        (root / "modules" / "const-sample").mkdir(parents=True)
        (root / "modules" / "const-sample" / "MODULE.md").write_text("A module.\n", encoding="utf-8")
        (root / "docs").mkdir()
        (root / SPEC).write_text('<a id="const-sample"></a>\n', encoding="utf-8")

    def write(root: Path, path: str, text: str) -> None:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")

    failed = 0
    for name, (path, good, bad, count) in red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, path, good)
            green_before = not check_kit(root)[0]
            write(root, path, bad)
            findings = check_kit(root)[0]
            red_after = len(findings) == count and all(f.path == path for f in findings)
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
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "docs/policies/c.md", red["a capital at a sentence's start"][2])
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        (root / "docs" / "latin1.md").write_bytes(b"caf\xe9\n")
        try:
            check_kit(root)
            ok = False
        except UnicodeDecodeError:  # the decoding escaped the check: its fix is gone
            ok = False
        except Broken as broken:
            ok = str(broken).startswith("docs/latin1.md is not UTF-8") and "fix: save it as UTF-8" in str(
                broken
            )
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a file that is not UTF-8 is a teaching BROKEN line, never a traceback")
    # the names known, one per module folder of the kit's one listing: what stands under modules/
    names_known: dict[str, tuple[dict[str, str], set[str]]] = {  # case: files written, the names known
        "a folder `.x` and a folder `_x` are skipped silently": (
            {"modules/.x/MODULE.md": "A module.\n", "modules/_x/MODULE.md": "A module.\n"},
            {"const-sample"},
        ),
        "a folder named without const- is a name known, and its plain mention is not read": (
            {"modules/glossary/MODULE.md": "A module.\n"},
            {"const-sample", "glossary"},
        ),
        "a plain file of modules/ is no name": ({"modules/const-file": "not a folder\n"}, {"const-sample"}),
    }
    for name, (files, known) in names_known.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            for path, text in files.items():
                write(root, path, text)
            # a mention is read for `const-` names alone: each known name without it stands in a
            # plain mention of a document outside module prose, which is no finding
            plain_mentions = [f"See module `{n}`.\n" for n in sorted(known) if not n.startswith("const-")]
            if plain_mentions:
                write(root, "docs/policies/g.md", "".join(plain_mentions))
            ok = module_names(root) == known and check_kit(root)[2] == len(known)
            ok = ok and not check_kit(root)[0]
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    with tempfile.TemporaryDirectory() as tmp:  # no MODULE.md: BROKEN, where the folder was a name before
        root = Path(tmp).resolve()
        fresh(root)
        (root / "modules" / "const-ghost").mkdir()
        try:
            check_kit(root)
            ok = False
        except Broken as broken:
            ok = str(broken) == "modules/const-ghost has no MODULE.md — fix: restore the module document"
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a module folder without its MODULE.md is a teaching BROKEN line")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        try:
            check_kit(root)
            ok = False
        except Broken as broken:
            ok = (
                str(broken)
                == f"{root} has no modules/ directory — fix: run the check from a checkout of the kit"
            )
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a tree with no modules/ is a teaching BROKEN line")
    total = len(red) + len(green) + 2 + len(names_known) + 2
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
