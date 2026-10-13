"""The shell command as the gate reads it. The platform splits a command into subcommands to
match its permission rules; this module repeats that split on the raw text so that a wrapper
or a subshell does not hide the program; the options between a program and its verb stay in the
words, and the entry's matching steps over them. Where the reader cannot split a text
cleanly it errs toward examining more — the text is one subcommand of its words; what it does
not see at all — a verb built from a variable, an `eval`, a heredoc fed to a shell, a quote
opened on an earlier line, a wrapper flag the lists it is given omit — is stated as its limit in the
module's document."""

from __future__ import annotations

import re
import shlex
from collections.abc import Sequence
from dataclasses import dataclass, field

from .model import ReaderLists, Subcommand, Wrapper

# The operators that separate simple commands, longest first so `||` is not read as two pipes.
OPERATORS = ("&&", "||", "|&", ";", "|", "&", "\n")
# Shell words that precede a command without being a program: stripped so the verb is read.
SHELL_WORDS = frozenset({"{", "}", "!", "if", "then", "else", "elif", "while", "until", "do", "fi", "done"})
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
# `>&`, `&>` and `<&` redirect; they are no separators.
REDIRECT_BEFORE = frozenset({">", "<"})


def split(command: str, lists: ReaderLists) -> list[Subcommand]:
    """Every simple command of the text, in order of appearance: the top-level ones, then the
    contents of each `$(…)` and backtick substitution, then the string a shell is told to run
    with its command options (`-c`, fish's `-C`) or that a wrapper's command option names (`env -S`)
    with the words after it, each split in turn. A heredoc's body is data and is dropped. The wrappers and
    the shells are those of `lists`."""
    found: list[Subcommand] = []
    _collect(_drop_heredocs(command), found, lists)
    return found


def reading(words: Sequence[str], lists: ReaderLists) -> list[str] | None:
    """The words as the gate reads a piece that starts with them: none left out, or the words that
    stay. None where the reading hands a string on to be split again, as `bash -c "…"` and `env -S "…"`
    do. The dials loader asks it of an entry's command: one this does not give back as written can
    never match."""
    rest, inner = _normalise(list(words), lists)
    return None if inner else rest


def _collect(text: str, found: list[Subcommand], lists: ReaderLists) -> None:
    for piece in _separate(text):
        stripped = piece.strip()
        if not stripped:
            continue
        for inner in _substitutions(stripped):
            _collect(inner, found, lists)
        words = _words(stripped)
        if not words:
            continue
        words, inner_commands = _normalise(words, lists)
        if words:  # empty: nothing but shell words or assignments, or a wrapper whose value is the command
            found.append(Subcommand(tuple(words), stripped))
        for inner_command in inner_commands:
            _collect(inner_command, found, lists)


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
    separator = _Separator(text)
    while separator.i < len(text):
        separator.step()
    separator.pieces.append("".join(separator.current))
    return separator.pieces


@dataclass(slots=True)
class _Separator:
    """The state of `_separate`: the pieces cut so far, the piece being read, the open quote, the
    depth of the open substitutions and the quote each open `$(` interrupted, restored at its `)`."""

    text: str
    i: int = 0
    pieces: list[str] = field(default_factory=list)
    current: list[str] = field(default_factory=list)
    quote: str | None = None
    depth: int = 0
    interrupted: list[str | None] = field(default_factory=list)

    def step(self) -> None:
        """Reads the character at `i` — two for a `$(` or an escape — and moves past it."""
        ch = self.text[self.i]
        if self.quote == '"' and self.text.startswith("$(", self.i):  # a substitution opens a new context
            self._open_substitution()
        elif self.quote:
            self._quoted(ch)
        elif ch in ("'", '"', "`"):
            self.quote = ch
            self._take(1)
        elif ch == "\\" and self.i + 1 < len(self.text):
            self._take(2)
        elif self.text.startswith("$(", self.i):
            self._open_substitution()
        else:
            self._unquoted(ch)

    def _open_substitution(self) -> None:
        """A `$(` opens a substitution, interrupting the open quote, if any."""
        self.current.append("$(")
        self.interrupted.append(self.quote)
        self.quote = None
        self.depth += 1
        self.i += 2

    def _quoted(self, ch: str) -> None:
        """A character inside a quote: an escape in double quotes takes the next one with it, the
        quote's own character closes it."""
        if ch == "\\" and self.quote == '"' and self.i + 1 < len(self.text):
            self._take(2)
            return
        if ch == self.quote:
            self.quote = None
        self._take(1)

    def _unquoted(self, ch: str) -> None:
        """A character outside quotes: a parenthesis inside a substitution is counted, a bare one
        cuts the piece — a subshell's or a group's commands are the text's own — and an operator
        outside substitutions cuts it."""
        if self.depth > 0 and ch == "(":
            self.depth += 1
            self.interrupted.append(None)
        elif self.depth > 0 and ch == ")":
            self.depth -= 1
            self.quote = self.interrupted.pop() if self.interrupted else None
        elif ch in "()":
            self._cut(1)
            return
        operator = self._operator() if self.depth == 0 else None
        if operator is not None:
            self._cut(len(operator))
            return
        self._take(1)

    def _operator(self) -> str | None:
        """The operator that starts at `i`, or None; `>&`, `&>` and `<&` are redirections."""
        operator = next((op for op in OPERATORS if self.text.startswith(op, self.i)), None)
        if operator == "&" and (
            (self.i > 0 and self.text[self.i - 1] in REDIRECT_BEFORE) or self.text.startswith("&>", self.i)
        ):
            return None  # a redirection, not a background operator
        return operator

    def _take(self, size: int) -> None:
        """The next `size` characters join the piece being read."""
        self.current.append(self.text[self.i : self.i + size])
        self.i += size

    def _cut(self, size: int) -> None:
        """The piece being read ends; the `size` characters that end it belong to no piece."""
        self.pieces.append("".join(self.current))
        self.current = []
        self.i += size


def _substitutions(text: str) -> list[str]:
    """The contents of every `$(…)` and every backtick pair, outermost first."""
    inner: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("$(", i):
            j = _substitution_end(text, i + 2)
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


def _substitution_end(text: str, j: int) -> int:
    """Where the `$(` whose contents start at `j` ends: just past its `)`, or at the text's end. A
    quoted `)` closes nothing; a nested `$(`, unquoted or in a string, or a `(`, opens a level."""
    depth = 1
    quote: str | None = None
    opened: list[str | None] = []  # the quote each nested `$(` interrupted
    while j < len(text) and depth:
        ch = text[j]
        if quote != "'" and text.startswith("$(", j):  # a nested substitution, counted once
            opened.append(quote)
            quote = None
            depth += 1
            j += 2
            continue
        if quote:  # a quoted `)` closes nothing
            if ch == "\\" and quote == '"':
                j += 1
            elif ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
        elif ch == "(":
            depth += 1
            opened.append(None)
        elif ch == ")":
            depth -= 1
            if depth:
                quote = opened.pop() if opened else None
        j += 1
    return j


def _words(text: str) -> list[str]:
    text = text.replace("\\\n", " ")  # a backslash-newline continues the line
    try:
        return shlex.split(text, posix=True)
    except ValueError:  # an unbalanced quote: examined as its whitespace-separated words, never dropped
        return text.split()


def _normalise(words: list[str], lists: ReaderLists) -> tuple[list[str], list[str]]:
    """Strip assignments, shell words and wrappers, reduce the program to its base name, and leave
    every option after the program in the words; a shell told to run strings hands back each, in the
    order they stand, and a wrapper whose option names one hands back that one, each for its own
    split. The list is empty when no string is handed on."""
    rest = list(words)
    while rest:
        head = rest[0].rsplit("/", 1)[-1]  # `/usr/bin/env` is `env`
        if ASSIGNMENT.match(rest[0]) or head in SHELL_WORDS:
            rest.pop(0)
            continue
        wrapper = _wrapper(rest, lists.wrappers)
        if wrapper is None:
            break
        del rest[: len(wrapper.command)]
        string = _after_wrapper(wrapper, rest)
        if string is not None:  # `env -S "<command>" <more>`: the value and what follows are the command
            return [], [string]
    if not rest:
        return rest, []
    rest[0] = rest[0].rsplit("/", 1)[-1]
    shell = next((shell for shell in lists.shells if shell.command == rest[0]), None)
    if shell is None:
        return rest, []
    arguments = rest[1:]
    # the words after the strings are the shell's arguments: not read
    return rest, _shell_strings(arguments, shell.with_value, shell.command_flags)


def _wrapper(rest: list[str], wrappers: tuple[Wrapper, ...]) -> Wrapper | None:
    """The wrapper the words start with, the longest of its words when several match: the base
    name of the first word is the wrapper's first, and the words after it are the wrapper's own."""
    head = rest[0].rsplit("/", 1)[-1]
    found: Wrapper | None = None
    for wrapper in wrappers:
        size = len(wrapper.command)
        if (
            wrapper.command[0] == head
            and tuple(rest[1:size]) == wrapper.command[1:]
            and (found is None or size > len(found.command))
        ):
            found = wrapper
    return found


def _after_wrapper(wrapper: Wrapper, rest: list[str]) -> str | None:
    """Take a wrapper's own words off the front of `rest`, its name already gone: its options, then
    its plain positional words, then the words that are numbers, then a command option that stands
    after them, then assignments. A command string, with the words that follow it appended, is
    handed back whole."""
    string = _options(rest, wrapper.with_value, wrapper.command_flags, ("-",))
    if string is None:
        del rest[: wrapper.positionals]
        for _ in range(wrapper.numbers):
            if not rest or not (rest[0].isascii() and rest[0].isdigit()):
                break
            rest.pop(0)
        if rest and rest[0] in wrapper.command_flags:
            string = _option(rest.pop(0), rest, wrapper.with_value, wrapper.command_flags)
    if string is not None:
        return shlex.join([*_words(string), *rest])
    while rest and ASSIGNMENT.match(rest[0]):  # `env FOO=1 cmd`
        rest.pop(0)
    return None


def _options(
    rest: list[str], with_value: tuple[str, ...], command_flags: tuple[str, ...], starts: tuple[str, ...]
) -> str | None:
    """Take the options off the front of `rest`: the words that start as `starts` say, `--` the
    last of them. The command string of a command option, if one is met, is handed back and the
    reading ends there."""
    while rest and rest[0].startswith(starts):
        word = rest.pop(0)
        if word == "--":
            return None
        string = _option(word, rest, with_value, command_flags)
        if string is not None:
            return string
    return None


def _shell_strings(rest: list[str], with_value: tuple[str, ...], command_flags: tuple[str, ...]) -> list[str]:
    """The command strings of a shell, in the order they stand, `rest` being the words after its name. The
    options are walked as a shell reads them: a word that starts with `-` or `+`, `--` the last of them, a
    short cluster read letter by letter, where a wrapper's cluster ends at its first valued letter
    (`_option`). Shells differ on a valued letter that is not the cluster's last: bash gives it the next
    word, whatever its place (`-oe pipefail`); zsh and ksh, the cluster's command-flag letters taken out
    first, give the first valued letter left the letters after it (`-oerrexit`). Where the reader cannot
    tell which shell runs the text it errs toward examining more: the words are walked both ways, and the
    strings are those either walk finds, each read once. Every command flag met yields a string: its
    attached value (`--command=x`), else the next word when that is not an option and is no other option's
    value, else the first operand after the options. A word taken as a string is taken off `rest`, so the
    one string of `bash -c "…"` is the next word and never the operand as well, and several command flags
    that found no word share the one operand. The walk goes on after a string (`fish -C "…" -c "…"` has
    two); the words after it end are arguments, not read, and with no command flag the first operand is a
    script file and nothing is read."""
    bash = _walk_shell(list(rest), with_value, command_flags, True)
    seen = {string for _, string in bash}
    for place, string in _walk_shell(list(rest), with_value, command_flags, False):
        if string not in seen:
            seen.add(string)
            bash.append((place, string))
    return [string for _, string in sorted(bash, key=lambda one: one[0])]


def _walk_shell(
    rest: list[str], with_value: tuple[str, ...], command_flags: tuple[str, ...], next_word: bool
) -> list[tuple[int, str]]:
    """One walk of `_shell_strings`, its strings as (place, string); `next_word` says a valued letter
    takes the next word whatever its place in a cluster (bash's), else, the cluster's command-flag
    letters taken out first, the first valued letter left takes the letters after it, or the next word
    when none follow (zsh's and ksh's); the command flags of the cluster stand in either case."""
    total = len(rest)
    strings: list[tuple[int, str]] = []
    waiting = False  # a command flag found no next word: the first operand after the options is its string
    while rest and rest[0].startswith(("-", "+")):
        place = total - len(rest)
        word = rest.pop(0)
        if word == "--":
            break
        wants = False
        if word.startswith("--"):
            name, equals, attached = word.partition("=")
            if name in command_flags:
                if equals:
                    strings.append((place, attached))
                else:
                    wants = True
            else:
                _option(word, rest, with_value, ())
        else:
            wants = _cluster(word, rest, with_value, command_flags, next_word)
        if wants:
            if rest and not rest[0].startswith(("-", "+")):
                strings.append((total - len(rest), rest.pop(0)))
            else:
                waiting = True
    if waiting and rest:
        strings.append((total - len(rest), rest.pop(0)))
    return strings


def _cluster(
    word: str, rest: list[str], with_value: tuple[str, ...], command_flags: tuple[str, ...], next_word: bool
) -> bool:
    """Whether a shell's short cluster holds a command flag; the words its valued letters take are
    taken off `rest` as one walk of `_walk_shell` reads them, `next_word` saying which."""
    if not next_word:
        letters = "".join(letter for letter in word[1:] if word[0] + letter not in command_flags)
        _option(word[0] + letters, rest, with_value, ())  # its valued letter takes the rest, else a word
        return len(letters) < len(word) - 1
    wants = False
    for letter in word[1:]:  # every valued letter takes the next word, whatever its place
        flag = word[0] + letter
        if flag in command_flags:
            wants = True
        elif flag in with_value and rest:
            rest.pop(0)
    return wants


def _option(
    word: str, rest: list[str], with_value: tuple[str, ...], command_flags: tuple[str, ...]
) -> str | None:
    """One option, already taken off `rest`, with its value: the next word of `rest`, taken too,
    unless the value is attached. Unknown options take none. A long word `--name=value` is one word.
    A short word's letters are read in order, and the first whose `-x` or `+x` is a known option ends
    the reading, its value the rest of the word, else the next word — `-uSHELL` names a variable,
    `-iu SHELL` is a flag and an option with its value. The value of a command option is its command
    string, handed back; None for every other option. A shell's long options go through it with no
    command flags, its short clusters and command flags are read by `_shell_strings`."""
    if word.startswith("--"):
        name, equals, attached = word.partition("=")
        if name in command_flags:
            return attached if equals else _value(rest)
        if name in with_value and not equals and rest:
            rest.pop(0)
        return None
    for index, letter in enumerate(word[1:], 1):
        flag = word[0] + letter
        if flag in command_flags:
            return word[index + 1 :] or _value(rest)
        if flag in with_value:
            if index + 1 == len(word) and rest:
                rest.pop(0)
            return None
    return None


def _value(rest: list[str]) -> str | None:
    """The next word, taken, as the value of a wrapper's command option; a `--` before it is skipped,
    when a word follows it: `flock -c -- "…"`."""
    if len(rest) > 1 and rest[0] == "--":
        rest.pop(0)
    return rest.pop(0) if rest else None
