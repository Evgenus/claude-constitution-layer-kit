#!/usr/bin/env python3
"""Kit review aid, never a gate: list each message function whose text no fixture types by hand.

Rule 14 of the template's §6 asks that every message a gate can print stand, in the fixtures that
run it, at least once as a line typed by hand: an expectation built by the message's own function
cannot catch a defect in that function's text. This script lists the candidates for the review to
judge; it decides nothing, and exits 0 whatever it finds.

For each function of shared/const_gate/messages.py and of the messages.py of each package of a
module — every folder at the top of modules/<m>/scripts/, itself no link, that holds an
__init__.py, whose name starts with neither . nor _, save const_gate, as the kit's
check-shared-links derives them — docstrings aside, it takes the constant text the function
holds — string literals, f-string parts and the module's string constants, split where a value is
filled in — and asks whether one piece of at least 15 characters, its edge punctuation trimmed,
stands inside a string of the fixtures that run it: the module's tests/run.py for a module's
messages; for the shared ones every module's tests/run.py, shared/tests/shared_items.py and the
harness that runs those items, shared/tests/harness.py. A string
of a fixture is a literal, an f-string or a `+` chain, docstrings aside. A function with no piece
that long is listed apart: its text is too short to find, and the review reads it whole.

What it cannot see: whether the typed line is compared with that function's output (a fixture may
hold the text as input), text built at run time, and a branch of a function whose other piece is
typed. So a function it lists may be covered, and one it passes may not be.

Modes:  no arguments   list for the kit;
        --module <m>   list for one module, the shared messages left out.
Exit:   0 always, save 1, with a BROKEN line and its fix, when the kit's folders cannot be read,
        the arguments are misused, --module names no module, a package holds no messages.py, a
        module with a package has no tests/run.py, the shared messages module is gone, or a file it
        reads cannot be read or does not parse.
Its name is list-, never check-: the kit's check-gate-lists holds every scripts/check-*.py to the
gate group, and this script is no check.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
LENGTH = 15  # the shortest piece of a message's text the list looks for
TRIM = " .,:;'\"(){}[]—-"
SHARED = "shared/const_gate/messages.py"
SHARED_TESTS = ("shared/tests/shared_items.py", "shared/tests/harness.py")


class Broken(Exception):
    """A file the list needs is missing or cannot be parsed: the message is its BROKEN line."""


@dataclass(frozen=True)
class Verdict:
    function: str
    line: int
    typed: str  # the piece found typed, or ""
    longest: str  # the longest piece the function holds


def parsed(path: Path, fix: str) -> ast.Module:
    """The file's syntax tree, or Broken naming the file and the fix."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise Broken(f"{path.relative_to(KIT)} is missing — fix: {fix}") from None
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as bad:
        raise Broken(
            f"{path.relative_to(KIT)} cannot be read or parsed ({bad}) — fix: make it valid UTF-8 Python"
        ) from None


def packages(module: Path) -> list[Path]:
    """The module's own packages, derived as the kit's check-shared-links derives them."""
    scripts = module / "scripts"
    if not scripts.is_dir():
        return []
    return sorted(
        path
        for path in scripts.iterdir()
        if not path.is_symlink()
        and path.is_dir()
        and not path.name.startswith((".", "_"))
        and path.name != "const_gate"
        and (path / "__init__.py").is_file()
    )


def is_docstring(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def constants(tree: ast.Module) -> dict[str, str]:
    """The module's top-level names bound to text that is constant through and through."""
    found: dict[str, str] = {}
    for _ in range(3):  # a constant built from another resolves on a later pass
        for node in tree.body:
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                parts = pieces(node.value, found)
                if parts and all(part is not None for part in parts):
                    found[node.targets[0].id] = "".join(part for part in parts if part is not None)
    return found


def pieces(node: ast.AST, known: dict[str, str]) -> list[str | None]:
    """The text of an expression, None where a value is filled in at run time."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.Name) and node.id in known:
        return [known[node.id]]
    if isinstance(node, ast.JoinedStr):
        out: list[str | None] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                out.append(value.value)
            elif isinstance(value, ast.FormattedValue) and value.format_spec is None:
                out.extend(pieces(value.value, known) if isinstance(value.value, ast.Name) else [None])
            else:
                out.append(None)
        return out
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return pieces(node.left, known) + pieces(node.right, known)
    return [None]


def joined(parts: list[str | None]) -> list[str]:
    """The runs of constant text between the values filled in."""
    runs, current = [], ""
    for part in [*parts, None]:
        if part is None:
            if current:
                runs.append(current)
            current = ""
        else:
            current += part
    return runs


def message_texts(path: Path, fix: str) -> dict[str, tuple[int, list[str]]]:
    """Each function of a messages module: its line and the constant pieces of its text."""
    tree = parsed(path, fix)
    known = constants(tree)
    found: dict[str, tuple[int, list[str]]] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        body = node.body[1:] if node.body and is_docstring(node.body[0]) else node.body
        texts: set[str] = set()
        for statement in body:
            for inner in ast.walk(statement):
                if isinstance(inner, ast.JoinedStr | ast.BinOp | ast.Constant):
                    texts.update(joined(pieces(inner, known)))
        found[node.name] = (node.lineno, sorted(texts, key=len, reverse=True))
    return found


def fixture_strings(path: Path) -> list[str]:
    """Every string a fixture file holds, docstrings aside, a filled-in value read as a break."""
    tree = parsed(path, "restore the module's fixture runner")
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            if node.body and is_docstring(node.body[0]):
                docstrings.add(id(node.body[0]))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and id(node) in docstrings:
            continue
        if isinstance(node, ast.JoinedStr | ast.BinOp) or (
            isinstance(node, ast.Constant) and isinstance(node.value, str)
        ):
            text = "\0".join(run for run in joined(pieces(node, {})))
            if text.strip():
                out.append(text)
    return out


def verdicts(messages: Path, fix: str, fixtures: list[Path]) -> list[Verdict]:
    strings = [text for path in fixtures for text in fixture_strings(path)]
    out = []
    for name, (line, texts) in message_texts(messages, fix).items():
        if not texts:
            continue  # a helper with no text of its own
        typed = ""
        for text in texts:
            core = text.strip(TRIM)
            if len(core) >= LENGTH and any(core in string for string in strings):
                typed = core
                break
        out.append(Verdict(name, line, typed, texts[0]))
    return out


def report(title: str, found: list[Verdict]) -> int:
    untyped = [v for v in found if not v.typed and len(v.longest.strip(TRIM)) >= LENGTH]
    short = [v for v in found if not v.typed and len(v.longest.strip(TRIM)) < LENGTH]
    print(
        f"{title}: {len(found)} message function(s), {len(untyped)} not typed, {len(short)} too short to find"
    )
    for v in untyped:
        print(f"  not typed: {v.function} (line {v.line}) — longest text: {v.longest.strip(TRIM)[:80]!r}")
    for v in short:
        print(f"  too short: {v.function} (line {v.line}) — read it whole")
    return len(untyped) + len(short)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="list-message-literals", add_help=False, allow_abbrev=False)
    parser.add_argument("--module")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --module <name>")
        return 1
    try:
        modules = sorted(p for p in (KIT / "modules").iterdir() if (p / "MODULE.md").is_file())
    except OSError as bad:
        print(
            f"BROKEN: the kit's modules/ cannot be read ({bad}) — fix: run the script from a clone of the kit"
        )
        return 1
    if args.module:
        modules = [m for m in modules if m.name == args.module]
        if not modules:
            print(f"BROKEN: no module {args.module} — fix: name a folder of modules/")
            return 1
    listed = 0
    try:
        for module in modules:
            for package in packages(module):
                fix = (
                    f"put the package's messages in {package.name}/messages.py, as rule 2 of template §6 asks"
                )
                found = verdicts(package / "messages.py", fix, [module / "tests" / "run.py"])
                listed += report(module.name, found)
        if not args.module:
            fixtures = [KIT / p for p in SHARED_TESTS] + [m / "tests" / "run.py" for m in modules]
            found = verdicts(
                KIT / SHARED, "restore the shared messages module", [f for f in fixtures if f.is_file()]
            )
            listed += report("shared", found)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        return 1
    print(f"{listed} function(s) for the review to judge — a list, never a verdict")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
