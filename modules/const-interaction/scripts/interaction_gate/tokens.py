"""The shell command as the gate reads it. The platform splits a command into subcommands to
match its permission rules; this module repeats that split on the raw text so that a wrapper,
a subshell or a global option does not hide the verb. Every step but two errs toward examining
more — a text the reader cannot split cleanly is examined as one subcommand of its words; the
two that err toward silence, a quote opened on an earlier line and a wrapper flag the lists
below omit, are stated as limits in the module's document."""

from __future__ import annotations

import re
import shlex

from .model import Subcommand

# The operators that separate simple commands, longest first so `||` is not read as two pipes.
OPERATORS = ("&&", "||", "|&", ";", "|", "&", "\n")
# Programs that run another program: stripped with their own options, the rest is the command.
# Per wrapper, the flags that take a value of their own: `nice -n 5`, `sudo -u root`, `xargs -I {}`;
# a `--flag=value` is one token and needs no entry.
WRAPPERS: dict[str, frozenset[str]] = {
    "time": frozenset(),
    "nohup": frozenset(),
    "command": frozenset(),
    "builtin": frozenset(),
    "noglob": frozenset(),
    # Sources, read 2026-09-25: sudo's upstream man page (sudo.ws; -r, -t and their long forms are
    # SELinux-only and absent from the macOS page); the xargs pages of macOS 26 (BSD) and of GNU
    # findutils; env of macOS 26 and GNU coreutils, with FreeBSD's -L and -U; doas of OpenBSD; nice,
    # stdbuf and timeout of GNU coreutils. A long flag whose value is the next word is listed as the
    # page spells it — an abbreviation of it, which GNU getopt_long accepts, is not read as it, since
    # telling one apart needs every flag of the program; `--flag=value` is one token and needs no
    # entry; a GNU flag whose value is optional (`--max-lines[=N]`, `--eof[=STR]`) takes it attached
    # only and is left out on purpose, since given bare it takes no word.
    "xargs": frozenset(
        {
            "-I",
            "-J",
            "-d",
            "-P",
            "-s",
            "-n",
            "-L",
            "-a",
            "-E",
            "-R",
            "-S",
            "--max-args",
            "--max-procs",
            "--max-chars",
            "--arg-file",
            "--delimiter",
            "--process-slot-var",
        }
    ),
    "sudo": frozenset(
        {
            "-u",
            "-g",
            "-C",
            "-p",
            "-h",
            "-U",
            "-r",
            "-t",
            "-D",
            "-R",
            "-T",
            "-a",
            "-c",
            "--user",
            "--group",
            "--close-from",
            "--prompt",
            "--host",
            "--other-user",
            "--role",
            "--type",
            "--chdir",
            "--chroot",
            "--command-timeout",
            "--auth-type",
            "--login-class",
        }
    ),
    "doas": frozenset({"-u", "-C", "-a"}),
    "env": frozenset({"-C", "-u", "-S", "-P", "-L", "-U", "--chdir", "--unset", "--split-string"}),
    "nice": frozenset({"-n", "--adjustment"}),
    "stdbuf": frozenset({"-i", "-o", "-e", "--input", "--output", "--error"}),
    "timeout": frozenset({"-s", "-k", "--signal", "--kill-after"}),
}
WRAPPERS_WITH_VALUE = {"timeout": 1}  # `timeout <n> <command>`: one positional value before the command
# env's short flags that take a value, the rest of the token or the next; `-S` is among them, its value
# the command, and is read apart.
ENV_VALUE_LETTERS = frozenset(flag[1] for flag in WRAPPERS["env"] if len(flag) == 2 and flag != "-S")
# Shell words that precede a command without being a program: stripped so the verb is read.
SHELL_WORDS = frozenset(
    {"exec", "{", "}", "!", "if", "then", "else", "elif", "while", "until", "do", "fi", "done"}
)
SHELLS = frozenset({"bash", "sh", "zsh", "dash", "ksh"})
GIT_GLOBAL_WITH_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"})
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
# `>&`, `&>` and `<&` redirect; they are no separators.
REDIRECT_BEFORE = frozenset({">", "<"})


def split(command: str) -> list[Subcommand]:
    """Every simple command of the text, in order of appearance: the top-level ones, then the
    contents of each `$(…)` and backtick substitution, then the string a shell is told to run
    with -c or that `env -S` names with the words after it, each split in turn. A heredoc's body
    is data and is dropped."""
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
        if words:  # empty: nothing but shell words or assignments, or a wrapper whose value is the command
            found.append(Subcommand(tuple(words), stripped))
        if inner_command is not None:
            _collect(inner_command, found)


def _drop_heredocs(text: str) -> str:
    """A heredoc's body is data: the lines after an operator `<<WORD` that stands outside quotes,
    up to the line that is exactly WORD, are dropped — only when that line exists; an operator
    with no terminator drops nothing, so nothing is hidden by a marker inside a string."""
    lines = text.split("\n")
    kept: list[str] = []
    skip_until: str | None = None
    for index, line in enumerate(lines):
        if skip_until is not None:
            if line.strip() == skip_until:
                skip_until = None
            continue
        kept.append(line)
        for match in HEREDOC.finditer(line):
            word = match.group(2)
            terminated = any(later.strip() == word for later in lines[index + 1 :])
            if terminated and not _inside_quotes(line, match.start()):
                skip_until = word
                break
    return "\n".join(kept)


def _inside_quotes(line: str, position: int) -> bool:
    """Whether the position stands inside a quote opened on this line. A `$(` opens a new
    context, unquoted or in double quotes — `"$(cat <<'EOF'` puts the operator outside the outer
    quote — and its `)` restores the one it interrupted; inside single quotes it is text."""
    quote: str | None = None
    stack: list[str | None] = []
    i = 0
    while i < position:
        ch = line[i]
        if quote != "'" and line.startswith("$(", i):  # inside single quotes `$(` is literal text
            stack.append(quote)
            quote = None
            i += 2
            continue
        if quote:
            if ch == "\\" and quote == '"':
                i += 1
            elif ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
        elif ch == "\\":
            i += 1
        elif ch == ")" and stack:
            quote = stack.pop()
        i += 1
    return quote is not None


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
        if text.startswith("$(", i):
            depth += 1
            current.append("$(")
            i += 2
            continue
        if depth > 0 and ch == "(":
            depth += 1
        elif depth > 0 and ch == ")":
            depth -= 1
        elif ch in "()":  # a bare subshell or group: its commands are the text's own
            pieces.append("".join(current))
            current = []
            i += 1
            continue
        if depth == 0:
            operator = next((op for op in OPERATORS if text.startswith(op, i)), None)
            if operator == "&" and ((i > 0 and text[i - 1] in REDIRECT_BEFORE) or text.startswith("&>", i)):
                operator = None  # a redirection, not a background operator
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
    text = text.replace("\\\n", " ")  # a backslash-newline continues the line
    try:
        return shlex.split(text, posix=True)
    except ValueError:  # an unbalanced quote: examined as its whitespace-separated words, never dropped
        return text.split()


def _env_split_string(rest: list[str]) -> str | None:
    """The command `env -S` names — the flag as a token, attached (`-S'…'`), inside a cluster
    (`-iS`) or long (`--split-string`, `--split-string=`) — with the words env would append after
    it; None when env is not told to split a string."""
    i = 0
    while i < len(rest) and rest[i].startswith("-"):
        flag = rest[i]
        if flag in ("-S", "--split-string") and i + 1 < len(rest):
            return shlex.join([*_words(rest[i + 1]), *rest[i + 2 :]])
        if flag.startswith("--split-string="):
            return shlex.join([*_words(flag.split("=", 1)[1]), *rest[i + 1 :]])
        if not flag.startswith("--"):
            split_at = _split_letter(flag)
            if split_at is not None:
                attached = flag[split_at + 1 :]
                if attached:  # `-S'git push'`, `-iS'git push'`: the value is the rest of the token
                    return shlex.join([*_words(attached), *rest[i + 1 :]])
                if i + 1 < len(rest):  # `-iS 'git push'`: the value is the next token
                    return shlex.join([*_words(rest[i + 1]), *rest[i + 2 :]])
        i += 2 if _takes_next(flag, WRAPPERS["env"]) else 1
    return None


def _split_letter(flag: str) -> int | None:
    """The index of the `S` in a short cluster that is the split flag: the letters are read in
    order, and the first that takes a value — `-uSHELL` names a variable, not a split — ends the
    reading with the rest of the token as its value."""
    for index, letter in enumerate(flag[1:], 1):
        if letter == "S":
            return index
        if letter in ENV_VALUE_LETTERS:
            return None
    return None


def _drop_flags(rest: list[str], valued: frozenset[str]) -> None:
    """A wrapper's own flags, with the value of one that takes a value: `nice -n 5`, `env -i`,
    `sudo -iu root` — a cluster whose last letter takes a value takes the next word."""
    while rest and rest[0].startswith("-"):
        flag = rest.pop(0)
        if _takes_next(flag, valued) and rest:
            rest.pop(0)


def _takes_next(flag: str, valued: frozenset[str]) -> bool:
    """Whether the flag's value is the next word: a valued flag as a token, or a short cluster
    whose letters, read in order, reach a valued one last — `-iu` does, `-uSHELL` does not, its
    value being the rest of the token."""
    if flag in valued:
        return True
    if flag.startswith("--") or len(flag) < 3:  # `--` itself takes no word
        return False
    for index, letter in enumerate(flag[1:], 1):
        if "-" + letter in valued:
            return index == len(flag) - 1
    return False


def _is_shell_c(word: str) -> bool:
    """`-c`, or a short cluster ending in it: `bash -lc "…"`."""
    return word.startswith("-") and not word.startswith("--") and word.endswith("c")


def _normalise(words: list[str]) -> tuple[list[str], str | None]:
    """Strip assignments, shell words and wrappers, reduce the program to its base name, skip
    git's global options; a shell told to run a string hands that string back for its own split."""
    rest = list(words)
    while rest:
        head = rest[0].rsplit("/", 1)[-1]  # `/usr/bin/env` is `env`
        if ASSIGNMENT.match(rest[0]) or head in SHELL_WORDS:
            rest.pop(0)
        elif head in WRAPPERS:
            rest.pop(0)
            if head == "env":
                split = _env_split_string(rest)
                if (
                    split is not None
                ):  # `env -S "<command>" <more>`: the value and what follows are the command
                    return [], split
            _drop_flags(rest, WRAPPERS[head])
            for _ in range(WRAPPERS_WITH_VALUE.get(head, 0)):
                if rest:
                    rest.pop(0)
            while rest and ASSIGNMENT.match(rest[0]):  # `env FOO=1 cmd`
                rest.pop(0)
        else:
            break
    if not rest:
        return rest, None
    rest[0] = rest[0].rsplit("/", 1)[-1]
    if rest[0] in SHELLS:
        index = 1
        while index < len(rest):
            word = rest[index]
            if _is_shell_c(word) and index + 1 < len(rest):
                return rest, rest[index + 1]
            if not word.startswith(("-", "+")):
                break
            # `bash -o pipefail -c …`, `-eo pipefail`, `+o posix`, `-O extglob`: the option's value
            takes_value = not word.startswith("--") and word.endswith(("o", "O"))
            index += 2 if takes_value else 1
    if rest[0] == "git":
        i = 1
        while i < len(rest) and rest[i].startswith("-"):
            option = rest[i].split("=", 1)[0]
            i += 2 if option in GIT_GLOBAL_WITH_VALUE and "=" not in rest[i] else 1
        rest = [rest[0], *rest[i:]]
    return rest, None
