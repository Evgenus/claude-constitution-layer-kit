"""The shell command as the gate reads it. The platform splits a command into subcommands to
match its permission rules; this module repeats that split on the raw text so that a wrapper,
a subshell or a global option does not hide the verb. Every step errs toward examining more:
a text the reader cannot split cleanly is examined as one subcommand of its words."""

from __future__ import annotations

import re
import shlex

from .model import Subcommand

# The operators that separate simple commands, longest first so `||` is not read as two pipes.
OPERATORS = ("&&", "||", "|&", ";", "|", "&", "\n")
# Programs that run another program: stripped with their own options, the rest is the command.
WRAPPERS = frozenset({"time", "nohup", "command", "builtin", "noglob", "xargs", "sudo", "doas", "env"})
WRAPPERS_WITH_VALUE = {"timeout": 1, "nice": 0, "stdbuf": 0}  # `timeout <n>`; nice/stdbuf take -x flags
SHELLS = frozenset({"bash", "sh", "zsh", "dash", "ksh"})
GIT_GLOBAL_WITH_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"})
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


def split(command: str) -> list[Subcommand]:
    """Every simple command of the text, in order of appearance: the top-level ones, then the
    contents of each `$(…)` and backtick substitution, then the string a shell is told to run
    with -c, each split in turn. A heredoc's body is data and is dropped."""
    found: list[Subcommand] = []
    _collect(_drop_heredocs(command), found)
    return found


def _collect(text: str, found: list[Subcommand]) -> None:
    for piece in _separate(text):
        stripped = piece.strip()
        if not stripped:
            continue
        for inner in _substitutions(stripped):
            _collect(inner, found)
        words = _words(stripped)
        if not words:
            continue
        words, inner_command = _normalise(words)
        found.append(Subcommand(tuple(words), stripped))
        if inner_command is not None:
            _collect(inner_command, found)


def _drop_heredocs(text: str) -> str:
    lines = text.split("\n")
    kept: list[str] = []
    skip_until: str | None = None
    for line in lines:
        if skip_until is not None:
            if line.strip() == skip_until:
                skip_until = None
            continue
        kept.append(line)
        match = HEREDOC.search(line)
        if match:
            skip_until = match.group(2)
    return "\n".join(kept)


def _separate(text: str) -> list[str]:
    """Split on the operators outside quotes, parentheses and substitutions."""
    pieces: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            current.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(text):
                current.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            current.append(ch)
            i += 1
            continue
        if ch == "\\" and i + 1 < len(text):
            current.append(ch)
            current.append(text[i + 1])
            i += 2
            continue
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        if depth == 0:
            operator = next((op for op in OPERATORS if text.startswith(op, i)), None)
            if operator is not None:
                pieces.append("".join(current))
                current = []
                i += len(operator)
                continue
        current.append(ch)
        i += 1
    pieces.append("".join(current))
    return pieces


def _substitutions(text: str) -> list[str]:
    """The contents of every `$(…)` and every backtick pair, outermost first."""
    inner: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("$(", i):
            depth, j = 1, i + 2
            while j < len(text) and depth:
                if text.startswith("$(", j) or text[j] == "(":
                    depth += 1
                elif text[j] == ")":
                    depth -= 1
                j += 1
            inner.append(text[i + 2 : j - 1])
            i = j
            continue
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j == -1:
                break
            inner.append(text[i + 1 : j])
            i = j + 1
            continue
        i += 1
    return inner


def _words(text: str) -> list[str]:
    try:
        return shlex.split(text, posix=True)
    except ValueError:  # an unbalanced quote: examined as its whitespace-separated words, never dropped
        return text.split()


def _normalise(words: list[str]) -> tuple[list[str], str | None]:
    """Strip assignments and wrappers, reduce the program to its base name, skip git's global
    options; a shell told to run a string hands that string back for its own split."""
    rest = list(words)
    while rest:
        head = rest[0]
        if ASSIGNMENT.match(head):
            rest.pop(0)
        elif head in WRAPPERS:
            rest.pop(0)
            while rest and rest[0].startswith("-"):  # a wrapper's own flags: `sudo -u x`, `env -i`
                rest.pop(0)
        elif head in WRAPPERS_WITH_VALUE:
            rest.pop(0)
            while rest and rest[0].startswith("-"):
                rest.pop(0)
            for _ in range(WRAPPERS_WITH_VALUE[head]):
                if rest:
                    rest.pop(0)
        else:
            break
    if not rest:
        return rest, None
    rest[0] = rest[0].rsplit("/", 1)[-1]
    if rest[0] in SHELLS:
        for index, word in enumerate(rest[1:], 1):
            if word == "-c" and index + 1 < len(rest):
                return rest, rest[index + 1]
            if not word.startswith("-"):
                break
    if rest[0] == "git":
        i = 1
        while i < len(rest) and rest[i].startswith("-"):
            option = rest[i].split("=", 1)[0]
            i += 2 if option in GIT_GLOBAL_WITH_VALUE and "=" not in rest[i] else 1
        rest = [rest[0], *rest[i:]]
    return rest, None
