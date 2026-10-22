"""Kit tooling, never shipped in a module: how a kit check installs one module through Claude Code into a
bare repository, the steps `scripts/check-bare-install.py` and `scripts/check-session-load.py` share
(decision dec-0093-module-evals-with-local-receipts, R10).

`bare_repository` makes a git repository under a throwaway folder, the kit's kernel copied to
docs/constitution/ and committed. `install` adds the kit's marketplace from a source and installs the module
at the default scope, in that repository and in an empty configuration folder `<root>/config`, every
`claude` command in the person's environment less the four variables of `kit_module_doc.claude_env`; it
returns the installed copy's folder, as `listed_install` reads it from `claude plugin list --json`. A refusal
of the install is a `Refused`, a finding against the module; any other failure is a `Broken` whose message
says what failed and the fix. `run` starts one command and turns a failure to start it into a `Broken`; the
path lookups `file_at`, `folder_at`, `there` and `link_at` do the same for a path that cannot be looked up.
What each reads of Claude Code, and why, is the docstring of `scripts/check-bare-install.py`.

`shared_path` is the step that gives a check the change's own shared code (decision
dec-0099-shared-code-installed-as-a-pip-package, R17): a module's plugin holds no copy of
`shared/constitution_layer_kit/`, its entry files import the package that `python3` finds, and a check that
runs a session, a hook, a scan or a gate must run the working folder's shared code and never a release a
developer installed. The step makes a throwaway virtual environment under the check's own throwaway folder,
`<root>/shared-env`, from the `python3` the check runs under (`sys.executable`), with
`--system-site-packages`, so that PyYAML stays visible, and `--without-pip`, so that nothing is fetched;
writes into its site-packages a `.pth` file that names the absolute path of the kit's `shared/` folder, the
working folder's, which comes on `sys.path` before the folders of the system's python3 and a user's
site-packages; and returns the PATH with the environment's `bin` first. A check gives that PATH to every
`claude` command and every scan, hook or gate it starts: `scripts/check-bare-install.py` and
`scripts/check-session-load.py` do, and `scripts/check-install-guide.py` gives it to the run of the guide's
blocks. Nothing is built and nothing needs the network.
When the check itself runs under a virtual environment, whose packages a new environment does not inherit,
the `.pth` file names that environment's site-packages after `shared/`, so that PyYAML stays visible there
too. The step then asks the new environment's `python3` to import `constitution_layer_kit` and `yaml`, and
holds that the package comes from the kit's `shared/`. Each failure is a `Broken` with the fix: a kit with
no `shared/constitution_layer_kit/`; `python3 -m venv` that fails; a `.pth` file that cannot be written; an
import that fails or finds another copy of the package first, such as one a `PYTHONPATH` names.
"""

from __future__ import annotations

import errno
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import sysconfig
from pathlib import Path

from kit_module_doc import DocumentError, Note, claude_env, command_fix, marketplace_name, platform_fix

KIT = Path(__file__).resolve().parent.parent
FROM_ENV = "CONSTITUTION_KIT_INSTALL_FROM"  # the source to install from, `<owner>/<repo>#<branch>` in CI
SCRIPT = "scripts/kit_install.py"  # named in the fix of a reply its readers do not read
INSTALL_TIMEOUT = 300  # seconds the install is given, kit tuning and no platform fact
LIST_WHERE = (
    "a folder of your own, CLAUDE_CONFIG_DIR set to an empty folder"  # where the failed list is run again
)
RUN_FIX = (
    "give it a command that exists and can run, with no NUL byte in it or its arguments: a program on"
    " PATH, or a file with the execute permission (`chmod u+x` it), then run the check again"
)
SHARED_ENV = "shared-env"  # the folder of the shared code's virtual environment, under the check's own folder
SHARED_PTH = "constitution-kit-shared.pth"  # the file in its site-packages that names the kit's shared/
SHARED_PACKAGE = "constitution_layer_kit"  # the shared package, a folder of the kit's shared/
SHARED_PROBE = (
    f"import {SHARED_PACKAGE}, yaml; print({SHARED_PACKAGE}.__file__)"  # what the environment must do
)


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


class Refused(Exception):
    """The platform refused to install the module: a finding against the module."""


def plain(command: str) -> str:
    """A command as a message echoes it: a plain word as it is, else as `shown` quotes it, so that one with a
    space, a quote, a line break or no characters at all reads as one token."""
    return command if re.fullmatch(r"[\w@%+=:,./-]+", command) else shown(command)


def run(
    argv: list[str],
    cwd: Path,
    env: dict[str, str],
    stdin: str = "",
    timeout: float = 300,
    fix: str = RUN_FIX,
) -> tuple[int, str, str]:
    """The exit, the standard output and the standard error of one command. A command that is not found
    is a Broken saying to install it, as `plain` echoes it, and a working folder that does not exist a
    Broken of its own, naming the folder; any other `OSError` of starting it (an empty command, a file with no
    execute permission, a folder that cannot be searched) and a `ValueError` (a NUL byte) are a Broken that
    names the command, as `shown` quotes it, and the reason, with `fix` to follow; one that outlasts its
    `timeout` is the exit 124."""
    try:
        done = subprocess.run(
            argv, cwd=cwd, env=env, input=stdin, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError as bad:
        if not os.path.isdir(cwd):  # the working folder is what is missing, whichever command is asked for
            raise Broken(
                f"the working folder {cwd} does not exist — fix: make the folder"
                f" (`mkdir -p {shlex.quote(str(cwd))}`), then run the check again"
            ) from bad
        raise Broken(
            f"{plain(argv[0])} is not installed ({bad.strerror}) — fix: install it and put it on PATH"
        ) from bad
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout} s"
    except (OSError, ValueError) as bad:
        why = (bad.strerror if isinstance(bad, OSError) else None) or str(bad)
        raise Broken(f"the command {shown(argv)} could not be started ({why}) — fix: {fix}") from bad
    return done.returncode, done.stdout.strip(), done.stderr.strip()


def looked_up(path: Path, follow: bool = True) -> os.stat_result | None:
    """What `os.stat` says of a path (`os.lstat` when `follow` is False): None for a path that is not
    there (no entry, a path through a file, a link loop, a name that holds a NUL byte), a Broken for a
    path that cannot be looked up (a folder on the way cannot be searched, an I/O error). The check asks
    this and not `Path.is_file`, `is_dir` or `exists`: from release 3.14 of the language on they return
    False for the error that earlier releases raise, and the answer would differ by version, a path the
    check cannot look at read as a missing one."""
    try:
        return path.stat() if follow else path.lstat()
    except (FileNotFoundError, NotADirectoryError, ValueError):
        return None
    except OSError as bad:
        if bad.errno == errno.ELOOP:
            return None
        why = bad.strerror or str(bad)
        if bad.errno == errno.EACCES:
            folder = blocking_folder(path)
            fix = f"give the folder {folder} search permission, `chmod u+rx {shlex.quote(str(folder))}`"
        else:
            folder = path.parent
            fix = f"make the folder {folder} searchable, `ls -ld {shlex.quote(str(folder))}` shows why not"
        raise Broken(f"{path} cannot be searched ({why}) — fix: {fix}, then run the check again") from bad


def blocking_folder(path: Path) -> Path:
    """The folder on the way to a path that refuses the search: the first, from the root down, below which
    `os.stat` is denied; the path's own folder when none is."""
    chain = [*reversed(path.parents), path]
    for folder, below in zip(chain, chain[1:], strict=False):
        try:
            os.stat(below)
        except PermissionError:
            return folder
        except OSError:
            continue
    return path.parent


def file_at(path: Path) -> bool:
    """Whether a regular file (or a link to one) stands at the path; a Broken where it cannot be looked up."""
    found = looked_up(path)
    return found is not None and stat.S_ISREG(found.st_mode)


def folder_at(path: Path) -> bool:
    """Whether a folder (or a link to one) stands at the path; a Broken where it cannot be looked up."""
    found = looked_up(path)
    return found is not None and stat.S_ISDIR(found.st_mode)


def there(path: Path) -> bool:
    """Whether anything stands at the path (a link is followed); a Broken where it cannot be looked up."""
    return looked_up(path) is not None


def link_at(path: Path) -> bool:
    """Whether a link stands at the path, itself and not what it leads to; a Broken where it cannot be
    looked up."""
    found = looked_up(path, follow=False)
    return found is not None and stat.S_ISLNK(found.st_mode)


def last_line(out: str, err: str) -> str:
    said = err or out
    return said.splitlines()[-1] if said else "no output"


def git_command(argv: list[str]) -> str:
    """The name of a git command: `git <subcommand>`, the subcommand being the first argument after `git`
    that is neither an option nor the value of one. `-c` and `-C` take the next argument as their value (an
    option joined to its value with `=` takes none); the commands of `bare_repository` use no other option
    that does. An argv with no subcommand is named `git`."""
    skip = False
    for arg in argv[1:]:
        if skip:
            skip = False
        elif arg in ("-c", "-C"):
            skip = True
        elif not arg.startswith("-"):
            return f"git {arg}"
    return "git"


def git_failed(argv: list[str], out: str, err: str) -> Broken:
    """The BROKEN line of a git command of `bare_repository` that exited other than 0. `run` has turned a
    missing git into its own line, so git ran and "install git" would be no fix: run the command by hand."""
    name = git_command(argv)
    return Broken(
        f"{name} failed in the bare repository ({last_line(out, err)}) — fix: run {name} in a new"
        " repository by hand and read why it fails"
    )


def bare_repository(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    env = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull}
    for argv in (["git", "init", "-q", "-b", "main"],):
        code, out, err = run(argv, repo, env)
        if code != 0:
            raise git_failed(argv, out, err)
    shutil.copytree(KIT / "kernel", repo / "docs" / "constitution")
    for argv in (
        ["git", "add", "-A"],
        [
            "git",
            "-c",
            "user.name=bare",
            "-c",
            "user.email=bare@example.invalid",
            "commit",
            "-q",
            "-m",
            "kernel",
        ],
    ):
        code, out, err = run(argv, repo, env)
        if code != 0:
            raise git_failed(argv, out, err)
    return repo


def kit_marketplace(kit: Path) -> str:
    """The name of the marketplace the kit at `kit` declares, read from its marketplace.json by
    `kit_module_doc.marketplace_name`; a file that gives none is a Broken with that function's line."""
    try:
        return marketplace_name(kit)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


def shown(value: object) -> str:
    """A reply of Claude Code, or a field of it, as a message quotes it: its repr, at most 200 characters."""
    text = repr(value)
    return text if len(text) <= 200 else text[:200] + "…"


def install_scope(key: str, code: int, out: str, timeout: float, note: Note) -> str:
    """The scope the install of `key` wrote, from the result of `claude plugin install --json`: the
    last non-empty line of its standard output, one JSON object whose `outcome` is "ok" or "failed". The
    run's own timeout (exit 124), no such line, an `outcome` of neither value, and "ok" with an exit other
    than 0 or with no `scope` string are a Broken; "failed" is a Refused, carrying the result's
    `failureCode` and `message` when present."""
    command = f"`claude plugin install {key} --json`"
    fix = platform_fix(note, SCRIPT, "install_scope", "a reply")
    if code == 124:
        raise Broken(
            f"{command} gave no result in {timeout:g} s — fix: run the check again, and check that git can"
            " reach the source"
        )
    lines = [line for line in out.splitlines() if line.strip()]
    if not lines:
        raise Broken(f"{command} printed nothing on standard output (exit {code}){fix}")
    try:
        result = json.loads(lines[-1])
    except ValueError:
        result = None
    if not isinstance(result, dict):
        raise Broken(f"{command} ended with {shown(lines[-1])}, not one JSON object (exit {code}){fix}")
    outcome = result.get("outcome")
    if outcome == "failed":
        said = [str(result[k]) for k in ("failureCode", "message") if isinstance(result.get(k), str)]
        raise Refused(": ".join(s for s in said if s) or f"exit {code}")
    if outcome != "ok":
        what = "has no outcome" if "outcome" not in result else f"has the outcome {shown(outcome)}"
        raise Broken(f'{command} ended with an object that {what}, not "ok" or "failed" (exit {code}){fix}')
    if code != 0:
        raise Broken(f"{command} said ok and exited {code}{fix}")
    scope = result.get("scope")
    if not isinstance(scope, str):
        what = "absent" if "scope" not in result else shown(scope)
        raise Broken(f"{command} said ok without a scope string (scope is {what}){fix}")
    return scope


def listed_install(key: str, scope: str, repo: Path, env: dict[str, str], note: Note) -> Path:
    """The installed copy's folder, from `claude plugin list --json` run in the bare repository: a JSON
    list with exactly one entry whose `id` is `key` and whose `scope` is the one the install wrote, its
    `installPath` a string naming an existing folder; anything else is a Broken saying what was found."""
    command = "`claude plugin list --json`"
    fix = platform_fix(note, SCRIPT, "listed_install", "a reply")
    code, out, err = run(["claude", "plugin", "list", "--json"], repo, env)
    if code != 0:  # no reply was written: no reader to update, whatever the exit; 124 is `run`'s timeout
        said = command_fix(note, "claude plugin list --json", LIST_WHERE, timed_out=code == 124)
        raise Broken(f"{command} exited {code} ({last_line(out, err)}){said}")
    try:
        entries = json.loads(out)
    except ValueError as bad:
        raise Broken(f"{command} printed no JSON ({shown(out)}: {bad}){fix}") from bad
    if not isinstance(entries, list):
        raise Broken(f"{command} printed a JSON {type(entries).__name__}, not a list{fix}")
    own = [e for e in entries if isinstance(e, dict) and e.get("id") == key and e.get("scope") == scope]
    if len(own) != 1:
        found = ", ".join(
            f"{e.get('id')!r} at {e.get('scope')!r}" if isinstance(e, dict) else shown(e) for e in entries[:5]
        )
        listed = f"entries: {found}{', …' if len(entries) > 5 else ''}" if entries else "no entries"
        what = f"lists {len(own)} entries" if own else "lists no entry"
        raise Broken(
            f"{command} {what} whose id is {key} at the scope {scope} the install wrote ({listed}){fix}"
        )
    path = own[0].get("installPath")
    if not isinstance(path, str):
        raise Broken(
            f"{command} gives no installPath string for {key} at scope {scope} (installPath is"
            f" {shown(path) if 'installPath' in own[0] else 'absent'}){fix}"
        )
    if not folder_at(Path(path)):
        raise Broken(f"{command} names an installPath that is no folder ({path}){fix}")
    return Path(path)


def outer_site_packages() -> list[str]:
    """The site-packages folders of the python3 this check runs under when that is a virtual environment, in
    the order `sysconfig` gives them with a repeat dropped, else none: a new environment inherits the
    packages of the base python3 and not those of the one it was made from."""
    if sys.prefix == sys.base_prefix:
        return []
    paths = sysconfig.get_paths()
    return list(dict.fromkeys([paths["purelib"], paths["platlib"]]))


def shared_path(root: Path, shared: Path | None = None, path: str | None = None) -> str:
    """The PATH with the bin of a new virtual environment first, whose python3 imports the shared package from
    `shared`, the kit's `shared/` folder (the working folder's by default), and PyYAML as the python3 this
    check runs under does (decision dec-0099-shared-code-installed-as-a-pip-package, R17). The environment is
    made at `root/shared-env`, so it goes with the check's throwaway folder `root`; `path` is the PATH it is
    put before, else the person's. The steps and each failure are in the docstring of this file."""
    package = (KIT / "shared" if shared is None else shared) / SHARED_PACKAGE
    if not folder_at(package):
        raise Broken(
            f"the shared code is not at {package} — fix: run the check from a clone of the kit, which holds"
            f" shared/{SHARED_PACKAGE}/"
        )
    home, env = root / SHARED_ENV, dict(os.environ)
    made = [sys.executable, "-m", "venv", "--system-site-packages", "--without-pip", str(home)]
    code, out, err = run(made, root, env)
    if code != 0:
        raise Broken(
            f"{shlex.join(made)} exited {code} ({last_line(out, err)}) — fix: run that command by hand and"
            " read why it fails, then run the check again"
        )
    python = home / "bin" / "python3"
    code, out, err = run(
        [str(python), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"], root, env
    )
    if code != 0 or not out:
        raise Broken(
            f"the new environment {home} does not say where its packages go ({last_line(out, err)}) — fix:"
            f" run {shlex.quote(str(python))} by hand and read why, then run the check again"
        )
    pth = Path(out.splitlines()[-1]) / SHARED_PTH
    folders = [str(package.parent.resolve()), *outer_site_packages()]
    try:
        pth.write_text("".join(f"{folder}\n" for folder in folders), encoding="utf-8")
    except OSError as bad:
        raise Broken(
            f"{pth} could not be written ({bad.strerror or bad}) — fix: make the folder {root} writable,"
            " then run the check again"
        ) from bad
    code, out, err = run([str(python), "-c", SHARED_PROBE], root, env)
    if code != 0:
        raise Broken(
            f"the new environment cannot import the shared code and PyYAML ({last_line(out, err)}) — fix:"
            " PyYAML must be installed for the python3 that runs the check (`python3 -m pip install PyYAML`);"
            f" for another cause run {shlex.quote(str(python))} -c {shlex.quote(SHARED_PROBE)} by hand and"
            " read why, then run the check again"
        )
    found = Path(out.splitlines()[-1]).resolve().parent
    if found != package.resolve():
        raise Broken(
            f"the new environment imports {SHARED_PACKAGE} from {found}, not from {package} — fix: take the"
            " other copy off the way for this run: unset PYTHONPATH, which puts a folder first, then run the"
            " check again"
        )
    folder = str(home / "bin")
    return os.pathsep.join(p for p in (folder, os.environ.get("PATH", "") if path is None else path) if p)


def install(
    module: str,
    root: Path,
    repo: Path,
    source: str,
    marketplace: str,
    note: Note,
    timeout: float = INSTALL_TIMEOUT,
    path: str | None = None,
) -> Path:
    """Add the marketplace and install the module at the default scope, in the bare repository and an
    empty configuration folder `root/config`, every `claude` command in the person's environment less the
    four variables of `claude_env` that steer where Claude Code finds, keeps or loads plugins, so that the
    platform's plugins root is that folder's `plugins`, and with `path`, when given, as its PATH (the one
    `shared_path` makes); the installed copy's folder, as `listed_install` finds it."""
    if source.startswith("#"):
        raise Broken(
            f"the source {source} names a branch of no repository — the pull request's head repository is"
            " gone — fix: open the change again from a branch of a repository that exists"
        )
    config = root / "config"
    config.mkdir()
    env = (
        claude_env(os.environ) | ({} if path is None else {"PATH": path}) | {"CLAUDE_CONFIG_DIR": str(config)}
    )
    code, out, err = run(["claude", "plugin", "marketplace", "add", source], repo, env)
    if code != 0:
        last = last_line(out, err)
        raise Broken(
            f"`claude plugin marketplace add {source}` exited {code} ({last}) — fix: check the kit's"
            " marketplace.json, and that git can reach the source"
        )
    key = f"{module}@{marketplace}"
    code, out, _ = run(["claude", "plugin", "install", key, "--json"], repo, env, timeout=timeout)
    return listed_install(key, install_scope(key, code, out, timeout, note), repo, env, note)
