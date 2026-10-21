#!/usr/bin/env python3
"""Kit check: no installed component of a module names a place in someone's project, nor a document of
the kit.

The grep of requirement A12.1, as the row words it since decision
dec-0056-portability-grep-and-gate-lists. It reads the installed components of every module —
the files git lists under the module's `plugin/` folder, the folder that installs, in `skills/`, `hooks/`,
`scripts/`, `commands/`, `agents/`, the install note `INSTALL.md` and `.claude-plugin/`, never the module
document `MODULE.md`, never a module's `README.md`, which is reader prose like `MODULE.md` and held by
review, nor `tests/` or `evals/`, which stand beside `plugin/` and install nowhere —
and the shared gate code under `shared/constitution_layer_kit/`, which every module installs as its
`scripts/constitution_layer_kit`. A symbolic link is read at its source, once. A module is every folder under
`modules/` whose name opens with neither a dot nor an underscore, as `kit_module_doc.module_folders`
lists them for every kit check: a plain file there is none, a name without `const-` is one, and a
module folder without its `MODULE.md` is no tree the check can read (BROKEN), nor is a tree with no
`modules/`.

A finding is one of these forms, outside a public URL:
  - a path under a home directory: `/Users/…`, `/home/…`, `~/`, `$HOME/…`, `${HOME}/…` or a
    Windows user folder;
  - a `file:/` link;
  - a relative path with a slash and a file extension or a glob, `docs/notes.md`, `docs/**` or
    `**/docs/*.md`, that is no file or directory of the plugin, the module's `plugin/` folder; for the
    shared code, of the `plugin/` folder of any module. A glob whose parts before the last
    are all wildcards and whose last part is wildcards before an extension, `**/*.md`, names no
    particular place, so it is no finding; `**/decisions`, `**/.github`, `**/index.md` and `**/*`
    are findings.
    `constitution.yaml`, the one repository path a module may name, has no slash and so is never
    one;
  - a document folder of the kit, `docs/decisions`, `docs/research`, `docs/policies` or
    `docs/requirements`, as written, with no extension and no glob needed: the two segments whole,
    no letter, digit, `_`, `.` or `-` just before `docs`; after the second segment no letter, digit, `_`
    or `-` and no `.` with a letter, digit or `_` behind it, so a full stop closing a sentence is allowed
    (`mydocs/decisions`, `docs/decisionsx`, `docs/decisions-old` and `docs/decisions.v2` are none), and a
    slash after it and further segments are allowed (`docs/decisions/`, `a/docs/research/x`); a place
    already a finding in its line, a home path or a relative path that holds it, is not a second one.
Not read, by the forms above, the kit's folders included: in Markdown, fenced blocks and inline code,
which show an example to adapt, not a location. There is no exemption marker; an interpreter line is
read as any other, so `#!/usr/bin/env` passes and a home path there does not.

One more form, over the same files and the same shared code, a kit document's name; each is a
finding, with its why and its fix:
  - a fixed file name of the kit, a plain match, upper and lower case as written, no word bounds:
    `MODULE.md`, `requirements.md`, `rollout-plan`, `CONVENTIONS.md`, `GATE.md`, `kernel/`;
  - an id of a catalog the kit declares under `const-catalogs.catalogs` in its `constitution.yaml`,
    `<prefix>-<digits>`, the prefix and the number of digits read from the dials and never typed here:
    `width` as the catalog module reads it, an integer from 1 to 9, 4 when the entry has none. Matched
    in either case (`dec-0049`, `DEC-0049`), since the catalog module's skill says a bare id in prose
    resolves in either case; at word bounds: no letter, digit or `_` just before the prefix, none
    just after the digits, so a letter after the digits starts a slug only after a hyphen
    (`dec-0049-module-links-held-by-a-kit-check` is a name; `dec-0049x`, `dec-00490`, `dec-49` and
    `xdec-0049` are not).
    A prefix the kit does not declare, in a consumer's example, is no name.
It is read in every line, a fenced block and a code span too, since the forms of A12.1 read every
installed text; a public URL is no exception either. The kit's own `MODULE.md` is no installed
component and is not read, and neither are a module's `README.md`, `tests/` or `shared/GATE.md` —
of `shared/`, only `shared/constitution_layer_kit/`, which each module installs as its
`scripts/constitution_layer_kit`, is read. A prefix is looked for only where the dials declare it: a
`constitution.yaml` that is missing, is no YAML, lacks a `const-catalogs` mapping or its `catalogs` list, or
holds an entry that the catalog module would refuse for a prefix (a lowercase word of letters and digits,
listed once) or a width, is BROKEN, never a pass — stricter than the catalog module, which reads a namespace
or a list that is absent as no catalogs, since the kit always declares them and a check that looked for
nothing would pass in silence; `catalogs: []` declares none and is read so. PyYAML reads the file: without it
the check exits 1 with the install command.

A heuristic, as the row says: the bare-repository run on defaults stays the gate of record. Not
seen here — a folder named with neither an extension nor a glob, the kit's four document folders
aside, a system path such as `/srv/…`, a home path in a form not listed — is held by review, and by
that run where the path acts on a bare repository.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway tree: each form red with its count typed
                       by hand and green once fixed; every place not read stays green; the report
                       of one finding as literal lines with exit 2; a module folder not named
                       `const-` read as a module, a folder `.x` or `_x` and a plain file of
                       `modules/` not; a module folder without its `MODULE.md`, a tree with no
                       `modules/` and a file that is not UTF-8 as a BROKEN line; the modules
                       read sorted by name, whatever order the folder lists; the kit's four document
                       folders, red as written and green in code, in a URL and inside another name,
                       once where a relative path holds the same place; the kit documents' names:
                       each fixed name and each id form typed by hand, in an install note and in a
                       skill, red or green; the width, its default and a prefix added to the dials,
                       read from the dials file; fenced code, a code span and a URL read, a test,
                       the module document, a module's README, a folder named like an installed
                       part beside `plugin/` and `shared/GATE.md` not; the order of
                       the findings; the report as literal lines; each dials file that cannot be read,
                       and PyYAML missing, as a BROKEN line with its literal text.
Exit:   0 green; 2 a finding; 1 the check could not run.
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
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from kit_module_doc import DocumentError, module_folders

try:
    import yaml
except ImportError:
    print("BROKEN: PyYAML is not installed — fix: python3 -m pip install pyyaml")
    print("BROKEN: the check could not run — 0 files examined")
    sys.exit(1)

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
PLUGIN = "plugin"  # the module's folder that installs; MODULE.md, README.md, tests/, evals/ stand beside it
INSTALLED = ("skills/", "hooks/", "scripts/", "commands/", "agents/", "INSTALL.md", ".claude-plugin/")
SHARED = "shared/constitution_layer_kit"
DIALS = "constitution.yaml"
NAMESPACE = "const-catalogs"  # the dials namespace that declares the kit's numbered kinds
DEFAULT_WIDTH, MAX_WIDTH = 4, 9  # the catalog module's own: a width is a whole number from 1 to 9
PREFIX = re.compile(r"[a-z0-9]+")  # the catalog module's own form of a prefix, used with fullmatch
FIXED_NAMES = ("MODULE.md", "requirements.md", "rollout-plan", "CONVENTIONS.md", "GATE.md", "kernel/")
KIT_FOLDERS = ("docs/decisions", "docs/research", "docs/policies", "docs/requirements")

URL = re.compile(r"https?://[^\s)>\"'`]+")
HOME = re.compile(
    r"(?<![\w.$}~-])/(?:Users|home)/[^\s)>\"'`]*"
    r"|\$\{?HOME\}?/[^\s)>\"'`]*"
    r"|\b[A-Za-z]:[\\/]Users[\\/][^\s)>\"'`]*"
)
TILDE = re.compile(r"~/")
FILE_LINK = re.compile(r"\bfile:/")
KIT_FOLDER = re.compile(rf"(?<![\w.-])(?:{'|'.join(map(re.escape, KIT_FOLDERS))})(?![\w-]|\.\w)")
RELATIVE = re.compile(r"(?<![\w/.$}{~:*-])((?:[\w.*-]+/)+[\w.*-]*)")
WILDCARD = re.compile(r"\*+")
FILES_BY_EXTENSION = re.compile(r"\*+\.[A-Za-z0-9]{1,5}")
NAMES_A_FILE = re.compile(r"(\.[A-Za-z]{1,5}$|\*)")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1")
WHY = "a module installs into any project, so it names no place in one (law 2 of CLAUDE.md)"
FIXES = {
    "home": "name the place in words, or read it from the dials file",
    "tilde": "name the place in words, or read it from the dials file",
    "file": "link a public URL, or name the document in words",
    "relative": "write it `${CLAUDE_PLUGIN_ROOT}`-relative if it is the plugin's, read it from the dials"
    " file if it is the project's, or show it in a fenced example",
    "kit_folder": "name the place through the dials file, or, in a Markdown file, show it as an example in a"
    " fenced block or a code span",
    "kit_file": "say in words what the document holds, or drop the mention",
    "kit_id": "say in words what the item holds, or drop the mention; an example of a project's own id"
    " takes a prefix that const-catalogs.catalogs in the kit's constitution.yaml does not declare",
}
WHAT = {
    "home": "a path under a home directory",
    "tilde": "a path under `~/`",
    "file": "a `file:/` link",
    "relative": "a relative path that is no file of the plugin",
    "kit_folder": "a document folder of the kit",
    "kit_file": "a file name of the kit",
    "kit_id": "an id of a catalog the kit declares",
}
WHY_KIT = (
    "a module installs into any project, where the kit's own documents do not exist, so it names none"
    " of them (law 2 of CLAUDE.md)"
)
WHY_FOLDER = (
    "a module that names the kit's own folders carries the kit's layout into a project, where they do not"
    " exist (law 2 of CLAUDE.md)"
)
WHYS = {"kit_file": WHY_KIT, "kit_id": WHY_KIT, "kit_folder": WHY_FOLDER}  # the other forms give WHY


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    text: str

    def render(self) -> str:
        return (
            f"RED: {self.path}:{self.line}: {WHAT[self.kind]}, '{self.text}'\n"
            f"  why: {WHYS.get(self.kind, WHY)}\n"
            f"  fix: {FIXES[self.kind]}"
        )


@dataclass(frozen=True)
class Catalog:
    """A numbered kind of the kit, as its dials declare it: the prefix and the digits of an id."""

    prefix: str
    width: int


def listed(root: Path, where: str) -> list[str]:
    try:
        done = subprocess.run(
            ["git", "ls-files", "-z", "--", where], cwd=root, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as missing:
        raise Broken("git is not on PATH — fix: install git, then run the check again") from missing
    if done.returncode != 0:
        first = (done.stderr.splitlines() or ["no message"])[0]
        raise Broken(f"git ls-files failed: {first} — fix: run the check from a checkout of the kit")
    return sorted(p for p in done.stdout.split("\0") if p)


def read(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{path} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}) — fix: make it readable") from bad


def catalogs_of(root: Path) -> tuple[Catalog, ...]:
    """The numbered kinds the kit declares in its dials file, each prefix and width as the catalog module
    reads them. Anything the catalog module would refuse in a prefix or a width, and a namespace or a list
    it would read as no catalogs, is BROKEN here, with the fix."""
    try:
        text = (root / DIALS).read_text(encoding="utf-8")
    except FileNotFoundError as missing:
        raise Broken(
            f"{DIALS} is missing — fix: restore the dials file at the kit root, which declares the"
            f" numbered kinds whose ids no module names"
        ) from missing
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{DIALS} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad
    except OSError as bad:
        raise Broken(f"{DIALS} cannot be read ({bad.strerror}) — fix: make it readable") from bad
    try:
        dials = yaml.safe_load(text)
    except (yaml.YAMLError, ValueError) as bad:
        first = (str(bad).splitlines() or ["no message"])[0]
        raise Broken(f"{DIALS} is not YAML ({first}) — fix: repair the file") from bad
    namespace = dials.get(NAMESPACE) if isinstance(dials, dict) else None
    if not isinstance(namespace, dict):
        raise Broken(
            f"{DIALS} has no {NAMESPACE} mapping, so the kit's numbered kinds cannot be read — fix: declare"
            f" them under {NAMESPACE}.catalogs"
        )
    entries = namespace.get("catalogs")
    if not isinstance(entries, list):
        raise Broken(
            f"{NAMESPACE}.catalogs in {DIALS} is absent or no list, so the kit's numbered kinds cannot be"
            " read — fix: write it as a list of entries with a prefix, `[]` where the kit has none"
        )
    catalogs: list[Catalog] = []
    for position, entry in enumerate(entries, start=1):
        where = f"{NAMESPACE}.catalogs entry {position} in {DIALS}"
        if not isinstance(entry, dict):
            raise Broken(f"{where} is no mapping — fix: write it as prefix, width and territory")
        prefix = entry.get("prefix")
        if not isinstance(prefix, str) or not PREFIX.fullmatch(prefix):
            raise Broken(
                f"{where} has no prefix of lowercase letters and digits, which the catalog module"
                " refuses — fix: write the entry's prefix as one"
            )
        width = entry.get("width", DEFAULT_WIDTH)
        # YAML's true is an int to Python, and no width
        if isinstance(width, bool) or not isinstance(width, int) or not 1 <= width <= MAX_WIDTH:
            raise Broken(
                f"{where} has a width that is not a whole number from 1 to {MAX_WIDTH}, which the catalog"
                " module refuses — fix: write the width as one, or leave it out for 4"
            )
        if any(earlier.prefix == prefix for earlier in catalogs):
            raise Broken(
                f"{where} lists the prefix '{prefix}' a second time, which the catalog module refuses — fix:"
                " list each prefix once"
            )
        catalogs.append(Catalog(prefix, width))
    return tuple(catalogs)


def either_case(word: str) -> str:
    """A pattern for a lowercase word of letters and digits in either case, spelt out letter by letter:
    the ignore-case flag would let a few non-ASCII letters stand for an ASCII one."""
    return "".join(f"[{c}{c.upper()}]" if c.isalpha() else c for c in word)


def id_pattern(catalogs: tuple[Catalog, ...]) -> re.Pattern[str] | None:
    """An id of any declared catalog: its prefix in either case, a hyphen, exactly `width` digits, at word
    bounds on both sides; a slug after a hyphen is not part of the match."""
    if not catalogs:
        return None
    ids = "|".join(f"{either_case(c.prefix)}-[0-9]{{{c.width}}}" for c in catalogs)
    return re.compile(rf"(?<!\w)(?:{ids})(?!\w)")


def kit_names(path: str, text: str, ids: re.Pattern[str] | None) -> list[Finding]:
    """The kit documents a file names, in every line, a fenced block and a code span too: by line, and
    within a line by column, whichever form it is."""
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        hits = [
            (m.start(), "kit_file", m[0]) for name in FIXED_NAMES for m in re.finditer(re.escape(name), line)
        ]
        if ids:
            hits.extend((m.start(), "kit_id", m[0]) for m in ids.finditer(line))
        findings.extend(Finding(path, number, kind, named) for _, kind, named in sorted(hits))
    return findings


def examine(path: str, text: str, plugins: list[Path], ids: re.Pattern[str] | None) -> list[Finding]:
    """The findings of one file; `plugins` are the roots against which a relative path is looked up, `ids`
    the pattern of the kit's catalog ids. Each line's places first, then its kit documents."""
    findings = places(path, text, plugins)
    findings.extend(kit_names(path, text, ids))
    return sorted(findings, key=lambda found: found.line)  # stable: the order within a line stays


def places(path: str, text: str, plugins: list[Path]) -> list[Finding]:
    """The findings of the forms that name a place in a project. In a line, by kind: a home path, a `~/`,
    a `file:/` link, then the relative paths in the order they stand, then the kit's folders in the
    order they stand; the kit documents' names come after, in `examine`."""
    findings: list[Finding] = []
    markdown = path.endswith(".md")
    fence: str | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        if markdown:
            opener = FENCE.match(line)
            if fence is not None:
                if opener and opener[1][0] == fence[0] and len(opener[1]) >= len(fence):
                    fence = None
                continue
            if opener:
                fence = opener[1]
                continue
            line = CODE_SPAN.sub(" ", line)
        line = URL.sub(" ", line)
        taken: list[tuple[int, int]] = []  # where this line has a finding already: no second one there
        for kind, pattern in (("home", HOME), ("tilde", TILDE), ("file", FILE_LINK)):
            for m in pattern.finditer(line):
                findings.append(Finding(path, number, kind, m[0][:60]))
                taken.append((m.start(), token_end(line, m.start())))
        for m in RELATIVE.finditer(line):
            candidate = m[1].rstrip(".")
            if not NAMES_A_FILE.search(candidate):
                continue
            parts = candidate.split("/")
            if all(WILDCARD.fullmatch(part) for part in parts[:-1]) and FILES_BY_EXTENSION.fullmatch(
                parts[-1]
            ):
                continue  # wildcards, then wildcards before an extension: no particular place
            plain = candidate.split("*")[0].rstrip("/")
            if plain and any((plugin / plain).exists() for plugin in plugins):
                continue
            findings.append(Finding(path, number, "relative", candidate[:60]))
            taken.append((m.start(1), m.end(1)))
        findings.extend(
            Finding(path, number, "kit_folder", m[0])
            for m in KIT_FOLDER.finditer(line)
            if not any(start <= m.start() < end for start, end in taken)
        )
    return findings


def token_end(line: str, start: int) -> int:
    """Where the run of non-space characters that opens at `start` ends: the place a home path, a `~/`
    or a `file:/` link names reaches to."""
    end = start
    while end < len(line) and not line[end].isspace() and line[end] not in ")>\"'`":
        end += 1
    return end


def check_kit(root: Path) -> tuple[list[Finding], int, int]:
    try:
        modules = module_folders(root)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    ids = id_pattern(catalogs_of(root))
    findings: list[Finding] = []
    files = 0
    plugins = [module / PLUGIN for module in modules]
    for module, plugin in zip(modules, plugins, strict=True):
        prefix = f"modules/{module.name}/{PLUGIN}/"
        for path in listed(root, prefix):
            inside = path[len(prefix) :]
            if not inside.startswith(INSTALLED) or (root / path).is_symlink() or not (root / path).is_file():
                continue
            files += 1
            findings.extend(examine(path, read(root, path), [plugin], ids))
    for path in listed(root, SHARED):
        if (root / path).is_file():
            files += 1
            findings.extend(examine(path, read(root, path), plugins, ids))
    return findings, files, len(modules)


def report(findings: list[Finding], files: int, modules: int) -> int:
    counts = f"{files} installed file(s) of {modules} module(s) and the shared code examined"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: no installed component names a place in a project — {counts}")
    return EXIT_GREEN


@contextlib.contextmanager
def listed_in_reverse() -> Iterator[None]:
    """For the cases inside, `Path.iterdir` yields its entries sorted by name and reversed, whatever the
    filesystem lists: a case that holds an order is then red on every filesystem for a check that does not
    sort, never by the chance of a listing that happens to be unsorted. Restored on leaving."""
    real = Path.iterdir

    def reversed_iterdir(self: Path) -> Iterator[Path]:
        return iter(sorted(real(self), key=lambda path: path.name, reverse=True))

    Path.iterdir = reversed_iterdir  # type: ignore[method-assign,assignment]
    try:
        yield
    finally:
        Path.iterdir = real  # type: ignore[method-assign]


KIT_DIALS = """\
const-catalogs:
  catalogs:
    - prefix: dec
      width: 4
      territory:
        - "docs/decisions/**"
    - prefix: plc
      territory:
        - "docs/policies/**"
    - prefix: res
      width: 4
      territory:
        - "docs/research/**"
"""  # the kit's three catalogs; plc leaves its width out, which reads as the default 4


def write(root: Path, path: str, text: str | bytes) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        (root / path).write_bytes(text)
    else:
        (root / path).write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", path], cwd=root, check=True, capture_output=True)


def fresh(root: Path, dials: str | bytes | None = KIT_DIALS) -> None:
    """A throwaway kit: one module with a skill and an install note, the shared code, the dials file."""
    try:
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as failed:
        raise Broken(f"git init failed in {root} — fix: install git, then run the self-test") from failed
    write(root, "modules/const-x/MODULE.md", "A module.\n")
    write(root, "modules/const-x/plugin/skills/s/SKILL.md", "A skill.\n")
    write(root, "modules/const-x/plugin/INSTALL.md", "Install.\n")
    write(root, f"{SHARED}/model.py", "Y = 2\n")
    if dials is not None:
        write(root, DIALS, dials)


BESIDE_PLUGIN = ("MODULE.md", "README.md", "tests/")  # the toy module's files that stand beside `plugin/`


def at(path: str) -> str:
    """Where the toy kit keeps `path`: a part of the plugin under `plugin/`, a file beside it at the
    module's top, the shared code at its own place."""
    if path == "SHARED":
        return f"{SHARED}/state.py"
    return f"modules/const-x/{path if path.startswith(BESIDE_PLUGIN) else f'{PLUGIN}/{path}'}"


def self_test() -> int:
    """Red→green on a throwaway tree: each form is red where the check reads, with its number of
    findings typed by hand, and green once fixed; every place not read stays green; the report of
    one finding is its literal text with exit 2; a module folder not named `const-` is read; a file
    that is not UTF-8 is a teaching BROKEN."""
    red: dict[str, tuple[str, str, str, int]] = {  # case: file, green, red, its findings by hand
        "a home path in a script": (
            "scripts/gate.py",
            "ROOT = 'docs'\n",
            "ROOT = '/home/ann/project/docs'\n",
            1,
        ),
        "a macOS home path in a skill": (
            "skills/s/SKILL.md",
            "Read the dials file.\n",
            "Read /Users/ann/work/constitution.yaml.\n",
            1,
        ),
        "a tilde path in an install note": ("INSTALL.md", "Clone the kit.\n", "Clone into ~/kit.\n", 1),
        "a home path through the variable": ("scripts/gate.sh", "cd docs\n", "cd $HOME/work/notes.md\n", 1),
        "a braced home variable and a Windows user folder": (
            "INSTALL.md",
            "Install.\n",
            "Copy ${HOME}/x/y.md or C:\\Users\\ann\\x.md there.\n",
            2,
        ),
        "a glob ending in a folder after a wildcard": (
            "scripts/gate.py",
            "P = 'docs'\n",
            "P = '**/decisions'\n",
            1,
        ),
        "a glob ending in a dotted folder": ("scripts/gate.py", "P = 'docs'\n", "P = '**/.github'\n", 1),
        "a glob ending in a named file": ("scripts/gate.py", "P = 'docs'\n", "P = '**/index.md'\n", 1),
        "a glob of wildcards alone": ("scripts/gate.py", "P = 'docs'\n", "P = '**/*'\n", 1),
        "a glob naming a folder after a wildcard": (
            "skills/s/SKILL.md",
            'paths: "**/*.md"\n',
            'paths: "**/docs/decisions/*.md"\n',
            1,
        ),
        "a home path in an interpreter line": (
            "scripts/run.sh",
            "#!/usr/bin/env sh\n",
            "#!/home/ann/bin/sh\n",
            1,
        ),
        "a file link in a hook": ("hooks/hooks.json", '{"a": 1}\n', '{"a": "file:///srv/x"}\n', 1),
        "a project path in a message": (
            "scripts/gate/messages.py",
            "FIX = 'name it in the dials file'\n",
            "FIX = 'edit docs/decisions/index.md and docs/**'\n",
            2,
        ),
        "a path on the manifest": (
            ".claude-plugin/plugin.json",
            '{"name": "const-x"}\n',
            '{"name": "const-x", "docs": "notes/readme.md"}\n',
            1,
        ),
        "a project path in the shared code": ("SHARED", "X = 1\n", "X = 'var/data/state.json'\n", 1),
        "a kit file name in the shared code": ("SHARED", "X = 1\n", "# the rules are in GATE.md\n", 1),
        "a kit folder in an install note, in prose": (
            "INSTALL.md",
            "Install.\n",
            "See docs/decisions for more.\n",
            1,
        ),
        "a kit folder with a trailing slash": ("INSTALL.md", "Install.\n", "Read docs/research/ first.\n", 1),
        "a kit folder closing a sentence": ("INSTALL.md", "Install.\n", "Put them in docs/policies.\n", 1),
        "a kit folder with further segments": (
            "skills/s/SKILL.md",
            "A skill.\n",
            "Open docs/requirements/a5 now.\n",
            1,
        ),
        "a kit folder after other segments": ("scripts/gate.sh", "cd docs\n", "cd ../docs/decisions\n", 1),
        "a kit folder in a script string": ("scripts/gate.py", "P = 'docs'\n", "P = 'docs/research'\n", 1),
        "a kit folder in a hooks file, where no code is exempt": (
            "hooks/hooks.json",
            '{"a": 1}\n',
            '{"a": "docs/policies"}\n',
            1,
        ),
        "the four kit folders in one line": (
            "INSTALL.md",
            "Install.\n",
            "docs/decisions docs/research docs/policies docs/requirements\n",
            4,
        ),
        "a kit folder after a fenced block closed": (
            "INSTALL.md",
            "```\nx\n```\nInstall.\n",
            "```\nx\n```\nSee docs/decisions here.\n",
            1,
        ),
        "a kit folder in the shared code": ("SHARED", "X = 1\n", "X = 'docs/requirements'\n", 1),
    }
    green: dict[str, tuple[str, str]] = {  # case: file, text with a form the check does not read
        "the module document": ("MODULE.md", "See /home/ann/notes.md, docs/x.md, dec-0049 and GATE.md.\n"),
        "the module readme": ("README.md", "See /home/ann/notes.md, docs/x.md, dec-0049 and GATE.md.\n"),
        "a test": ("tests/run.py", "PATH = '/Users/someone/a.md'\nNAMES = 'MODULE.md dec-0049'\n"),
        "a system interpreter line": ("scripts/gate.sh", "#!/usr/bin/env sh\necho ok\n"),
        "a fenced example": ("INSTALL.md", "```yaml\npaths:\n  - docs/records/*.md\n```\n"),
        "inline code": ("skills/s/SKILL.md", "Name `docs/**` in the dial.\n"),
        "a public URL": ("INSTALL.md", "See https://example.org/~/docs/page.md for more.\n"),
        "a file of the plugin": ("INSTALL.md", "The skill is skills/s/SKILL.md.\n"),
        "a file of the plugin, named in the shared code": ("SHARED", "X = 'skills/s/SKILL.md'\n"),
        "the dials file": ("scripts/gate.py", "NAME = 'constitution.yaml'\n"),
        "a folder of the plugin by its glob": ("INSTALL.md", "Every skills/**/SKILL.md file.\n"),
        "wildcards before wildcards and an extension": ("skills/s/SKILL.md", 'paths: "**/*.md"\n'),
        "a path with no extension or glob": ("scripts/gate.py", "REF = 'refs/heads/main'\n"),
        "a plugin-root path": ("hooks/hooks.json", '{"args": ["${CLAUDE_PLUGIN_ROOT}/scripts/x/y.sh"]}\n'),
        "a kit folder with a glob in a fenced example": (
            "skills/s/SKILL.md",
            '```yaml\nterritory: ["docs/policies/**"]\n```\n',
        ),
        "a kit folder in a fenced example, with no glob": (
            "INSTALL.md",
            "```\ndocs/decisions\ndocs/research/\n```\n",
        ),
        "a kit folder in a code span": (
            "INSTALL.md",
            "Put them in `docs/decisions`, not `docs/research/`.\n",
        ),
        "a kit folder in a public URL": ("INSTALL.md", "See https://example.org/docs/decisions for more.\n"),
        "a kit folder in a URL with segments": (
            "INSTALL.md",
            "See (https://example.org/docs/policies/x) and <http://a.b/docs/research/>.\n",
        ),
        "a name ending in a kit folder's first segment": ("INSTALL.md", "Put them in mydocs/decisions.\n"),
        "a kit folder's name with more letters": ("INSTALL.md", "Put them in docs/decisionsx.\n"),
        "a kit folder's name with a dotted tail": (
            "INSTALL.md",
            "Put them in docs/decisions.v2 or docs/research.123.\n",
        ),
        "a kit folder's name with a hyphened tail": ("INSTALL.md", "Put them in docs/decisions-old.\n"),
        "a kit folder after a hyphened word": ("INSTALL.md", "Put them in my-docs/research.\n"),
        "a kit folder after a dotted word": ("INSTALL.md", "Put them in .docs/research.\n"),
        "a kit folder in other case": ("INSTALL.md", "Put them in Docs/Decisions.\n"),
        "docs with a different second segment": ("INSTALL.md", "Put them in docs/notes and docs/decision.\n"),
        "the second segment alone": ("INSTALL.md", "Put them in decisions or research.\n"),
    }
    report_lines = [  # the report of the tilde case, typed by hand: a message function cannot check itself
        "RED: modules/const-x/plugin/INSTALL.md:1: a path under `~/`, '~/'",
        "  why: a module installs into any project, so it names no place in one (law 2 of CLAUDE.md)",
        "  fix: name the place in words, or read it from the dials file",
        "RED: 1 finding(s) — 3 installed file(s) of 1 module(s) and the shared code examined",
    ]

    failed = 0
    for name, (path, good, bad, count) in red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, at(path), good)
            green_before = not check_kit(root)[0]
            write(root, at(path), bad)
            findings = check_kit(root)[0]
            red_after = len(findings) == count and all(f.path == at(path) for f in findings)
        ok = green_before and red_after
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the fixed text is green, {name} is red")
    for name, (path, text) in green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, at(path), text)
            ok = not check_kit(root)[0]
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is not a finding")
    with tempfile.TemporaryDirectory() as tmp:  # a module folder of another name is read too
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "modules/other/MODULE.md", "A module.\n")
        write(root, "modules/other/plugin/INSTALL.md", "Clone into ~/kit.\n")
        ok = [f.path for f in check_kit(root)[0]] == ["modules/other/plugin/INSTALL.md"]
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a module folder not named const- is read as a module")
    # the module folders, as the kit's one listing gives them: each class of what stands under modules/
    for name, extra in (
        ("a folder `.x` and a folder `_x` of modules/ are skipped silently", ("modules/.x", "modules/_x")),
        ("a plain file of modules/ is no module", ("modules/const-file",)),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            for path in extra:
                if path.endswith("file"):
                    write(root, path, "Clone into ~/kit.\n")
                else:
                    write(root, f"{path}/{PLUGIN}/INSTALL.md", "Clone into ~/kit.\n")
            result = check_kit(root)
        ok = result[0] == [] and result[2] == 1
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    with tempfile.TemporaryDirectory() as tmp:  # no MODULE.md: BROKEN, where the folder was read before
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "modules/other/plugin/INSTALL.md", "Install.\n")
        try:
            check_kit(root)
            ok = False
        except Broken as broken:
            ok = str(broken) == "modules/other has no MODULE.md — fix: restore the module document"
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
    with tempfile.TemporaryDirectory() as tmp:  # the findings follow the folders sorted by name
        root = Path(tmp).resolve()
        fresh(root)
        for module in ("const-b", "const-a"):
            write(root, f"modules/{module}/MODULE.md", "A module.\n")
            write(root, f"modules/{module}/plugin/INSTALL.md", "Clone into ~/kit.\n")
        with listed_in_reverse():  # modules/ is listed reversed, whatever the filesystem lists
            found = [f.path for f in check_kit(root)[0]]
    ok = found == ["modules/const-a/plugin/INSTALL.md", "modules/const-b/plugin/INSTALL.md"]
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the modules are read sorted by name, whatever order the folder lists")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, at("INSTALL.md"), red["a tilde path in an install note"][2])
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        (root / "modules/const-x/plugin/INSTALL.md").write_bytes(b"caf\xe9\n")
        try:
            check_kit(root)
            ok = False
        except Broken as broken:
            ok = str(broken).startswith("modules/const-x/plugin/INSTALL.md is not UTF-8") and "fix:" in str(
                broken
            )
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a file that is not UTF-8 is a teaching BROKEN line, never a traceback")
    named, named_failed = self_test_names()
    total = len(red) + len(green) + 8 + named
    failed += named_failed
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


@dataclass
class Cases:
    """The cases of the names self-test judged so far, and how many of them failed."""

    cases: int = 0
    failed: int = 0

    def case(self, ok: bool, text: str) -> None:
        """Count one case and print its line."""
        self.cases += 1
        self.failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {text}")


NOTE, SKILL = at("INSTALL.md"), at("skills/s/SKILL.md")
TYPED_FIXED_NAMES = ("MODULE.md", "requirements.md", "rollout-plan", "CONVENTIONS.md", "GATE.md", "kernel/")
TYPED_FOLDERS = ("docs/decisions", "docs/research", "docs/policies", "docs/requirements")


def seen(root: Path, path: str, text: str) -> list[tuple[str, int, str, str]]:
    """The findings with `path` holding `text` and the install note and the skill clean."""
    write(root, NOTE, "Install.\n")
    write(root, SKILL, "A skill.\n")
    write(root, path, text)
    return [(f.path, f.line, f.kind, f.text) for f in check_kit(root)[0]]


def broken_line(root: Path) -> str | None:
    """The BROKEN line the check ends on over this tree, None when it runs."""
    try:
        check_kit(root)
    except Broken as broken:
        return str(broken)
    return None


def run_fixed_names(c: Cases, root: Path) -> None:
    """Each fixed name is red in an install note and in a skill, once."""
    for name in TYPED_FIXED_NAMES:
        ok = all(
            seen(root, path, f"See {name} for more.\n") == [(path, 1, "kit_file", name)]
            for path in (NOTE, SKILL)
        )
        c.case(ok, f"{name} is red in an install note and in a skill, once")


def run_id_forms(c: Cases, root: Path) -> None:
    """Each id form typed by hand is red in an install note and in a skill, as the id it matched."""
    for written, matched in (
        ("dec-0049", "dec-0049"),
        ("DEC-0049", "DEC-0049"),
        ("Dec-0049", "Dec-0049"),
        ("dec-0049-module-links-held-by-a-kit-check", "dec-0049"),
        ("plc-0001", "plc-0001"),
        ("PLC-0001-x", "PLC-0001"),
        ("res-0012", "res-0012"),
        ("x-dec-0049", "dec-0049"),
        ("(see dec-0049.)", "dec-0049"),
    ):
        ok = all(
            seen(root, path, f"See {written} here.\n") == [(path, 1, "kit_id", matched)]
            for path in (NOTE, SKILL)
        )
        c.case(ok, f"{written} is red in an install note and in a skill, as '{matched}'")


def run_no_names(c: Cases, root: Path) -> None:
    """What is no name of the kit is green in an install note and in a skill."""
    for written in (
        "dec-49",
        "dec-00490",
        "xdec-0049",
        "dec-0049x",
        "_dec-0049",
        "dec-0049_x",
        "1dec-0049",
        "édec-0049",
        "dec 0049",
        "plc-00001",  # plc declares no width: the default, 4
        "adr-0007",
        "ADR-0007",
        "module.md",  # the fixed names are a plain match, case as written
        "gate.md",
        "Kernel/",
        "Requirements.md",
        "conventions.md",
        "Rollout-plan",
        "MODULExmd",  # and the dot of a name is a dot, no wildcard
        "requirementsXmd",
        "CONVENTIONS_md",
        "GATExmd",
    ):
        ok = all(seen(root, path, f"See {written} here.\n") == [] for path in (NOTE, SKILL))
        c.case(ok, f"{written} is no name of the kit, green in an install note and in a skill")


def run_text_read(c: Cases, root: Path) -> None:
    """Fenced code, a code span and a URL are read like any other text."""
    found = seen(root, NOTE, "```\nsee dec-0049\n```\nand `GATE.md` and `kernel/`.\n")
    c.case(
        found
        == [
            (NOTE, 2, "kit_id", "dec-0049"),
            (NOTE, 4, "kit_file", "GATE.md"),
            (NOTE, 4, "kit_file", "kernel/"),
        ],
        "a fenced block and a code span are read like any other text",
    )
    found = seen(root, NOTE, "https://example.org/dec-0049/MODULE.md\n")
    c.case(
        found == [(NOTE, 1, "kit_id", "dec-0049"), (NOTE, 1, "kit_file", "MODULE.md")],
        "a public URL is no exception",
    )


def run_unread(c: Cases, root: Path) -> None:
    """A module's own documents and tests, and the shared files outside the code, are not read."""
    for path in ("MODULE.md", "README.md", "tests/run.py"):
        c.case(
            seen(root, at(path), "MODULE.md dec-0049 GATE.md docs/decisions\n") == [],
            f"{path} of a module is not read",
        )
    c.case(
        seen(root, "modules/const-x/scripts/gate.py", "MODULE.md dec-0049 /home/ann/x GATE.md\n") == [],
        "a scripts/ folder beside plugin/ is not read: only plugin/ installs",
    )
    for path in ("shared/GATE.md", "shared/tests/run.py"):
        c.case(
            seen(root, path, "MODULE.md dec-0049 GATE.md docs/decisions\n") == [],
            f"{path} is not read: only {SHARED}/ is",
        )


def run_line_order(c: Cases, root: Path) -> None:
    """The findings go by line, a place before the names of its line, then by column."""
    found = seen(
        root,
        NOTE,
        "MODULE.md\n~/x\n~/a dec-0049 GATE.md MODULE.md\nplc-0001 rollout-plan\nMODULE.md GATE.md res-0012\n",
    )
    c.case(
        found
        == [
            (NOTE, 1, "kit_file", "MODULE.md"),
            (NOTE, 2, "tilde", "~/"),
            (NOTE, 3, "tilde", "~/"),
            (NOTE, 3, "kit_id", "dec-0049"),
            (NOTE, 3, "kit_file", "GATE.md"),
            (NOTE, 3, "kit_file", "MODULE.md"),
            (NOTE, 4, "kit_id", "plc-0001"),
            (NOTE, 4, "kit_file", "rollout-plan"),
            (NOTE, 5, "kit_file", "MODULE.md"),
            (NOTE, 5, "kit_file", "GATE.md"),
            (NOTE, 5, "kit_id", "res-0012"),
        ],
        "the findings go by line whatever the form, a place before the names of its line, then by column",
    )


def run_folder_forms(c: Cases, root: Path) -> None:
    """Each kit folder, as written, with a slash or with a path below it, is red once."""
    c.case(
        set(TYPED_FOLDERS) == set(KIT_FOLDERS) and len(KIT_FOLDERS) == len(TYPED_FOLDERS),
        "the self-test types the four folders of the check, no more and no fewer",
    )
    for folder in TYPED_FOLDERS:
        for written, matched in ((folder, folder), (f"{folder}/", folder), (f"{folder}/a/b", folder)):
            ok = all(
                seen(root, path, f"See {written} for more.\n") == [(path, 1, "kit_folder", matched)]
                for path in (NOTE, SKILL)
            )
            c.case(ok, f"{written} is red in an install note and in a skill, once, as '{matched}'")


def run_folder_places(c: Cases, root: Path) -> None:
    """A kit folder inside a place gives the one finding of the place, never a second for the folder."""
    for written, wanted in (
        ("edit docs/decisions/index.md now", [(NOTE, 1, "relative", "docs/decisions/index.md")]),
        ("a **/docs/decisions/*.md glob", [(NOTE, 1, "relative", "**/docs/decisions/*.md")]),
        ("at /Users/ann/docs/decisions now", [(NOTE, 1, "home", "/Users/ann/docs/decisions")]),
        ("at $HOME/docs/research now", [(NOTE, 1, "home", "$HOME/docs/research")]),
        ("at ~/docs/policies now", [(NOTE, 1, "tilde", "~/")]),
        ("at file:///docs/requirements now", [(NOTE, 1, "file", "file:/")]),
        ("docs/decisions.md", [(NOTE, 1, "relative", "docs/decisions.md")]),
        (
            "a docs/decisions/x.md and docs/research",
            [(NOTE, 1, "relative", "docs/decisions/x.md"), (NOTE, 1, "kit_folder", "docs/research")],
        ),
    ):
        c.case(
            seen(root, NOTE, f"{written}\n") == wanted,
            f"'{written}' gives the one finding of its place, never a second for the kit folder in it",
        )


def run_long_places(c: Cases, root: Path) -> None:
    """A place longer than 60 characters is quoted in its finding by its first 60."""
    for written, wanted in (
        (
            "at /Users/ann/projects/a-long-folder-name/and-a-second-long-one/notes.md now",
            [
                (NOTE, 1, "home", "/Users/ann/projects/a-long-folder-name/and-a-second-long-one")
            ],  # typed by hand
        ),
        (
            "edit docs/projects/a-long-folder-name/and-a-second-long-one/notes.md now",
            [
                (NOTE, 1, "relative", "docs/projects/a-long-folder-name/and-a-second-long-one/notes")
            ],  # by hand
        ),
    ):
        c.case(
            seen(root, NOTE, f"{written}\n") == wanted, f"a long place is cut to 60 characters: '{written}'"
        )


def run_folder_order(c: Cases, root: Path) -> None:
    """A kit folder sorts after the places of its line and before the documents; fenced text is not read."""
    found = seen(root, NOTE, "docs/decisions\n~/a docs/research x/y.md dec-0049 docs/policies\n")
    c.case(
        found
        == [
            (NOTE, 1, "kit_folder", "docs/decisions"),
            (NOTE, 2, "tilde", "~/"),
            (NOTE, 2, "relative", "x/y.md"),
            (NOTE, 2, "kit_folder", "docs/research"),
            (NOTE, 2, "kit_folder", "docs/policies"),
            (NOTE, 2, "kit_id", "dec-0049"),
        ],
        "a kit folder sorts after the places of its line, in the order they stand, before the documents",
    )
    found = seen(root, NOTE, "see docs/decisions/dec-0049 and MODULE.md\n")
    c.case(
        found
        == [
            (NOTE, 1, "kit_folder", "docs/decisions"),
            (NOTE, 1, "kit_id", "dec-0049"),
            (NOTE, 1, "kit_file", "MODULE.md"),
        ],
        "a kit folder and the id after it are two findings, the folder first",
    )
    found = seen(
        root,
        NOTE,
        "```\ndocs/decisions\n```\n`docs/research` and docs/policies. https://a.b/docs/requirements\n",
    )
    c.case(
        found == [(NOTE, 4, "kit_folder", "docs/policies")],
        "a fenced block, a code span and a URL are not read, the rest of the line is",
    )


def run_names_in_one_tree(c: Cases) -> None:
    """The cases that read one tree of a module with the kit's own dials, one after the other."""
    c.case(
        set(TYPED_FIXED_NAMES) == set(FIXED_NAMES) and len(FIXED_NAMES) == len(TYPED_FIXED_NAMES),
        "the self-test types the six fixed names of the check, no more and no fewer",
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        run_fixed_names(c, root)
        run_id_forms(c, root)
        run_no_names(c, root)
        run_text_read(c, root)
        run_unread(c, root)
        run_line_order(c, root)
        run_folder_forms(c, root)
        run_folder_places(c, root)
        run_folder_order(c, root)
        run_long_places(c, root)


def run_names_by_module(c: Cases) -> None:
    """The modules in reverse: the findings still go by name."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        for module in ("const-b", "const-a"):
            write(root, f"modules/{module}/MODULE.md", "A module.\n")
            write(root, f"modules/{module}/plugin/INSTALL.md", "See dec-0049.\n")
        with listed_in_reverse():
            paths = [f.path for f in check_kit(root)[0]]
    c.case(
        paths == ["modules/const-a/plugin/INSTALL.md", "modules/const-b/plugin/INSTALL.md"],
        "a name in two modules is reported by module name, whatever order the folder lists",
    )


def run_widths(c: Cases) -> None:
    """The width and the prefix of an entry of the dials file decide which ids are red."""
    width_five = (
        'const-catalogs:\n  catalogs:\n    - prefix: dec\n      width: 5\n      territory: ["d/**"]\n'
    )
    for name, dials, text, expect in (
        ("width 5 makes dec-00049 red", width_five, "dec-00049", [(NOTE, 1, "kit_id", "dec-00049")]),
        ("width 5 makes dec-0049 green", width_five, "dec-0049", []),
        ("width 5 makes dec-000490 green", width_five, "dec-000490", []),
        (
            "an entry with no width reads 4: dec-0049 red",
            "const-catalogs:\n  catalogs:\n    - prefix: dec\n",
            "dec-0049",
            [(NOTE, 1, "kit_id", "dec-0049")],
        ),
        (
            "an entry with no width reads 4: dec-00490 green",
            "const-catalogs:\n  catalogs:\n    - prefix: dec\n",
            "dec-00490",
            [],
        ),
        (
            "`catalogs: []` declares no id: dec-0049 green",
            "const-catalogs:\n  catalogs: []\n",
            "dec-0049",
            [],
        ),
        (
            "`catalogs: []` leaves the fixed names red",
            "const-catalogs:\n  catalogs: []\n",
            "MODULE.md",
            [(NOTE, 1, "kit_file", "MODULE.md")],
        ),
        (
            "a prefix with a digit, in either case: W3C-0001 red",
            "const-catalogs:\n  catalogs:\n    - prefix: w3c\n",
            "W3C-0001",
            [(NOTE, 1, "kit_id", "W3C-0001")],
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root, dials)
            c.case(seen(root, NOTE, f"See {text}.\n") == expect, name)
    with tempfile.TemporaryDirectory() as tmp:  # width 9, the upper bound the catalog module accepts
        root = Path(tmp).resolve()
        fresh(root, width_five.replace("width: 5", "width: 9"))
        c.case(
            broken_line(root) is None  # `and` stops here on a BROKEN: one FAIL line, no abort
            and seen(root, NOTE, "See dec-000000049 and dec-00000049 and dec-0000000049.\n")
            == [(NOTE, 1, "kit_id", "dec-000000049")],
            "width 9, the upper bound, is no BROKEN line and reads dec-000000049 red, 8 and 10 digits green",
        )
    with tempfile.TemporaryDirectory() as tmp:  # a prefix added to the dials, no code change
        root = Path(tmp).resolve()
        fresh(root)
        before = seen(root, NOTE, "See rfc-0001.\n")
        write(root, DIALS, KIT_DIALS + '    - prefix: rfc\n      territory: ["docs/rfc/**"]\n')
        after = seen(root, NOTE, "See rfc-0001.\n")
    c.case(
        before == [] and after == [(NOTE, 1, "kit_id", "rfc-0001")],
        "rfc-0001 is green until the dials declare rfc, then red",
    )


def run_name_reports(c: Cases) -> None:
    """The report of a file name with an id, and of a kit folder, as literal lines."""
    with tempfile.TemporaryDirectory() as tmp:  # the report of two findings, typed by hand
        root = Path(tmp).resolve()
        fresh(root)
        write(root, NOTE, "See MODULE.md and dec-0049-module-links-held-by-a-kit-check.\n")
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    why = (
        "  why: a module installs into any project, where the kit's own documents do not exist, so it names"
        " none of them (law 2 of CLAUDE.md)"
    )
    literal = [
        "RED: modules/const-x/plugin/INSTALL.md:1: a file name of the kit, 'MODULE.md'",
        why,
        "  fix: say in words what the document holds, or drop the mention",
        "RED: modules/const-x/plugin/INSTALL.md:1: an id of a catalog the kit declares, 'dec-0049'",
        why,
        "  fix: say in words what the item holds, or drop the mention; an example of a project's own id takes"
        " a prefix that const-catalogs.catalogs in the kit's constitution.yaml does not declare",
        "RED: 2 finding(s) — 3 installed file(s) of 1 module(s) and the shared code examined",
    ]
    c.case(
        code == EXIT_RED and printed.getvalue().splitlines() == literal,
        "the report of a file name and an id is its literal text, exit 2",
    )
    if printed.getvalue().splitlines() != literal:
        print(printed.getvalue())
    with tempfile.TemporaryDirectory() as tmp:  # the report of a kit folder, typed by hand
        root = Path(tmp).resolve()
        fresh(root)
        write(root, NOTE, "See docs/decisions for more.\n")
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    folder_report = [
        "RED: modules/const-x/plugin/INSTALL.md:1: a document folder of the kit, 'docs/decisions'",
        "  why: a module that names the kit's own folders carries the kit's layout into a project, where they"
        " do not exist (law 2 of CLAUDE.md)",
        "  fix: name the place through the dials file, or, in a Markdown file, show it as an example in a"
        " fenced block or a code span",
        "RED: 1 finding(s) — 3 installed file(s) of 1 module(s) and the shared code examined",
    ]
    c.case(
        code == EXIT_RED and printed.getvalue().splitlines() == folder_report,
        "the report of a kit folder is its literal text, exit 2",
    )
    if printed.getvalue().splitlines() != folder_report:
        print(printed.getvalue())


def broken_dials_cases() -> list[tuple[str, str | bytes | None, str | tuple[str, str]]]:
    """Each dials file that cannot be read: its name, its content (None: no file) and the line wanted,
    whole or as its start and its end."""
    where = "const-catalogs.catalogs entry"
    absent = (
        "const-catalogs.catalogs in constitution.yaml is absent or no list, so the kit's numbered kinds"
        " cannot be read — fix: write it as a list of entries with a prefix, `[]` where the kit has none"
    )
    no_namespace = (
        "constitution.yaml has no const-catalogs mapping, so the kit's numbered kinds cannot be read — fix:"
        " declare them under const-catalogs.catalogs"
    )
    no_prefix = (
        f"{where} 1 in constitution.yaml has no prefix of lowercase letters and digits, which the catalog"
        " module refuses — fix: write the entry's prefix as one"
    )
    no_width = (
        f"{where} 1 in constitution.yaml has a width that is not a whole number from 1 to 9, which the"
        " catalog module refuses — fix: write the width as one, or leave it out for 4"
    )
    one = "const-catalogs:\n  catalogs:\n"
    return [
        (
            "a dials file that is missing",
            None,
            "constitution.yaml is missing — fix: restore the dials file at the kit root, which declares the"
            " numbered kinds whose ids no module names",
        ),
        (
            "a dials file that is not UTF-8",
            b"\xe9\n",
            "constitution.yaml is not UTF-8 (invalid continuation byte at byte 0) — fix: save it as UTF-8",
        ),
        (
            "a dials file that is no YAML",
            "\tx: 1\n",
            "constitution.yaml is not YAML (while scanning for the next token) — fix: repair the file",
        ),
        (
            "a dials file whose YAML is a date no calendar has",
            "a: 2020-13-45\n",
            # PyYAML words the reason by the interpreter, so the line is held by its start and its end.
            ("constitution.yaml is not YAML (", ") — fix: repair the file"),
        ),
        ("a dials file that is a list", "- a\n", no_namespace),
        ("a dials file with no const-catalogs", "other: {}\n", no_namespace),
        ("a const-catalogs namespace with no value", "const-catalogs:\n", no_namespace),
        ("a const-catalogs namespace that is a list", "const-catalogs: [1]\n", no_namespace),
        ("a namespace with no catalogs", "const-catalogs:\n  severity: block\n", absent),
        ("catalogs with no value", "const-catalogs:\n  catalogs:\n", absent),
        ("catalogs that is a word", "const-catalogs:\n  catalogs: dec\n", absent),
        (
            "an entry that is a word",
            one + "    - dec\n",
            f"{where} 1 in constitution.yaml is no mapping — fix: write it as prefix, width and territory",
        ),
        ("an entry with no prefix", one + "    - width: 4\n", no_prefix),
        ("a prefix in capitals", one + "    - prefix: DEC\n", no_prefix),
        ("a prefix that is a number", one + "    - prefix: 7\n", no_prefix),
        ("a prefix with a hyphen", one + "    - prefix: a-b\n", no_prefix),
        ("an empty prefix", one + '    - prefix: ""\n', no_prefix),
        (
            "a bad prefix and a bad width: the prefix first",
            one + "    - prefix: A\n      width: 0\n",
            no_prefix,
        ),
        ("a width of true", one + "    - prefix: dec\n      width: true\n", no_width),
        ("a width of 0", one + "    - prefix: dec\n      width: 0\n", no_width),
        ("a width of 10", one + "    - prefix: dec\n      width: 10\n", no_width),
        ("a width that is a word", one + "    - prefix: dec\n      width: '4'\n", no_width),
        ("a width of 4.0", one + "    - prefix: dec\n      width: 4.0\n", no_width),
        ("a width with no value", one + "    - prefix: dec\n      width:\n", no_width),
        (
            "a prefix listed twice",
            one + "    - prefix: res\n    - prefix: dec\n    - prefix: dec\n",
            f"{where} 3 in constitution.yaml lists the prefix 'dec' a second time, which the catalog module"
            " refuses — fix: list each prefix once",
        ),
    ]


def run_broken_dials(c: Cases) -> None:
    """A dials file that cannot be read is a teaching BROKEN line, with its literal text."""
    for name, content, expect in broken_dials_cases():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root, content)
            line = broken_line(root)
            if isinstance(expect, tuple):
                start, end = expect
                text = line or ""
                holds = text.startswith(start) and text.endswith(end) and len(text) > len(start) + len(end)
            else:
                holds = line == expect
            c.case(holds, f"{name} is a teaching BROKEN line")
    with tempfile.TemporaryDirectory() as tmp:  # the dials file is read after the module folders
        root = Path(tmp).resolve()
        fresh(root, None)
        write(root, "modules/other/plugin/INSTALL.md", "Install.\n")
        c.case(
            broken_line(root) == "modules/other has no MODULE.md — fix: restore the module document",
            "a missing dials file and a module without MODULE.md: the module is reported",
        )


def run_yaml_missing(c: Cases) -> None:
    """PyYAML missing: a `yaml` that raises ImportError comes first."""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "yaml.py").write_text("raise ImportError('PyYAML is hidden')\n", encoding="utf-8")
        done = subprocess.run(
            [sys.executable, str(Path(__file__).resolve())],
            env={**os.environ, "PYTHONPATH": tmp},
            capture_output=True,
            text=True,
            check=False,
        )
    c.case(
        done.returncode == EXIT_BROKEN
        and done.stdout.splitlines()
        == [
            "BROKEN: PyYAML is not installed — fix: python3 -m pip install pyyaml",
            "BROKEN: the check could not run — 0 files examined",
        ]
        and done.stderr == "",
        "PyYAML missing is a BROKEN line with the install command, exit 1, no traceback",
    )


def self_test_names() -> tuple[int, int]:
    """The kit documents' names, case by case: every fixed name and every id form typed by hand, each in an
    install note and in a skill; what is no name; the width, the default and a prefix added to the dials
    read from the dials file; fenced code, a code span and a URL read; what is not read; the order of
    the findings; the report as literal lines; each dials file that cannot be read, with its literal line;
    PyYAML missing. Returns the number of cases and of those that failed."""
    c = Cases()
    run_names_in_one_tree(c)
    run_names_by_module(c)
    run_widths(c)
    run_name_reports(c)
    run_broken_dials(c)
    run_yaml_missing(c)
    return c.cases, c.failed


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-portability", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 files examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(*check_kit(KIT))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 files examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
