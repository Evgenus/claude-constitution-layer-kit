#!/usr/bin/env python3
"""Kit check: every module that uses the shared gate code reaches it through a link, and the
link leads to the one source.

The shared code has one source in the kit: shared/const_gate/ for the gates, shared/tests/
for the fixture harness. A module's scripts/const_gate, and the harness files in its tests/,
are symbolic links to it, relative ones, so that they survive a clone into any directory. The
platform copies what such a link points at into an installed plugin, so an installed module
carries the code; inside the kit there is one copy to read, to fix and to review.

Modes:  no arguments   check every module under modules/;
        --self-test    prove the check on a throwaway tree: red for a missing link, a copy, a dangling
                       link, a link leading elsewhere, an absolute one, a text file left by a
                       checkout without symlink support; green for the right link.
Exit:   0 green; 2 a link is wrong; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2

# link inside a module -> its one source in the kit, both relative to their roots
LINKS = {
    "scripts/const_gate": "shared/const_gate",
    "tests/harness.py": "shared/tests/harness.py",
    "tests/consumer.py": "shared/tests/consumer.py",
    "tests/shared_items.py": "shared/tests/shared_items.py",
}
WHY = "the shared code has one source; a module that carries its own copy drifts from it silently"


@dataclass(frozen=True)
class Finding:
    headline: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.headline}\n  why: {WHY}\n  fix: {self.fix}"


def uses_shared_code(module: Path) -> bool:
    """A module whose scripts import the shared code — a hook's gate, or a generator alone — owes the
    links. A module of skills alone owes none."""
    scripts = module / "scripts"
    imports = any(
        "const_gate" in path.read_text(encoding="utf-8", errors="replace")
        for path in scripts.glob("*.py")
        if path.is_file()
    )
    return (
        (module / "hooks" / "hooks.json").is_file()
        or imports
        or any((module / link).is_symlink() for link in LINKS)
    )


def check_link(kit: Path, module: Path, link: str, source: str) -> Finding | None:
    path, target = module / link, kit / source
    shown = path.relative_to(kit).as_posix()
    wanted = os.path.relpath(target, path.parent)
    make = f"from {path.parent.relative_to(kit).as_posix()}/ run: ln -s {wanted} {path.name}"
    if not path.is_symlink():
        if path.is_dir():
            return Finding(f"{shown} is a directory of its own, not a link to {source}", f"remove it; {make}")
        if path.is_file():
            return Finding(
                f"{shown} is a plain file, not a link to {source} (a checkout without symlink support"
                " leaves one)",
                f"enable symlinks (git config core.symlinks true), remove the file; {make}",
            )
        return Finding(f"{shown} is missing", make)
    if os.path.isabs(os.readlink(path)):
        return Finding(f"{shown} is an absolute link, which breaks in any other clone", f"remove it; {make}")
    if not path.exists():
        return Finding(f"{shown} is a dangling link to {os.readlink(path)}", f"remove it; {make}")
    if path.resolve() != target.resolve():
        return Finding(f"{shown} leads to {os.readlink(path)}, not to {source}", f"remove it; {make}")
    return None


def check_kit(kit: Path) -> tuple[list[Finding], int, int]:
    modules = sorted(m for m in (kit / "modules").iterdir() if m.is_dir() and uses_shared_code(m))
    findings = [
        finding
        for module in modules
        for link, source in LINKS.items()
        if (finding := check_link(kit, module, link, source)) is not None
    ]
    return findings, len(modules), len(modules) * len(LINKS)


def report(findings: list[Finding], modules: int, links: int) -> int:
    counts = f"{links} link(s) in {modules} module(s) examined"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every module reaches the shared code through a link to its one source — {counts}")
    return EXIT_GREEN


def self_test() -> int:
    """Red→green on a throwaway kit: each wrong state must be red, the right link green."""

    def fresh(root: Path) -> Path:
        for source in LINKS.values():
            target = root / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.mkdir() if "." not in target.name else target.write_text("", encoding="utf-8")
        module = root / "modules" / "const-sample"
        (module / "hooks").mkdir(parents=True)
        (module / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
        for link, source in LINKS.items():
            (module / link).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(os.path.relpath(root / source, (module / link).parent), module / link)
        return module / "scripts" / "const_gate"

    def as_copy(link: Path) -> None:
        link.unlink()
        link.mkdir()

    def as_text_file(link: Path) -> None:
        link.unlink()
        link.write_text("../../../shared/const_gate", encoding="utf-8")

    def as_dangling(link: Path) -> None:
        link.unlink()
        os.symlink("../../../shared/no_such_gate", link)

    def as_elsewhere(link: Path) -> None:
        link.unlink()
        os.symlink("../tests", link)

    def as_absolute(link: Path) -> None:
        target = link.resolve()
        link.unlink()
        os.symlink(target, link)

    def as_missing(link: Path) -> None:
        link.unlink()

    def harness_as_copy(link: Path) -> None:
        harness = link.parent.parent / "tests" / "harness.py"
        harness.unlink()
        harness.write_text("", encoding="utf-8")

    def hookless_without_links(link: Path) -> None:
        """A generator alone: no hook, a script importing the shared code, and the link gone."""
        module = link.parent.parent
        (module / "hooks" / "hooks.json").unlink()
        (module / "hooks").rmdir()
        (module / "scripts" / "generate.py").write_text("from const_gate import cli\n", encoding="utf-8")
        link.unlink()

    wrong = {
        "a missing link": as_missing,
        "a copied harness in tests/": harness_as_copy,
        "a hookless module importing the shared code, its link missing": hookless_without_links,
        "a copy": as_copy,
        "a text file": as_text_file,
        "a dangling link": as_dangling,
        "a link leading elsewhere": as_elsewhere,
        "an absolute link": as_absolute,
    }
    failed = 0
    for name, damage in wrong.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            link = fresh(root)
            green_before = not check_kit(root)[0]
            damage(link)
            red_after = len(check_kit(root)[0]) == 1
        ok = green_before and red_after
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the right link is green, {name} is red")
    print(f"{len(wrong) - failed}/{len(wrong)} red→green cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-shared-links", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 links examined")
        return EXIT_BROKEN
    if args.self_test:
        return self_test()
    if not (KIT / "modules").is_dir():
        print(f"BROKEN: {KIT} has no modules/ directory — fix: run the script from a checkout of the kit")
        print("BROKEN: the check could not run — 0 links examined")
        return EXIT_BROKEN
    return report(*check_kit(KIT))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
