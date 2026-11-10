"""The setup: the two hooks of the commit log, written into git's configuration by a person, removed by a
person, and checked.

Each hook is a whole command of git's own configuration, `hook.<name>.command` with `hook.<name>.event`:
git runs it with no plugin path, so its command is one line of POSIX shell that runs `python3 -c` with a
program of the standard library alone. The program takes its clock in milliseconds first, then appends the
SHA of `HEAD`, that time, the value of `CLAUDE_CODE_SESSION_ID` (empty when unset) and its event, in one
write, to `commits.jsonl` in the folder of the logs in git's common directory, making the folder where it is
missing. Only the setup command, run by a person, writes the two keys, and it writes nothing else into git's
configuration."""

from __future__ import annotations

from pathlib import Path

from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.output import Output

from . import git as gitpart
from . import logs, messages
from .model import COMMITS, FOLDER, HOOK_COMMIT, HOOK_MERGE

# The program of both commands. It holds no single quote, so that the shell holds it whole in single quotes,
# and no compound statement, which would swallow what follows it on the line. It takes the clock first.
_CLOCK = "import time;ms=int(time.time()*1000)"
_IMPORTS = "import json,os,sys,subprocess as p"
_ASK = 'q=lambda*a:p.run(["git",*a],capture_output=True,text=True)'
_APPEND = (
    'c=os.path.abspath(q("rev-parse","--git-common-dir").stdout.strip());'
    f'd=os.path.join(c,"{FOLDER}");os.makedirs(d,exist_ok=True);'
    'h=q("rev-parse","HEAD").stdout.strip();'
    'l=json.dumps({"sha":h,"ms":ms,"session":os.environ.get("CLAUDE_CODE_SESSION_ID",""),"event":"%s"},'
    'separators=(",",":"))+"\\n";'
    f'f=os.open(os.path.join(d,"{COMMITS}"),os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o644);'
    "os.write(f,l.encode());os.close(f)"
)
# A merge commit whose reflog entry is no fast-forward: a fast-forward and a pull fire post-merge too.
_MERGE_ONLY = (
    'q("rev-parse","-q","--verify","HEAD^2").returncode==0 and '
    '"Fast-forward" not in q("reflog","-1","--format=%gs","HEAD").stdout or sys.exit(0);'
)


def program(event: str) -> str:
    """The Python program of one hook: the whole of it, on one line."""
    head = f"{_CLOCK};{_IMPORTS};{_ASK};"
    append = _APPEND % event
    return f"{head}{_MERGE_ONLY}{append}" if event == "merge" else f"{head}{append}"


def command(event: str) -> str:
    """The command of the hook, one line of POSIX shell."""
    return f"python3 -c '{program(event)}'"


EVENT_OF = {HOOK_COMMIT: ("post-commit", "commit"), HOOK_MERGE: ("post-merge", "merge")}


def run_set(output: Output, directory: Path) -> int:
    common = gitpart.common_directory(directory)
    if gitpart.is_old(directory):
        raise ConfigurationFailure(messages.j6_10_old_git(gitpart.version_text(directory)))
    for key, (git_event, name) in EVENT_OF.items():
        gitpart.set_config(directory, common, f"{key}.command", [command(name)])
        gitpart.set_config(directory, common, f"{key}.event", [git_event])
    output.out(messages.j17_set(str(gitpart.config_file(common))))
    return 0


def run_remove(output: Output, directory: Path) -> int:
    common = gitpart.common_directory(directory)
    for key in EVENT_OF:
        gitpart.remove_section(directory, common, key)
    output.out(messages.j18_removed(str(gitpart.config_file(common)), str(logs.folder_of(common))))
    return 0


def run_check(output: Output, directory: Path) -> int:
    gitpart.common_directory(directory)
    output.out(messages.j19_check(gitpart.missing_hooks(directory)))
    return 0
