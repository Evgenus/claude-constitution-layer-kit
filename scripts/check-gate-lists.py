#!/usr/bin/env python3
"""Kit check: every scan a module declares stands in the kit's gate list, in its CI list and in its
module's job, the list's modules are exactly the module folders, each module folder is named
`const-<aspect>`, named so by its manifest, listed once in the marketplace and enabled in the kit's
settings, which declare the marketplace, every kit check is run by an entry of the gate group, every
top-level `const-<aspect>` key of the kit's dials file names a module folder, the `types` entry of
the gate list puts on `MYPYPATH` the module folders the schema mirror imports from and `../shared`, the
scan block of the install guide names every declared scan and nothing else, and each module folder has its
pair in the coverage map of the range check.

A module declares its scan in its document's enforcement section (template §9, anchor `t9`), read
by `kit_module_doc.enforcement` row by row, whatever a row's indent: a line whose stripped form
starts with `|`, the header and the separator skipped. A row opens `E<n>` or `**E<n>**`. A code span
in a row that reads exactly `<entry> --scan`, or `<entry>.py --scan`, declares a scan. A span
`<entry> --scan --<flag> …`, an explain mode (`--scan --command …`) or a report (`--scan --since …`),
is no tree scan and declares none, when the cell that holds it also holds the words `not a tree scan`
outside a code span. Each of these is a finding of the form, with the line, why and fix: a row whose
first cell is anything else; a span in a row that holds `--scan` in any other form; a flag after
`--scan` in a cell without the words; a span in the declared form in the section's prose, outside
the table (any other span there is not read). A row whose first cell is off has its spans read all
the same, and every row's last cell is read whether or not the row closes with a bar. A module
document whose enforcement section has no end, `t10` gone while a later anchor stands, or whose
`t10` stands elsewhere while another anchor, or none, follows `t9`, is no document the check can read
(BROKEN), since the section would run on into the acceptance table; the first message says to restore
`t10`, the second to put the sections in the template's order. For each
declared scan:
  - the gate list, the entries `sh scripts/gate-list.sh --names gate` prints, has one whose
    commands (`--show <entry>`) run `modules/<module>/plugin/scripts/<entry>.sh --scan` or `….py --scan`;
  - one such entry stands in the module's own job, the entries `--names <module>` prints for a job
    `--json` names, never in `kit` or another module's job, where a red would name no module or the
    wrong one;
  - every entry that runs it puts `PYTHONPATH="$PWD/shared"` before the command on the same line, as the
    list's `scan` function prints it, since a plugin holds no shared code (decision
    dec-0099-shared-code-installed-as-a-pip-package, R7) and a scan run without the kit's `shared/` on
    the path imports a release a person installed, or none; the setting after the command, in a comment,
    on another line of the entry, or another value, holds nothing;
  - the CI list is every entry of that script, when the lines of `.github/workflows/gates.yml`,
    comments aside — a whole comment line, or a `#` after a space or a tab — call
    `sh scripts/gate-list.sh --json` and `sh scripts/gate-list.sh --run`; a workflow that does not
    leaves every declared scan out of CI. That the matrix is built from the one and runs the other
    is the workflow's own text, held by review and by its run; that each entry falls in one of the
    jobs `--json` prints is the list script's own, its jobs read from its entries, not this check's.
Every folder under `modules/` whose name opens with neither a dot nor an underscore is a module
and must hold its `MODULE.md`: `kit_module_doc.module_folders`, the kit's one listing, which every
kit check that walks the modules reads, gives them sorted by name and fails when `modules/` or a
`MODULE.md` is missing, as a BROKEN here, and the self-test proves it over every class of entry
(`folder_probes`). A module that declares no scan is examined and needs no scan entry.
The list's modules, its `MODULES`, are read from its entries `install-<module>`, `fixtures-<module>`,
`lint-<module>` and `types-<module>` in `--names all`: each module folder has all four, and no
module that has one lacks its folder (decisions dec-0056-portability-grep-and-gate-lists,
dec-0058-ci-runs-each-check-in-parallel and dec-0061-ci-runs-one-job-per-module).
Each of those folders is also held against the three files that name a module, one RED finding with
why and fix for each copy that disagrees, listed by folder and then by file, the entries and keys that
name no module folder by name:
  - its name matches `const-[a-z0-9]+(-[a-z0-9]+)*` in full, kernel §7;
  - `modules/<m>/plugin/.claude-plugin/plugin.json` is a JSON object, and its `name` is the string `<m>`;
  - `.claude-plugin/marketplace.json` is a JSON object with a `name`, a non-empty string, the
    marketplace's name, read there and typed nowhere in this check, and a list `plugins`: for each
    folder exactly one entry, an object, whose `name` is `<m>`, whose `source` is the string
    `./modules/<m>/plugin`, the folder that installs, and whose `description` is the string the
    manifest's `description` is, character for character, a description missing or no string on either
    side being one finding, the manifest's named first, and a module with no entry or two being judged by
    those findings alone; no entry names anything that is no module folder, and an entry's other keys,
    the marketplace's other keys and its `owner` are the platform's and are never read;
  - `.claude/settings.json` is a JSON object: under `enabledPlugins` the key `<m>@<marketplace name>`
    is `true`, the JSON boolean and nothing else, for each folder, a committed `false` included, the one
    switch-off being a clone's git-ignored `.claude/settings.local.json`, which this check never reads;
    no other key ends `@<marketplace name>`, and keys of other marketplaces stand; under
    `extraKnownMarketplaces` the key `<marketplace name>` has a `source` that is exactly
    `{"source": "directory", "path": "."}`, the kit's own folder, other marketplaces and other keys of
    the value standing.
A file that cannot be read is BROKEN, not RED: one that is missing, is no JSON or is no JSON object, a
manifest included; a marketplace with no `name` that is a non-empty string, no list `plugins` or an
entry that is no object with a string `name`, since it is then no marketplace the check can compare;
`enabledPlugins` or `extraKnownMarketplaces` present and no object. A key the platform lets stand
absent, `enabledPlugins` or `extraKnownMarketplaces` in the settings, is read as empty and is RED for
what it leaves out. The green line counts the marketplace's entries and the enabled keys it read.
No code line of the list script or of the workflow, comments aside, names pytest save in an exact pin, so that
the gate list and CI never run pytest themselves and so never select some tests only: a module's tests run
through `python3 scripts/check-aspects.py --run --module <module>` (decision
dec-0080-fixtures-run-through-check-aspects), which builds the pytest command and runs it whole. That the
lists run them that way is held by review; this check holds the names. A word names pytest when it is `pytest`
or `py.test` standing as a word, after a path, `~/.venv/bin/pytest`, or stuck to `-m`, `-mpytest`; a name that
goes on, `pytest-xdist`, `pytest_plugins`, `pytest.ini`, one with another name before it, `allure-pytest`, and
an exact pin, `pytest==9.1.1`, name none, while an unpinned install and a range pin do. No code line passes
`--item`, the old runners' filter, or names `PYTEST_ADDOPTS`, through which any option reaches every run, a
line that clears it included. And no pytest configuration file in the folders a run of a module's tests reads
from the kit down — `pytest.toml`, `.pytest.toml`, `pytest.ini`, `.pytest.ini`, `pyproject.toml`, `tox.ini`,
`setup.cfg`, at the kit root, in `modules/`, in a module's folder or its `tests/` — holds a line `addopts =`
or `addopts:`, which adds its options to every run. A file above the kit root, which pytest may also read, is
outside the kit and not held; a code line ends at its first ` #`, inside quotes too.
Every `scripts/check-*.py` that git tracks at the top of `scripts/` (`git ls-files`; an untracked
file, a library such as `kit_module_doc.py` and a file in a folder are none) is run by an entry of the
gate group: a code line of that entry's `--show`, comments aside, holds `python3 scripts/check-<x>.py`
as whole words, with or without arguments — not after a name or path character, so `xpython3` and
`/usr/bin/python3` are no run, and not before one, so `check-<x>.py.bak` is none. The kit root must be
the git repository itself.
The kit's dials file, `constitution.yaml`, is read as YAML, Python 3 with PyYAML: a PyYAML that is not
installed is BROKEN with the install command, exit 1, before anything else is read. Every top-level key
of it that bears a module's name, `const-<aspect>` in full, names a module folder (kernel §7: a module's
namespace is its plugin name), one RED finding for each that does not, by key; a key of any other form,
a kernel key or a policy's namespace, a key that is no string, and a key below the top level, are not
judged. A dials file that is missing, is no YAML or is no mapping is BROKEN. The `types` entry of the
list, `--show types`, puts on `MYPYPATH` exactly the module folders `scripts/check-schema-mirror.py` puts
on its import path, each as `../modules/<m>/plugin/scripts`, and `../shared`, where the shared package stands
now that no plugin holds a link to it (decision dec-0099-shared-code-installed-as-a-pip-package, R7): the
folders are the strings of the one `for module in (...)` over a non-empty tuple of strings, read from the
syntax tree and never run; the entry's are the items of every `MYPYPATH=` setting on a code line of its
commands, comments aside, an empty element from a stray colon an item like another; the two are compared as
sets, `../shared` being one more of the wanted, and a difference is one RED finding naming both. A mirror
that is missing, is no Python or has not that one loop is BROKEN, and so is a list with no `types` entry.
These two holds come after every other kind of finding, the dials file's first.
The install guide, `INSTALL.md` at the kit root, holds one fenced block whose info string is `bash
check=scan`; its first line is `for s in <path> … ; do …`, and the words between `for s in` and `; do`
are the paths the guide runs with `sh`, each `<module>/plugin/scripts/<stem>.sh`, the POSIX entry point of a
declared scan, its stem the declared name without `.py`. The paths are held against the declared
scans both ways, after the types hold: a declared scan whose path the block does not list, and a listed
path no module declares, are one RED finding each, by path, the fix naming the path to add or to
remove; a path listed twice is no finding; a module that declares no scan owes none; the command after
`; do` and every other block are not read (`scripts/check-install-guide.py` runs the block and holds
none of this). A guide that is missing, with no such block or two, or whose block does not begin
`for s in … ; do`, is BROKEN, since the check cannot read what it holds.
The coverage map is `const-task-close.coverage` of the dials file, the code territories of the kit's
current-state documents, each an entry with a `name`, a `code` list and a `docs` list. It is held after
the guide's scan block, for each module folder: exactly one entry whose `name` is the folder's name (a
module with two is judged by that finding alone); its `docs` the one path `modules/<m>/MODULE.md`; every
`code` pattern opening with `modules/<m>/`, one finding for each that does not; and for each of the paths
`plugin/scripts`, `plugin/hooks`, `plugin/skills`, `tests` and `evals` that is a directory below the
module's folder, the pattern `modules/<m>/<path>/**` among its `code`, a pattern for a path that does
not exist being allowed. The installed parts sit in the module's `plugin/` folder, the tests and the
evals beside it, so a folder of one of those names at another place, `scripts/` at the module's top or
`tests/` inside `plugin/`, is none of them and is owed no pattern. The range check of module
`const-task-close` asks a change for a module's document only through its pair, so a module with no
pair, or code outside its pair, is never asked. A missing entry's fix is the whole entry in block style,
every existing folder listed. Entries named for no module folder (`shared-gate-code`, `kit-scripts`,
`kernel-schemas`) are not judged. A map that is absent or no list, or an entry that is no mapping with
a string `name` and `code` and `docs` lists of strings, is BROKEN.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway tree, itself a git repository: a scan missing
                       from the gate list, or from a workflow that does not read the list, red; a
                       scan in both green; an extra entry no gate; a span with a flag after `--scan`
                       and the words no scan; a scan whose entry falls into `kit` or another
                       module's job red; a scan whose command lacks `PYTHONPATH="$PWD/shared"`
                       before it on its line red, also when the setting stands after the command, in
                       a comment, on another line, with another value or as the end of a longer
                       name, and green after other commands on the line, one finding for the entry
                       that lacks it when two run the scan; a module folder the list leaves out,
                       and a listed module with no folder, red, its fix offering to restore the
                       folder only to a name `const-<aspect>`; an `--item` in the list or the
                       workflow red, and one in a comment green; a word that names pytest —
                       `-m pytest`, a path, `py.test`,
                       `-mpytest`, an unpinned install or a range pin — PYTEST_ADDOPTS and an
                       addopts line of a configuration file in the kit's folders a module's run
                       reads red, one in another folder green, an exact pin,
                       a name that goes on or has another before it and a comment green; the
                       folder name over a whole set of names; a manifest, a
                       marketplace entry, its description included, its source the module's folder,
                       another's plugin folder or one below its own red, an enabled key and the
                       declaration each changed one at a time, the platform's other keys allowed,
                       the marketplace renamed in all three places green and in each pair of them
                       red or green as the rule says,
                       the name read and never typed; the findings of every kind as literal
                       lines with exit 2, whatever the order of the files' keys, of their lists
                       and of the folder listing, and each file the check cannot read as its
                       literal BROKEN line with exit 1; the forms of the enforcement table over
                       one whole set of probes (indent, bold, first cells, span forms, the words,
                       an escaped bar);
                       a tracked check no entry of the gate group runs red, also when only an
                       extra entry, a fixtures entry or a comment names it, one a gate entry runs
                       green, with arguments too, the same file untracked, a library and a
                       module's script of that name no check, and the name filter over a whole
                       set of names; the report of each kind of finding, the form's and the
                       checks' included, as literal lines with exit 2, and of a green kit as its
                       literal line; a list that cannot be read, jobs that are no JSON list, a
                       module document without its enforcement anchor, with it on a heading or
                       twice, without its end anchor with a later one standing, or with `t11` before
                       it, a module folder without its document, a tree that is no repository
                       and a git that cannot be run, each a BROKEN line; a `.py` scan held by its
                       python3 line and taught by it; the dials file's keys over a whole set of
                       names, each file of those two holds that cannot be read as its BROKEN line,
                       the types pair changed one at a time (a folder more on either side, none, a
                       comment, another path, a quote, two settings, a stray colon), and PyYAML
                       missing as a BROKEN line with the install command, exit 1; the guide's scan
                       block against the declared scans (a block of exactly those, a scan missing, a
                       path no module declares, a path twice, a module with no scan, a path at the
                       module's top outside `plugin/`), each fix text
                       followed on the tree until green, and a guide that is missing, has no block,
                       two, or a block that does not begin `for s in … ; do` as a BROKEN line; the
                       coverage map against the module folders (every module with its pair, a module
                       with no entry, two entries, other docs, a pattern outside the module, a folder
                       present with no pattern, an absent folder with one, the three non-module entries
                       ignored, `scripts/`, `hooks/` and `skills/` at the module's top and `tests/`
                       and `evals/` inside `plugin/` no folders of the map, a map that cannot be read
                       as a BROKEN line), each fix text followed on
                       the tree until green. The self-test reads the map under a dials key no module
                       bears, so that its trees need no module named for the real one.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, replace
from enum import StrEnum
from pathlib import Path
from typing import Any

from kit_module_doc import DocumentError, Fault, Problem, enforcement, module_folders

try:
    import yaml
except ImportError:
    print("BROKEN: PyYAML is not installed — fix: python3 -m pip install pyyaml")
    print("BROKEN: the check could not run — 0 module documents examined")
    sys.exit(1)

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
GATE_LIST = "scripts/gate-list.sh"
WORKFLOW = ".github/workflows/gates.yml"
READS_LIST = ("sh scripts/gate-list.sh --json", "sh scripts/gate-list.sh --run")
KINDS = ("install", "fixtures", "lint", "types")  # the entries the list gives each of its MODULES
OF_MODULE = re.compile(rf"({'|'.join(KINDS)})-(.+)")
WHY = "a scan the kit does not run holds nothing, and the lists are where the kit says what it runs"
WHY_JOB = (
    "a module's scan runs in that module's job, so a red CI line names the module whose rule the tree broke"
)
SHARED_SETTING = 'PYTHONPATH="$PWD/shared"'  # what the list's `scan` function puts before a module's scan
SHARED_SET = re.compile(r"(?<!\w)" + re.escape(SHARED_SETTING) + r"(?=\s)")  # the setting as a word
WHY_PATH = (
    "a plugin holds no shared code, so a scan run without the kit's shared/ first on PYTHONPATH imports a"
    " release a person installed, or none, and the gate list would not check the change's own code"
)
WHY_MISSING = "a module the list leaves out is never installed, run, linted or typed in CI"
WHY_STRAY = (
    "the list's modules are exactly the module folders, and an entry of a missing module checks nothing"
)
ITEM_FILTER = re.compile(
    r"(?<![\w-])--item(?![\w-])"
)  # the old runners' filter, `--item <n>` or `--item=<n>`
PYTEST_NAME = re.compile(r"py\.?test")  # pytest's two command names, `pytest` and `py.test`
NAME_GOES_ON = re.compile(
    r"[\w-]|\.\w|=="
)  # after the name: `pytest-xdist`, `pytest.ini`, a pin `pytest==9.1.1`
STUCK_TO_M = re.compile(
    r"(?:^|[\s'\"])-[A-Za-z]*m$"
)  # before the name: `-mpytest`, `-Impytest`, `"-mpytest"`
WORD_START = re.compile(
    r"(?:-[A-Za-z]*m|[\w.~${}/-]*/)?$"
)  # the part of the word before the name: `~/.venv/bin/`, `-m`
# the configuration files pytest 9 looks for, in the folder of its arguments and each one above it
PYTEST_CONFIGS = (
    "pytest.toml",
    ".pytest.toml",
    "pytest.ini",
    ".pytest.ini",
    "pyproject.toml",
    "tox.ini",
    "setup.cfg",
)
ADDOPTS = re.compile(r"^\s*addopts\s*[=:]")  # an ini file takes `addopts =` and `addopts:`
EVERY_RUN = "through which any option, a selection included, reaches every pytest run"
ASPECTS_RUN = "python3 scripts/check-aspects.py --run --module <module>"  # the one way a module's tests run
WHY_FILTER = "the gate list and CI run every item of every runner, so that their green is a full pass"
WHY_FORM = "a scan the check cannot read is never held in the gate list and CI"
KIT_CHECK = re.compile(
    r"scripts/check-[^/]+\.py"
)  # a tracked path, whole: a check stands at the top of scripts/
WHY_CHECK = "a kit check no entry runs is never run in CI, and its green says nothing"
NAME = re.compile(
    r"const-[a-z0-9]+(?:-[a-z0-9]+)*"
)  # kernel §7: `const-<aspect>`, kebab-case, the whole name
MARKETPLACE_FILE = ".claude-plugin/marketplace.json"
SETTINGS_FILE = ".claude/settings.json"
DIALS = "constitution.yaml"
MIRROR = "scripts/check-schema-mirror.py"  # puts the kit-side module folders on its import path
TYPES_ENTRY = "types"  # the entry of the list that type-checks the shared code and the kit's scripts
MYPYPATH = re.compile(r"(?<![\w-])MYPYPATH=(\S*)")
TYPES_SHARED = "../shared"  # where the module folders and the kit's scripts find the shared package
DIRECTORY_SOURCE = {"source": "directory", "path": "."}  # the kit's own folder, as a settings source
WHY_NAME = (
    "the kernel names every module `const-<aspect>`, lowercase kebab-case, and the CI gives a job"
    " Claude Code by that prefix"
)
WHY_MANIFEST = (
    "a plugin installs under its manifest's name, so a name that is not the folder's splits the install"
    " from the marketplace entry and the settings key"
)
WHY_MARKET = "a module the marketplace leaves out cannot be installed, by the kit's CI or by a consumer"
WHY_SOURCE = (
    "the marketplace tells the platform where a plugin loads from, and a source that is not the module's"
    " plugin folder loads another plugin or none"
)
WHY_TWICE = (
    "a plugin's name must lead to one source, and with two entries it is open which one an install reads"
)
WHY_MARKET_STRAY = (
    "the marketplace lists exactly the module folders, and an entry that names no module folder is a"
    " plugin no module backs"
)
WHY_DESCRIPTION = (
    "a module's README opens with its manifest's description, so a marketplace entry that words it"
    " otherwise shows an installer another text for the same module"
)
WHY_NAMESPACE = (
    "a module reads only the dials namespace named after its plugin (kernel §7), so a namespace that names"
    " no module folder is a dial nobody applies"
)
WHY_TYPES = (
    "the schema mirror imports gate code from those module folders and the shared package from shared/, so"
    " the type check of the kit's scripts resolves them only through a MYPYPATH that names the same folders"
    " and ../shared"
)
WHY_ENABLED = (
    "the kit's sessions load only the plugins its committed settings enable, and the one switch-off,"
    " `false`, belongs in a clone's .claude/settings.local.json"
)
WHY_ENABLED_STRAY = (
    "the settings enable exactly the module folders, and a key that names no module folder enables a"
    " plugin no module backs"
)
WHY_KNOWN = (
    "a session finds the kit's plugins only through a marketplace its settings declare, and the enabled"
    " keys name it"
)
WHY_KNOWN_SOURCE = (
    "the kit loads its own modules from its own folder, so any other source loads another marketplace or none"
)
GUIDE_FILE = "INSTALL.md"  # the install guide; its `bash check=scan` block runs every scan of a project
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")  # as scripts/check-install-guide.py opens a block
SCAN_FOR = re.compile(r"for s in (.*?)\s*; do(?:\s|$)")  # the first line of the guide's scan block
BLOCK = "`bash check=scan`"
WHY_GUIDE = (
    "the guide's scan block is what a project runs to verify an install, so a scan it leaves out is never"
    " run there and a path no module declares fails there"
)
COVERAGE_OWNER = "const-task-close"  # the dials namespace whose `coverage` key is the range check's map
COVERAGE_KEY = "coverage"
COVERAGE_FOLDERS = (  # the folders that carry code, as paths below a module folder: the plugin's three, then
    "plugin/scripts",  # the module's own `tests` and `evals`, which stay outside the plugin folder
    "plugin/hooks",
    "plugin/skills",
    "tests",
    "evals",
)
WHY_COVERAGE = (
    "the range check of module const-task-close asks a change for a module's document only through the"
    " module's pair, so a module with no pair, or code outside its pair, is never asked"
)


@dataclass
class Dial:
    """Where the coverage map stands. The self-test points `owner` at a key no module bears, so that its
    throwaway trees need no module folder named for the owner; the plain run reads the real one."""

    owner: str = COVERAGE_OWNER


COVERAGE = Dial()


@contextlib.contextmanager
def coverage_owner(key: str) -> Iterator[None]:
    """For the code inside, the coverage map is read under the dials key `key`. Restored on leaving."""
    saved = COVERAGE.owner
    COVERAGE.owner = key
    try:
        yield
    finally:
        COVERAGE.owner = saved


def coverage_entry(module: str, folders: tuple[str, ...]) -> str:
    """The pair of a module as the kit writes it in block style, one pattern for each folder given, each a
    path below the module folder (`plugin/scripts`, `tests`), the module's document as its docs; an empty
    `code` is the one flow-style list."""
    code = (
        ["      code:", *(f'        - "modules/{module}/{folder}/**"' for folder in folders)]
        if folders
        else ["      code: []"]
    )
    return "\n".join(
        [f"    - name: {module}", *code, "      docs:", f'        - "modules/{module}/MODULE.md"']
    )


FORM_WHAT = {  # what a problem of the enforcement section says; its text is the first cell or the span
    Fault.FIRST_CELL: "a row of its enforcement table opens with {}, not E<n>",
    Fault.SPAN: "its enforcement table names `--scan` in a form the check cannot read: {}",
    Fault.UNMARKED: (
        "its enforcement table has a flag after `--scan` in {}, and the words `not a tree scan` are not in"
        " the cell that holds the span, outside a code span"
    ),
    Fault.PROSE: "{} declares a scan outside the enforcement table",
}
_FORM_SPAN_FIX = (
    "write it `<entry> --scan`, or, for a mode that is no tree scan, `<entry> --scan --<flag> …`"
    " with the words `not a tree scan` in the same cell as the span, outside the code span"
)
FORM_FIX = {
    Fault.FIRST_CELL: "open the row with E<n>, its number in the table",
    Fault.SPAN: _FORM_SPAN_FIX,
    Fault.UNMARKED: _FORM_SPAN_FIX,
    Fault.PROSE: "move it into a row of the enforcement table, or write it another way",
}


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


class Where(StrEnum):
    GATE = "gate list"
    CI = "CI list"
    JOB = "module's job"
    PATH = "scan's PYTHONPATH"
    MISSING = "list's modules"
    STRAY = "module folders"
    FILTER = "test selection"
    FORM = "enforcement table"
    CHECK = "kit checks"
    NAME = "folder name"
    MANIFEST = "manifest"
    MARKETPLACE = "marketplace entry"
    MARKET_SOURCE = "marketplace source"
    MARKET_TWICE = "marketplace entries"
    MARKET_STRAY = "marketplace strays"
    MARKET_DESCRIPTION = "marketplace description"
    DIALS_KEY = "dials namespace"
    TYPES_PATH = "types entry"
    SETTINGS = "enabled plugin"
    SETTINGS_STRAY = "enabled strays"
    KNOWN_MISSING = "declared marketplace"
    KNOWN_SOURCE = "marketplace source declared"
    GUIDE_ADD = "guide's scan block"
    GUIDE_DROP = "guide's listed paths"
    COVERAGE_MISSING = "coverage pair"
    COVERAGE_TWICE = "coverage pairs"
    COVERAGE_DOCS = "coverage docs"
    COVERAGE_OUTSIDE = "coverage pattern"
    COVERAGE_FOLDER = "coverage folder pattern"


REGISTRY = frozenset(
    {
        Where.NAME,
        Where.MANIFEST,
        Where.MARKETPLACE,
        Where.MARKET_SOURCE,
        Where.MARKET_TWICE,
        Where.MARKET_STRAY,
        Where.MARKET_DESCRIPTION,
        Where.SETTINGS,
        Where.SETTINGS_STRAY,
        Where.KNOWN_MISSING,
        Where.KNOWN_SOURCE,
    }
)  # the findings about the files that name a module, in `Finding.registry`
COVERAGE_WHERE = frozenset(
    {
        Where.COVERAGE_MISSING,
        Where.COVERAGE_TWICE,
        Where.COVERAGE_DOCS,
        Where.COVERAGE_OUTSIDE,
        Where.COVERAGE_FOLDER,
    }
)  # the findings about a module's pair in the coverage map, in `Finding.coverage`


def plugin_source(module: str) -> str:
    """The marketplace `source` of the module folder `module`: its plugin folder, the one that installs."""
    return f"./modules/{module}/plugin"


@dataclass(frozen=True)
class Finding:
    module: str
    where: Where
    entry: str = ""  # the declared scan, `<entry>` or `<entry>.py`
    runner: str = ""  # the list's entry that runs the scan
    job: str = ""  # the job that entry stands in, empty for none
    names: tuple[str, ...] = field(default=())  # the list's entries of a module
    line: int = 0  # a selection or a form: its line in the file, `module` holding the file's path
    fault: Fault = Fault.SPAN  # a form: what is wrong; `entry` then holds the first cell or the span
    said: str = ""  # a registry finding: what the file holds, as JSON text; empty: it holds nothing there
    tag: str = ""  # a registry finding: the marketplace name, read from marketplace.json
    side: str = ""  # a description finding: which text is wrong, "manifest", "entry" or "differs"
    owner: str = ""  # a coverage finding: the dials key that holds the map; `said` the detail, `names` the
    # folders the module has when its pair is missing

    def render(self) -> str:
        if self.where in (Where.FILTER, Where.CHECK, Where.FORM):
            return self.report_alone()
        what, why, fix = self.parts()
        return f"RED: {self.module}: {what}\n  why: {why}\n  fix: {fix}"

    def report_alone(self) -> str:
        """The whole report of a finding about a line of a file, a kit check or a form, whose `module` holds
        the path: it names no module."""
        if self.where is Where.FILTER and self.entry == "PYTEST_ADDOPTS":
            return (
                f"RED: {self.module}:{self.line}: it names `PYTEST_ADDOPTS`, {EVERY_RUN}\n  why: {WHY_FILTER}"
                f"\n  fix: remove `PYTEST_ADDOPTS` and its value from line {self.line} of {self.module}"
            )
        if self.where is Where.FILTER and self.entry == "addopts":  # a line of a configuration file
            return (
                f"RED: {self.module}:{self.line}: it sets `addopts`, {EVERY_RUN}\n  why: {WHY_FILTER}"
                f"\n  fix: remove the `addopts` setting at line {self.line}, with any lines that continue it,"
                f" from {self.module}"
            )
        if self.where is Where.FILTER and self.entry == "--item":
            return (
                f"RED: {self.module}:{self.line}: it passes `--item`, which selects some tests only"
                f"\n  why: {WHY_FILTER}\n  fix: remove `--item` and what it selects from line {self.line} of"
                f" {self.module}"
            )
        if self.where is Where.FILTER:  # a word that names pytest
            return (
                f"RED: {self.module}:{self.line}: it names `{self.entry}`, and the lists' code lines "
                "name pytest only in an exact pin `pytest==<version>`: a module's tests run only "
                f"through `{ASPECTS_RUN}`, which runs them whole\n  why: {WHY_FILTER}\n  fix: where "
                f"line {self.line} of {self.module} runs pytest, run the module's tests through "
                f"`{ASPECTS_RUN}` in its place; where it installs pytest, pin it as "
                "`pytest==<version>`; elsewhere, reword the line so that it names pytest no more"
            )
        if self.where is Where.CHECK:  # `module` holds the check's path
            return (
                f"RED: {self.module} is run by no entry of the gate group\n  why: {WHY_CHECK}"
                f"\n  fix: add an entry to GATES in {GATE_LIST} and an arm in commands() that runs"
                f" `python3 {self.module}`, with its `--self-test` where it has one"
            )
        shown = f"`{self.entry}`" if self.entry else "nothing"
        return (
            f"RED: {self.module}:{self.line}: {FORM_WHAT[self.fault].format(shown)}"
            f"\n  why: {WHY_FORM}\n  fix: {FORM_FIX[self.fault]}"
        )

    def parts(self) -> tuple[str, str, str]:
        """What, why and fix of every finding that reports under its module's name."""
        if self.where in REGISTRY:
            return self.registry()
        if self.where in COVERAGE_WHERE:
            return self.coverage()
        if self.where in (Where.GATE, Where.CI, Where.JOB, Where.PATH):
            return self.scan_parts()
        if self.where in (Where.DIALS_KEY, Where.GUIDE_ADD, Where.GUIDE_DROP, Where.TYPES_PATH):
            return self.file_parts()
        return self.list_parts()

    def scan_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a declared scan that the gate list, the CI list or the module's job lacks, or
        whose command in the gate list does not put the kit's shared/ on PYTHONPATH."""
        if self.where is Where.GATE:
            run = (
                f"python3 modules/{self.module}/plugin/scripts/{self.entry} --scan"
                if self.entry.endswith(".py")
                else f"sh modules/{self.module}/plugin/scripts/{self.entry}.sh --scan"
            )
            what = f"its scan `{self.entry} --scan` is not in the {self.where}"
            fix = f"add an entry to the gate group of {GATE_LIST} that runs `{SHARED_SETTING} {run}`"
            return what, WHY, fix
        if self.where is Where.PATH:
            what = (
                f"its scan `{self.entry} --scan`, the entry `{self.runner}`, runs without {SHARED_SETTING}"
                " before its command"
            )
            fix = (
                f"in the `{self.runner}` arm of commands() in {GATE_LIST}, write the scan as"
                f" `scan <command>`, which prints {SHARED_SETTING} before the command"
            )
            return what, WHY_PATH, fix
        if self.where is Where.CI:
            what = f"its scan `{self.entry} --scan` is not in the {self.where}"
            fix = (
                f"let {WORKFLOW} build its jobs from `{READS_LIST[0]}` and run each with"
                f" `{READS_LIST[1]} <job>`"
            )
            return what, WHY, fix
        held = f"the CI job `{self.job}`" if self.job else "no CI job"
        what = f"its scan `{self.entry} --scan`, the entry `{self.runner}`, runs in {held}, not in its own"
        fix = f"map the entry to its module in job() of {GATE_LIST}: `{self.runner}) echo {self.module} ;;`"
        return what, WHY_JOB, fix

    def file_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a finding about the dials file, the install guide or the `types` entry."""
        if self.where is Where.DIALS_KEY:  # `module` holds the key
            what = f"{DIALS} has a top-level key for it, but modules/{self.module} is no module folder"
            fix = (
                f"rename the key `{self.module}` in {DIALS} to the name of the module folder whose dials it"
                " holds, or remove the key and what is under it"
            )
            return what, WHY_NAMESPACE, fix
        if self.where is Where.GUIDE_ADD:
            what = f"its scan `{self.entry} --scan` is not in the scan block of {GUIDE_FILE}"
            fix = (
                f"add `{scan_path(self.module, self.entry)}` to the list after `for s in` in the {BLOCK}"
                f" block of {GUIDE_FILE}"
            )
            return what, WHY_GUIDE, fix
        if self.where is Where.GUIDE_DROP:  # `module` holds the path
            what = f"the scan block of {GUIDE_FILE} lists it, but no module declares that scan"
            fix = (
                f"remove `{self.module}` from the list after `for s in` in the {BLOCK} block of {GUIDE_FILE}"
            )
            return what, WHY_GUIDE, fix
        # Where.TYPES_PATH: `module` holds the list's path, `said` the entry's MYPYPATH
        folders = ":".join([*(f"../modules/{name}/plugin/scripts" for name in self.names), TYPES_SHARED])
        held = f"`{self.said}`" if self.said else "nothing"
        what = f"its `{TYPES_ENTRY}` entry puts {held} on MYPYPATH, but {MIRROR} imports from `{folders}`"
        fix = (
            f"in the `{TYPES_ENTRY}` entry of {GATE_LIST}, set MYPYPATH to `{folders}`, one setting, on"
            " the command that type-checks scripts/*.py"
        )
        return what, WHY_TYPES, fix

    def list_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a module the list lacks entries for, or entries of a name with no folder."""
        spans = ", ".join(f"`{name}`" for name in self.names)
        if self.where is Where.MISSING:
            fix = (
                f"add `{self.module}` to MODULES in {GATE_LIST}, which gives each module its install,"
                " fixtures, lint and types entries"
            )
            return f"the list lacks its entries {spans}", WHY_MISSING, fix
        what = f"the list has its entries {spans}, but modules/{self.module} is no module folder"
        # restoring the folder turns the check green only for a name that can be a module folder's,
        # `const-<aspect>`; for any other name a restored folder stays red, being skipped as no module
        # (`_draft`, `.x`) or turning the folder-name finding on (`glossary`), and the removal is the fix
        restore = (
            f", or restore modules/{self.module} with its MODULE.md"
            if NAME.fullmatch(self.module) is not None
            else ""
        )
        return what, WHY_STRAY, f"remove `{self.module}` from MODULES in {GATE_LIST}{restore}"

    def coverage(self) -> tuple[str, str, str]:
        """What, why and fix of a finding about a module's pair in the coverage map: `module` is the folder,
        `said` the detail (the number of pairs, the docs as JSON, the pattern or the folder), `names` the
        folders of a module whose pair is missing."""
        m, said, owner = self.module, self.said, self.owner
        held = f"`{owner}.{COVERAGE_KEY}` of {DIALS}"
        pair = f"the pair named `{m}`"
        listing = f"the list under `{COVERAGE_KEY}:` of the `{owner}` namespace in {DIALS}"
        if self.where is Where.COVERAGE_MISSING:
            fix = (
                f"add this entry to {listing}, in place of `[]` when it is empty:\n"
                f"{coverage_entry(m, self.names)}"
            )
            return f"{held} has no pair for it", WHY_COVERAGE, fix
        if self.where is Where.COVERAGE_TWICE:
            fix = f"remove every pair named `{m}` after the first from {listing}"
            return f"{held} has {said} pairs named for it", WHY_COVERAGE, fix
        if self.where is Where.COVERAGE_DOCS:
            fix = f"set `docs` of {pair} to the one path `modules/{m}/MODULE.md`"
            return f"its pair in {held} lists docs {said}, not its module document alone", WHY_COVERAGE, fix
        if self.where is Where.COVERAGE_OUTSIDE:
            what = f"its pair in {held} lists the code pattern `{said}`, which is outside modules/{m}/"
            return what, WHY_COVERAGE, f"remove `{said}` from `code` of {pair}"
        what = f"modules/{m}/{said} is a folder, but its pair in {held} lists no pattern for it"
        return what, WHY_COVERAGE, f'add the line `- "modules/{m}/{said}/**"` to `code` of {pair}'

    @property
    def manifest_file(self) -> str:
        """The path of the manifest of the module folder `module`."""
        return f"modules/{self.module}/plugin/.claude-plugin/plugin.json"

    def stray_folder(self) -> str:
        """A stray's folder name: the entry's name, the key's before `@`."""
        return self.module.removesuffix(f"@{self.tag}")

    def make_folder_hint(self) -> str:
        """The other way to fix a stray, naming its folder, only where the name could be a module's."""
        named = self.stray_folder()
        # modules/<named> could become a module folder, and pass every hold, only when it bears a module's
        # name, `const-<aspect>`; for any other name, "" included, the removal is the one fix
        if NAME.fullmatch(named) is None:
            return ""
        return f", or make modules/{named} a module folder holding its MODULE.md"

    def registry(self) -> tuple[str, str, str]:
        """What, why and fix of a finding about the files that name a module: `module` is the folder, the
        entry's name or the key, `said` what the file holds there as JSON text, `tag` the marketplace name."""
        parts = {
            Where.NAME: self.folder_name_parts,
            Where.MANIFEST: self.manifest_parts,
            Where.MARKETPLACE: self.marketplace_parts,
            Where.MARKET_SOURCE: self.market_source_parts,
            Where.MARKET_TWICE: self.market_twice_parts,
            Where.MARKET_STRAY: self.market_stray_parts,
            Where.MARKET_DESCRIPTION: self.description_parts,
            Where.SETTINGS: self.settings_parts,
            Where.SETTINGS_STRAY: self.settings_stray_parts,
            Where.KNOWN_MISSING: self.known_missing_parts,
        }
        return parts.get(self.where, self.known_source_parts)()

    def folder_name_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a module folder whose name is not `const-<aspect>`."""
        m = self.module
        if not m.startswith("const") and NAME.fullmatch(f"const-{m}"):
            rename = f"to modules/const-{m}"
        else:
            rename = "to a name `const-<aspect>`, lowercase letters and digits joined by single hyphens"
        fix = (
            f"rename modules/{m} {rename}, and name its manifest, marketplace entry, settings key and"
            " entry in MODULES the same"
        )
        return "a module folder's name is not const-<aspect>", WHY_NAME, fix

    def manifest_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a manifest whose name is not its folder's."""
        m = self.module
        named = (
            f"is named {self.said}, not {json.dumps(m)}"
            if self.said
            else f"has no name, where it must be {json.dumps(m)}"
        )
        return (
            f"its manifest {self.manifest_file} {named}",
            WHY_MANIFEST,
            f'set "name": {json.dumps(m)} in {self.manifest_file}',
        )

    def marketplace_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a module the marketplace has no entry for."""
        m = self.module
        entry = json.dumps({"name": m, "source": plugin_source(m)})
        return (
            "the marketplace has no entry for it",
            WHY_MARKET,
            f"add {entry} to plugins in {MARKETPLACE_FILE}",
        )

    def market_source_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a marketplace entry whose source is not the module's plugin folder."""
        m = self.module
        what = f"its marketplace entry has {self.said}, not source {json.dumps(plugin_source(m))}"
        fix = (
            f'set "source" to {json.dumps(plugin_source(m))} in the entry named {json.dumps(m)}'
            f" of plugins in {MARKETPLACE_FILE}"
        )
        return what, WHY_SOURCE, fix

    def market_twice_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a module the marketplace has more than one entry for."""
        m = self.module
        fix = (
            f"remove all but one entry named {json.dumps(m)} from plugins in {MARKETPLACE_FILE},"
            f" the one whose source is {json.dumps(plugin_source(m))}"
        )
        return f"the marketplace has {self.said} entries for it", WHY_TWICE, fix

    def market_stray_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a marketplace entry that is no module folder's."""
        m = self.module
        what = f"the marketplace has an entry for it, but modules/{m} is no module folder"
        fix = (
            f"remove the entry named {json.dumps(m)} from plugins in {MARKETPLACE_FILE}"
            f"{self.make_folder_hint()}"
        )
        return what, WHY_MARKET_STRAY, fix

    def description_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a marketplace entry whose description is not its manifest's; `side` tells
        which text is wrong."""
        m, said, manifest = self.module, self.said, self.manifest_file
        entry = f"the entry named {json.dumps(m)} of plugins in {MARKETPLACE_FILE}"
        if self.side == "manifest":
            what = (
                f"its manifest {manifest} has a description that is {said}, not a string"
                if said
                else f"its manifest {manifest} has no description"
            )
            fix = (
                f"set `description` in {manifest} to a string, the words a module's README opens with,"
                f" and copy it, as written, into {entry}"
            )
            return what, WHY_DESCRIPTION, fix
        if self.side == "entry":
            what = (
                f"its marketplace entry has a description that is {said}, not a string"
                if said
                else "its marketplace entry has no description"
            )
        else:
            what = (
                f"its marketplace entry's description differs from its manifest's, first at character"
                f" {said} (counting from 1)"
            )
        return what, WHY_DESCRIPTION, f"copy `description` of {manifest}, as written, into {entry}"

    def settings_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a module the kit's settings do not enable with `true`."""
        m, tag = self.module, self.tag
        enable = f"{json.dumps(f'{m}@{tag}')}: true"
        what = (
            f"the kit's settings set {json.dumps(f'{m}@{tag}')} to {self.said}, not true"
            if self.said
            else "the kit's settings do not enable it"
        )
        return what, WHY_ENABLED, f"set {enable} under enabledPlugins in {SETTINGS_FILE}"

    def settings_stray_parts(self) -> tuple[str, str, str]:
        """What, why and fix of an enabled key of the marketplace that is no module folder's."""
        what = f"the kit's settings enable it, but modules/{self.stray_folder()} is no module folder"
        fix = (
            f"remove the key {json.dumps(self.module)} from enabledPlugins in {SETTINGS_FILE}"
            f"{self.make_folder_hint()}"
        )
        return what, WHY_ENABLED_STRAY, fix

    def known_missing_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a marketplace the kit's settings do not declare."""
        declared = f'{json.dumps(self.module)}: {{"source": {json.dumps(DIRECTORY_SOURCE)}}}'
        what = "the kit's settings do not declare the marketplace under extraKnownMarketplaces"
        return what, WHY_KNOWN, f"add {declared} under extraKnownMarketplaces in {SETTINGS_FILE}"

    def known_source_parts(self) -> tuple[str, str, str]:
        """What, why and fix of a declared marketplace whose source is not the directory at `.`."""
        what = (
            f"the kit's settings declare the marketplace with {self.said},"
            f" not source {json.dumps(DIRECTORY_SOURCE)}"
        )
        fix = (
            f"set the source of {json.dumps(self.module)} under extraKnownMarketplaces in {SETTINGS_FILE}"
            f" to {json.dumps(DIRECTORY_SOURCE)}"
        )
        return what, WHY_KNOWN_SOURCE, fix


def read(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{path} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}) — fix: make it readable") from bad


def declared_scans(text: str, path: str = "the module document") -> tuple[list[str], list[Problem]]:
    """The scans a module document declares and what is wrong with the form of its enforcement section."""
    try:
        return enforcement(text, path)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


def listed(root: Path, *args: str) -> str:
    """What `sh scripts/gate-list.sh <args>` prints, run from `root`."""
    try:
        done = subprocess.run(["sh", GATE_LIST, *args], cwd=root, capture_output=True, text=True, check=False)
    except OSError as bad:
        raise Broken(f"{GATE_LIST} cannot be run ({bad.strerror}) — fix: install a POSIX sh") from bad
    if done.returncode != 0:
        said = (done.stderr or done.stdout).strip().splitlines()
        raise Broken(
            f"{GATE_LIST} {' '.join(args)} exited {done.returncode}"
            f" ({said[-1] if said else 'no output'}) — fix: restore the list script"
        )
    return done.stdout


def gate_list(root: Path) -> dict[str, str]:
    """Each entry of the gate group, with its commands."""
    return {name: listed(root, "--show", name) for name in listed(root, "--names", "gate").split()}


def tracked_checks(root: Path) -> list[str]:
    """The kit checks git tracks: `scripts/check-*.py` at the top of scripts/; an untracked file is none."""
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(root.parent)}  # the repository is `root` itself
    try:
        done = subprocess.run(
            ["git", "ls-files", "-z", "--", "scripts"],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as bad:
        raise Broken(f"git cannot be run ({bad.strerror}) — fix: install git") from bad
    if done.returncode != 0:
        said = done.stderr.strip().splitlines()
        raise Broken(
            f"git ls-files scripts exited {done.returncode} ({said[-1] if said else 'no output'})"
            " — fix: run the check from a clone of the kit"
        )
    return sorted(path for path in done.stdout.split("\0") if KIT_CHECK.fullmatch(path))


def jobs_of(root: Path) -> dict[str, str]:
    """Each entry of the list, with the job `--json` and `--names <job>` put it in."""
    try:
        jobs = json.loads(listed(root, "--json"))
    except json.JSONDecodeError as bad:
        raise Broken(
            f"{GATE_LIST} --json printed no JSON ({bad.msg}) — fix: restore the list script"
        ) from bad
    if not isinstance(jobs, list) or not all(isinstance(job, str) for job in jobs):
        raise Broken(f"{GATE_LIST} --json printed no list of job names — fix: restore the list script")
    return {entry: job for job in jobs for entry in listed(root, "--names", job).split()}


def code_of(line: str) -> str:
    """A line of the list script or the workflow, comments aside: a whole comment line, or a `#`
    after a space or a tab."""
    return "" if line.lstrip().startswith("#") else re.split(r"\s#", line, maxsplit=1)[0]


def ci_reads_list(root: Path) -> bool:
    if not (root / WORKFLOW).is_file():
        return False
    steps = "\n".join(code_of(line) for line in read(root, WORKFLOW).splitlines())
    return all(phrase in steps for phrase in READS_LIST)


def pytest_names(code: str) -> list[str]:
    """Each word of a code line that names pytest — `pytest` or `py.test` standing as a word, after a
    path or stuck to `-m` — quoted with that path or `-m`, without brackets or quotes around it; a name
    that goes on, `pytest-xdist`, `pytest_plugins`, `pytest.ini`, one with another name before it,
    `allure-pytest`, and an exact pin, `pytest==9.1.1`, name none."""
    found = []
    for match in PYTEST_NAME.finditer(code):
        before, after = code[: match.start()], code[match.end() :]
        if NAME_GOES_ON.match(after):
            continue
        if re.search(r"[\w.-]$", before) and not STUCK_TO_M.search(before):
            continue  # the end of another name, `allure-pytest`, `xpytest`, never `-mpytest`
        start = WORD_START.search(before)  # always matches: the pattern may match nothing at the end
        found.append((start[0] if start else "") + match[0])
    return found


def selections(code: str) -> list[str]:
    """The entries of a code line that may run a module's tests otherwise than whole, or reach every run:
    `--item`, each `PYTEST_ADDOPTS`, and each word that names pytest (pytest_names)."""
    found = [match[0] for match in ITEM_FILTER.finditer(code)]
    found += ["PYTEST_ADDOPTS"] * code.count("PYTEST_ADDOPTS")
    return found + pytest_names(code)


def config_folders(root: Path) -> list[Path]:
    """The folders where pytest may find its configuration for a run of a module's tests: the kit root,
    `modules/`, and each module's folder and its `tests/`, the folders pytest walks up from its argument."""
    modules = root / "modules"
    folders = [root, modules]
    for module in sorted(modules.iterdir()) if modules.is_dir() else []:
        if module.is_dir():
            folders += [module, module / "tests"]
    return folders


def item_filters(root: Path) -> list[Finding]:
    """Every entry of selections on a code line of the list script and of the workflow, and every
    `addopts` line of a pytest configuration file where a run of a module's tests finds it: a run that
    selects is never a full pass, so neither list may run one."""
    found = [
        Finding(path, Where.FILTER, entry=word, line=number)
        for path in (GATE_LIST, WORKFLOW)
        if (root / path).is_file()
        for number, line in enumerate(read(root, path).splitlines(), start=1)
        for word in selections(code_of(line))
    ]
    configs = [
        (folder / name).relative_to(root).as_posix()
        for folder in config_folders(root)
        for name in PYTEST_CONFIGS
        if (folder / name).is_file()
    ]
    return found + [
        Finding(path, Where.FILTER, entry="addopts", line=number)
        for path in configs
        for number, line in enumerate(read(root, path).splitlines(), start=1)
        if ADDOPTS.match(line)
    ]


def unpathed(runs: re.Pattern[str], commands: str) -> bool:
    """Whether a code line of `commands`, comments aside, runs the scan that `runs` matches without
    SHARED_SETTING as a word before it on that line."""
    for line in map(code_of, commands.splitlines()):
        found = runs.search(line)
        if found is not None and SHARED_SET.search(line[: found.start()]) is None:
            return True
    return False


def check_scan(
    module: str, entry: str, gates: dict[str, str], jobs: dict[str, str], ci: bool
) -> list[Finding]:
    stem = re.escape(entry.removesuffix(".py"))
    runs = re.compile(rf"modules/{re.escape(module)}/plugin/scripts/{stem}\.(?:sh|py) --scan\b")
    runners = [name for name, commands in gates.items() if runs.search(commands)]
    findings: list[Finding] = []
    if not runners:
        findings.append(Finding(module, Where.GATE, entry))
    elif all(jobs.get(name) != module for name in runners):
        findings.append(Finding(module, Where.JOB, entry, runners[0], jobs.get(runners[0], "")))
    findings += [Finding(module, Where.PATH, entry, name) for name in runners if unpathed(runs, gates[name])]
    if not ci:
        findings.append(Finding(module, Where.CI, entry))
    return findings


def check_checks(checks: list[str], gates: dict[str, str]) -> list[Finding]:
    """A tracked kit check that no line of the gate group runs as `python3 scripts/check-<x>.py`, with or
    without arguments: the lines are `--show`'s, comments aside, and a path under modules/ is no kit check."""
    code = [code_of(line) for commands in gates.values() for line in commands.splitlines()]
    findings: list[Finding] = []
    for check in checks:
        runs = re.compile(rf"(?<![\w/.-])python3 {re.escape(check)}(?![\w.-])")
        if not any(runs.search(line) for line in code):
            findings.append(Finding(check, Where.CHECK))
    return findings


def check_modules(modules: list[str], entries: list[str]) -> list[Finding]:
    """The list's modules, read from its entries of each kind, against the module folders."""
    named: dict[str, list[str]] = {}
    for entry in entries:
        if (match := OF_MODULE.fullmatch(entry)) is not None:
            named.setdefault(match[2], []).append(entry)
    findings: list[Finding] = []
    for module in modules:
        lacking = tuple(f"{kind}-{module}" for kind in KINDS if f"{kind}-{module}" not in entries)
        if lacking:
            findings.append(Finding(module, Where.MISSING, names=lacking))
    for module in sorted(set(named) - set(modules)):
        findings.append(Finding(module, Where.STRAY, names=tuple(named[module])))
    return findings


def read_json(root: Path, path: str) -> dict[str, Any]:
    """A JSON object of the tree; a file that is missing, is no JSON or is no object is BROKEN."""
    if not (root / path).is_file():
        raise Broken(f"{path} is no file — fix: restore it as a JSON file holding an object")
    try:
        data = json.loads(read(root, path))
    except json.JSONDecodeError as bad:
        raise Broken(
            f"{path} is no JSON ({bad.msg}, line {bad.lineno}) — fix: restore it as a JSON object"
        ) from bad
    if not isinstance(data, dict):
        raise Broken(
            f"{path} is no JSON object, it holds a {type(data).__name__} — fix: restore it as a JSON object"
        )
    return data


def shown(value: object) -> str:
    """A JSON value as text for a finding, its keys sorted so that the file's order never shows."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def read_marketplace(root: Path) -> tuple[str, dict[str, list[dict[str, Any]]], int]:
    """The marketplace's name, its entries by name, and how many entries it has. The name is read here,
    never typed in the check. A file with no name, no list `plugins` or an entry that is no object with
    a name is no marketplace the check can read."""
    market = read_json(root, MARKETPLACE_FILE)
    tag = market.get("name")
    if not isinstance(tag, str) or not tag:
        raise Broken(
            f'{MARKETPLACE_FILE} has no marketplace name, "name" is no non-empty string'
            " — fix: restore it, the name the kit's settings enable plugins under"
        )
    plugins = market.get("plugins")
    if not isinstance(plugins, list):
        raise Broken(
            f'{MARKETPLACE_FILE} has no list "plugins" — fix: restore it as a list of entries'
            ' {"name": …, "source": …}'
        )
    entries: dict[str, list[dict[str, Any]]] = {}
    for position, entry in enumerate(plugins, start=1):
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            raise Broken(
                f"{MARKETPLACE_FILE}: entry {position} of plugins is no object with a string name"
                ' — fix: write each entry as {"name": …, "source": …}'
            )
        entries.setdefault(entry["name"], []).append(entry)
    return tag, entries, len(plugins)


def settings_object(settings: dict[str, Any], key: str) -> dict[str, Any]:
    """A key of the kit's settings that must be an object where it stands; absent is the empty one, as
    the platform reads it."""
    value = settings.get(key, {})
    if not isinstance(value, dict):
        raise Broken(f"{SETTINGS_FILE}: {key} is no JSON object — fix: restore it as an object")
    return value


def description_finding(module: str, manifest: dict[str, Any], entry: dict[str, Any]) -> Finding | None:
    """The marketplace entry's `description` against the manifest's: equal strings are none. A manifest
    whose description is missing or no string is the finding's first cause, since copying it would copy
    nothing, whatever the entry holds; then an entry whose description is missing or no string; then two
    strings that differ, with the position of the first character that does."""
    wanted, got = manifest.get("description"), entry.get("description")
    if not isinstance(wanted, str):
        return Finding(
            module,
            Where.MARKET_DESCRIPTION,
            said=shown(wanted) if "description" in manifest else "",
            side="manifest",
        )
    if not isinstance(got, str):
        return Finding(
            module, Where.MARKET_DESCRIPTION, said=shown(got) if "description" in entry else "", side="entry"
        )
    if got == wanted:
        return None
    first = next(
        (at for at, pair in enumerate(zip(wanted, got, strict=False), start=1) if pair[0] != pair[1]),
        min(len(wanted), len(got)) + 1,
    )
    return Finding(module, Where.MARKET_DESCRIPTION, said=str(first), side="differs")


def manifest_findings(root: Path, modules: list[str]) -> tuple[list[Finding], dict[str, dict[str, Any]]]:
    """The folders whose name is not `const-<aspect>` and the manifests that do not bear their folder's
    name, by folder, name then manifest; and the manifests read."""
    findings: list[Finding] = []
    manifests: dict[str, dict[str, Any]] = {}
    for module in modules:
        if not NAME.fullmatch(module):
            findings.append(Finding(module, Where.NAME))
        manifest = manifests[module] = read_json(root, f"modules/{module}/plugin/.claude-plugin/plugin.json")
        if manifest.get("name") != module:
            said = shown(manifest["name"]) if "name" in manifest else ""
            findings.append(Finding(module, Where.MANIFEST, said=said))
    return findings, manifests


def entry_finding(module: str, got: list[dict[str, Any]]) -> Finding | None:
    """The finding about a module's entries in the marketplace, `got`: none, more than one, or one whose
    source is not the module's plugin folder."""
    if not got:
        return Finding(module, Where.MARKETPLACE)
    if len(got) > 1:
        return Finding(module, Where.MARKET_TWICE, said=str(len(got)))
    if got[0].get("source") != plugin_source(module):
        said = f"source {shown(got[0]['source'])}" if "source" in got[0] else "no source"
        return Finding(module, Where.MARKET_SOURCE, said=said)
    return None


def marketplace_findings(
    modules: list[str], entries: dict[str, list[dict[str, Any]]], manifests: dict[str, dict[str, Any]]
) -> list[Finding]:
    """The findings about the marketplace's entries, by folder: each one's source then its description;
    then the strays by name."""
    findings: list[Finding] = []
    for module in modules:
        got = entries.get(module, [])
        if (found := entry_finding(module, got)) is not None:
            findings.append(found)
        if len(got) == 1 and (told := description_finding(module, manifests[module], got[0])) is not None:
            findings.append(told)
    findings += [Finding(name, Where.MARKET_STRAY) for name in sorted(set(entries) - set(modules))]
    return findings


def enabled_findings(
    modules: list[str], tag: str, enabled: dict[str, Any]
) -> tuple[list[Finding], list[str]]:
    """The findings about the keys of `enabledPlugins`, by folder then the strays by name; and the keys of
    the marketplace `tag`, sorted."""
    findings: list[Finding] = []
    for module in modules:
        value = enabled.get(f"{module}@{tag}")
        if value is not True:
            said = shown(value) if f"{module}@{tag}" in enabled else ""
            findings.append(Finding(module, Where.SETTINGS, said=said, tag=tag))
    ours = sorted(key for key in enabled if key.endswith(f"@{tag}"))
    findings += [
        Finding(key, Where.SETTINGS_STRAY, tag=tag)
        for key in ours
        if key.removesuffix(f"@{tag}") not in modules
    ]
    return findings, ours


def known_findings(tag: str, known: dict[str, Any]) -> list[Finding]:
    """The finding about the settings' declaration of the marketplace `tag`: absent, or not a directory
    source at `.`."""
    if tag not in known:
        return [Finding(tag, Where.KNOWN_MISSING)]
    entry = known[tag]
    source = entry.get("source") if isinstance(entry, dict) else None
    if source == DIRECTORY_SOURCE:
        return []
    said = f"source {shown(source)}" if isinstance(entry, dict) and "source" in entry else "no source"
    return [Finding(tag, Where.KNOWN_SOURCE, said=said)]


def check_registries(root: Path, modules: list[str]) -> tuple[list[Finding], int, int]:
    """Each module folder is named `const-<aspect>` (kernel §7), is named so by its manifest, in its plugin
    folder, stands once in the marketplace with `./modules/<folder>/plugin` as its source, and is enabled,
    `true`, in the kit's settings, which declare the marketplace by a `directory` source at `.`; neither
    file names anything else of the marketplace. The marketplace's name is read from marketplace.json. The
    findings come in a fixed order, whatever the files' key order: by folder, name then manifest; the
    marketplace entries by folder, each one's source then its description, then the strays by name; the
    enabled keys the same; the declaration last. Returns them, the entry count of the marketplace and the
    count of its keys in `enabledPlugins`."""
    findings, manifests = manifest_findings(root, modules)
    tag, entries, plugins = read_marketplace(root)
    findings += marketplace_findings(modules, entries, manifests)
    settings = read_json(root, SETTINGS_FILE)
    enabled = settings_object(settings, "enabledPlugins")
    known = settings_object(settings, "extraKnownMarketplaces")
    told, ours = enabled_findings(modules, tag, enabled)
    findings += told
    findings += known_findings(tag, known)
    return findings, plugins, len(ours)


def read_dials(root: Path) -> dict[Any, Any]:
    """The kit's dials file as a mapping; a file that is missing, is no YAML or is no mapping is BROKEN."""
    if not (root / DIALS).is_file():
        raise Broken(f"{DIALS} is no file — fix: restore the kit's dials file at the kit root")
    try:
        data = yaml.safe_load(read(root, DIALS))
    except (yaml.YAMLError, ValueError) as bad:  # a date such as 2001-13-45 is a ValueError
        first = (str(bad).splitlines() or ["no message"])[0]
        raise Broken(f"{DIALS} is no YAML ({first}) — fix: repair the file") from bad
    if not isinstance(data, dict):
        raise Broken(
            f"{DIALS} is no YAML mapping, it holds a {type(data).__name__}"
            " — fix: restore it as a mapping of namespaces"
        )
    return data


def dials_namespaces(root: Path, modules: list[str]) -> list[Finding]:
    """A top-level key of the dials file that bears a module's name, `const-<aspect>`, names a module
    folder (kernel §7: a module's namespace is its plugin name); a key of any other form, a kernel key or
    a policy's namespace, is not judged, nor is a key that is no string. Findings come by key."""
    stray = {key for key in read_dials(root) if isinstance(key, str) and NAME.fullmatch(key)} - set(modules)
    return [Finding(key, Where.DIALS_KEY) for key in sorted(stray)]


def mirror_folders(root: Path) -> tuple[str, ...]:
    """The module folders `scripts/check-schema-mirror.py` puts on its import path: the strings of its one
    `for module in (...)` over a non-empty tuple of strings, read from the syntax tree, never run."""
    if not (root / MIRROR).is_file():
        raise Broken(f"{MIRROR} is no file — fix: restore it")
    try:
        tree = ast.parse(read(root, MIRROR), MIRROR)
    except (SyntaxError, ValueError) as bad:  # a source with a NUL byte is a ValueError before 3.12
        raise Broken(
            f"{MIRROR} is no Python (a syntax error at line {getattr(bad, 'lineno', None) or 1})"
            " — fix: repair the file"
        ) from bad
    loops = [
        [element.value for element in node.iter.elts if isinstance(element, ast.Constant)]
        for node in ast.walk(tree)
        if isinstance(node, ast.For)
        and isinstance(node.target, ast.Name)
        and node.target.id == "module"
        and isinstance(node.iter, ast.Tuple)
        and node.iter.elts
        and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.iter.elts)
    ]
    if len(loops) != 1:
        raise Broken(
            f"{MIRROR} has {len(loops)} loops `for module in (...)` over a tuple of folder names, not one"
            " — fix: restore the one loop that puts the module folders on its import path"
        )
    return tuple(loops[0])


def types_path(root: Path) -> list[Finding]:
    """The `types` entry of the gate list puts on MYPYPATH exactly the module folders the schema mirror
    imports from, each as `../modules/<m>/plugin/scripts`, and `../shared`: the items of every MYPYPATH
    setting on a code line of the entry's commands, comments aside, against the mirror's folders and the
    shared one, as sets."""
    items = [
        part
        for line in listed(root, "--show", TYPES_ENTRY).splitlines()
        for value in MYPYPATH.findall(code_of(line))
        for part in value.strip("\"'").split(":")
    ]
    folders = mirror_folders(root)
    if set(items) == {*(f"../modules/{name}/plugin/scripts" for name in folders), TYPES_SHARED}:
        return []
    return [Finding(GATE_LIST, Where.TYPES_PATH, said=":".join(items), names=folders)]


def scan_path(module: str, entry: str) -> str:
    """The path the guide's scan block lists for a declared scan: `<module>/plugin/scripts/<stem>.sh`, the
    POSIX entry point every scan has (template §6, gate-script rule 6), which the guide's loop runs with
    `sh`; the stem is the declared name without `.py`, so `check-x` and `check-x.py` both stand for
    `check-x.sh`."""
    return f"{module}/plugin/scripts/{entry.removesuffix('.py')}.sh"


def scan_block(root: Path) -> list[str]:
    """The paths of the guide's scan block: the words between `for s in` and `; do` on the first line of the
    one fenced block whose info string is `bash check=scan`. A guide that is missing, with no such block or
    two, or whose block does not begin `for s in … ; do`, is BROKEN: the check cannot read what it holds."""
    if not (root / GUIDE_FILE).is_file():
        raise Broken(
            f"{GUIDE_FILE} is no file — fix: restore the install guide at the kit root, with the fenced block"
            f" {BLOCK} that lists every scan"
        )
    lines = read(root, GUIDE_FILE).splitlines()
    blocks: list[tuple[int, str]] = []  # the line of each block's fence and its first line
    at = 0
    while at < len(lines):
        opened = FENCE.match(lines[at])
        if opened is None:
            at += 1
            continue
        indent, fence, info = opened.group(1), opened.group(2), opened.group(3).split()
        end = at + 1
        while end < len(lines):
            closing = FENCE.match(lines[end])
            if (
                closing is not None
                and closing.group(2)[0] == fence[0]
                and len(closing.group(2)) >= len(fence)
                and not closing.group(3).strip()
            ):
                break
            end += 1
        if info[:1] == ["bash"] and "check=scan" in info[1:]:
            first = lines[at + 1] if at + 1 < end else ""
            blocks.append((at + 1, first[len(indent) :] if first.startswith(indent) else first.lstrip()))
        at = end + 1
    if not blocks:
        raise Broken(
            f"{GUIDE_FILE} has no block {BLOCK} — fix: add the fenced block that runs every module's scan"
            f" in the guide's verify step, its fence {BLOCK}"
        )
    if len(blocks) > 1:
        where = " and ".join(str(line) for line, _ in blocks)
        raise Broken(
            f"{GUIDE_FILE} has {len(blocks)} blocks {BLOCK}, at lines {where} — fix: keep one: list the"
            " paths of both in the first and give the other `check=none`"
        )
    line, first = blocks[0]
    listed_in = SCAN_FOR.match(first)
    if listed_in is None:
        raise Broken(
            f"{GUIDE_FILE}:{line}: the first line of the block {BLOCK} is not `for s in <paths>; do …`"
            " — fix: begin it with `for s in <module>/plugin/scripts/<stem>.sh …; do`, the paths being the"
            " scans the modules declare, each `<stem>` the declared scan's name without `.py`,"
            ' and run each as `"$s"` after `do`'
        )
    return listed_in.group(1).split()


def guide_scans(root: Path, declared: list[tuple[str, str]]) -> list[Finding]:
    """The paths of the guide's scan block against the declared scans, as sets: a declared scan whose path is
    not listed, in the order the modules declare them, then a listed path no module declares, sorted."""
    listed_paths = set(scan_block(root))
    wanted = {scan_path(module, entry): (module, entry) for module, entry in declared}
    findings = [
        Finding(module, Where.GUIDE_ADD, entry)
        for path, (module, entry) in wanted.items()
        if path not in listed_paths
    ]
    findings += [Finding(path, Where.GUIDE_DROP) for path in sorted(listed_paths - set(wanted))]
    return findings


@dataclass(frozen=True)
class Pair:
    """One entry of the coverage map: a code territory, its path patterns, and the documents describing it."""

    name: str
    code: list[str]
    docs: list[str]


def coverage_pairs_of(root: Path) -> list[Pair]:
    """The entries of the coverage map, `<owner>.coverage` of the dials file. A map that is absent or no
    list, or an entry that is no mapping with a string `name` and two lists of strings, `code` and `docs`,
    is BROKEN: the check cannot read what it holds."""
    owner = COVERAGE.owner
    namespace = read_dials(root).get(owner)
    declared = namespace.get(COVERAGE_KEY) if isinstance(namespace, dict) else None
    if not isinstance(declared, list):
        said = "it is absent" if declared is None else f"it holds a {type(declared).__name__}"
        raise Broken(
            f"{DIALS}: `{owner}.{COVERAGE_KEY}` is no list ({said}) — fix: restore it as a list of pairs,"
            f" each `- name: <territory>` with a `code` list and a `docs` list, under `{COVERAGE_KEY}:` in"
            f" the `{owner}` namespace"
        )
    pairs: list[Pair] = []
    for position, entry in enumerate(declared, start=1):
        if not (
            isinstance(entry, dict)
            and isinstance(entry.get("name"), str)
            and all(
                isinstance(entry.get(key), list) and all(isinstance(item, str) for item in entry[key])
                for key in ("code", "docs")
            )
        ):
            raise Broken(
                f"{DIALS}: entry {position} of `{owner}.{COVERAGE_KEY}` is no mapping with a string `name`,"
                " a `code` list and a `docs` list of strings — fix: write each pair as `- name: <territory>`"
                " with `code:` and `docs:` lists of path patterns"
            )
        pairs.append(Pair(entry["name"], list(entry["code"]), list(entry["docs"])))
    return pairs


def coverage_pairs(root: Path, modules: list[str]) -> list[Finding]:
    """Each module folder has its pair in the coverage map of the range check: exactly one entry named for
    the folder, whose `docs` are the one path `modules/<m>/MODULE.md`, whose `code` patterns all open with
    `modules/<m>/`, and which lists `modules/<m>/<path>/**` for each of `COVERAGE_FOLDERS`, the paths
    `plugin/scripts`, `plugin/hooks`, `plugin/skills`, `tests` and `evals`, that is a directory below the
    module's folder; a pattern for a path that does not exist is allowed, and a folder of one of those
    names at another place is none of them. A module with two entries is judged by that finding alone.
    Entries named for no module folder are not judged. The findings come by module, then docs, patterns
    outside, folders in the order above."""
    owner, pairs = COVERAGE.owner, coverage_pairs_of(root)
    findings: list[Finding] = []
    for module in modules:
        folders = tuple(path for path in COVERAGE_FOLDERS if (root / "modules" / module / path).is_dir())
        mine = [pair for pair in pairs if pair.name == module]
        if len(mine) != 1:
            kind = Where.COVERAGE_TWICE if mine else Where.COVERAGE_MISSING
            findings.append(Finding(module, kind, names=folders, said=str(len(mine)), owner=owner))
            continue
        code, prefix = mine[0].code, f"modules/{module}/"
        if mine[0].docs != [f"{prefix}MODULE.md"]:
            findings.append(Finding(module, Where.COVERAGE_DOCS, said=shown(mine[0].docs), owner=owner))
        findings += [
            Finding(module, Where.COVERAGE_OUTSIDE, said=pattern, owner=owner)
            for pattern in code
            if not pattern.startswith(prefix)
        ]
        findings += [
            Finding(module, Where.COVERAGE_FOLDER, said=folder, owner=owner)
            for folder in folders
            if f"{prefix}{folder}/**" not in code
        ]
    return findings


def check_kit(root: Path) -> tuple[list[Finding], int, int, int, int, int]:
    try:
        modules = [folder.name for folder in module_folders(root)]
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    gates, jobs, ci = gate_list(root), jobs_of(root), ci_reads_list(root)
    findings: list[Finding] = []
    scans = 0
    declared: list[tuple[str, str]] = []
    for module in modules:
        document = f"modules/{module}/MODULE.md"
        entries, problems = declared_scans(read(root, document), document)
        findings += [Finding(document, Where.FORM, p.text, line=p.line, fault=p.fault) for p in problems]
        for entry in entries:
            scans += 1
            declared.append((module, entry))
            findings += check_scan(module, entry, gates, jobs, ci)
    findings += check_modules(modules, listed(root, "--names", "all").split())
    registry, plugins, enabled = check_registries(root, modules)
    findings += registry
    findings += item_filters(root)
    checks = tracked_checks(root)
    findings += check_checks(checks, gates)
    findings += dials_namespaces(root, modules)
    findings += types_path(root)
    findings += guide_scans(root, declared)
    findings += coverage_pairs(root, modules)
    return findings, len(modules), scans, len(checks), plugins, enabled


def report(findings: list[Finding], modules: int, scans: int, checks: int, plugins: int, enabled: int) -> int:
    counts = f"{modules} module document(s) examined, {scans} declared scan(s), {checks} kit check(s)"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(
        "GREEN: every declared scan stands in the gate list, the CI list and its module's job and runs with "
        "the kit's shared/ first on PYTHONPATH, the list's "
        "modules are the module folders, each named const-<aspect> and by its manifest, listed once in the "
        "marketplace and enabled in the kit's settings, which declare the marketplace, neither list, "
        "comments aside, names pytest save in an exact pin, passes --item or names PYTEST_ADDOPTS, no pytest "
        "configuration file of the kit's folders a module's run reads sets addopts, every kit check is run "
        "by an entry of the gate group, the install guide's scan block names exactly the declared scans, and "
        f"the coverage map of the range check holds one pair for each module folder — {counts}, {plugins} "
        f"marketplace plugin(s), {enabled} enabled plugin(s)"
    )
    return EXIT_GREEN


def broken_report(broken: Broken) -> int:
    print(f"BROKEN: {broken}")
    print("BROKEN: the check could not run — 0 module documents examined")
    return EXIT_BROKEN


def run(root: Path) -> int:
    """The plain run on `root`: its report, or the two BROKEN lines."""
    try:
        return report(*check_kit(root))
    except Broken as broken:
        return broken_report(broken)


TEST_OWNER = (
    "task-close"  # the dials key of the self-test's coverage map: no module's name, no namespace to judge
)
MIRROR_FOLDERS = ("const-p", "const-q")  # the self-test's schema mirror folders, no tree's module folders
TYPES_COMMAND = (  # the self-test's `types` entry, agreeing with MIRROR_FOLDERS
    "cd scripts && MYPYPATH=../modules/const-p/plugin/scripts:../modules/const-q/plugin/scripts:../shared"
    " python3 -m mypy --strict *.py"
)


@dataclass(frozen=True)
class Case:
    """One self-test tree: the gate and extra entries with their commands, the workflow, the job of
    each entry that is not `kit` beyond the module entries' own, the folders and the listed modules, and
    the commands of the `types` entry, None for a list that has no such entry."""

    gates: dict[str, str]
    extras: dict[str, str] = field(default_factory=dict)
    workflow: str = ""
    jobs: dict[str, str] = field(default_factory=dict)
    folders: tuple[str, ...] = ("const-x", "const-quiet")
    listed: tuple[str, ...] | None = None  # the list's MODULES; None: the folders
    document: str = ""  # const-x's module document; empty: the self-test's own
    documents: dict[str, str] = field(default_factory=dict)  # another folder's module document, by name
    scripts: dict[str, bool] = field(default_factory=dict)  # a file of the tree, a path: git tracks it
    types: str | None = TYPES_COMMAND  # the commands of the list's `types` entry
    comment: str = ""  # a comment line at the head of the list script
    repo: bool = True  # the tree is a git repository
    tag: str = "kit-test"  # the marketplace name of the default registry files
    files: dict[str, object] = field(default_factory=dict)
    # the registry files, by path, when the case writes its own: an object or list is written as JSON, a
    # text as it is, None leaves the file out; empty: `registry_tree(folders, tag)`
    guide: str | None = ""  # the install guide: a text as it is, None leaves it out; empty: `guide_text(...)`
    owner: str = ""  # the dials key the coverage map is read under; empty: the self-test's `TEST_OWNER`


def mirror_text(folders: tuple[str, ...]) -> str:
    """A schema mirror whose import path takes `folders`, in the form the check reads."""
    return f"import sys\n\nfor module in {folders!r}:\n    sys.path.insert(0, module)\n"


def guide_text(*paths: str, block: str = "bash check=scan") -> str:
    """An install guide in the kit's form: a step whose fenced block, `block` as its info string, runs the
    scans `paths` in a loop, the block indented as inside a numbered list, a `check=none` block beside it."""
    return (
        "# Install\n\n8. **Verify.** Run every scan:\n"
        f'   ```{block}\n   for s in {" ".join(paths)}; do sh ~/kit/modules/"$s" --scan; done\n   ```\n'
        "   Then the fixtures:\n   ```bash check=none\n"
        "   for m in ~/kit/modules/const-*; do true; done\n   ```\n"
    )


def full_pair(module: str, folders: tuple[str, ...] = COVERAGE_FOLDERS) -> dict[str, Any]:
    """The coverage pair of a module: a pattern for each of `folders`, a folder that does not exist
    included (allowed), and its module document alone."""
    return {
        "name": module,
        "code": [f"modules/{module}/{folder}/**" for folder in folders],
        "docs": [f"modules/{module}/MODULE.md"],
    }


def registry_tree(folders: tuple[str, ...], tag: str) -> dict[str, Any]:
    """The files that name the modules, matching `folders`: a manifest each, the marketplace `tag` with one
    entry each, the settings that enable each and declare the marketplace, the dials file with a namespace
    each and the coverage map, a pair for each, and a schema mirror whose folders agree with the `types`
    entry. Extra keys the platform allows stand in each, which the check never reads."""
    files: dict[str, Any] = {
        f"modules/{m}/plugin/.claude-plugin/plugin.json": {
            "name": m,
            "version": "0.0.1",
            "description": f"The module {m}.",
        }
        for m in folders
    }
    files[DIALS] = {  # YAML as JSON
        "root_policy": "policies",
        **{m: {"key": 1} for m in folders},
        TEST_OWNER: {COVERAGE_KEY: [full_pair(m) for m in folders]},
    }
    files[MIRROR] = mirror_text(MIRROR_FOLDERS)
    files[MARKETPLACE_FILE] = {
        "name": tag,
        "owner": {"name": "Someone"},
        "plugins": [
            {"name": m, "source": plugin_source(m), "description": f"The module {m}."} for m in folders
        ],
    }
    files[SETTINGS_FILE] = {
        "permissions": {"allow": []},
        "extraKnownMarketplaces": {tag: {"source": dict(DIRECTORY_SOURCE)}},
        "enabledPlugins": {f"{m}@{tag}": True for m in folders},
    }
    return files


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


def folder_probes() -> bool:
    """`kit_module_doc.module_folders`, the kit's one listing, over every class of what can stand under
    `modules/`, in one loop, the listing having no self-test of its own (the other checks that read
    through it prove their own mapping). A probe is a throwaway `modules/` of folders each with its
    MODULE.md, folders without one, plain files, and a MODULE.md that is a folder; `modules` None leaves
    it out, "file" makes it a plain file; the folders the listing gives, or the message of its error,
    with `{root}` for the tree. The listing is handed adversarial order, entries reversed. A probe that
    fails prints what it got."""
    gone = "{root} has no modules/ directory — fix: run the check from a checkout of the kit"
    undocumented = "modules/{} has no MODULE.md — fix: restore the module document"
    # name: documented folders, folders with no MODULE.md, plain files, folders whose MODULE.md is a folder
    probes: dict[str, tuple[list[str], list[str], list[str], list[str], str | None, list[str] | str]] = {
        "a folder `.x` and a folder `_x` are skipped silently, with a MODULE.md or without": (
            [".x", "_x", "const-a"],
            [".y", "_y"],
            [],
            [],
            "dir",
            ["const-a"],
        ),
        "a plain file of modules/ is not listed, whatever its name": (
            ["const-a"],
            [],
            ["const-file", ".hidden", "zzz"],
            [],
            "dir",
            ["const-a"],
        ),
        "a folder named without `const-` is listed": (
            ["glossary", "const-a"],
            [],
            [],
            [],
            "dir",
            ["const-a", "glossary"],
        ),
        "a name that only starts like the prefix is listed": (
            ["const", "const-"],
            [],
            [],
            [],
            "dir",
            ["const", "const-"],
        ),
        "the folders are sorted by name, whatever order the folder lists": (
            ["const-b", "const-c", "const-a", "x-d"],
            [],
            [],
            [],
            "dir",
            ["const-a", "const-b", "const-c", "x-d"],
        ),
        "a folder without its MODULE.md is an error naming the folder": (
            ["const-a"],
            ["const-ghost"],
            [],
            [],
            "dir",
            undocumented.format("const-ghost"),
        ),
        "the first folder without its MODULE.md, in sorted order, is named": (
            ["const-a"],
            ["const-z", "const-b"],
            [],
            [],
            "dir",
            undocumented.format("const-b"),
        ),
        "a MODULE.md that is a folder is no document": (
            [],
            [],
            [],
            ["const-a"],
            "dir",
            undocumented.format("const-a"),
        ),
        "no modules/ directory is an error naming the tree": ([], [], [], [], None, gone),
        "modules/ a plain file is no directory": ([], [], [], [], "file", gone),
    }
    ok = True
    for name, (documented, bare, files, trap, modules, wanted) in probes.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            if modules == "file":
                (root / "modules").write_text("not a folder\n", encoding="utf-8")
            elif modules == "dir":
                (root / "modules").mkdir()
            for folder in (*documented, *bare, *trap):
                (root / "modules" / folder).mkdir()
            for folder in documented:
                (root / "modules" / folder / "MODULE.md").write_text("A module.\n", encoding="utf-8")
            for folder in trap:
                (root / "modules" / folder / "MODULE.md").mkdir()
            for file in files:
                (root / "modules" / file).write_text("not a folder\n", encoding="utf-8")
            try:
                with listed_in_reverse():
                    got: list[str] | str = [d.name for d in module_folders(root)]
            except DocumentError as bad:
                got = str(bad)
            want = wanted.replace("{root}", str(root)) if isinstance(wanted, str) else wanted
        if got != want:
            ok = False
            print(f"        {name}: got {got!r}, wanted {want!r}")
    return ok


def form_probes() -> bool:
    """The forms of the enforcement table, over one whole set of probes in one loop: each is the rows of
    a `t9` section, the scans it declares and the problems it holds, each as (line, fault); the section's
    anchor is line 1, its first row line 2. A probe that fails prints what it got."""
    explain = "`x --scan --command <text>`"
    marked = f"{explain}: not a tree scan"

    def row(artifact: str, handle: str = "E2", kind: str = "`gate`") -> str:
        return f"| {handle} | {artifact} | {kind} |"

    probes: dict[str, tuple[list[str], list[str], list[tuple[int, Fault]]]] = {
        "an indented row is read": ([f"   {row('`x --scan`')}"], ["x"], []),
        "a bold handle is read": ([row("`x --scan`", "**E2**")], ["x"], []),
        "no space after the bar is read": (["|E2 | `x --scan` | `gate` |"], ["x"], []),
        "no space round any cell is read": (["|E2|`x --scan`|`gate`|"], ["x"], []),
        "a `.py` entry is declared as written": ([row("`x.py --scan`: all")], ["x.py"], []),
        "a row with two scans declares both": ([row("`y --scan`, `x --scan`")], ["x", "y"], []),
        "`sh scripts/x.sh --scan` is a problem": ([row("`sh scripts/x.sh --scan`")], [], [(2, Fault.SPAN)]),
        "`python3 scripts/x.py --scan` is a problem": (
            [row("`python3 scripts/x.py --scan`")],
            [],
            [(2, Fault.SPAN)],
        ),
        "`x.py --scan [DIR]` is a problem": ([row("`x.py --scan [DIR]`")], [], [(2, Fault.SPAN)]),
        "the entry and the flag in two spans is a problem": (
            [row("`x.py` `--scan`")],
            [],
            [(2, Fault.SPAN)],
        ),
        "a word after the flag is a problem": ([row("`x --scan all`")], [], [(2, Fault.SPAN)]),
        "a space after the flag is a problem": ([row("`x --scan `")], [], [(2, Fault.SPAN)]),
        "a capital in the entry is a problem": ([row("`X --scan`")], [], [(2, Fault.SPAN)]),
        "a span in the kind cell is read like one in any other cell": (
            [row("`x`", kind="`sh x.sh --scan`")],
            [],
            [(2, Fault.SPAN)],
        ),
        "a first cell `G2` is a problem, its scan still read": (
            [row("`x --scan`", "G2")],
            ["x"],
            [(2, Fault.FIRST_CELL)],
        ),
        "a first cell `Example` is a problem": ([row("`x`", "Example")], [], [(2, Fault.FIRST_CELL)]),
        "an empty first cell is a problem": (["|  | `x` | `gate` |"], [], [(2, Fault.FIRST_CELL)]),
        "a first cell `E` with no number is a problem": ([row("`x`", "E")], [], [(2, Fault.FIRST_CELL)]),
        "a first cell `E1a` is a problem": ([row("`x`", "E1a")], [], [(2, Fault.FIRST_CELL)]),
        "a first cell `e1` is a problem": ([row("`x`", "e1")], [], [(2, Fault.FIRST_CELL)]),
        "a first cell `**E1` is a problem": ([row("`x`", "**E1")], [], [(2, Fault.FIRST_CELL)]),
        "a flag after `--scan` with the mark is no scan and no problem": (
            [row(marked)],
            [],
            [],
        ),
        "a flag after `--scan` without the mark is a problem": (
            [row(explain)],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the words only inside a code span are no mark": (
            [row(f"{explain}: `not a tree scan`")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the words in another cell of the row are no mark": (
            [row(explain, kind="not a tree scan")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the words in another row are no mark": (
            [row(marked), row(explain, "E3")],
            [],
            [(3, Fault.UNMARKED)],
        ),
        "the words one word short are no mark": (
            [row(f"{explain}: not a scan")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the mark in capitals is no mark": (
            [row(f"{explain}: Not a tree scan")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the mark with a longer last word is no mark": (
            [row(f"{explain}: not a tree scanner")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the mark at the end of a longer first word is no mark": (
            [row(f"{explain}: cannot a tree scan")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "the mark inside parentheses is a mark": (
            [row(f"{explain} (not a tree scan)")],
            [],
            [],
        ),
        "an explain's argument that starts with `-` is a problem": (
            [row("`x --scan --command -y`: not a tree scan")],
            [],
            [(2, Fault.SPAN)],
        ),
        "an escaped bar in the span keeps it in its cell, so the unmarked flag is found": (
            [row("`x --scan --command <a\\|b>`")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "an escaped bar before the mark keeps the mark in the cell of the span": (
            [row("`x --scan --command <text>`: the a\\|b form, not a tree scan")],
            [],
            [],
        ),
        "`x --scan --since <date>` with the mark is no scan": (
            [row("`x --scan --since <date>`: the history report, not a tree scan")],
            [],
            [],
        ),
        "two flags and a word with the mark are no scan": (
            [row("`x --scan --all --since today`: not a tree scan")],
            [],
            [],
        ),
        "a flag with no argument and the mark is no scan": (
            [row("`x.py --scan --all`: not a tree scan")],
            [],
            [],
        ),
        "the mark beside a declared scan leaves it declared": (
            [row("`x --scan`, `y --scan --since <date>`: not a tree scan")],
            ["x"],
            [],
        ),
        "a declared scan beside an unmarked flag form is read, the other a problem": (
            [row("`x --scan`, `y --scan --since <date>`")],
            ["x"],
            [(2, Fault.UNMARKED)],
        ),
        "no closing bar, the span in the last cell is read": (
            ["| E2 | `gate` | `x --scan`"],
            ["x"],
            [],
        ),
        "no closing bar, the span in the second and last cell is read": (["| E2 | `x --scan`"], ["x"], []),
        "no closing bar, a flag after `--scan` without the mark is a problem": (
            ["| E2 | `gate` | `x --scan --command <t>`"],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "no closing bar, a flag after `--scan` with the mark is no scan and no problem": (
            ["| E2 | `gate` | `x --scan --command <t>`: not a tree scan"],
            [],
            [],
        ),
        "no closing bar, a span of another form in the last cell is a problem": (
            ["| E2 | `gate` | `sh x.sh --scan`"],
            [],
            [(2, Fault.SPAN)],
        ),
        "a row that closes with a bar reads its last cell as before": (
            ["| E2 | `gate` | `x --scan` |", "| E3 | `gate` | `y --scan` |  "],
            ["x", "y"],
            [],
        ),
        "a one-cell line with no closing bar is a row, `E2` its first cell": (["| E2"], [], []),
        "a one-cell line with no closing bar, `G2`, is a first-cell problem": (
            ["| G2"],
            [],
            [(2, Fault.FIRST_CELL)],
        ),
        "a line of one bar has no cell, so no first cell": (["|"], [], [(2, Fault.FIRST_CELL)]),
        "a flag with a hyphen and a digit, with the mark, is no scan and no problem": (
            [row("`x --scan --since-2 <d>`: not a tree scan")],
            [],
            [],
        ),
        "a flag with a hyphen inside, with the mark, is no scan and no problem": (
            [row("`x --scan --a-b`: not a tree scan")],
            [],
            [],
        ),
        "a flag with a hyphen and a digit, without the mark, is an unmarked problem": (
            [row("`x --scan --since-2 <d>`")],
            [],
            [(2, Fault.UNMARKED)],
        ),
        "a `--scan` span in a first cell that is no `E<n>` is a problem and is read": (
            ["| `x --scan` | `gate` |"],
            ["x"],
            [(2, Fault.FIRST_CELL)],
        ),
        "a header and its separator are skipped": (
            ["| # | artifact | kind |", "|---|---|---|", row("`x --scan`")],
            ["x"],
            [],
        ),
        "an aligned separator is skipped": (
            ["| # | artifact | kind |", "|:--|:-:|--:|", row("`x --scan`")],
            ["x"],
            [],
        ),
        "a table with no header reads every row": (
            [row("`x --scan`"), row("`y --scan`", "E3")],
            ["x", "y"],
            [],
        ),
        "a row below the header is read as a row": (
            ["| # | artifact | kind |", "|---|---|---|", row("`x`", "G1")],
            [],
            [(4, Fault.FIRST_CELL)],
        ),
        "no table, `t9` directly followed by `t10`": ([], [], []),
        "a scan named in prose is a problem": (
            [row("`y`"), "", "It runs `x --scan` here."],
            [],
            [(4, Fault.PROSE)],
        ),
        "a `.py` scan named in prose is a problem": (["Run `x.py --scan`."], [], [(2, Fault.PROSE)]),
        "`--scan --command` in prose, with no entry, is no problem": (
            ["Backstop: the explain, `--scan --command`, shows it."],
            [],
            [],
        ),
        "another mode named in prose is no problem": (
            ["See `x --scan --since <date>` and `sh x.sh --scan`."],
            [],
            [],
        ),
    }
    ok = True
    for name, (rows, scans, faults) in probes.items():
        text = '<a id="t9"></a>\n' + "".join(f"{line}\n" for line in rows) + '<a id="t10"></a>\n'
        got_scans, problems = declared_scans(text)
        got_faults = [(p.line, p.fault) for p in problems]
        if (got_scans, got_faults) != (scans, faults):
            ok = False
            print(f"        probe {name!r}: got {got_scans} and {got_faults}, wanted {scans} and {faults}")
    return ok


REGISTRY_TAG = "kit-test"  # the marketplace name of the self-test's registry files, never the kit's own
MANIFEST_X = "modules/const-x/plugin/.claude-plugin/plugin.json"


def registry_case(
    scan: str,
    change: Callable[[dict[str, Any]], object],
    folders: tuple[str, ...] = ("const-x", "const-quiet"),
    types: str | None = TYPES_COMMAND,
) -> Case:
    """A case whose registry files are the matching ones for `folders` after `change` edited them, over a
    list whose `types` entry has the commands `types`."""
    files = registry_tree(folders, REGISTRY_TAG)
    change(files)
    return Case({"x": scan}, folders=folders, files=files, types=types)


def registry_entry(f: dict[str, Any], at: int = 0) -> dict[str, Any]:
    """The `at`-th plugin entry of the marketplace file among the registry files `f`."""
    entries: dict[str, Any] = f[MARKETPLACE_FILE]["plugins"][at]
    return entries


def registry_enabled(f: dict[str, Any]) -> dict[str, Any]:
    """The `enabledPlugins` object of the settings among the registry files `f`."""
    keys: dict[str, Any] = f[SETTINGS_FILE]["enabledPlugins"]
    return keys


def registry_known(f: dict[str, Any]) -> dict[str, Any]:
    """The `extraKnownMarketplaces` object of the settings among the registry files `f`."""
    declared: dict[str, Any] = f[SETTINGS_FILE]["extraKnownMarketplaces"]
    return declared


def with_dials(content: object) -> Callable[[dict[str, Any]], object]:
    """The dials file replaced by `content`, the coverage map of the tree's two folders kept beside it;
    an object is written as JSON, which YAML reads."""
    owned = {COVERAGE_KEY: [full_pair(m) for m in ("const-x", "const-quiet")]}

    def put(f: dict[str, Any]) -> None:
        f[DIALS] = (
            {**content, TEST_OWNER: owned}
            if isinstance(content, dict)
            else f"{content}{TEST_OWNER}: {json.dumps(owned)}\n"
        )

    return put


def with_mirror(*folders: str) -> Callable[[dict[str, Any]], object]:
    """The schema mirror replaced by one that loops over `folders`."""
    return lambda f: f.update({MIRROR: mirror_text(folders)})


def mypypath(*folders: str, shared: bool = True) -> str:
    """The folders as the items of a MYPYPATH setting, `../shared` last unless `shared` is False."""
    return ":".join(
        [*(f"../modules/{name}/plugin/scripts" for name in folders), *([TYPES_SHARED] if shared else [])]
    )


def types_with(setting: str) -> str:
    """The `types` entry's commands, the scripts' one with `setting` first."""
    return (
        "cd shared && python3 -m mypy --strict constitution_layer_kit\n"
        f"cd scripts && {setting}python3 -m mypy --strict *.py"
    )


def declared_as(source: object) -> Callable[[dict[str, Any]], object]:
    """The settings' declaration of the marketplace with its `source` set to `source`."""
    return lambda f: registry_known(f)[REGISTRY_TAG].update({"source": source})


def enabled_as(value: object) -> Callable[[dict[str, Any]], object]:
    """The settings' key that enables const-x set to `value`."""
    return lambda f: registry_enabled(f).update({f"const-x@{REGISTRY_TAG}": value})


def registry_cases(scan: str) -> dict[str, tuple[Case, list[Where]]]:
    """The cases of the files that name a module, each a matching registry edited once: the findings it
    must give, in their fixed order. The registry's plugins stand in the order of its folders, const-x
    first, the folders' sorted order being const-quiet, const-x. The dials file's namespaces and the
    `types` entry against the schema mirror are rows of the same table: the dials file and the mirror
    are two files of the registry, and the entry's commands a parameter of the case."""
    market, settings, tag = MARKETPLACE_FILE, SETTINGS_FILE, REGISTRY_TAG

    def edit(
        change: Callable[[dict[str, Any]], object], wanted: list[Where], types: str | None = TYPES_COMMAND
    ) -> tuple[Case, list[Where]]:
        return registry_case(scan, change, types=types), wanted

    p, q = MIRROR_FOLDERS
    stray, one = [Where.DIALS_KEY], [Where.TYPES_PATH]
    yaml_text = (
        "# the kit's dials, in the forms YAML allows\n"
        "root_policy: policies   # kernel\n"
        "base: &base {key: 1}\n"
        '"const-gone": *base\n'
        "'const-two':\n"
        "  const-nested: 1\n"
        "const-x: *base\n"
    )

    cases: dict[str, tuple[Case, list[Where]]] = {
        "an entry, a manifest and the settings carry the platform's other keys: allowed": edit(
            lambda f: (
                registry_enabled(f).update({"other@elsewhere": True, "const-gone@elsewhere": False}),
                registry_enabled(f).update({f"const-gone@{tag}-2": True, f"const-gone@x{tag}": True}),
                registry_known(f).update({"elsewhere": {"source": {"source": "github", "repo": "a/b"}}}),
                registry_known(f)[tag].update({"autoUpdate": True}),
                registry_entry(f).update({"version": "9", "homepage": "https://example.org"}),
            ),
            [],
        ),
        "the marketplace renamed in all three places": (Case({"x": scan}, tag="kit-b"), []),
        "the marketplace renamed in its own file only": edit(
            lambda f: f[market].update({"name": "kit-b"}),
            [Where.SETTINGS, Where.SETTINGS, Where.KNOWN_MISSING],
        ),
        "the marketplace renamed in its file and the declaration, the enabled keys left": edit(
            lambda f: (
                f[market].update({"name": "kit-b"}),
                f[settings].update({"extraKnownMarketplaces": {"kit-b": {"source": dict(DIRECTORY_SOURCE)}}}),
            ),
            [Where.SETTINGS, Where.SETTINGS],
        ),
        "the marketplace renamed in its file and the enabled keys, the declaration left": edit(
            lambda f: (
                f[market].update({"name": "kit-b"}),
                f[settings].update(
                    {"enabledPlugins": {f"{m}@kit-b": True for m in ("const-x", "const-quiet")}}
                ),
            ),
            [Where.KNOWN_MISSING],
        ),
        "a manifest that names another plugin": edit(
            lambda f: f[MANIFEST_X].update({"name": "const-y"}), [Where.MANIFEST]
        ),
        "a manifest with no name": edit(lambda f: f[MANIFEST_X].pop("name"), [Where.MANIFEST]),
        "a manifest whose name is no string": edit(
            lambda f: f[MANIFEST_X].update({"name": 5}), [Where.MANIFEST]
        ),
        "a manifest whose name differs from the folder's in case": edit(
            lambda f: f[MANIFEST_X].update({"name": "CONST-X"}), [Where.MANIFEST]
        ),
        "a module the marketplace leaves out": edit(
            lambda f: f[market]["plugins"].pop(0), [Where.MARKETPLACE]
        ),
        "a marketplace with no entry at all": edit(
            lambda f: f[market].update({"plugins": []}), [Where.MARKETPLACE, Where.MARKETPLACE]
        ),
        "an entry whose source is another folder": edit(
            lambda f: registry_entry(f).update({"source": "./modules/other"}), [Where.MARKET_SOURCE]
        ),
        "an entry whose source is another module's folder": edit(
            lambda f: registry_entry(f).update({"source": "./modules/const-quiet"}), [Where.MARKET_SOURCE]
        ),
        "an entry whose source is another module's plugin folder": edit(
            lambda f: registry_entry(f).update({"source": plugin_source("const-quiet")}),
            [Where.MARKET_SOURCE],
        ),
        "an entry whose source is the module's folder, not its plugin folder": edit(
            lambda f: registry_entry(f).update({"source": "./modules/const-x"}), [Where.MARKET_SOURCE]
        ),
        "an entry whose source is a folder below the plugin folder": edit(
            lambda f: registry_entry(f).update({"source": "./modules/const-x/plugin/scripts"}),
            [Where.MARKET_SOURCE],
        ),
        "an entry whose source is an object": edit(
            lambda f: registry_entry(f).update({"source": {"source": "github", "repo": "a/b"}}),
            [Where.MARKET_SOURCE],
        ),
        "an entry with no source": edit(lambda f: registry_entry(f).pop("source"), [Where.MARKET_SOURCE]),
        "an entry whose source ends in a slash": edit(
            lambda f: registry_entry(f).update({"source": f"{plugin_source('const-x')}/"}),
            [Where.MARKET_SOURCE],
        ),
        "an entry whose source has no `./`": edit(
            lambda f: registry_entry(f).update({"source": "modules/const-x/plugin"}), [Where.MARKET_SOURCE]
        ),
        "an entry whose description differs from its manifest's": edit(
            lambda f: registry_entry(f).update({"description": "Another."}), [Where.MARKET_DESCRIPTION]
        ),
        "an entry whose description differs in its last character only": edit(
            lambda f: registry_entry(f).update({"description": "The module const-x!"}),
            [Where.MARKET_DESCRIPTION],
        ),
        "an entry whose description differs by a trailing space": edit(
            lambda f: registry_entry(f).update({"description": "The module const-x. "}),
            [Where.MARKET_DESCRIPTION],
        ),
        "an entry whose description differs in case": edit(
            lambda f: registry_entry(f).update({"description": "the module const-x."}),
            [Where.MARKET_DESCRIPTION],
        ),
        "an entry whose description is empty": edit(
            lambda f: registry_entry(f).update({"description": ""}), [Where.MARKET_DESCRIPTION]
        ),
        "an entry with no description": edit(
            lambda f: registry_entry(f).pop("description"), [Where.MARKET_DESCRIPTION]
        ),
        "an entry whose description is no string": edit(
            lambda f: registry_entry(f).update({"description": 5}), [Where.MARKET_DESCRIPTION]
        ),
        "an entry whose description is null": edit(
            lambda f: registry_entry(f).update({"description": None}), [Where.MARKET_DESCRIPTION]
        ),
        "a manifest with no description": edit(
            lambda f: f[MANIFEST_X].pop("description"), [Where.MARKET_DESCRIPTION]
        ),
        "a manifest whose description is no string": edit(
            lambda f: f[MANIFEST_X].update({"description": ["The module const-x."]}),
            [Where.MARKET_DESCRIPTION],
        ),
        "a manifest and its entry with no description are one finding": edit(
            lambda f: (f[MANIFEST_X].pop("description"), registry_entry(f).pop("description")),
            [Where.MARKET_DESCRIPTION],
        ),
        "a description of long, accented and dashed words, equal in both": edit(
            lambda f: (
                f[MANIFEST_X].update({"description": "Ask — only at stakes; é, ü and 한 \u2014 " * 20}),
                registry_entry(f).update({"description": "Ask — only at stakes; é, ü and 한 \u2014 " * 20}),
            ),
            [],
        ),
        "an entry with another source and another description: the source first": edit(
            lambda f: registry_entry(f).update({"source": "./modules/other", "description": "Another."}),
            [Where.MARKET_SOURCE, Where.MARKET_DESCRIPTION],
        ),
        "a module the marketplace leaves out is not judged on its description": edit(
            lambda f: (f[market]["plugins"].pop(0), f[MANIFEST_X].pop("description")),
            [Where.MARKETPLACE],
        ),
        "two entries for one module, the second with another description, are not judged on it": edit(
            lambda f: f[market]["plugins"].append(
                {"name": "const-x", "source": plugin_source("const-x"), "description": "Another."}
            ),
            [Where.MARKET_TWICE],
        ),
        "an entry with no folder, whatever its description, is the stray alone": edit(
            lambda f: f[market]["plugins"].append(
                {"name": "const-gone", "source": plugin_source("const-gone"), "description": 5}
            ),
            [Where.MARKET_STRAY],
        ),
        "the descriptions of both modules differ: both are found": edit(
            lambda f: (
                registry_entry(f).update({"description": "Another."}),
                registry_entry(f, 1).update({"description": "Another."}),
            ),
            [Where.MARKET_DESCRIPTION, Where.MARKET_DESCRIPTION],
        ),
        "an entry with no folder": edit(
            lambda f: f[market]["plugins"].append(
                {"name": "const-gone", "source": plugin_source("const-gone")}
            ),
            [Where.MARKET_STRAY],
        ),
        "two entries of a name with no folder are one finding": edit(
            lambda f: f[market]["plugins"].extend([{"name": "const-gone"}, {"name": "const-gone"}]),
            [Where.MARKET_STRAY],
        ),
        "two entries for one module": edit(
            lambda f: f[market]["plugins"].append(dict(registry_entry(f))), [Where.MARKET_TWICE]
        ),
        "two entries for one module, one with another source, are one finding": edit(
            lambda f: f[market]["plugins"].append({"name": "const-x", "source": "./modules/other"}),
            [Where.MARKET_TWICE],
        ),
        "a module the settings leave out": edit(
            lambda f: registry_enabled(f).pop(f"const-x@{tag}"), [Where.SETTINGS]
        ),
        "settings with no enabledPlugins at all": edit(
            lambda f: f[settings].pop("enabledPlugins"), [Where.SETTINGS, Where.SETTINGS]
        ),
        "a key with no folder": edit(
            lambda f: registry_enabled(f).update({f"const-gone@{tag}": True}), [Where.SETTINGS_STRAY]
        ),
        "a key with no folder, set to false": edit(
            lambda f: registry_enabled(f).update({f"const-gone@{tag}": False}), [Where.SETTINGS_STRAY]
        ),
        "a key of the marketplace with no module name": edit(
            lambda f: registry_enabled(f).update({f"@{tag}": True}), [Where.SETTINGS_STRAY]
        ),
        "a declaration the settings lack": edit(lambda f: registry_known(f).pop(tag), [Where.KNOWN_MISSING]),
        "a declaration of another marketplace only": edit(
            lambda f: f[settings].update(
                {"extraKnownMarketplaces": {"elsewhere": {"source": dict(DIRECTORY_SOURCE)}}}
            ),
            [Where.KNOWN_MISSING],
        ),
        "settings with no extraKnownMarketplaces at all": edit(
            lambda f: f[settings].pop("extraKnownMarketplaces"), [Where.KNOWN_MISSING]
        ),
        "a top-level key of a module's form with no module folder": edit(
            with_dials({"root_policy": "p", "const-x": {}, "const-gone": {}}), stray
        ),
        "two such keys are two findings": edit(
            with_dials({"const-gone": {}, "const-away": {}}), stray + stray
        ),
        "a namespace for each module folder and nothing else": edit(
            with_dials({"const-x": {}, "const-quiet": 1}), []
        ),
        "a dials file with no namespace of a module at all": edit(with_dials({"root_policy": "p"}), []),
        "the same name below a top-level key is no top-level key": edit(
            with_dials({"const-x": {"const-gone": 1}, "plc-0001-root-policy": {"const-away": 1}}), []
        ),
        "kernel keys and policy namespaces are not judged": edit(
            with_dials(
                {"root_policy": "p", "territory_dialect": "git", "plc-0001-root-policy": {}, "dec": {}}
            ),
            [],
        ),
        "a key that is no string is not judged": edit(
            with_dials("root_policy: p\n1: a\ntrue: b\nnull: c\n"), []
        ),
        "comments, an anchor, an alias and quoted keys are read as YAML": edit(
            with_dials(yaml_text), stray + stray
        ),
        "a third module the mirror imports from, MYPYPATH lacking it": edit(
            with_mirror(p, q, "const-r"), one
        ),
        "a third module on MYPYPATH, the mirror lacking it": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={mypypath(p, q, 'const-r')} ")
        ),
        "the same pair in the other order": edit(
            with_mirror(p, q), [], types_with(f"MYPYPATH={mypypath(q, p)} ")
        ),
        "a mirror of one folder and a MYPYPATH of the same one": edit(
            with_mirror(p), [], types_with(f"MYPYPATH={mypypath(p)} ")
        ),
        "a types entry with no MYPYPATH": edit(with_mirror(p, q), one, types_with("")),
        "a MYPYPATH named only in a comment of the entry": edit(
            with_mirror(p, q), one, types_with("") + f"  # MYPYPATH={mypypath(p, q)}"
        ),
        "a MYPYPATH with a path that is no module folder's nor the shared one": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={mypypath(p, q)}:../other ")
        ),
        "the shared package missing from MYPYPATH": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={mypypath(p, q, shared=False)} ")
        ),
        "../shared first and the pair after it": edit(
            with_mirror(p, q), [], types_with(f"MYPYPATH={TYPES_SHARED}:{mypypath(p, q, shared=False)} ")
        ),
        "../shared alone, the mirror importing from a pair": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={TYPES_SHARED} ")
        ),
        "the shared package under another path": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={mypypath(p, q, shared=False)}:../x/shared ")
        ),
        "the shared folder of the kit's root, not of the scripts' folder": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={mypypath(p, q, shared=False)}:shared ")
        ),
        "a folder of the pair under another path": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={mypypath(p)}:../x/{q}/scripts ")
        ),
        "the pair on a quoted MYPYPATH": edit(
            with_mirror(p, q), [], types_with(f'MYPYPATH="{mypypath(p, q)}" ')
        ),
        "the pair split over two settings of the entry": edit(
            with_mirror(p, q),
            [],
            types_with(f"MYPYPATH={mypypath(p)} ")
            + f"\ncd scripts && MYPYPATH={mypypath(q)} python3 -m mypy --strict check-x.py",
        ),
        # "exactly": an empty element of the path is one more entry, so it is a difference, never dropped
        "the pair with a colon at the end of MYPYPATH": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={mypypath(p, q)}: ")
        ),
        "the pair with a colon at the start of MYPYPATH": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH=:{mypypath(p, q)} ")
        ),
        "the pair with a doubled colon in MYPYPATH": edit(
            with_mirror(p, q), one, types_with(f"MYPYPATH={mypypath(p)}::{mypypath(q)} ")
        ),
        "an empty MYPYPATH": edit(with_mirror(p, q), one, types_with("MYPYPATH= ")),
    }
    for what, source in {  # the declaration's source must be exactly a directory at `.`
        "a path ./x": {"source": "directory", "path": "./x"},
        "a path ./": {"source": "directory", "path": "./"},
        "no path": {"source": "directory"},
        "a github source": {"source": "github", "repo": "a/b"},
        "a key beside the two": {"source": "directory", "path": ".", "extra": 1},
        "an empty object": {},
        "a string": ".",
        "null": None,
    }.items():
        cases[f"a declaration whose source is {what}"] = edit(declared_as(source), [Where.KNOWN_SOURCE])
    cases["a declaration with no source"] = edit(
        lambda f: registry_known(f)[tag].pop("source"), [Where.KNOWN_SOURCE]
    )
    cases["a declaration that is a string"] = edit(
        lambda f: registry_known(f).update({tag: "."}), [Where.KNOWN_SOURCE]
    )
    for what, value in {  # a module is enabled by the JSON boolean `true` and nothing else
        "false": False,
        "1": 1,
        "1.0": 1.0,
        '"true"': "true",
        "null": None,
        "a list": [True],
        "an object": {"enabled": True},
    }.items():
        cases[f"a module enabled as {what}"] = edit(enabled_as(value), [Where.SETTINGS])
    return cases


def backwards(value: Any) -> Any:
    """`value` with the keys of every object and the items of every list in reverse order."""
    if isinstance(value, dict):
        return {key: backwards(item) for key, item in reversed(list(value.items()))}
    if isinstance(value, list):
        return [backwards(item) for item in reversed(value)]
    return value


def messy_case(scan: str, reverse: bool) -> Case:
    """One tree with a finding of every kind of registry finding but the declaration's absence, over six
    folders; `reverse` writes every object's keys and every list in the opposite order, which must change
    nothing of the report."""
    market, settings, tag = MARKETPLACE_FILE, SETTINGS_FILE, REGISTRY_TAG
    folders = ("const-x", "glossary", "const-A", "const-m", "const-n", "const-s")
    files = registry_tree(folders, tag)
    files["modules/const-m/plugin/.claude-plugin/plugin.json"]["name"] = "const-y"
    files["modules/const-n/plugin/.claude-plugin/plugin.json"].pop("name")
    plugins: list[dict[str, Any]] = files[market]["plugins"]
    plugins[:] = [entry for entry in plugins if entry["name"] != "const-m"]
    for entry in plugins:
        if entry["name"] == "const-n":
            entry["source"] = {"type": "github", "repo": "a/b"}
        if entry["name"] == "const-s":
            plugins.append(dict(entry))
            break
    files["modules/const-m/plugin/.claude-plugin/plugin.json"]["description"] = 5  # no entry: not judged
    files["modules/const-s/plugin/.claude-plugin/plugin.json"].pop("description")  # two entries: not judged
    files["modules/const-x/plugin/.claude-plugin/plugin.json"].pop("description")  # judged: the manifest's
    for entry in plugins:
        if entry["name"] == "const-n":
            entry["description"] = "The module const-n!"  # the first difference, at character 19
        if entry["name"] == "glossary":
            entry["description"] = 7  # an entry whose description is no string
    # six strays, written in neither their sorted order nor its reverse, nor in the order `backwards` gives
    # them: no chance order of a set is likelier than 1 in 720 to be the sorted one, so a sort holds it
    strays = ("const-gone", "const-away", "const-zed", "const-mid", "const-bar", "const-old")
    plugins += [{"name": name, "source": plugin_source(name)} for name in strays]
    enabled: dict[str, Any] = files[settings]["enabledPlugins"]
    enabled.update({f"const-m@{tag}": False, f"const-s@{tag}": "true", "other@elsewhere": True})
    enabled.update({f"const-gone@{tag}": True, f"const-away@{tag}": True})
    enabled.pop(f"const-n@{tag}")
    files[settings]["extraKnownMarketplaces"][tag]["source"]["path"] = "./x"
    return Case({"x": scan}, folders=folders, files=backwards(files) if reverse else files)


def strays_case(scan: str) -> Case:
    """One tree whose marketplace and settings name seven things that are no module folder: a module's
    name whose folder is missing, a plain file of a module's name, a missing folder of another name, one
    opening with `_`, one opening with `.`, a name of two path parts and the empty name; the folders that
    exist but are no module's carry a MODULE.md, the file a plain one."""
    market, settings, tag = MARKETPLACE_FILE, SETTINGS_FILE, REGISTRY_TAG
    names = ("", ".x", "_x", "a/b", "const-gone", "const-plain", "gone")
    files = registry_tree(("const-x", "const-quiet"), tag)
    files[market]["plugins"] += [{"name": name, "source": plugin_source(name)} for name in names]
    files[settings]["enabledPlugins"].update({f"{name}@{tag}": True for name in names})
    return Case(
        {"x": scan},
        scripts={"modules/_x/MODULE.md": False, "modules/.x/MODULE.md": False, "modules/const-plain": False},
        files=files,
    )


GUIDE_X = "const-x/plugin/scripts/check-x.sh"  # the scan const-x declares, as the guide lists it
GUIDE_P = "const-p/plugin/scripts/check-p.sh"  # the scan const-p declares as `check-p.py --scan`: its .sh
GUIDE_GONE = "const-gone/plugin/scripts/check-gone.sh"  # a path no module declares


def guide_case(scan: str, module_text: str, guide: str | None) -> Case:
    """Three folders: const-x declares `check-x`, const-p declares `check-p.py`, const-quiet declares none;
    the install guide is `guide`."""
    p_text = module_text.replace("check-x", "check-p").replace("`check-p --scan`", "`check-p.py --scan`")
    return Case(
        {"x": scan, "p": f"{SHARED_SETTING} python3 modules/const-p/plugin/scripts/check-p.py --scan"},
        jobs={"p": "const-p"},
        folders=("const-x", "const-quiet", "const-p"),
        documents={"const-p": p_text},
        guide=guide,
    )


def guide_cases(scan: str, module_text: str) -> dict[str, tuple[Case, list[Where]]]:
    """The guide's scan block against the declared scans, each a guide edited once: the findings it must
    give, in their fixed order (the missing scans in the folders' order, then the strays by path). Beside
    `registry_cases`, whose files name the modules the same way."""
    add, drop = Where.GUIDE_ADD, Where.GUIDE_DROP

    def edit(*paths: str, tail: str = "") -> Case:
        return guide_case(scan, module_text, guide_text(*paths) + tail)

    other = "   ```bash check=none\n   for s in " + GUIDE_GONE + '; do sh ~/kit/modules/"$s"; done\n   ```\n'
    return {
        "the guide's scan block names exactly the declared scans, `check-x` and `check-p.py` alike": (
            edit(GUIDE_X, GUIDE_P),
            [],
        ),
        "the guide's scan block names them in another order": (edit(GUIDE_P, GUIDE_X), []),
        "the guide's scan block leaves out a scan declared as `check-x`": (edit(GUIDE_P), [add]),
        "the guide's scan block leaves out a scan declared as `check-p.py`": (edit(GUIDE_X), [add]),
        "the guide's scan block lists nothing": (edit(), [add, add]),
        "the guide's scan block lists a path no module declares": (
            edit(GUIDE_X, GUIDE_P, GUIDE_GONE),
            [drop],
        ),
        "the guide's scan block lists a module that declares no scan": (
            edit(GUIDE_X, GUIDE_P, "const-quiet/plugin/scripts/check-q.sh"),
            [drop],
        ),
        "the guide's scan block lists the .py file of a scan its loop runs with sh": (
            edit("const-x/plugin/scripts/check-x.py", GUIDE_P),
            [add, drop],
        ),
        "the guide's scan block lists every scan at the module's top, outside its plugin folder": (
            edit("const-x/scripts/check-x.sh", "const-p/scripts/check-p.sh"),
            [add, add, drop, drop],
        ),
        "the guide's scan block lists a path twice": (edit(GUIDE_X, GUIDE_X, GUIDE_P), []),
        "a module that declares no scan is owed no path": (
            Case({"o": "true"}, folders=("const-quiet",), guide=guide_text()),
            [],
        ),
        "a block other than the scan block lists a path no module declares: not read": (
            edit(GUIDE_X, GUIDE_P, tail=other),
            [],
        ),
    }


def coverage_text(owner: str, *pairs: dict[str, Any]) -> str:
    """A dials file with the coverage map under `owner`, in the block style the kit writes it, so that a fix
    text can be followed on it line by line; an empty list is the one flow-style form."""
    lines = ["root_policy: policies", f"{owner}:"]
    if not pairs:
        return "\n".join([*lines, f"  {COVERAGE_KEY}: []"]) + "\n"
    lines.append(f"  {COVERAGE_KEY}:")
    for pair in pairs:
        lines.append(f"    - name: {pair['name']}")
        for key in ("code", "docs"):
            lines += (
                [f"      {key}:", *(f'        - "{item}"' for item in pair[key])]
                if pair[key]
                else [f"      {key}: []"]
            )
    return "\n".join(lines) + "\n"


def pair_span(lines: list[str], name: str, nth: int = 0) -> tuple[int, int]:
    """The lines of the `nth` pair named `name` in a dials text from `coverage_text`: its `- name:` line up to
    the next pair's, or the end."""
    starts = [at for at, line in enumerate(lines) if line == f"    - name: {name}"]
    start = starts[nth]
    end = next((at for at in range(start + 1, len(lines)) if lines[at].startswith("    - name:")), len(lines))
    return start, end


def follow_coverage_fix(text: str, report: str) -> str:
    """The dials text `text` after the fix a coverage finding teaches, `report` being the finding's text, done
    to the letter of its fix line: an entry added after `coverage:` (in place of `[]`), the pairs of a name
    after the first removed, the `docs` of a pair set, a pattern removed from a pair's `code`, a line added to
    it. The text unchanged for a fix of no form known here, which the caller's rerun then holds red."""
    first, *block = report.split("  fix: ", 1)[1].splitlines()
    lines = text.splitlines()
    if first.startswith("add this entry to "):
        at = next(i for i, line in enumerate(lines) if line.startswith(f"  {COVERAGE_KEY}:"))
        lines[at : at + 1] = [f"  {COVERAGE_KEY}:", *block]
    elif (
        told := re.fullmatch(r"remove every pair named `([^`]+)` after the first from .*", first)
    ) is not None:
        count = sum(1 for line in lines if line == f"    - name: {told[1]}")
        for nth in range(count - 1, 0, -1):  # from the last, so that the earlier spans keep their places
            start, end = pair_span(lines, told[1], nth)
            del lines[start:end]
    elif (
        told := re.fullmatch(r"set `docs` of the pair named `([^`]+)` to the one path `([^`]+)`", first)
    ) is not None:
        start, end = pair_span(lines, told[1])
        at = next(i for i in range(start, end) if lines[i].startswith("      docs:"))
        lines[at:end] = ["      docs:", f'        - "{told[2]}"']
    elif (
        told := re.fullmatch(r"remove `([^`]+)` from `code` of the pair named `([^`]+)`", first)
    ) is not None:
        start, end = pair_span(lines, told[2])
        for at in range(start, end):
            if lines[at] == f'        - "{told[1]}"':
                del lines[at]
                break
    elif (
        told := re.fullmatch(r'add the line `- "([^`]+)"` to `code` of the pair named `([^`]+)`', first)
    ) is not None:
        start, end = pair_span(lines, told[2])
        at = next(i for i in range(start, end) if lines[i].startswith("      code:"))
        lines[at : at + 1] = ["      code:", f'        - "{told[1]}"']  # the pair's other patterns follow
    return "\n".join(lines) + "\n"


def coverage_case(
    scan: str,
    pairs: list[dict[str, Any]],
    *folders: str,
    plain: tuple[str, ...] = (),
    modules: tuple[str, ...] = ("const-x", "const-quiet"),
    owner: str = "",
) -> Case:
    """The tree of `modules` whose coverage map holds `pairs`, the folders `folders` (`<module>/<folder>`)
    as directories under modules/, a file in each, and the paths `plain` as plain files there; the map is
    read under `owner` when given."""
    files = registry_tree(modules, REGISTRY_TAG)
    files[DIALS] = coverage_text(owner or TEST_OWNER, *pairs)
    return Case(
        {"o": "true"} if "const-x" not in modules else {"x": scan},
        folders=modules,
        files=files,
        scripts={
            **{f"modules/{folder}/file": False for folder in folders},
            **{f"modules/{p}": False for p in plain},
        },
        owner=owner,
    )


def coverage_cases(scan: str) -> dict[str, tuple[Case, list[Where]]]:
    """A module's pair in the coverage map against the module folders, each a map edited once: the findings
    it must give, by module, then docs, patterns outside, folders. Beside `registry_cases`, whose dials file
    and files name the modules the same way. The folders of the tree are const-x and const-quiet."""
    missing, twice, docs = Where.COVERAGE_MISSING, Where.COVERAGE_TWICE, Where.COVERAGE_DOCS
    outside, folder = Where.COVERAGE_OUTSIDE, Where.COVERAGE_FOLDER
    x, quiet = full_pair("const-x"), full_pair("const-quiet")
    all_folders = tuple(f"const-x/{name}" for name in COVERAGE_FOLDERS)
    outside_cases = {
        "a pattern of no module": "scripts/**",
        "a pattern of another module": "modules/const-quiet/plugin/scripts/**",
        "a pattern of a module whose name opens with the module's": "modules/const-xy/plugin/scripts/**",
        "a pattern that is the module's folder with no slash": "modules/const-x",
        "a pattern anchored at the root": "/modules/const-x/plugin/scripts/**",
    }

    def case(*pairs: dict[str, Any], dirs: tuple[str, ...] = (), plain: tuple[str, ...] = ()) -> Case:
        return coverage_case(scan, list(pairs), *dirs, plain=plain)

    def with_docs(*paths: str) -> dict[str, Any]:
        return {**x, "docs": list(paths)}

    def with_code(*patterns: str) -> dict[str, Any]:
        return {**x, "code": list(patterns)}

    cases: dict[str, tuple[Case, list[Where]]] = {
        "the coverage map has a pair for each module, a pattern for each folder it has": (
            case(x, quiet, dirs=all_folders),
            [],
        ),
        "a module without a plugin/hooks/ folder and with no hooks pattern": (
            case(
                full_pair("const-x", ("plugin/scripts", "plugin/skills", "tests")),
                quiet,
                dirs=("const-x/plugin/scripts", "const-x/plugin/skills", "const-x/tests"),
            ),
            [],
        ),
        "a module with a skills pattern and no plugin/skills/ folder": (
            case(x, quiet, dirs=("const-x/plugin/scripts", "const-x/plugin/hooks", "const-x/tests")),
            [],
        ),
        "a module with a pattern for each folder and none of the folders": (case(x, quiet), []),
        "a plugin/hooks entry that is a plain file is no folder": (
            case(
                full_pair("const-x", ("plugin/scripts", "plugin/skills", "tests")),
                quiet,
                dirs=("const-x/plugin",),
                plain=("const-x/plugin/hooks",),
            ),
            [],
        ),
        "scripts/, hooks/ and skills/ at the module's top, outside plugin/, are no folders of the map": (
            case(
                full_pair("const-x", ("tests", "evals")),
                quiet,
                dirs=("const-x/scripts", "const-x/hooks", "const-x/skills", "const-x/tests", "const-x/evals"),
            ),
            [],
        ),
        "tests/ and evals/ inside plugin/, outside the module's own, are no folders of the map": (
            case(
                full_pair("const-x", ("plugin/scripts",)),
                quiet,
                dirs=("const-x/plugin/scripts", "const-x/plugin/tests", "const-x/plugin/evals"),
            ),
            [],
        ),
        "the pairs in another order": (case(quiet, x, dirs=all_folders), []),
        "a pair that lists more patterns inside the module": (
            case(with_code(*x["code"], "modules/const-x/README.md"), quiet),
            [],
        ),
        "the three entries of no module are not judged, whatever they hold": (
            case(
                {
                    "name": "shared-gate-code",
                    "code": ["shared/constitution_layer_kit/**"],
                    "docs": ["shared/GATE.md"],
                },
                x,
                {"name": "kit-scripts", "code": ["scripts/**", "/pyproject.toml"], "docs": ["CLAUDE.md"]},
                quiet,
                {"name": "kernel-schemas", "code": [], "docs": []},
            ),
            [],
        ),
        "an entry named for a missing module folder is not judged": (
            case(x, quiet, {"name": "const-gone", "code": ["elsewhere/**"], "docs": ["a.md", "b.md"]}),
            [],
        ),
        "the map read under the real key, const-task-close, with a pair for each module": (
            coverage_case(
                scan,
                [full_pair("const-task-close"), full_pair("const-quiet")],
                modules=("const-task-close", "const-quiet"),
                owner=COVERAGE_OWNER,
            ),
            [],
        ),
        "a module with no pair": (case(quiet), [missing]),
        "a module with no pair, its folders existing": (case(quiet, dirs=all_folders), [missing]),
        "no pair for either module": (case(), [missing, missing]),
        "a module with no pair beside a module with a wrong one: by module": (
            case(with_docs("modules/const-x/README.md")),
            [missing, docs],
        ),
        "a name that only opens like the module's is no pair for it": (
            case({**x, "name": "const-xy"}, quiet),
            [missing],
        ),
        "a pair named for the module in another case is no pair for it": (
            case({**x, "name": "Const-x"}, quiet),
            [missing],
        ),
        "two pairs of one name": (case(x, quiet, x), [twice]),
        "three pairs of one name": (case(x, x, quiet, x), [twice]),
        "two pairs of one name, the second with other docs: judged by the two alone": (
            case(x, with_docs("modules/const-x/README.md"), quiet),
            [twice],
        ),
        "two pairs of one name, the first wrong: judged by the two alone": (
            case(with_docs("README.md"), x, quiet),
            [twice],
        ),
        "docs of another file": (case(with_docs("modules/const-x/README.md"), quiet), [docs]),
        "docs of two files": (
            case(with_docs("modules/const-x/MODULE.md", "modules/const-x/README.md"), quiet),
            [docs],
        ),
        "docs of the module document twice": (
            case(with_docs("modules/const-x/MODULE.md", "modules/const-x/MODULE.md"), quiet),
            [docs],
        ),
        "docs of no file": (case(with_docs(), quiet), [docs]),
        "docs of another module's document": (
            case(with_docs("modules/const-quiet/MODULE.md"), quiet),
            [docs],
        ),
        "docs that open with ./": (case(with_docs("./modules/const-x/MODULE.md"), quiet), [docs]),
        "two patterns of no module are two findings": (
            case(with_code(*x["code"], "scripts/**", "docs/constitution/**"), quiet),
            [outside, outside],
        ),
        "a pattern missing and a pattern outside, the folders existing: by kind": (
            case(with_code("scripts/**", "modules/const-x/plugin/scripts/**"), quiet, dirs=all_folders),
            [outside, *[folder] * (len(COVERAGE_FOLDERS) - 1)],
        ),
        "a wrong doc, a pattern outside and a folder without a pattern: in that order": (
            case(
                {**x, "docs": ["README.md"], "code": ["scripts/**", *x["code"][1:]]},
                quiet,
                dirs=all_folders,
            ),
            [docs, outside, folder],
        ),
        "a folder present with a pattern that is not the whole folder": (
            case(
                with_code("modules/const-x/plugin/hooks/*.json", *x["code"][:1], *x["code"][2:]),
                quiet,
                dirs=all_folders,
            ),
            [folder],
        ),
        "a folder present and its pattern one level too deep": (
            case(
                with_code("modules/const-x/plugin/hooks/**/*", *x["code"][:1], *x["code"][2:]),
                quiet,
                dirs=all_folders,
            ),
            [folder],
        ),
        "two folders present and no pattern for either": (
            case(
                with_code(*x["code"][2:]),
                quiet,
                dirs=("const-x/plugin/scripts", "const-x/plugin/hooks", "const-x/plugin/skills"),
            ),
            [folder, folder],
        ),
        "a pattern for scripts/ at the module's top is none for plugin/scripts/": (
            case(with_code("modules/const-x/scripts/**", *x["code"][1:]), quiet, dirs=all_folders),
            [folder],
        ),
        "a pattern for tests/ inside plugin/ is none for the module's tests/": (
            case(
                with_code(*x["code"][:3], "modules/const-x/plugin/tests/**", *x["code"][4:]),
                quiet,
                dirs=all_folders,
            ),
            [folder],
        ),
    }
    for what, pattern in outside_cases.items():
        cases[f"{what} is outside the module"] = (case(with_code(*x["code"], pattern), quiet), [outside])
    for name in COVERAGE_FOLDERS:
        cases[f"a {name}/ folder present and no pattern for it"] = (
            case(
                with_code(*(c for c in x["code"] if c != f"modules/const-x/{name}/**")),
                quiet,
                dirs=all_folders,
            ),
            [folder],
        )
    return cases


def broken_no_json(path: str, said: str = "Expecting property name enclosed in double quotes, line 1") -> str:
    """The BROKEN line of a JSON file that does not parse, `said` the parser's words."""
    return f"{path} is no JSON ({said}) — fix: restore it as a JSON object"


def broken_no_object(path: str, kind: str) -> str:
    """The BROKEN line of a JSON file that holds a `kind` and no object."""
    return f"{path} is no JSON object, it holds a {kind} — fix: restore it as a JSON object"


def broken_no_file(path: str) -> str:
    """The BROKEN line of a JSON file that is missing."""
    return f"{path} is no file — fix: restore it as a JSON file holding an object"


def broken_dials_fix(what: str) -> str:
    """The BROKEN line of the dials file that is missing: `what`, then the fix."""
    return f"{what} — fix: restore the kit's dials file at the kit root"


def broken_not_mapping(kind: str) -> str:
    """The BROKEN line of a dials file that holds a `kind` and no mapping."""
    return f"{DIALS} is no YAML mapping, it holds a {kind} — fix: restore it as a mapping of namespaces"


def broken_loops(count: int) -> str:
    """The BROKEN line of a schema mirror with `count` loops over its folders, not one."""
    return (
        f"{MIRROR} has {count} loops `for module in (...)` over a tuple of folder names, not one"
        " — fix: restore the one loop that puts the module folders on its import path"
    )


def broken_no_list(said: str, key: str = TEST_OWNER) -> str:
    """The BROKEN line of a coverage map under `key` that is no list, `said` what it is."""
    return (
        f"{DIALS}: `{key}.coverage` is no list ({said}) — fix: restore it as a list of pairs, each"
        f" `- name: <territory>` with a `code` list and a `docs` list, under `coverage:` in the `{key}`"
        " namespace"
    )


def broken_bad_entry(position: int) -> str:
    """The BROKEN line of the coverage map's entry `position` that is no pair of the right form."""
    return (
        f"{DIALS}: entry {position} of `{TEST_OWNER}.coverage` is no mapping with a string `name`, a"
        " `code` list and a `docs` list of strings — fix: write each pair as `- name: <territory>` with"
        " `code:` and `docs:` lists of path patterns"
    )


def broken_cases(scan: str) -> dict[str, tuple[Case, str]]:
    """The files the check cannot read, each a matching registry with one file or key spoilt: the first
    line of the BROKEN report, which names the file and how to fix it."""
    m, s, x = MARKETPLACE_FILE, SETTINGS_FILE, MANIFEST_X
    quiet = "modules/const-quiet/plugin/.claude-plugin/plugin.json"
    entry_fix = '{"name": …, "source": …}'

    def spoil(change: Callable[[dict[str, Any]], object]) -> Case:
        return registry_case(scan, change)

    def put(path: str, text: str | None) -> Case:  # `text`: the file's whole text, None for no file
        return spoil(lambda f: f.update({path: text}))

    name_line = (
        f'{m} has no marketplace name, "name" is no non-empty string'
        " — fix: restore it, the name the kit's settings enable plugins under"
    )
    plugins_line = f'{m} has no list "plugins" — fix: restore it as a list of entries {entry_fix}'
    one_line = (
        f"{m}: entry 2 of plugins is no object with a string name — fix: write each entry as {entry_fix}"
    )

    def market(change: Callable[[dict[str, Any]], object]) -> Case:
        return spoil(lambda f: change(f[MARKETPLACE_FILE]))

    def settings(change: Callable[[dict[str, Any]], object]) -> Case:
        return spoil(lambda f: change(f[SETTINGS_FILE]))

    no_block = (
        f"{GUIDE_FILE} has no block `bash check=scan` — fix: add the fenced block that runs every module's"
        " scan in the guide's verify step, its fence `bash check=scan`"
    )
    form_fix = (
        " — fix: begin it with `for s in <module>/plugin/scripts/<stem>.sh …; do`, the paths being the"
        " scans the modules declare, each `<stem>` the declared scan's name without `.py`,"
        ' and run each as `"$s"` after `do`'
    )
    form_line = (
        f"{GUIDE_FILE}:4: the first line of the block `bash check=scan` is not `for s in <paths>; do …`"
        + form_fix
    )

    def coverage(*entries: str) -> Case:  # the map's entries as YAML lines, under the self-test's key
        return put(DIALS, f"{TEST_OWNER}:\n  coverage:\n" + "".join(f"    {line}\n" for line in entries))

    good = ["- name: const-x", "  code: []", "  docs: []"]

    return {
        "a manifest that is missing": (put(x, None), broken_no_file(x)),
        "a manifest that is no JSON": (put(x, "{ not json\n"), broken_no_json(x)),
        "a manifest that is empty": (put(x, ""), broken_no_json(x, "Expecting value, line 1")),
        "a manifest that is a list": (put(x, "[]\n"), broken_no_object(x, "list")),
        "a manifest that is a string": (put(x, '"const-x"\n'), broken_no_object(x, "str")),
        "a manifest that is null": (put(x, "null\n"), broken_no_object(x, "NoneType")),
        "two manifests that are broken: the first folder in sorted order is named": (
            spoil(lambda f: f.update({x: None, quiet: "[]"})),
            broken_no_object(quiet, "list"),
        ),
        "a manifest and the marketplace broken: the manifest is named": (
            spoil(lambda f: f.update({x: "[]", m: "[]"})),
            broken_no_object(x, "list"),
        ),
        "a marketplace that is missing": (put(m, None), broken_no_file(m)),
        "a marketplace that is no JSON": (put(m, "{ not json\n"), broken_no_json(m)),
        "a marketplace that is a list": (put(m, "[]\n"), broken_no_object(m, "list")),
        "a marketplace with no name": (market(lambda d: d.pop("name")), name_line),
        "a marketplace whose name is empty": (market(lambda d: d.update({"name": ""})), name_line),
        "a marketplace whose name is no string": (market(lambda d: d.update({"name": 5})), name_line),
        "a marketplace with no plugins": (market(lambda d: d.pop("plugins")), plugins_line),
        "a marketplace whose plugins are an object": (
            market(lambda d: d.update({"plugins": {"const-x": {}}})),
            plugins_line,
        ),
        "a marketplace whose plugins are null": (market(lambda d: d.update({"plugins": None})), plugins_line),
        "a marketplace with an entry that is a string": (
            market(lambda d: d["plugins"].__setitem__(1, "const-quiet")),
            one_line,
        ),
        "a marketplace with an entry that has no name": (
            market(lambda d: d["plugins"][1].pop("name")),
            one_line,
        ),
        "a marketplace with an entry whose name is no string": (
            market(lambda d: d["plugins"][1].update({"name": 7})),
            one_line,
        ),
        "settings that are missing": (put(s, None), broken_no_file(s)),
        "settings that are no JSON": (put(s, "{ not json\n"), broken_no_json(s)),
        "settings that are a list": (put(s, "[]\n"), broken_no_object(s, "list")),
        "settings whose enabledPlugins are a list": (
            settings(lambda d: d.update({"enabledPlugins": ["const-x@kit-test"]})),
            f"{s}: enabledPlugins is no JSON object — fix: restore it as an object",
        ),
        "settings whose enabledPlugins are null": (
            settings(lambda d: d.update({"enabledPlugins": None})),
            f"{s}: enabledPlugins is no JSON object — fix: restore it as an object",
        ),
        "settings whose extraKnownMarketplaces are a string": (
            settings(lambda d: d.update({"extraKnownMarketplaces": "kit-test"})),
            f"{s}: extraKnownMarketplaces is no JSON object — fix: restore it as an object",
        ),
        "settings whose two objects are wrong: enabledPlugins is named": (
            settings(lambda d: d.update({"enabledPlugins": [], "extraKnownMarketplaces": []})),
            f"{s}: enabledPlugins is no JSON object — fix: restore it as an object",
        ),
        "a dials file that is missing": (put(DIALS, None), broken_dials_fix(f"{DIALS} is no file")),
        "a dials file that is no YAML": (
            put(DIALS, "a: b: c\n"),
            f"{DIALS} is no YAML (mapping values are not allowed here) — fix: repair the file",
        ),
        "a dials file that is a list": (put(DIALS, "- a\n"), broken_not_mapping("list")),
        "a dials file that is empty": (put(DIALS, ""), broken_not_mapping("NoneType")),
        "a dials file that is a string": (put(DIALS, "x\n"), broken_not_mapping("str")),
        "a schema mirror that is missing": (put(MIRROR, None), f"{MIRROR} is no file — fix: restore it"),
        "a schema mirror that is no Python": (
            put(MIRROR, "for module in (:\n"),
            f"{MIRROR} is no Python (a syntax error at line 1) — fix: repair the file",
        ),
        "a schema mirror with no loop over its folders": (put(MIRROR, "x = 1\n"), broken_loops(0)),
        "a schema mirror with two such loops": (
            put(MIRROR, mirror_text(("a",)) + mirror_text(("b",))),
            broken_loops(2),
        ),
        "a schema mirror whose loop runs over a list": (
            put(MIRROR, "for module in ['a']:\n    pass\n"),
            broken_loops(0),
        ),
        "a schema mirror whose tuple holds a non-string": (
            put(MIRROR, "for module in ('a', 3):\n    pass\n"),
            broken_loops(0),
        ),
        "a schema mirror whose loop variable is not `module`": (
            put(MIRROR, "for folder in ('a',):\n    pass\n"),
            broken_loops(0),
        ),
        "a schema mirror whose tuple is empty": (
            put(MIRROR, "for module in ():\n    pass\n"),
            broken_loops(0),
        ),
        "a gate list with no types entry": (
            Case({"x": scan}, types=None),
            f"{GATE_LIST} --show types exited 1 (no output) — fix: restore the list script",
        ),
        "an install guide that is missing": (
            Case({"x": scan}, guide=None),
            f"{GUIDE_FILE} is no file — fix: restore the install guide at the kit root, with the fenced"
            " block `bash check=scan` that lists every scan",
        ),
        "an install guide whose only scan block is marked check=none": (
            Case({"x": scan}, guide=guide_text(GUIDE_X, block="bash check=none")),
            no_block,
        ),
        "an install guide whose scan mark stands on a fence that is not bash": (
            Case({"x": scan}, guide=guide_text(GUIDE_X, block="text check=scan")),
            no_block,
        ),
        "an install guide with two scan blocks": (
            Case(
                {"x": scan}, guide=guide_text(GUIDE_X) + "```bash check=scan\nfor s in ; do true; done\n```\n"
            ),
            f"{GUIDE_FILE} has 2 blocks `bash check=scan`, at lines 4 and 11 — fix: keep one: list the paths"
            " of both in the first and give the other `check=none`",
        ),
        "an install guide whose scan block runs a command, not a loop": (
            Case({"x": scan}, guide=guide_text(GUIDE_X).replace("for s in const-x", "sh const-x", 1)),
            form_line,
        ),
        "an install guide whose scan block has a command before its loop": (
            Case({"x": scan}, guide=guide_text(GUIDE_X).replace("for s in", "cd x; for s in", 1)),
            form_line,
        ),
        "an install guide whose scan block holds a tilde line, then a second scan block": (
            Case(
                {"x": scan},
                guide=guide_text(GUIDE_X).replace(
                    "   ```\n   Then the fixtures:",
                    "   ~~~\n   ```\n```bash check=scan\nfor s in ; do true; done\n```\n"
                    "   Then the fixtures:",
                    1,
                ),
            ),
            f"{GUIDE_FILE} has 2 blocks `bash check=scan`, at lines 4 and 8 — fix: keep one: list the paths"
            " of both in the first and give the other `check=none`",
        ),
        "an install guide whose scan loop runs over another variable": (
            Case({"x": scan}, guide=guide_text(GUIDE_X).replace("for s in", "for m in", 1)),
            form_line,
        ),
        "an install guide whose scan loop has no `; do`": (
            Case({"x": scan}, guide=guide_text(GUIDE_X).replace("; do sh", "; sh", 1)),
            form_line,
        ),
        "an install guide whose scan block is empty": (
            Case({"x": scan}, guide="# Install\n\n   ```bash check=scan\n   ```\n"),
            f"{GUIDE_FILE}:3: the first line of the block `bash check=scan` is not `for s in <paths>; do …`"
            + form_fix,
        ),
        "a coverage map under the real key, const-task-close, when only the self-test's key holds one": (
            Case({"x": scan}, owner=COVERAGE_OWNER),
            broken_no_list("it is absent", COVERAGE_OWNER),
        ),
        "a dials file with no coverage namespace": (
            put(DIALS, "root_policy: p\n"),
            broken_no_list("it is absent"),
        ),
        "a coverage namespace that is a string": (
            put(DIALS, f"{TEST_OWNER}: x\n"),
            broken_no_list("it is absent"),
        ),
        "a coverage map that is empty": (
            put(DIALS, f"{TEST_OWNER}:\n  coverage:\n"),
            broken_no_list("it is absent"),
        ),
        "a coverage map that is a mapping": (
            put(DIALS, f"{TEST_OWNER}:\n  coverage: {{a: 1}}\n"),
            broken_no_list("it holds a dict"),
        ),
        "a coverage map that is a string": (
            put(DIALS, f"{TEST_OWNER}:\n  coverage: x\n"),
            broken_no_list("it holds a str"),
        ),
        "a coverage entry that is a string": (coverage("- const-x"), broken_bad_entry(1)),
        "a coverage entry that is the second and has no name": (
            coverage(*good, "- code: []", "  docs: []"),
            broken_bad_entry(2),
        ),
        "a coverage entry whose name is no string": (
            coverage("- name: 7", "  code: []", "  docs: []"),
            broken_bad_entry(1),
        ),
        "a coverage entry with no code": (coverage("- name: const-x", "  docs: []"), broken_bad_entry(1)),
        "a coverage entry with no docs": (coverage("- name: const-x", "  code: []"), broken_bad_entry(1)),
        "a coverage entry whose code is a mapping": (
            coverage("- name: const-x", "  code: {a: 1}", "  docs: []"),
            broken_bad_entry(1),
        ),
        "a coverage entry whose code holds a non-string": (
            coverage("- name: const-x", "  code: [1]", "  docs: []"),
            broken_bad_entry(1),
        ),
        "a coverage entry whose docs hold a non-string": (
            coverage("- name: const-x", "  code: []", "  docs: [1]"),
            broken_bad_entry(1),
        ),
        "a coverage entry whose docs are a string": (
            coverage("- name: const-x", "  code: []", "  docs: MODULE.md"),
            broken_bad_entry(1),
        ),
    }


@dataclass
class Tally:
    """The cases the self-test has judged, and those that failed."""

    judged: int = 0
    failed: int = 0

    def judge(self, ok: bool, text: str) -> None:
        """Count one case and print its line."""
        self.judged += 1
        self.failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {text}")


MODULE_TEXT = (
    '<a id="t9"></a>\n## 9\n\n| # | artifact | kind |\n|---|---|---|\n'
    "| E1 | hook + `check-x` (hook mode) | `gate` |\n| E2 | `check-x --scan`: all | `gate` |\n"
    "| E3 | `check-x --scan --since <date>`: the report, not a tree scan | `advisory` |\n\n"
    "A sibling's `check-y` is not this module's.\n\n<a id=\"t10\"></a>\n## 10\n\n"
    "| item | kind | rows | what it proves |\n|---|---|---|---|\n| T1 | fixture | none | x |\n\n"
    '<a id="t11"></a>\n## 11\n\n<a id="t12"></a>\n## 12\n'
)

QUIET_TEXT = (
    '<a id="t9"></a>\n| E1 | `explain --scan --command <text>`: not a tree scan | `gate` |\n'
    '<a id="t10"></a>\n'
)

SCAN_COMMAND = "sh modules/const-x/plugin/scripts/check-x.sh --scan"
SCAN = f"{SHARED_SETTING} {SCAN_COMMAND}"  # as the list's `scan` function prints it


def scans_of(text: str) -> list[str]:
    """The scans a module document declares in its enforcement section."""
    return declared_scans(text)[0]


READS = f'jobs:\n  list:\n    run: {READS_LIST[0]}\n  check:\n    run: {READS_LIST[1]} "$JOB"\n'

FILTER_LINES = [
    "RED: .github/workflows/gates.yml:7: it passes `--item`, which selects some tests only",
    "  why: the gate list and CI run every item of every runner, so that their green is a full pass",
    "  fix: remove `--item` and what it selects from line 7 of .github/workflows/gates.yml",
    "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
]


def script(case: Case) -> str:
    """A stand-in for the list script: `--names gate|all|<job>`, `--json` and `--show <entry>`."""
    own = {f"{kind}-{m}": m for m in (case.folders if case.listed is None else case.listed) for kind in KINDS}
    types = {} if case.types is None else {TYPES_ENTRY: case.types}
    extras = {**dict.fromkeys((n for n in own if n not in case.gates), "true"), **types, **case.extras}
    jobs = {**{name: "kit" for name in {**case.gates, **extras}}, "x": "const-x", **own, **case.jobs}
    names = {"gate": list(case.gates), "all": [*case.gates, *extras]}
    for name, job in jobs.items():
        names.setdefault(job, []).append(name)
    groups = "".join(f"            {key}) set -- {' '.join(value)} ;;\n" for key, value in names.items())
    arms = "".join(f"            {name}) echo '{cmd}' ;;\n" for name, cmd in {**extras, **case.gates}.items())
    listing = json.dumps(sorted(set(jobs.values())))
    return (
        f'#!/bin/sh\n{f"# {case.comment}" if case.comment else ""}\ncase "$1" in\n'
        f'    --names) case "$2" in\n{groups}            *) exit 1 ;;\n        esac\n'
        '        for n in "$@"; do echo "$n"; done ;;\n'
        f"    --json) echo '{listing}' ;;\n"
        f'    --show) case "$2" in\n{arms}            *) exit 1 ;;\n        esac ;;\n'
        "    *) exit 1 ;;\nesac\n"
    )


def build(root: Path, case: Case) -> None:
    """Write the throwaway kit of the case under root."""
    documents = {"const-x": case.document or MODULE_TEXT, "const-quiet": QUIET_TEXT, **case.documents}
    for path, text in (
        *((f"modules/{m}/MODULE.md", documents.get(m, QUIET_TEXT)) for m in case.folders),
        (GATE_LIST, script(case)),
        (WORKFLOW, case.workflow or READS),
    ):
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
    for path in case.scripts:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    for path, content in (case.files or registry_tree(case.folders, case.tag)).items():
        if content is not None:
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            text = content if isinstance(content, str) else json.dumps(content, indent=2)
            (root / path).write_text(text, encoding="utf-8")
    if case.guide is not None:  # the default guide lists the scans the case's documents declare
        paths: list[str] = []
        for m in case.folders:
            with contextlib.suppress(Broken):  # a document the check cannot read declares none here
                paths += [scan_path(m, entry) for entry in scans_of(documents.get(m, QUIET_TEXT))]
        (root / GUIDE_FILE).write_text(case.guide or guide_text(*paths), encoding="utf-8")
    if case.repo:  # `git add` for the tracked files alone, so an untracked one is no kit check
        git = ["git", "-c", "init.defaultBranch=main"]
        subprocess.run([*git, "init", "-q"], cwd=root, check=True)
        tracked = [path for path, yes in case.scripts.items() if yes]
        if tracked:
            subprocess.run(["git", "add", "--", *tracked], cwd=root, check=True)


def findings_of(case: Case) -> list[Finding]:
    """The findings of the check on the throwaway kit of the case."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        build(root, case)
        with coverage_owner(case.owner or COVERAGE.owner):
            return check_kit(root)[0]


NEW_CHECK = "scripts/check-new.py"

TRACKED = {NEW_CHECK: True}

RUN_NEW = f"python3 {NEW_CHECK}"

NAME_WHY = (  # the registry reports, typed by hand: a message function cannot check itself
    "  why: the kernel names every module `const-<aspect>`, lowercase kebab-case, and the CI gives a job"
    " Claude Code by that prefix"
)

MANIFEST_WHY = (
    "  why: a plugin installs under its manifest's name, so a name that is not the folder's splits the"
    " install from the marketplace entry and the settings key"
)

SOURCE_WHY = (
    "  why: the marketplace tells the platform where a plugin loads from, and a source that is not the"
    " module's plugin folder loads another plugin or none"
)

STRAY_WHY = (
    "  why: the marketplace lists exactly the module folders, and an entry that names no module folder is"
    " a plugin no module backs"
)

DESCRIPTION_WHY = (
    "  why: a module's README opens with its manifest's description, so a marketplace entry that words it"
    " otherwise shows an installer another text for the same module"
)

ENABLED_WHY = (
    "  why: the kit's sessions load only the plugins its committed settings enable, and the one"
    " switch-off, `false`, belongs in a clone's .claude/settings.local.json"
)

KEY_WHY = (
    "  why: the settings enable exactly the module folders, and a key that names no module folder enables"
    " a plugin no module backs"
)

MAKE_FIX = ", or make modules/{} a module folder holding its MODULE.md"  # a stray named `const-<aspect>`

MARKET = ".claude-plugin/marketplace.json"

SETTINGS = ".claude/settings.json"

RENAMED = "and name its manifest, marketplace entry, settings key and entry in MODULES the same"

MESSY_LINES = [
    "RED: const-A: a module folder's name is not const-<aspect>",
    NAME_WHY,
    "  fix: rename modules/const-A to a name `const-<aspect>`, lowercase letters and digits joined by"
    f" single hyphens, {RENAMED}",
    'RED: const-m: its manifest modules/const-m/plugin/.claude-plugin/plugin.json is named "const-y", not'
    ' "const-m"',
    MANIFEST_WHY,
    '  fix: set "name": "const-m" in modules/const-m/plugin/.claude-plugin/plugin.json',
    "RED: const-n: its manifest modules/const-n/plugin/.claude-plugin/plugin.json has no name, where it"
    ' must be "const-n"',
    MANIFEST_WHY,
    '  fix: set "name": "const-n" in modules/const-n/plugin/.claude-plugin/plugin.json',
    "RED: glossary: a module folder's name is not const-<aspect>",
    NAME_WHY,
    f"  fix: rename modules/glossary to modules/const-glossary, {RENAMED}",
    "RED: const-m: the marketplace has no entry for it",
    "  why: a module the marketplace leaves out cannot be installed, by the kit's CI or by a consumer",
    f'  fix: add {{"name": "const-m", "source": "./modules/const-m/plugin"}} to plugins in {MARKET}',
    'RED: const-n: its marketplace entry has source {"repo": "a/b", "type": "github"}, not source'
    ' "./modules/const-n/plugin"',
    SOURCE_WHY,
    f'  fix: set "source" to "./modules/const-n/plugin" in the entry named "const-n" of plugins in {MARKET}',
    "RED: const-n: its marketplace entry's description differs from its manifest's, first at character"
    " 19 (counting from 1)",
    DESCRIPTION_WHY,
    "  fix: copy `description` of modules/const-n/plugin/.claude-plugin/plugin.json, as written, into the"
    f' entry named "const-n" of plugins in {MARKET}',
    "RED: const-s: the marketplace has 2 entries for it",
    "  why: a plugin's name must lead to one source, and with two entries it is open which one an install"
    " reads",
    f'  fix: remove all but one entry named "const-s" from plugins in {MARKET}, the one whose source is'
    ' "./modules/const-s/plugin"',
    "RED: const-x: its manifest modules/const-x/plugin/.claude-plugin/plugin.json has no description",
    DESCRIPTION_WHY,
    "  fix: set `description` in modules/const-x/plugin/.claude-plugin/plugin.json to a string, the words a"
    ' module\'s README opens with, and copy it, as written, into the entry named "const-x" of plugins'
    f" in {MARKET}",
    "RED: glossary: its marketplace entry has a description that is 7, not a string",
    DESCRIPTION_WHY,
    "  fix: copy `description` of modules/glossary/plugin/.claude-plugin/plugin.json, as written, into the"
    f' entry named "glossary" of plugins in {MARKET}',
    *(  # the six strays of the marketplace, by name
        line
        for stray in ("away", "bar", "gone", "mid", "old", "zed")
        for line in (
            f"RED: const-{stray}: the marketplace has an entry for it, but modules/const-{stray} is no"
            " module folder",
            STRAY_WHY,
            f'  fix: remove the entry named "const-{stray}" from plugins in {MARKET}'
            + MAKE_FIX.format(f"const-{stray}"),
        )
    ),
    'RED: const-m: the kit\'s settings set "const-m@kit-test" to false, not true',
    ENABLED_WHY,
    f'  fix: set "const-m@kit-test": true under enabledPlugins in {SETTINGS}',
    "RED: const-n: the kit's settings do not enable it",
    ENABLED_WHY,
    f'  fix: set "const-n@kit-test": true under enabledPlugins in {SETTINGS}',
    'RED: const-s: the kit\'s settings set "const-s@kit-test" to "true", not true',
    ENABLED_WHY,
    f'  fix: set "const-s@kit-test": true under enabledPlugins in {SETTINGS}',
    "RED: const-away@kit-test: the kit's settings enable it, but modules/const-away is no module folder",
    KEY_WHY,
    f'  fix: remove the key "const-away@kit-test" from enabledPlugins in {SETTINGS}'
    + MAKE_FIX.format("const-away"),
    "RED: const-gone@kit-test: the kit's settings enable it, but modules/const-gone is no module folder",
    KEY_WHY,
    f'  fix: remove the key "const-gone@kit-test" from enabledPlugins in {SETTINGS}'
    + MAKE_FIX.format("const-gone"),
    "RED: kit-test: the kit's settings declare the marketplace with source"
    ' {"path": "./x", "source": "directory"}, not source {"source": "directory", "path": "."}',
    "  why: the kit loads its own modules from its own folder, so any other source loads another"
    " marketplace or none",
    f'  fix: set the source of "kit-test" under extraKnownMarketplaces in {SETTINGS} to'
    ' {"source": "directory", "path": "."}',
    "RED: 22 finding(s) — 6 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
]

KNOWN_WHY = (
    "  why: a session finds the kit's plugins only through a marketplace its settings declare, and the"
    " enabled keys name it"
)

ABSENT_LINES = [
    'RED: const-quiet: its marketplace entry has no source, not source "./modules/const-quiet/plugin"',
    SOURCE_WHY,
    '  fix: set "source" to "./modules/const-quiet/plugin" in the entry named "const-quiet" of plugins in'
    f" {MARKET}",
    "RED: const-quiet: its manifest modules/const-quiet/plugin/.claude-plugin/plugin.json has a description"
    ' that is ["a"], not a string',
    DESCRIPTION_WHY,
    "  fix: set `description` in modules/const-quiet/plugin/.claude-plugin/plugin.json to a string, the words"
    ' a module\'s README opens with, and copy it, as written, into the entry named "const-quiet" of'
    f" plugins in {MARKET}",
    "RED: const-x: its marketplace entry has no description",
    DESCRIPTION_WHY,
    "  fix: copy `description` of modules/const-x/plugin/.claude-plugin/plugin.json, as written, into the"
    " entry"
    f' named "const-x" of plugins in {MARKET}',
    "RED: const-quiet: the kit's settings do not enable it",
    ENABLED_WHY,
    f'  fix: set "const-quiet@kit-test": true under enabledPlugins in {SETTINGS}',
    "RED: const-x: the kit's settings do not enable it",
    ENABLED_WHY,
    f'  fix: set "const-x@kit-test": true under enabledPlugins in {SETTINGS}',
    "RED: kit-test: the kit's settings do not declare the marketplace under extraKnownMarketplaces",
    KNOWN_WHY,
    '  fix: add "kit-test": {"source": {"source": "directory", "path": "."}} under'
    f" extraKnownMarketplaces in {SETTINGS}",
    "RED: 6 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
]

DECLARED_SOURCE_LINES = [
    "RED: kit-test: the kit's settings declare the marketplace with no source, not source"
    ' {"source": "directory", "path": "."}',
    "  why: the kit loads its own modules from its own folder, so any other source loads another"
    " marketplace or none",
    f'  fix: set the source of "kit-test" under extraKnownMarketplaces in {SETTINGS} to'
    ' {"source": "directory", "path": "."}',
]


def cases_gate_list(tally: Tally) -> None:
    """Each state of the gate list, the workflow, the registry files and the guide is held."""
    trailing = f"\t# {READS_LIST[1]}\n"
    cases: dict[str, tuple[Case, list[Where]]] = {
        "a gate runs the scan in its module's job, CI reads the list, a module with none needs none": (
            Case({"x": SCAN}),
            [],
        ),
        "the gate group lacks it (an extra entry does not count)": (
            Case({"other": "python3 scripts/other.py"}, {"extra": SCAN}),
            [Where.GATE],
        ),
        "the workflow names --json only in a comment line": (
            Case({"x": SCAN}, workflow=f"# {READS_LIST[0]}\njobs:\n  one:\n    run: {READS_LIST[1]} x\n"),
            [Where.CI],
        ),
        "the workflow names --run only in a trailing comment": (
            Case(
                {"x": SCAN},
                workflow=f"jobs:\n  one:\n    run: {READS_LIST[0]}\n  two:\n    run: make{trailing}",
            ),
            [Where.CI],
        ),
        "the workflow does not read the list": (
            Case({"x": SCAN}, workflow="jobs:\n  one:\n    run: make\n"),
            [Where.CI],
        ),
        "the scan's entry falls into `kit`": (Case({"x": SCAN}, jobs={"x": "kit"}), [Where.JOB]),
        "the scan's entry stands in another module's job": (
            Case({"x": SCAN}, jobs={"x": "const-quiet"}),
            [Where.JOB],
        ),
        "a second entry runs the scan in its module's job": (
            Case({"x": SCAN, "again": SCAN}, jobs={"x": "kit", "again": "const-x"}),
            [],
        ),
        "the scan's command without the shared code on PYTHONPATH is a finding": (
            Case({"x": SCAN_COMMAND}),
            [Where.PATH],
        ),
        "the setting after the command holds nothing": (
            Case({"x": f"{SCAN_COMMAND} {SHARED_SETTING}"}),
            [Where.PATH],
        ),
        "the setting in a trailing comment holds nothing": (
            Case({"x": f"{SCAN_COMMAND}  # {SHARED_SETTING} sh"}),
            [Where.PATH],
        ),
        "the setting on another line of the entry holds nothing for the line that runs the scan": (
            Case({"x": f"{SHARED_SETTING} true\n{SCAN_COMMAND}"}),
            [Where.PATH],
        ),
        'another value, PYTHONPATH="$PWD/other", holds nothing': (
            Case({"x": f'PYTHONPATH="$PWD/other" {SCAN_COMMAND}'}),
            [Where.PATH],
        ),
        "the setting stuck to a longer name (XPYTHONPATH) holds nothing": (
            Case({"x": f"X{SHARED_SETTING} {SCAN_COMMAND}"}),
            [Where.PATH],
        ),
        "the setting after other commands on the scan's line holds": (
            Case({"x": f"cd . && {SHARED_SETTING} {SCAN_COMMAND}"}),
            [],
        ),
        "two entries run the scan, the second without the setting: one finding, for the second": (
            Case({"x": SCAN, "again": SCAN_COMMAND}, jobs={"again": "const-x"}),
            [Where.PATH],
        ),
        "the scan's entry in `kit` and without the setting gives both findings, the job's first": (
            Case({"x": SCAN_COMMAND}, jobs={"x": "kit"}),
            [Where.JOB, Where.PATH],
        ),
        "the list's modules leave a module folder out": (
            Case({"x": SCAN}, listed=("const-x",)),
            [Where.MISSING],
        ),
        "the list names a module with no folder": (
            Case({"x": SCAN}, listed=("const-x", "const-quiet", "const-gone")),
            [Where.STRAY],
        ),
        "the list runs a fixture runner with --item": (
            Case({"x": SCAN}, {"filtered": "python3 modules/const-x/tests/run.py --item 3"}),
            [Where.FILTER],
        ),
        "the workflow runs a fixture runner with --item=": (
            Case(
                {"x": SCAN},
                workflow=f"{READS}  more:\n    run: python3 modules/const-x/tests/run.py --item=3\n",
            ),
            [Where.FILTER],
        ),
        "a row of the enforcement table the check cannot read is a finding of its own": (
            Case(
                {"x": SCAN},
                document='<a id="t9"></a>\n| G2 | `check-x --scan` | `gate` |\n<a id="t10"></a>\n',
            ),
            [Where.FORM],
        ),
        "--item only in comments, and --items, filter nothing": (
            Case(
                {"x": SCAN},
                {"noted": "python3 modules/const-x/tests/run.py  # not --item 3"},
                workflow=f"{READS}  # run.py --item 3\n  more:\n    run: run.py --items 3\n",
            ),
            [],
        ),
        "a tracked kit check an entry of the gate group runs": (
            Case({"x": SCAN, "new": f"{RUN_NEW}\n{RUN_NEW} --self-test"}, scripts=TRACKED),
            [],
        ),
        "a tracked kit check no entry runs": (Case({"x": SCAN}, scripts=TRACKED), [Where.CHECK]),
        "the same file untracked is no kit check": (Case({"x": SCAN}, scripts={NEW_CHECK: False}), []),
        "a kit check run only by its --self-test": (
            Case({"x": SCAN, "new": f"{RUN_NEW} --self-test"}, scripts=TRACKED),
            [],
        ),
        "a kit check run only by --module in an install entry of the gate group": (
            Case({"x": SCAN, "install-const-x": f"{RUN_NEW} --module const-x"}, scripts=TRACKED),
            [],
        ),
        "a kit check run only by the extra entry lint": (
            Case({"x": SCAN}, {"lint": RUN_NEW}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a kit check run only by a fixtures entry": (
            Case({"x": SCAN}, {"fixtures-const-x": f"{RUN_NEW} --self-test"}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a kit check named in a comment of the list script only": (
            Case({"x": SCAN}, comment=RUN_NEW, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a kit check named after a # in a gate's command only": (
            Case({"x": SCAN, "noted": f"true  # {RUN_NEW}"}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a kit check no entry runs, beside one whose name it opens": (
            Case(
                {"x": SCAN, "newer": "python3 scripts/check-newer.py"},
                scripts={**TRACKED, "scripts/check-newer.py": True},
            ),
            [Where.CHECK],
        ),
        "a module's script of that name is no run of the kit check": (
            Case(
                {"x": SCAN, "new": "python3 modules/const-x/plugin/scripts/check-new.py --scan"},
                scripts=TRACKED,
            ),
            [Where.CHECK],
        ),
        "a library and a helper no entry runs are no kit checks": (
            Case({"x": SCAN}, scripts={"scripts/kit_module_doc.py": True, "scripts/helper.py": True}),
            [],
        ),
        # the word bounds of the run match, one gate entry whose only command line is the form named
        "a name that continues past .py (check-new.py.bak) is no run of the kit check": (
            Case({"x": SCAN, "new": f"{RUN_NEW}.bak"}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a name that continues past .py (check-new.pyc) is no run of the kit check": (
            Case({"x": SCAN, "new": f"{RUN_NEW}c"}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a word that ends in python3 (xpython3) is no run of the kit check": (
            Case({"x": SCAN, "new": f"x{RUN_NEW}"}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "an absolute python3 (/usr/bin/python3), as the code stands, is no run of the kit check": (
            Case({"x": SCAN, "new": f"/usr/bin/{RUN_NEW}"}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a run after other commands on its line (cd x && python3 ...) is a run of the kit check": (
            Case({"x": SCAN, "new": f"cd x && {RUN_NEW}"}, scripts=TRACKED),
            [],
        ),
        "a name that follows a dot (.python3) is no run of the kit check": (
            Case({"x": SCAN, "new": f".{RUN_NEW}"}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a name that continues with a hyphen (check-new.py-x) is no run of the kit check": (
            Case({"x": SCAN, "new": f"{RUN_NEW}-x"}, scripts=TRACKED),
            [Where.CHECK],
        ),
        "a check named with a metacharacter (check-a+b.py) is run by its own line": (
            Case({"x": SCAN, "new": "python3 scripts/check-a+b.py"}, scripts={"scripts/check-a+b.py": True}),
            [],
        ),
        "a check named with a metacharacter (check-a+b.py) is no run by the line of check-aab.py": (
            Case({"x": SCAN, "new": "python3 scripts/check-aab.py"}, scripts={"scripts/check-a+b.py": True}),
            [Where.CHECK],
        ),
    }
    cases.update(registry_cases(SCAN))
    cases.update(guide_cases(SCAN, MODULE_TEXT))
    cases.update(coverage_cases(SCAN))
    for name, (case, wanted) in cases.items():
        ok = [f.where for f in findings_of(case)] == wanted
        tally.judge(ok, f"{name}")


def cases_selections(tally: Tally) -> None:
    """A word of a code line of the list or the workflow that names pytest is red — a run by `-m pytest`,
    by a path, as `py.test` or stuck to `-m`, an unpinned install, a range pin, a message — one finding
    for each, and so is one that names PYTEST_ADDOPTS; an exact pin, a name that goes on or has another
    before it, a run of check-aspects and a comment are green. An `addopts` line of a pytest configuration
    file in the kit's folders a module's run reads is red, one in another folder green, and the reports
    are literal lines."""
    aspects = "python3 scripts/check-aspects.py --run --module const-x"
    cases: dict[str, tuple[Case, list[str]]] = {  # case: the tree, the entries its findings name, in order
        "the list runs python3 -m pytest": (
            Case({"x": SCAN}, {"run": "python3 -m pytest modules/const-x/tests"}),
            ["pytest"],
        ),
        "the list runs pytest by its path, and runs it twice": (
            Case({"x": SCAN}, {"run": "venv/bin/pytest modules/const-x/tests -k slow; pytest -q"}),
            ["venv/bin/pytest", "pytest"],
        ),
        "the workflow runs pytest after coverage": (
            Case({"x": SCAN}, workflow=f"{READS}  more:\n    run: python3 -m coverage run -m pytest t\n"),
            ["pytest"],
        ),
        "the workflow sets PYTEST_ADDOPTS": (
            Case({"x": SCAN}, workflow=f"{READS}  more:\n    env:\n      PYTEST_ADDOPTS: -k slow\n"),
            ["PYTEST_ADDOPTS"],
        ),
        "pytest's exact pin, its plugin, its configuration file and check-aspects name no pytest": (
            Case(
                {"x": SCAN},
                {"run": f'{aspects} && pip install "pytest==9.1.1" pytest-xdist && cat pytest.ini'},
            ),
            [],
        ),
        "py.test, -mpytest and -Impytest run pytest": (
            Case({"x": SCAN}, {"run": "py.test t; python3 -mpytest t; python3 -Impytest t"}),
            ["py.test", "-mpytest", "-Impytest"],
        ),
        "a path to pytest is named whole": (
            Case({"x": SCAN}, {"run": "~/.venv/bin/pytest modules/const-x/tests"}),
            ["~/.venv/bin/pytest"],
        ),
        "an unpinned install, a range pin and a message name pytest": (
            Case({"x": SCAN}, {"run": 'pip install pytest "pytest>=9.1" && echo "runs under pytest"'}),
            ["pytest", "pytest", "pytest"],
        ),
        "a quoted stuck -m, and a name in brackets, quoted without them; a name with another before it": (
            Case({"x": SCAN}, {"run": 'python3 "-mpytest" t; echo "(pytest)" allure-pytest'}),
            ["-mpytest", "pytest"],
        ),
        "names that go on name no pytest": (
            Case({"x": SCAN}, {"run": "echo pytest_plugins PYTEST_CURRENT_TEST pytest.toml pytest_cov"}),
            [],
        ),
        "pytest only in a comment runs nothing": (
            Case({"x": SCAN}, {"run": f"{aspects}  # not python3 -m pytest -k slow"}),
            [],
        ),
    }
    for name, (case, wanted) in cases.items():
        found = findings_of(case)
        ok = [f.where for f in found] == [Where.FILTER] * len(wanted) and [f.entry for f in found] == wanted
        tally.judge(ok, name)
    for config, text, wanted_line in (  # a pytest configuration file a module's run finds, its addopts red
        ("pyproject.toml", "[tool.pytest.ini_options]\naddopts = -k slow\n", 2),
        ("pytest.ini", "[pytest]\n  addopts=--lf\n", 2),
        ("pytest.toml", '[pytest]\naddopts = ["-k", "slow"]\n', 2),
        (".pytest.ini", "[pytest]\naddopts = -ra\n", 2),
        ("modules/const-x/tests/pytest.ini", "[pytest]\naddopts = -k slow\n", 2),
        ("modules/tox.ini", "[pytest]\naddopts = --lf\n", 2),
        ("tox.ini", "[pytest]\naddopts: -k slow\n", 2),
        ("setup.cfg", "[tool:pytest]\nmarkers = item\n", 0),
        ("docs/pytest.ini", "[pytest]\naddopts = -k slow\n", 0),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, Case({"x": SCAN}))
            (root / config).parent.mkdir(parents=True, exist_ok=True)
            (root / config).write_text(text, encoding="utf-8")
            with coverage_owner(COVERAGE.owner):
                found = check_kit(root)[0]
        got = [(f.module, f.entry, f.line) for f in found]
        ok = got == ([(config, "addopts", wanted_line)] if wanted_line else [])
        tally.judge(ok, f"{config} {'with' if wanted_line else 'without'} an addopts line read")
    why = "  why: the gate list and CI run every item of every runner, so that their green is a full pass"
    addopts_lines = [  # typed by hand: the report of a configuration file's addopts line
        "RED: pytest.ini:2: it sets `addopts`, through which any option, a selection included, reaches every"
        " pytest run",
        why,
        "  fix: remove the `addopts` setting at line 2, with any lines that continue it, from pytest.ini",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        build(root, Case({"x": SCAN}))
        (root / "pytest.ini").write_text("[pytest]\naddopts = -ra\n", encoding="utf-8")
        with coverage_owner(COVERAGE.owner):
            found = check_kit(root)[0]
    tally.judge(
        [line for f in found for line in f.render().splitlines()] == addopts_lines,
        "the report of an addopts line is its literal text",
    )
    reports = {  # typed by hand: the reports of PYTEST_ADDOPTS and of a run of pytest itself
        "PYTEST_ADDOPTS": (
            Case({"x": SCAN}, workflow=f"{READS}  more:\n    env:\n      PYTEST_ADDOPTS: -k slow\n"),
            [
                "RED: .github/workflows/gates.yml:8: it names `PYTEST_ADDOPTS`, through which any option, a"
                " selection included, reaches every pytest run",
                why,
                "  fix: remove `PYTEST_ADDOPTS` and its value from line 8 of .github/workflows/gates.yml",
            ],
        ),
        "a run of pytest itself": (
            Case({"x": SCAN}, workflow=f"{READS}  more:\n    run: python3 -m pytest t -k slow\n"),
            [
                "RED: .github/workflows/gates.yml:7: it names `pytest`, and the lists' code lines name "
                "pytest only in an exact pin `pytest==<version>`: a module's tests run only through "
                "`python3 scripts/check-aspects.py --run --module <module>`, which runs them whole",
                why,
                "  fix: where line 7 of .github/workflows/gates.yml runs pytest, run the module's tests"
                " through `python3 scripts/check-aspects.py --run --module <module>` in its place; where it"
                " installs pytest, pin it as `pytest==<version>`; elsewhere, reword the line so that it names"
                " pytest no more",
            ],
        ),
    }
    for name, (case, wanted_lines) in reports.items():
        got_lines = [line for f in findings_of(case) for line in f.render().splitlines()]
        tally.judge(got_lines == wanted_lines, f"the report of {name} is its literal text")


def cases_kit_check_names(tally: Tally) -> None:
    """Only a script at the top of scripts/ named check-<x>.py is a kit check."""
    names = {  # which tracked path is a kit check: the name filter over its whole set
        "scripts/check-x.py": True,
        "scripts/check-x.sh": False,
        "scripts/check_x.py": False,
        "scripts/checkx.py": False,
        "scripts/check-.py": False,
        "scripts/Check-x.py": False,
        "scripts/check-x.pyc": False,
        "scripts/check-x.py.bak": False,
        "scripts/kit_module_doc.py": False,
        "scripts/helper.py": False,
        "scripts/sub/check-y.py": False,  # a script under a folder is none: only the top of scripts/ counts
        "scripts/check-sub/z.py": False,  # nor is one in a folder whose name opens `check-`
        "modules/const-x/plugin/scripts/check-x.py": False,
    }
    ok = True
    for path, is_check in names.items():
        got = [f.module for f in findings_of(Case({"x": SCAN}, scripts={path: True}))]
        if got != ([path] if is_check else []):
            ok = False
            print(f"        name {path!r}: got {got}, a kit check is {is_check}")
    tally.judge(
        ok, "only `scripts/check-<x>.py` at the top of scripts/ is a kit check, over the whole set of names"
    )


def cases_module_folder_names(tally: Tally) -> None:
    """Only `const-<aspect>` in full is a module's name."""
    folder_names = {  # which folder name is a module's: `const-<aspect>` in full, over the whole set of names
        "const-a": True,
        "const-a-b": True,
        "const-a1": True,
        "const-1": True,
        "const-a-b-c2": True,
        "glossary": False,
        "const-": False,
        "const": False,
        "const--a": False,
        "const-a-": False,
        "const-A": False,
        "const-a-B": False,
        "Const-a": False,
        "xconst-a": False,
        "const_a": False,
        "const-a.b": False,
        "const-ä": False,
        "const-٣": False,  # an Arabic-Indic digit is no digit here
        "const-a\n": False,  # a newline at the end is no name: `$` lets it stand
    }
    ok = True
    for folder, is_module in folder_names.items():
        # the list's names are read split on whitespace, so a name with a newline cannot stand in MODULES:
        # it is left out of `listed`, and of its findings only the name's own is held
        newline = "\n" in folder
        case = Case({"x": SCAN}, folders=("const-x", folder), listed=("const-x",) if newline else None)
        held = [(f.where, f.module) for f in findings_of(case) if f.where is Where.NAME or not newline]
        if held != ([] if is_module else [(Where.NAME, folder)]):
            ok = False
            print(f"        folder {folder!r}: got {held}, a module name is {is_module}")
    tally.judge(ok, "only `const-<aspect>` in full is a module's name, over the whole set of names")


def cases_folder_renames(tally: Tally) -> None:
    """The rename told for a folder name offers `const-<name>` only where it would then be a module's."""
    name_report = (  # the NAME finding's whole report, typed by hand, `{fix}` what is said after "rename"
        "RED: {m}: a module folder's name is not const-<aspect>\n"
        "  why: the kernel names every module `const-<aspect>`, lowercase kebab-case, and the CI gives a job"
        " Claude Code by that prefix\n"
        "  fix: rename modules/{m} {fix}, and name its manifest, marketplace entry, settings key and entry in"
        " MODULES the same"
    )
    to_aspect = "to a name `const-<aspect>`, lowercase letters and digits joined by single hyphens"
    renames = {  # a name `const-<name>` would be is offered only to a name that does not open with `const`
        "glossary": "to modules/const-glossary",
        "const": to_aspect,  # not `const-const`: it opens with `const`
        "constx": to_aspect,  # nor `const-constx`
        "Glossary": to_aspect,  # `const-Glossary` is no name either
        "g_s": to_aspect,
    }
    ok = True
    for folder, fix in renames.items():
        got = [
            f.render()
            for f in findings_of(Case({"x": SCAN}, folders=("const-x", folder)))
            if f.where is Where.NAME
        ]
        if got != [name_report.format(m=folder, fix=fix)]:
            ok = False
            print(f"        folder {folder!r}: got {got}, wanted the rename {fix!r}")
    tally.judge(
        ok,
        "the rename told for a folder name offers `const-<name>` only to a name"
        " that does not open with `const` and would then be a module's name",
    )


def cases_stray_dials_keys(tally: Tally) -> None:
    """Only a top-level key `const-<aspect>` in full with no module folder is a stray namespace."""
    key_names = {  # which top-level key of the dials file is a stray: a module's name in full with no folder
        "const-gone": True,
        "const-gone-2": True,
        "const-1": True,
        "const-a-b-c2": True,
        "const-x": False,  # a module folder
        "const-quiet": False,  # a module folder
        "plc-0001-root-policy": False,  # a policy's namespace
        "root_policy": False,  # a kernel key
        "territory_dialect": False,
        "const-": False,
        "const": False,
        "const--a": False,
        "const-a-": False,
        "const-A": False,
        "Const-a": False,
        "xconst-a": False,
        "const_a": False,
        "const-a.b": False,
        "const-ä": False,
        "const-a b": False,
        "const-a\n": False,  # a newline at the end is no name
    }
    ok = True
    for key, is_stray in key_names.items():
        files = registry_tree(("const-x", "const-quiet"), REGISTRY_TAG)
        files[DIALS] = {"root_policy": "p", key: {}, TEST_OWNER: files[DIALS][TEST_OWNER]}
        stray_keys = [(f.where, f.module) for f in findings_of(Case({"x": SCAN}, files=files))]
        if stray_keys != ([(Where.DIALS_KEY, key)] if is_stray else []):
            ok = False
            print(f"        key {key!r}: got {stray_keys}, a stray is {is_stray}")
    tally.judge(
        ok,
        "only a top-level key `const-<aspect>` in full with no module folder is a"
        " stray namespace, over the whole set of names",
    )


def cases_scan_readers(tally: Tally) -> None:
    """A scan is read from the enforcement section as declared, and its table forms and folders are probed."""
    with tempfile.TemporaryDirectory() as tmp:  # a scan declared by its Python file, run by python3
        root = Path(tmp).resolve()
        build(root, guide_case(SCAN, MODULE_TEXT, ""))  # const-p declares `check-p.py --scan`
        ok = check_kit(root)[0] == []
    tally.judge(ok, "a scan declared as `<entry>.py --scan` is held by its python3 line")
    ok = scans_of(MODULE_TEXT) == ["check-x"] and scans_of(QUIET_TEXT) == []
    taught = 'runs `PYTHONPATH="$PWD/shared" python3 modules/const-y/plugin/scripts/check-y.py --scan`'
    ok = ok and taught in Finding("const-y", Where.GATE, "check-y.py").render()
    ok = ok and scans_of(MODULE_TEXT.replace("`check-x --scan`", "`check-x.py --scan`")) == ["check-x.py"]
    tally.judge(ok, "a span with more after the flag is no scan; a .py entry is taught by python3")
    last_section = '## 9 <a id="t9"></a> is prose here\n\n<a id="t9"></a>\n| E1 | `check-x --scan` |\n'
    ok = scans_of(last_section) == ["check-x"]  # the last section reads to the end of the file
    ok = ok and scans_of('<a id="t9"></a>\n<a id="t10"></a>\n| E1 | `check-x --scan` |\n') == []
    ok = ok and scans_of('  <a id="t9"></a>  \n| E1 | `check-x --scan` |\n') == ["check-x"]
    # an anchor of another id, alone on its line, ends no section: the E-row after it is still read
    other_id = (
        '<a id="t9"></a>\n<a id="x"></a>\n| E1 | `check-x --scan` |\n'
        '<a id="r2"></a>\n| E2 | `check-y --scan` |\n'
    )
    ok = ok and scans_of(other_id) == ["check-x", "check-y"]
    # no anchor above the section's: it reads to the end, whether t12 is gone or t11 and t12 both
    ok = ok and scans_of(MODULE_TEXT.replace('<a id="t12"></a>\n', "")) == ["check-x"]
    ok = ok and scans_of(MODULE_TEXT[: MODULE_TEXT.index('<a id="t11"></a>')]) == ["check-x"]
    try:  # nor does it count as doubled: two of one id are no error
        ok = ok and scans_of(other_id.replace('<a id="r2"></a>', '<a id="x"></a>')) == [
            "check-x",
            "check-y",
        ]
    except Broken:
        ok = False
    tally.judge(
        ok,
        "the enforcement section reads to the end of the file when it is the"
        " last, is empty when the end anchor follows at once, an anchor inside prose is plain text, an"
        " anchor of another id alone on its line neither ends it nor counts as doubled, and it is read when"
        " no anchor stands above it, t11 and t12, or t12, gone",
    )
    ok = form_probes()
    tally.judge(ok, "the enforcement table's forms, over the whole set of probes")
    ok = folder_probes()
    tally.judge(ok, "the module folders of the kit's one listing, over every class of entry")


def reports_by_kind(tally: Tally) -> None:
    """The report of each kind of finding is its literal text, exit 2."""
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: its scan `check-x --scan` is not in the CI list",
        "  why: a scan the kit does not run holds nothing, and the lists are where the kit says what it runs",
        f"  fix: let {WORKFLOW} build its jobs from `{READS_LIST[0]}` and run each with"
        f" `{READS_LIST[1]} <job>`",
        "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    unpathed_lines = [
        'RED: const-x: its scan `check-x --scan`, the entry `x`, runs without PYTHONPATH="$PWD/shared" before'
        " its command",
        "  why: a plugin holds no shared code, so a scan run without the kit's shared/ first on PYTHONPATH"
        " imports a release a person installed, or none, and the gate list would not check the change's"
        " own code",
        "  fix: in the `x` arm of commands() in scripts/gate-list.sh, write the scan as `scan <command>`,"
        ' which prints PYTHONPATH="$PWD/shared" before the command',
        "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    placed_lines = [
        "RED: const-x: its scan `check-x --scan`, the entry `x`, runs in the CI job `kit`, not in its own",
        "  why: a module's scan runs in that module's job, so a red CI line names the module whose rule"
        " the tree broke",
        "  fix: map the entry to its module in job() of scripts/gate-list.sh: `x) echo const-x ;;`",
        "RED: const-quiet: the list lacks its entries `install-const-quiet`, `fixtures-const-quiet`,"
        " `lint-const-quiet`, `types-const-quiet`",
        "  why: a module the list leaves out is never installed, run, linted or typed in CI",
        "  fix: add `const-quiet` to MODULES in scripts/gate-list.sh, which gives each module its install,"
        " fixtures, lint and types entries",
        "RED: const-gone: the list has its entries `install-const-gone`, `fixtures-const-gone`,"
        " `lint-const-gone`, `types-const-gone`, but modules/const-gone is no module folder",
        "  why: the list's modules are exactly the module folders, and an entry of a missing module checks"
        " nothing",
        "  fix: remove `const-gone` from MODULES in scripts/gate-list.sh, or restore modules/const-gone"
        " with its MODULE.md",
        "RED: 3 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    form_text = (
        '<a id="t9"></a>\n| E1 | `check-x --scan` | `gate` |\n| G2 | `sh scripts/x.sh --scan` | `gate` |\n'
        "| E3 | `x --scan --since <date>` | `gate` |\n|  | none | `gate` |\n"
        'Declared in `y.py --scan` here.\n<a id="t10"></a>\n'
    )
    form_why = "  why: a scan the check cannot read is never held in the gate list and CI"
    form_fix = (
        "  fix: write it `<entry> --scan`, or, for a mode that is no tree scan,"
        " `<entry> --scan --<flag> …` with the words `not a tree scan` in the same cell as the span,"
        " outside the code span"
    )
    form_lines = [  # typed by hand
        "RED: modules/const-x/MODULE.md:3: a row of its enforcement table opens with `G2`, not E<n>",
        form_why,
        "  fix: open the row with E<n>, its number in the table",
        "RED: modules/const-x/MODULE.md:3: its enforcement table names `--scan` in a form the check cannot"
        " read: `sh scripts/x.sh --scan`",
        form_why,
        form_fix,
        "RED: modules/const-x/MODULE.md:4: its enforcement table has a flag after `--scan` in"
        " `x --scan --since <date>`, and the words `not a tree scan` are not in the cell that holds the span,"
        " outside a code span",
        form_why,
        form_fix,
        "RED: modules/const-x/MODULE.md:5: a row of its enforcement table opens with nothing, not E<n>",
        form_why,
        "  fix: open the row with E<n>, its number in the table",
        "RED: modules/const-x/MODULE.md:6: `y.py --scan` declares a scan outside the enforcement table",
        form_why,
        "  fix: move it into a row of the enforcement table, or write it another way",
        "RED: 5 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    two_lines = [  # typed by hand
        "RED: scripts/check-a.py is run by no entry of the gate group",
        "  why: a kit check no entry runs is never run in CI, and its green says nothing",
        "  fix: add an entry to GATES in scripts/gate-list.sh and an arm in commands() that runs"
        " `python3 scripts/check-a.py`, with its `--self-test` where it has one",
        "RED: scripts/check-b.py is run by no entry of the gate group",
        "  why: a kit check no entry runs is never run in CI, and its green says nothing",
        "  fix: add an entry to GATES in scripts/gate-list.sh and an arm in commands() that runs"
        " `python3 scripts/check-b.py`, with its `--self-test` where it has one",
        "RED: 2 finding(s) — 2 module document(s) examined, 1 declared scan(s), 3 kit check(s)",
    ]
    guide_lines = [  # typed by hand: a scan left out of the block, then a path no module declares
        "RED: const-x: its scan `check-x --scan` is not in the scan block of INSTALL.md",
        "  why: the guide's scan block is what a project runs to verify an install, so a scan it leaves out"
        " is never run there and a path no module declares fails there",
        "  fix: add `const-x/plugin/scripts/check-x.sh` to the list after `for s in` in the"
        " `bash check=scan` block of INSTALL.md",
        "RED: const-gone/plugin/scripts/check-gone.sh: the scan block of INSTALL.md lists it, but no module"
        " declares that scan",
        "  why: the guide's scan block is what a project runs to verify an install, so a scan it leaves out"
        " is never run there and a path no module declares fails there",
        "  fix: remove `const-gone/plugin/scripts/check-gone.sh` from the list after `for s in` in the"
        " `bash check=scan` block of INSTALL.md",
        "RED: 2 finding(s) — 3 module document(s) examined, 2 declared scan(s), 0 kit check(s)",
    ]
    coverage_why = (
        "  why: the range check of module const-task-close asks a change for a module's document only through"
        " the module's pair, so a module with no pair, or code outside its pair, is never asked"
    )
    cov = "`task-close.coverage` of constitution.yaml"  # the self-test's key, the map's file
    under = "the list under `coverage:` of the `task-close` namespace in constitution.yaml"
    coverage_lines = [  # typed by hand: by module, then docs, a pattern outside, a folder without one
        f"RED: const-p: {cov} has 2 pairs named for it",
        coverage_why,
        f"  fix: remove every pair named `const-p` after the first from {under}",
        f"RED: const-quiet: {cov} has no pair for it",
        coverage_why,
        f"  fix: add this entry to {under}, in place of `[]` when it is empty:",
        "    - name: const-quiet",
        "      code: []",
        "      docs:",
        '        - "modules/const-quiet/MODULE.md"',
        f'RED: const-x: its pair in {cov} lists docs ["modules/const-x/README.md"], not its module document'
        " alone",
        coverage_why,
        "  fix: set `docs` of the pair named `const-x` to the one path `modules/const-x/MODULE.md`",
        f"RED: const-x: its pair in {cov} lists the code pattern `scripts/**`, which is outside"
        " modules/const-x/",
        coverage_why,
        "  fix: remove `scripts/**` from `code` of the pair named `const-x`",
        f"RED: const-x: modules/const-x/plugin/hooks is a folder, but its pair in {cov} lists no pattern for"
        " it",
        coverage_why,
        '  fix: add the line `- "modules/const-x/plugin/hooks/**"` to `code` of the pair named `const-x`',
        "RED: 5 finding(s) — 3 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    real_under = "the list under `coverage:` of the `const-task-close` namespace in constitution.yaml"
    real_lines = [  # typed by hand: the real key, an entry listing the folders the module has
        "RED: const-quiet: `const-task-close.coverage` of constitution.yaml has no pair for it",
        coverage_why,
        f"  fix: add this entry to {real_under}, in place of `[]` when it is empty:",
        "    - name: const-quiet",
        "      code:",
        '        - "modules/const-quiet/plugin/hooks/**"',
        '        - "modules/const-quiet/tests/**"',
        "      docs:",
        '        - "modules/const-quiet/MODULE.md"',
        "RED: 1 finding(s) — 2 module document(s) examined, 0 declared scan(s), 0 kit check(s)",
    ]
    for name, case, lines in (
        (
            "the guide's scan block findings",
            guide_case(SCAN, MODULE_TEXT, guide_text(GUIDE_P, GUIDE_GONE)),
            guide_lines,
        ),
        (
            "the coverage map's findings, in the order of the modules and of the kinds",
            coverage_case(
                SCAN,
                [
                    full_pair("const-p"),
                    {
                        **full_pair("const-x"),
                        "docs": ["modules/const-x/README.md"],
                        "code": ["scripts/**", "modules/const-x/plugin/scripts/**"],
                    },
                    full_pair("const-p"),
                ],
                "const-x/plugin/scripts",
                "const-x/plugin/hooks",
                modules=("const-x", "const-quiet", "const-p"),
            ),
            coverage_lines,
        ),
        (
            "the coverage map's pair missing under the real key, its folders listed",
            coverage_case(
                SCAN,
                [full_pair("const-task-close")],
                "const-quiet/plugin/hooks",
                "const-quiet/tests",
                modules=("const-task-close", "const-quiet"),
                owner=COVERAGE_OWNER,
            ),
            real_lines,
        ),
        (
            "two kit checks no entry runs, in sorted order",
            Case(
                {"x": SCAN, "c": "python3 scripts/check-c.py"},
                scripts={f"scripts/check-{n}.py": True for n in ("b", "c", "a")},
            ),
            two_lines,
        ),
        ("one finding", Case({"x": SCAN}, workflow="jobs: {}\n"), report_lines),
        ("a scan run without the shared code on the path", Case({"x": SCAN_COMMAND}), unpathed_lines),
        ("the findings of a table the check cannot read", Case({"x": SCAN}, document=form_text), form_lines),
        (
            "the job and module findings",
            Case({"x": SCAN}, jobs={"x": "kit"}, listed=("const-x", "const-gone")),
            placed_lines,
        ),
        (
            "an item filter",
            Case(
                {"x": SCAN},
                workflow=f"{READS}  filtered:\n    run: python3 modules/const-x/tests/run.py --item 3\n",
            ),
            FILTER_LINES,
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, case)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed), coverage_owner(case.owner or COVERAGE.owner):
                code = report(*check_kit(root))
        ok = code == EXIT_RED and printed.getvalue().splitlines() == lines
        tally.judge(ok, f"the report of {name} is its literal text, exit 2")
        if not ok:
            print(printed.getvalue())


def fixes_of_the_guide(tally: Tally) -> None:
    """The fixes the guide's findings teach, followed to the letter, turn it green."""
    # the fix texts of the guide's findings, followed to the letter on the tree: the path named is added to
    # the list after `for s in`, or removed from it, and the check is then green
    followed = guide_text(GUIDE_P, GUIDE_GONE)
    taught = findings_of(guide_case(SCAN, MODULE_TEXT, followed))
    for finding in taught:
        act = re.search(r"fix: (add|remove) `([^`]+)`", finding.render())
        if act is None:
            followed = ""
        elif act[1] == "add":
            followed = followed.replace("for s in ", f"for s in {act[2]} ", 1)
        else:
            followed = followed.replace(f" {act[2]}", "", 1)
    ok = len(taught) == 2 and followed != "" and findings_of(guide_case(SCAN, MODULE_TEXT, followed)) == []
    tally.judge(ok, "the fixes the guide's findings teach, followed to the letter, turn it green")


def fixes_of_the_coverage(tally: Tally) -> None:
    """The fixes the coverage hold teaches, followed to the letter, turn it green."""
    x_pair, q_pair = full_pair("const-x"), full_pair("const-quiet")
    some = ("const-x/plugin/scripts", "const-x/plugin/hooks")
    for name, (case, count) in {  # the fix texts of the coverage hold, followed to the letter on the tree
        "a missing pair, with the folders the module has": (coverage_case(SCAN, [q_pair], *some), 1),
        "no pair at all, the list empty": (coverage_case(SCAN, [], *some), 2),
        "a pair twice": (coverage_case(SCAN, [x_pair, q_pair, x_pair, x_pair]), 1),
        "docs of two files": (
            coverage_case(SCAN, [{**x_pair, "docs": ["a.md", "modules/const-x/MODULE.md"]}, q_pair]),
            1,
        ),
        "a pattern outside the module": (
            coverage_case(SCAN, [{**x_pair, "code": [*x_pair["code"], "scripts/**"]}, q_pair]),
            1,
        ),
        "a folder without its pattern": (
            coverage_case(SCAN, [{**x_pair, "code": x_pair["code"][2:]}, q_pair], *some),
            2,
        ),
        "a pair with no pattern, docs and a pattern wrong": (
            coverage_case(SCAN, [{**x_pair, "code": ["scripts/**"], "docs": []}, q_pair], *some),
            4,
        ),
    }.items():
        text = str(case.files[DIALS])
        taught = findings_of(case)
        for finding in taught:
            text = follow_coverage_fix(text, finding.render())
        ok = len(taught) == count and text != case.files[DIALS]
        ok = ok and findings_of(replace(case, files={**case.files, DIALS: text})) == []
        tally.judge(
            ok, f"the fix the coverage hold teaches for {name}, followed to the letter, turns it green"
        )


def report_of_a_green_kit(tally: Tally) -> None:
    """The report of a kit whose checks all run is its literal green line."""
    with tempfile.TemporaryDirectory() as tmp:  # the green line, with every kit check run
        root = Path(tmp).resolve()
        green_files = registry_tree(("const-x", "const-quiet"), REGISTRY_TAG)
        # a key of another marketplace stands and is no enabled plugin of the kit: the count has two
        green_files[SETTINGS_FILE]["enabledPlugins"]["other@elsewhere"] = True
        build(root, Case({"x": SCAN, "new": RUN_NEW}, scripts=TRACKED, files=green_files))
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    green_line = (
        "GREEN: every declared scan stands in the gate list, the CI list and its module's job and runs with "
        "the kit's shared/ first on PYTHONPATH, the list's "
        "modules are the module folders, each named const-<aspect> and by its manifest, listed once in the "
        "marketplace and enabled in the kit's settings, which declare the marketplace, neither list, "
        "comments aside, names pytest save in an exact pin, passes --item or names PYTEST_ADDOPTS, no pytest "
        "configuration file of the kit's folders a module's run reads sets addopts, every kit check is run "
        "by an entry of the gate group, the install guide's scan block names exactly the declared scans, and "
        "the coverage map of the range check holds one pair for each module folder — 2 module document(s) "
        "examined, 1 declared scan(s), 1 kit check(s), 2 marketplace plugin(s), 2 enabled plugin(s)"
    )
    ok = code == EXIT_GREEN and printed.getvalue().splitlines() == [green_line]
    tally.judge(ok, "the report of a kit whose checks all run is its literal green line")
    if not ok:
        print(printed.getvalue())


def reports_in_order(tally: Tally) -> None:
    """The reports of findings of several kinds come in the order of the kinds, forwards and backwards."""
    scan_why = (
        "  why: a scan the kit does not run holds nothing, and the lists are where the kit says what it runs"
    )
    missing_why = "  why: a module the list leaves out is never installed, run, linted or typed in CI"
    ordered_lines = [  # the scans' findings by folder, then the list's, `const-z` being no scan's
        "RED: const-x: its scan `check-x --scan` is not in the gate list",
        scan_why,
        "  fix: add an entry to the gate group of scripts/gate-list.sh that runs"
        ' `PYTHONPATH="$PWD/shared" sh modules/const-x/plugin/scripts/check-x.sh --scan`',
        "RED: const-y: its scan `check-w --scan` is not in the gate list",
        scan_why,
        "  fix: add an entry to the gate group of scripts/gate-list.sh that runs"
        ' `PYTHONPATH="$PWD/shared" sh modules/const-y/plugin/scripts/check-w.sh --scan`',
        *(
            line
            for m in ("x", "y", "z")
            for line in (
                f"RED: const-{m}: the list lacks its entries `install-const-{m}`, `fixtures-const-{m}`,"
                f" `lint-const-{m}`, `types-const-{m}`",
                missing_why,
                f"  fix: add `const-{m}` to MODULES in scripts/gate-list.sh, which gives each module its"
                " install, fixtures, lint and types entries",
            )
        ),
        "RED: 5 finding(s) — 3 module document(s) examined, 2 declared scan(s), 0 kit check(s)",
    ]
    without_quiet = registry_tree(("const-x", "const-quiet"), REGISTRY_TAG)
    without_quiet[MARKETPLACE_FILE]["plugins"].pop(1)  # const-quiet: the marketplace leaves it out
    without_quiet[DIALS]["const-gone"] = {}  # a namespace with no module folder
    without_quiet[MIRROR] = mirror_text((*MIRROR_FOLDERS, "const-r"))  # a folder the types entry lacks
    namespace_why = (
        "  why: a module reads only the dials namespace named after its plugin (kernel §7), so a namespace"
        " that names no module folder is a dial nobody applies"
    )
    types_why = (
        "  why: the schema mirror imports gate code from those module folders and the shared package from"
        " shared/, so the type check of the kit's scripts resolves them only through a MYPYPATH that names"
        " the same folders and ../shared"
    )

    def namespace_lines(key: str) -> list[str]:  # typed by hand, the key the one thing that varies
        return [
            f"RED: {key}: constitution.yaml has a top-level key for it, but modules/{key} is no module"
            " folder",
            namespace_why,
            f"  fix: rename the key `{key}` in constitution.yaml to the name of the module folder whose dials"
            " it holds, or remove the key and what is under it",
        ]

    def types_lines(held: str, mirror: str) -> list[str]:
        return [
            f"RED: scripts/gate-list.sh: its `types` entry puts {held} on MYPYPATH, but"
            f" scripts/check-schema-mirror.py imports from `{mirror}`",
            types_why,
            f"  fix: in the `types` entry of scripts/gate-list.sh, set MYPYPATH to `{mirror}`, one setting,"
            " on the command that type-checks scripts/*.py",
        ]

    pair_path = "../modules/const-p/plugin/scripts:../modules/const-q/plugin/scripts:../shared"
    kinds_lines = [  # the list's modules, then the registry files, then the item filters, then the kit checks
        "RED: const-quiet: the list lacks its entries `install-const-quiet`, `fixtures-const-quiet`,"
        " `lint-const-quiet`, `types-const-quiet`",
        missing_why,
        "  fix: add `const-quiet` to MODULES in scripts/gate-list.sh, which gives each module its install,"
        " fixtures, lint and types entries",
        "RED: const-quiet: the marketplace has no entry for it",
        "  why: a module the marketplace leaves out cannot be installed, by the kit's CI or by a consumer",
        '  fix: add {"name": "const-quiet", "source": "./modules/const-quiet/plugin"} to plugins in'
        f" {MARKET}",
        *FILTER_LINES[:-1],
        "RED: scripts/check-new.py is run by no entry of the gate group",
        "  why: a kit check no entry runs is never run in CI, and its green says nothing",
        "  fix: add an entry to GATES in scripts/gate-list.sh and an arm in commands() that runs"
        f" `{RUN_NEW}`, with its `--self-test` where it has one",
        *namespace_lines("const-gone"),  # the dials file, then the types entry: after every earlier kind
        *types_lines(
            f"`{pair_path}`",
            "../modules/const-p/plugin/scripts:../modules/const-q/plugin/scripts"
            ":../modules/const-r/plugin/scripts:../shared",
        ),
        "RED: 6 finding(s) — 2 module document(s) examined, 1 declared scan(s), 1 kit check(s)",
    ]
    strays_lines = [  # typed by hand; a name that no folder can bear has the removal for its one fix
        "RED: : the marketplace has an entry for it, but modules/ is no module folder",
        STRAY_WHY,
        f'  fix: remove the entry named "" from plugins in {MARKET}',
        "RED: .x: the marketplace has an entry for it, but modules/.x is no module folder",
        STRAY_WHY,
        f'  fix: remove the entry named ".x" from plugins in {MARKET}',
        "RED: _x: the marketplace has an entry for it, but modules/_x is no module folder",
        STRAY_WHY,
        f'  fix: remove the entry named "_x" from plugins in {MARKET}',
        "RED: a/b: the marketplace has an entry for it, but modules/a/b is no module folder",
        STRAY_WHY,
        f'  fix: remove the entry named "a/b" from plugins in {MARKET}',
        "RED: const-gone: the marketplace has an entry for it, but modules/const-gone is no module folder",
        STRAY_WHY,
        f'  fix: remove the entry named "const-gone" from plugins in {MARKET}'
        + MAKE_FIX.format("const-gone"),
        "RED: const-plain: the marketplace has an entry for it, but modules/const-plain is no module folder",
        STRAY_WHY,
        f'  fix: remove the entry named "const-plain" from plugins in {MARKET}'
        + MAKE_FIX.format("const-plain"),
        "RED: gone: the marketplace has an entry for it, but modules/gone is no module folder",
        STRAY_WHY,
        f'  fix: remove the entry named "gone" from plugins in {MARKET}',
        "RED: .x@kit-test: the kit's settings enable it, but modules/.x is no module folder",
        KEY_WHY,
        f'  fix: remove the key ".x@kit-test" from enabledPlugins in {SETTINGS}',
        "RED: @kit-test: the kit's settings enable it, but modules/ is no module folder",
        KEY_WHY,
        f'  fix: remove the key "@kit-test" from enabledPlugins in {SETTINGS}',
        "RED: _x@kit-test: the kit's settings enable it, but modules/_x is no module folder",
        KEY_WHY,
        f'  fix: remove the key "_x@kit-test" from enabledPlugins in {SETTINGS}',
        "RED: a/b@kit-test: the kit's settings enable it, but modules/a/b is no module folder",
        KEY_WHY,
        f'  fix: remove the key "a/b@kit-test" from enabledPlugins in {SETTINGS}',
        "RED: const-gone@kit-test: the kit's settings enable it, but modules/const-gone is no module folder",
        KEY_WHY,
        f'  fix: remove the key "const-gone@kit-test" from enabledPlugins in {SETTINGS}'
        + MAKE_FIX.format("const-gone"),
        "RED: const-plain@kit-test: the kit's settings enable it, but modules/const-plain is no module"
        " folder",
        KEY_WHY,
        f'  fix: remove the key "const-plain@kit-test" from enabledPlugins in {SETTINGS}'
        + MAKE_FIX.format("const-plain"),
        "RED: gone@kit-test: the kit's settings enable it, but modules/gone is no module folder",
        KEY_WHY,
        f'  fix: remove the key "gone@kit-test" from enabledPlugins in {SETTINGS}',
        "RED: 14 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    list_strays_lines = [  # typed by hand: the restore is offered only to a name `const-<aspect>`
        *(
            line
            for stray, fix in (
                (".hidden", ""),  # its folder exists, and is skipped: no module
                ("_draft", ""),  # the same
                # a name that only starts like a module's, or holds a character none may: no restore either
                ("const-", ""),
                ("const-Bad", ""),
                ("const-a.b", ""),
                ("const-gone", ", or restore modules/const-gone with its MODULE.md"),
                ("glossary", ""),  # a restored folder would be red for its name
            )
            for line in (
                f"RED: {stray}: the list has its entries `install-{stray}`, `fixtures-{stray}`,"
                f" `lint-{stray}`, `types-{stray}`, but modules/{stray} is no module folder",
                "  why: the list's modules are exactly the module folders, and an entry of a missing module"
                " checks nothing",
                f"  fix: remove `{stray}` from MODULES in scripts/gate-list.sh{fix}",
            )
        ),
        "RED: 7 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    dials_strays = registry_tree(("const-x", "const-quiet"), REGISTRY_TAG)
    # six strays, in neither their sorted order nor its reverse (as the marketplace's): a sort holds it
    six = ("const-gone", "const-away", "const-zed", "const-mid", "const-bar", "const-old")
    dials_strays[DIALS] = {
        "root_policy": "p",
        **{key: {} for key in six},
        "plc-0001-root-policy": {},
        TEST_OWNER: dials_strays[DIALS][TEST_OWNER],
    }
    # a description that is the manifest's with something more, or with something less, differs where the
    # shorter one ends: after its last character, counted from 1
    prefix = registry_tree(("const-x", "const-quiet"), REGISTRY_TAG)
    prefix[MARKETPLACE_FILE]["plugins"][0]["description"] = "The module const-x. "  # const-x, 19 + a space
    prefix[MARKETPLACE_FILE]["plugins"][1]["description"] = "The module"  # const-quiet, cut short
    prefix_lines = [
        "RED: const-quiet: its marketplace entry's description differs from its manifest's, first at"
        " character 11 (counting from 1)",
        DESCRIPTION_WHY,
        "  fix: copy `description` of modules/const-quiet/plugin/.claude-plugin/plugin.json, as written, into"
        " the"
        f' entry named "const-quiet" of plugins in {MARKET}',
        "RED: const-x: its marketplace entry's description differs from its manifest's, first at character"
        " 20 (counting from 1)",
        DESCRIPTION_WHY,
        "  fix: copy `description` of modules/const-x/plugin/.claude-plugin/plugin.json, as written, into the"
        " entry"
        f' named "const-x" of plugins in {MARKET}',
        "RED: 2 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
    ]
    no_path = (
        "cd shared && python3 -m mypy --strict constitution_layer_kit\n"
        "cd scripts && python3 -m mypy --strict *.py"
    )
    for name, case, lines in (
        (
            "a description that continues its manifest's and one that is cut short of it",
            Case({"x": SCAN}, files=prefix),
            prefix_lines,
        ),
        (
            "six dials namespaces with no module folder, and a kernel key and a policy's namespace beside"
            " them, in the order of their names",
            Case({"x": SCAN}, files=dials_strays),
            [
                *(line for key in sorted(six) for line in namespace_lines(key)),
                "RED: 6 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
            ],
        ),
        (
            "a types entry with no MYPYPATH",
            Case({"x": SCAN}, types=no_path),
            [
                *types_lines("nothing", pair_path),
                "RED: 1 finding(s) — 2 module document(s) examined, 1 declared scan(s), 0 kit check(s)",
            ],
        ),
        (
            "the list's modules naming folders that are no module: the restore is offered only to a name"
            " `const-<aspect>`, the removal to every name",
            Case(
                {"x": SCAN},
                listed=(
                    "const-x",
                    "const-quiet",
                    ".hidden",
                    "_draft",
                    "const-",
                    "const-Bad",
                    "const-a.b",
                    "const-gone",
                    "glossary",
                ),
                scripts={"modules/.hidden/MODULE.md": False, "modules/_draft/MODULE.md": False},
            ),
            list_strays_lines,
        ),
        (
            "a marketplace entry and a settings key naming a module's missing folder or plain file, another"
            " missing folder, `_x`, `.x`, `a/b` or nothing, each told by the literal why and fix — the"
            " folder offered only to a module's name",
            strays_case(SCAN),
            strays_lines,
        ),
        (
            "every kind of finding about the files that name a module, written in order",
            messy_case(SCAN, reverse=False),
            MESSY_LINES,
        ),
        (
            "the same findings, every object's keys and every list written backwards",
            messy_case(SCAN, reverse=True),
            MESSY_LINES,
        ),
        (
            "the declaration and the enabled keys missing, an entry with no source, one with no"
            " description, a manifest whose description is no string",
            registry_case(
                SCAN,
                lambda f: (
                    f[SETTINGS_FILE].pop("enabledPlugins"),
                    f[SETTINGS_FILE].update({"extraKnownMarketplaces": {"elsewhere": {}}}),
                    f[MARKETPLACE_FILE]["plugins"][1].pop("source"),
                    f["modules/const-quiet/plugin/.claude-plugin/plugin.json"].update({"description": ["a"]}),
                    f[MARKETPLACE_FILE]["plugins"][0].pop("description"),
                ),
            ),
            ABSENT_LINES,
        ),
        (
            "findings of three folders written in the opposite order, the scans' and the list's together",
            Case(
                {"other": "true"},
                folders=("const-z", "const-y", "const-x"),
                listed=(),
                documents={"const-y": MODULE_TEXT.replace("check-x", "check-w")},
            ),
            ordered_lines,
        ),
        (
            "a list's module, a marketplace entry, an item filter and a kit check, in the order of the kinds",
            Case(
                {"x": SCAN},
                workflow=f"{READS}  filtered:\n    run: python3 modules/const-x/tests/run.py --item 3\n",
                listed=("const-x",),
                scripts=TRACKED,
                files=without_quiet,
            ),
            kinds_lines,
        ),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, case)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed), listed_in_reverse():
                code = report(*check_kit(root))
        ok = code == EXIT_RED and printed.getvalue().splitlines() == lines
        tally.judge(ok, f"the report of {name} is its literal text, exit 2")
        if not ok:
            print(printed.getvalue())


def report_of_no_source(tally: Tally) -> None:
    """The report of a declaration with no source is its literal text."""
    no_source = Finding("kit-test", Where.KNOWN_SOURCE, said="no source").render()
    ok = no_source == "\n".join(DECLARED_SOURCE_LINES)
    tally.judge(ok, "the report of a declaration with no source is its literal text")
    if not ok:
        print(no_source)


def sections_out_of_order(tally: Tally) -> None:
    """A document whose t11 section stands before t10 is BROKEN, and read once put in order."""
    blocks: list[list[str]] = [[]]  # the document cut before each section anchor
    for line in MODULE_TEXT.splitlines(keepends=True):
        if re.fullmatch(r'<a id="t\d+"></a>', line.strip()):
            blocks.append([])
        blocks[-1].append(line)
    order = [block[0].strip() for block in blocks[1:]]
    at10, at11 = order.index('<a id="t10"></a>') + 1, order.index('<a id="t11"></a>') + 1
    blocks[at10], blocks[at11] = blocks[at11], blocks[at10]  # the sections t11 and t10 trade places
    swapped = "".join("".join(block) for block in blocks)
    with tempfile.TemporaryDirectory() as tmp:  # t11 before t10: BROKEN; the fix applied, by number: read
        root = Path(tmp).resolve()
        build(root, Case({"x": SCAN}, document=swapped, guide=guide_text(GUIDE_X)))
        try:
            check_kit(root)
            before = None
        except Broken as bad:
            before = str(bad)
        blocks[1:] = sorted(blocks[1:], key=lambda block: int(re.findall(r"\d+", block[0])[0]))  # the fix
        build_text = "".join("".join(block) for block in blocks)
        (root / "modules/const-x/MODULE.md").write_text(build_text, encoding="utf-8")
        ok = before is not None and "the anchor after" in before
        ok = ok and build_text == MODULE_TEXT and check_kit(root)[0] == []
    tally.judge(
        ok,
        "a document whose t11 section stands before t10, put in the"
        " template's order as the fix says, is read",
    )


def damage_tree(root: Path, change: str) -> None:
    """Make the throwaway kit at root unreadable in the way `change` names."""
    if change == "LIST":
        (root / GATE_LIST).write_text("#!/bin/sh\necho 'BROKEN: no list' >&2\nexit 1\n", encoding="utf-8")
    if change == "JSON":
        text = (root / GATE_LIST).read_text(encoding="utf-8")
        (root / GATE_LIST).write_text(
            re.sub(r"--json\) echo '[^']*'", "--json) echo '{\"kit\": 1}'", text), encoding="utf-8"
        )
    if change == "NO-T9":
        (root / "modules/const-x/MODULE.md").write_text("no anchor\n", encoding="utf-8")
    if change in ("T9-ON-HEADING", "T9-TWICE", "T10-TWICE", "NO-T10", "T11-BEFORE-T10", "T9-LAST"):
        broken_text = {
            "T9-ON-HEADING": MODULE_TEXT.replace('<a id="t9"></a>\n## 9', '## 9 <a id="t9"></a>'),
            "T9-TWICE": MODULE_TEXT.replace("## 9\n", '## 9\n<a id="t9"></a>\n', 1),
            "T10-TWICE": MODULE_TEXT.replace("| E2 |", '<a id="t10"></a>\n| E2 |', 1),
            "NO-T10": MODULE_TEXT.replace('<a id="t10"></a>\n', ""),
            "T9-LAST": MODULE_TEXT.replace('<a id="t9"></a>\n', "") + '<a id="t9"></a>\n',
            "T11-BEFORE-T10": MODULE_TEXT.replace('<a id="t10"></a>\n', "@@")
            .replace('<a id="t11"></a>\n', '<a id="t10"></a>\n')
            .replace("@@", '<a id="t11"></a>\n'),
        }[change]
        (root / "modules/const-x/MODULE.md").write_text(broken_text, encoding="utf-8")
    if change == "DIALS-DATE":
        (root / DIALS).write_text("d: 2001-13-45\n", encoding="utf-8")
    if change == "NO-DOC":
        (root / "modules/empty").mkdir()
    if change == "NO-MODULES":
        shutil.rmtree(root / "modules")


def broken_lines(tally: Tally) -> None:
    """Each state the check cannot run on is a teaching BROKEN line."""
    for name, change, said in (
        ("a list script that fails", "LIST", f"{GATE_LIST} --names gate exited"),
        ("jobs that are no JSON list", "JSON", f"{GATE_LIST} --json printed no list of job names"),
        (
            "a module document without its anchor",
            "NO-T9",
            'modules/const-x/MODULE.md has no anchor <a id="t9"></a> on a line of its own',
        ),
        (
            "a module document whose anchor has text on its line",
            "T9-ON-HEADING",
            'modules/const-x/MODULE.md has no anchor <a id="t9"></a> on a line of its own',
        ),
        (
            "a module document whose enforcement anchor stands twice",
            "T9-TWICE",
            'modules/const-x/MODULE.md holds the anchor <a id="t9"></a> twice, lines 1 and 3',
        ),
        (
            "a module document with a second end anchor above its E-row",
            "T10-TWICE",
            'modules/const-x/MODULE.md holds the anchor <a id="t10"></a> twice, lines 7 and 13',
        ),
        (
            "a module document without its end anchor, t11 and t12 standing",
            "NO-T10",
            'modules/const-x/MODULE.md has no anchor <a id="t10"></a> after <a id="t9"></a>',
        ),
        (
            "a module document whose t11 anchor stands before t10",
            "T11-BEFORE-T10",
            'modules/const-x/MODULE.md: the anchor after <a id="t9"></a> is <a id="t11"></a>, not'
            ' <a id="t10"></a> — fix: put the sections in the template\'s order, t1 to t12, each anchor'
            " alone on the line above its section's heading",
        ),
        (
            "a module document whose t9 anchor is its last",
            "T9-LAST",
            'modules/const-x/MODULE.md: no anchor follows <a id="t9"></a>, and <a id="t10"></a> stands'
            " before it — fix: put the sections in the template's order, t1 to t12",
        ),
        (  # the message goes on by the Python: "…, not 13" from 3.14, so the line is held to its start
            "a dials file with a date out of range",
            "DIALS-DATE",
            f"{DIALS} is no YAML (month must be in 1..12",
        ),
        ("a module folder without its document", "NO-DOC", "modules/empty has no MODULE.md"),
        (
            "a tree with no modules/",
            "NO-MODULES",
            "has no modules/ directory — fix: run the check from a checkout of the kit",
        ),
        ("a tree that is no git repository", "NO-REPO", "git ls-files scripts exited"),
        (  # the folder around the tree is a repository: its index is never read for the kit's
            "a tree that is no git repository, inside a folder that is one",
            "NESTED-NO-REPO",
            "git ls-files scripts exited",
        ),
        ("a git that cannot be run", "NO-GIT", "git cannot be run"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            if change == "NESTED-NO-REPO":  # the temp folder is a repository, the kit tree a folder in it
                subprocess.run(["git", "init", "-q"], cwd=root, check=True)
                root = root / "kit"
                root.mkdir()
            build(root, Case({"x": SCAN}, repo=change not in ("NO-REPO", "NESTED-NO-REPO")))
            damage_tree(root, change)
            path = os.environ["PATH"]
            if change == "NO-GIT":
                os.environ["PATH"] = ""
            try:
                tracked_checks(root) if change == "NO-GIT" else check_kit(root)
                ok = False
            except Broken as broken:
                ok = said in str(broken) and "fix:" in str(broken)
            finally:
                os.environ["PATH"] = path
        tally.judge(ok, f"{name} is a teaching BROKEN line")


def unreadable_files(tally: Tally) -> None:
    """Each file the check cannot read gives its literal BROKEN line, exit 1."""
    unreadable = broken_cases(SCAN)
    for name, (case, line) in unreadable.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build(root, case)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed), coverage_owner(case.owner or COVERAGE.owner):
                code = run(root)
        lines = [f"BROKEN: {line}", "BROKEN: the check could not run — 0 module documents examined"]
        ok = code == EXIT_BROKEN and printed.getvalue().splitlines() == lines
        tally.judge(ok, f"{name} is its literal BROKEN line, exit 1")
        if not ok:
            print(printed.getvalue())


def pyyaml_missing(tally: Tally) -> None:
    """PyYAML missing is a BROKEN line with the install command, exit 1."""
    with tempfile.TemporaryDirectory() as tmp:  # PyYAML missing: a `yaml` that raises ImportError comes first
        (Path(tmp) / "yaml.py").write_text("raise ImportError('PyYAML is hidden')\n", encoding="utf-8")
        done = subprocess.run(
            [sys.executable, str(Path(__file__).resolve())],
            env={**os.environ, "PYTHONPATH": tmp},
            capture_output=True,
            text=True,
            check=False,
        )
    ok = (
        done.returncode == EXIT_BROKEN
        and done.stdout.splitlines()
        == [
            "BROKEN: PyYAML is not installed — fix: python3 -m pip install pyyaml",
            "BROKEN: the check could not run — 0 module documents examined",
        ]
        and done.stderr == ""
    )
    tally.judge(ok, "PyYAML missing is a BROKEN line with the install command, exit 1")


def failing_list_script(tally: Tally) -> None:
    """A list script that exits other than 0 is a BROKEN line that quotes the last line it said: the
    last of its standard error, or of its standard output when its standard error is empty."""
    said_by = {
        "standard error and standard output": ("echo out; echo err >&2", "err"),
        "standard output alone": ("echo first; echo last", "last"),
    }
    for name, (body, quoted) in said_by.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / GATE_LIST).parent.mkdir(parents=True)
            (root / GATE_LIST).write_text(f"#!/bin/sh\n{body}\nexit 3\n", encoding="utf-8")
            try:
                listed(root, "--names", "gate")
                got = "nothing raised"
            except Broken as broken:
                got = str(broken)
        want = f"{GATE_LIST} --names gate exited 3 ({quoted}) — fix: restore the list script"  # typed by hand
        tally.judge(got == want, f"a list script that fails after printing on {name} is quoted by that line")
        if got != want:
            print(f"        got: {got}")


def self_test() -> int:
    """Red→green on a throwaway tree: a scan missing from the gate group, and one in a kit whose
    workflow does not read the list or names it only in a comment line or a trailing comment, are red
    with one finding each and green once listed and read;
    an extra entry is no gate; a span with a flag after `--scan` and the words is no scan; a module
    with no scan needs no entry; a scan whose entry falls into `kit` or into another module's job is
    red, and so is one whose command lacks `PYTHONPATH="$PWD/shared"` before it; a module folder the
    list's modules leave out, and a listed module with no folder, are red; a
    tracked kit check no entry of the gate group runs is red; the forms of the enforcement table are
    held by `form_probes`; the report of each kind of finding is its literal text with exit 2; a list
    script that fails, jobs that are no JSON list, a module document without its enforcement anchor
    or with it twice, a module folder without its document, a tree that is no repository and a git
    that cannot be run are each a teaching BROKEN line; a scan declared as `<entry>.py --scan` is held
    by its python3 line and taught by it; the files that name a module are held by `registry_cases`
    (a copy changed one at a time), the name over a whole set of names, the reports of `messy_case`
    written in order and backwards, the scans' and the list's findings of three folders in the folders'
    sorted order, and `broken_cases` (each file the check cannot read, its literal
    BROKEN line with exit 1)."""
    tally = Tally()
    cases_gate_list(tally)
    cases_selections(tally)
    cases_kit_check_names(tally)
    cases_module_folder_names(tally)
    cases_folder_renames(tally)
    cases_stray_dials_keys(tally)
    cases_scan_readers(tally)
    reports_by_kind(tally)
    fixes_of_the_guide(tally)
    fixes_of_the_coverage(tally)
    report_of_a_green_kit(tally)
    reports_in_order(tally)
    report_of_no_source(tally)
    sections_out_of_order(tally)
    broken_lines(tally)
    unreadable_files(tally)
    pyyaml_missing(tally)
    failing_list_script(tally)
    print(f"{tally.judged - tally.failed}/{tally.judged} cases green")
    return EXIT_GREEN if tally.failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-gate-lists", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 module documents examined")
        return EXIT_BROKEN
    if not args.self_test:
        return run(KIT)
    try:
        with coverage_owner(TEST_OWNER):
            return self_test()
    except Broken as broken:
        return broken_report(broken)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
