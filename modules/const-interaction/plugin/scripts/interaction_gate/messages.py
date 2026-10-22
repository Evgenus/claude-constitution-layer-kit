"""The texts of this module's own findings, green lines, count lines, session-start lines and
dial failures, as functions with typed parameters; the texts every gate shares live in the
shared package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists
(one clause), and the exact fix; a configuration failure is one self-sufficient line. Every
function name starts with the stable key of its text (d1_, l1_, g1_, f9_, z1_, c5_, c12_), so a
text can be cited, reviewed and asserted by key. A reader must be able to act on a message
without holding any other document: no text here cites one.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from constitution_layer_kit import identity
from constitution_layer_kit.messages import echoed, escaped
from constitution_layer_kit.model import Broken, Finding, SharedKey

from .model import COMMAND_FLAG, Entry, Key, OptionFault, ReaderDial, ReaderField, Subcommand, Verbosity


def _ns() -> str:
    return identity.current().namespace


def _file() -> str:
    return identity.dials_file()


# ---------------------------------------------------------------- the findings


def d1_destructive(entry: Entry, subcommand: Subcommand, matched: str) -> Finding:
    what = f"'{echoed(subcommand.text)}' matches the entry {echoed(' '.join(entry.command))}"
    if matched:
        what += f" with {echoed(matched)}"
    return Finding(
        Key.D1,
        f"destructive command: {what}",
        escaped(entry.teach),
        f"{escaped(entry.alternative)}; to run it as written, confirm at the prompt — where no prompt can be"
        " shown, get the user's yes in chat and run it again, one yes per command; to stop gating it,"
        f" remove the entry from {_ns()}.destructive in {_file()}",
    )


def l1_list_item(rel: str, line: int, text: str) -> Finding:
    return Finding(
        Key.L1,
        f"{escaped(rel)}:{line}: list item without a handle — {echoed(text)}",
        "an item with no stable handle cannot be cited without quoting it, so a reader cannot point at one",
        "open the item with a handle — a number, a letter or a short key such as R1 or Q-a — or add the"
        f" form the document uses to {_ns()}.handles in {_file()}, or take the document out of"
        f" {_ns()}.territories by a negated pattern",
    )


# ---------------------------------------------------------------- green, skip, count


def g1_command_passed(entries: int, subcommands: int) -> str:
    """The whole green line of the shell gate: what it examined and against what."""
    return f"1 command examined: {subcommands} subcommand(s) against {entries} entries, none matched"


def g1_nothing_gated() -> str:
    return f"1 command examined against 0 entries — {_ns()}.destructive is empty, nothing is gated"


def g1_skip_no_command() -> str:
    return f"no command given: run the scan with {COMMAND_FLAG} '<text>' to see what the dial does to it"


def f9_count_command(findings: int, subcommands: int) -> str:
    return f"RED: {findings} finding(s) — 1 command examined ({subcommands} subcommand(s))"


def f9_command_tail(entries: int, subcommands: int) -> str:
    return f"1 command examined: {subcommands} subcommand(s) against {entries} entries"


def f9_lists_tail(documents: int, handles: int, scanned: int) -> str:
    return (
        f"{documents} document(s) examined for lists with {handles} handle form(s),"
        f" {scanned} Markdown file(s) scanned"
    )


# ---------------------------------------------------------------- session start: the visible zero (Z1)


def z1_empty() -> str:
    return f"{_ns()}: no command is gated — {_ns()}.destructive is an empty list in {_file()}"


def z1_dropped(dial: ReaderDial, command: Sequence[str]) -> str:
    """One default the dials dropped, said at every session start: which, what the gate no longer
    examines, and where it is set."""
    kind = "wrapper" if dial is ReaderDial.WRAPPERS else "shell"
    behind = "a command behind it" if dial is ReaderDial.WRAPPERS else "a command it is told to run"
    return (
        f"{_ns()}: the {kind} {escaped(' '.join(command))} is dropped, so {behind} is no longer examined —"
        f" {_ns()}.{dial} in {_file()} drops it"
    )


def z1_replaced(dial: ReaderDial, command: Sequence[str]) -> str:
    """One default the dials replaced, said at every session start: which, what its options now are,
    and where it is set."""
    kind = "wrapper" if dial is ReaderDial.WRAPPERS else "shell"
    return (
        f"{_ns()}: the {kind} {escaped(' '.join(command))} is replaced, so its options are those written for"
        f" it, not the defaults — {_ns()}.{dial} in {_file()} replaces it"
    )


def z1_no_dials(root: str) -> str:
    return (
        f"{_ns()}: no {_file()} in {escaped(root)} — the destructive-command gate examines nothing there"
        " until the file exists (an empty mapping, {}, is enough for the default list)"
    )


def z1_no_repo(cwd: str) -> str:
    return (
        f"{_ns()}: {escaped(cwd)} is not inside a git repository — the destructive-command gate examines"
        " nothing there"
    )


def z1_prefix() -> str:
    return _ns()


def z1_could_not_run() -> str:
    return "BROKEN: the session-start line could not be printed — the gate's state is unknown"


def z1_verbosity(value: Verbosity) -> str:
    return (
        f"{_ns()}: verbosity is {value.value} — the assumption block and the restatement appear only when"
        " triggered, never as an empty ritual"
    )


def z1_pair(number: int, violates: str, complies: str) -> str:
    """One boundary example: the content of the line is the example, so it stands whole, escaped."""
    return f"{number}. {escaped(violates)} / {escaped(complies)}"


def z1_pairs_heading() -> str:
    return f"Boundary examples of this project ({_ns()}.boundary_examples), each violates / complies:"


# ---------------------------------------------------------------- this module's dial failures (C5)


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{_file()}: {detail}", fix)


def c5_territories() -> Broken:
    return _c5(
        f"{_ns()}.territories must be a non-empty list of path patterns",
        'write the patterns of the documents to scan for lists, one per line under "- ", or leave the key'
        " out to cover every Markdown file; an empty list would examine nothing in silence",
    )


def c5_handles() -> Broken:
    return _c5(
        f"{_ns()}.handles must be a non-empty list of regular expressions",
        'write the handle forms a list item may open with, one per line under "- " in single quotes, or'
        " leave the key out for the defaults; an empty list would find every list red",
    )


def c5_handle_pattern(pattern: str, error: str) -> Broken:
    return _c5(
        f"{_ns()}.handles holds '{echoed(pattern)}', which is not a regular expression ({escaped(error)})",
        "repair the pattern; Python's re syntax, matched at the start of the item's text",
    )


def c5_destructive() -> Broken:
    return _c5(
        f"{_ns()}.destructive must be a list of entries",
        'write one entry per "- " item with the fields command (a list of words), flags (a list, optional),'
        " teach and alternative (texts); leave the key out for the default list; an empty list gates"
        " nothing and says so at session start",
    )


def c5_entry(index: int, detail: str) -> Broken:
    return _c5(
        f"{_ns()}.destructive entry {index}: {detail}",
        "write the entry as command: [<words>], flags: [<flags>] (optional), teach: <why the act is hard to"
        " reverse>, alternative: <the reversible way>",
    )


def _words(words: Sequence[str], echo: Callable[[str], str]) -> str:
    return "[" + ", ".join(echo(word) for word in words) + "]"


def _read_as(read: Sequence[str] | None) -> str:
    """What the gate does with the words of an entry: `read` is None where they hand a string on to be
    split again."""
    if read is None:
        return "has no reading, since it hands a string on to be split again"
    if not read or "" in read:  # nothing, or an empty word, as `x/` reduces to: no command to write back
        return "is read by the gate as nothing"
    return f"is read by the gate as {_words(read, echoed)}"


def c5_entry_unread(index: int, command: Sequence[str], read: Sequence[str] | None) -> Broken:
    """An entry whose words the reader does not read as themselves: it is compared by its reading,
    so it could never match. `read` is None where the words hand a string on to be split again."""
    never = "the gate compares the reading, so this entry can never match"
    if read is None:
        fix = f"write the command the shell runs instead, such as command: [rm]; {never}"
    elif not read or "" in read:
        fix = f"write the command the wrapper or shell runs instead, such as command: [rm]; {never}"
    else:
        fix = f"write command: {_words(read, escaped)}; {never}"
    detail = f"command {_words(command, echoed)} {_read_as(read)}"
    return _c5(f"{_ns()}.destructive entry {index}: {detail}", fix)


def c5_default_unread(command: Sequence[str], read: Sequence[str] | None) -> Broken:
    """A default entry that the reader dials make the gate read as something else, so that with the key
    absent it would never match. `command` is the default's own words, `read` its reading."""
    ns = _ns()
    return _c5(
        f"{ns}.destructive is absent, so its default entry, command {_words(command, echoed)},"
        f" {_read_as(read)}, which the lists of {ns}.wrappers and {ns}.shells cause",
        f"remove or change the entry of {ns}.wrappers or {ns}.shells whose command starts with"
        f" '{escaped(command[0])}', or write {ns}.destructive out with commands the gate reads as written;"
        " the gate compares the reading, so the default entry would never match",
    )


def c5_verbosity() -> Broken:
    return _c5(
        f"{_ns()}.verbosity must be one of: {', '.join(level.value for level in Verbosity)}",
        "write verbosity: triggered — the one value today: assumption and restatement lines appear only"
        " when triggered — or leave the key out for it",
    )


def c5_boundary_examples() -> Broken:
    return _c5(
        f"{_ns()}.boundary_examples must be a list of pairs {{violates: <text>, complies: <text>}}",
        'write one pair per "- " item with exactly those two fields, or leave the key out',
    )


# ---------------------------------------------------------------- the dials of the reader (C5)

_SHAPES = {
    ReaderDial.WRAPPERS: "command: [<words>] and, all optional, with_value: [<options>],"
    " positionals: <count>, numbers: <count>, command_flags: [<options>]; or as command: [<words>] with"
    " drop: true to remove a default",
    ReaderDial.SHELLS: "command: [<word>] and, all optional, with_value: [<options>],"
    " command_flags: [<options>]; or as command: [<word>] with drop: true to remove a default",
}
_FIELDS = {
    ReaderDial.WRAPPERS: "command, with_value, positionals, numbers, command_flags or drop",
    ReaderDial.SHELLS: "command, with_value, command_flags or drop",
}
_KINDS = {ReaderDial.WRAPPERS: "wrapper", ReaderDial.SHELLS: "shell"}
_OPTION_EXAMPLES = {ReaderDial.WRAPPERS: "-u or --user", ReaderDial.SHELLS: "-o, +o or --rcfile"}
_BASE_NAME = (
    "a program is read by its base name, so a first word with a '/' can never match, and a word with white"
    " space is two words"
)


def _reader(dial: ReaderDial, index: int, detail: str, fix: str) -> Broken:
    return _c5(f"{_ns()}.{dial} entry {index}: {detail}", fix)


def c5_reader_list(dial: ReaderDial) -> Broken:
    return _c5(
        f"{_ns()}.{dial} must be a list of entries",
        f'write one entry per "- " item as {_SHAPES[dial]}; leave the key out for the defaults, an empty'
        " list leaves them as they are",
    )


def c5_reader_entry(dial: ReaderDial, index: int, detail: str) -> Broken:
    return _reader(dial, index, detail, f"write the entry as {_SHAPES[dial]}")


def c5_reader_unknown(dial: ReaderDial, index: int, field: str) -> Broken:
    return _reader(
        dial,
        index,
        f"'{echoed(field)}' is no field of a {_KINDS[dial]} entry",
        f"a misspelt field would be ignored in silence, so none is: write {_FIELDS[dial]}",
    )


def c5_reader_command(dial: ReaderDial, index: int) -> Broken:
    if dial is ReaderDial.WRAPPERS:
        detail = (
            "command must be a non-empty list of words, none empty, none holding white space, the first with"
            " no '/'"
        )
        fix = "write the words of the program as list items, such as command: [uv, run]"
    else:
        detail = "command must be a list of one word, not empty, holding no white space and no '/'"
        fix = "write the shell's name as the one item, such as command: [fish]"
    return _reader(dial, index, detail, f"{fix}; {_BASE_NAME}")


def c5_reader_shell_words(index: int, command: Sequence[str]) -> Broken:
    return _reader(
        ReaderDial.SHELLS,
        index,
        f"command {_words(command, echoed)} has more than one word, and a shell is one word",
        "write one entry for each shell, command: [<word>]",
    )


def c5_reader_first_word(dial: ReaderDial, index: int, word: str) -> Broken:
    kind = _KINDS[dial]
    named = (
        "the program that runs the command"
        if dial is ReaderDial.WRAPPERS
        else "the program that runs the string"
    )
    return _reader(
        dial,
        index,
        f"command starts with '{echoed(word)}', which is a shell word or an assignment, and the reader takes"
        f" both off before it looks for a {kind}, so the entry can never match",
        f"remove the entry; a {kind} is named by {named}",
    )


def c5_reader_no_flags(index: int, word: str) -> Broken:
    return _reader(
        ReaderDial.SHELLS,
        index,
        f"the shell '{echoed(word)}' has no command_flags, so it reads no string, since only a command flag"
        " tells the reader that the first operand is one",
        "give the shell its command flag, such as command_flags: [-c], or remove the entry; a default shell"
        f" is removed by an entry with command: [{escaped(word)}] and drop: true",
    )


def c5_reader_both_fields(dial: ReaderDial, index: int, option: str) -> Broken:
    return _reader(
        dial,
        index,
        f"with_value and command_flags both hold '{echoed(option)}', and the reader tries command_flags"
        " first, so its place in with_value is never used",
        "keep it in one of the two, in command_flags if its value is a command to read, in with_value if not",
    )


def c5_reader_option(
    dial: ReaderDial, index: int, field: ReaderField, option: str, fault: OptionFault
) -> Broken:
    """An option the reader could never match, and the reason: `option` is what the dials gave."""
    example = _OPTION_EXAMPLES[dial]
    if fault is OptionFault.NOT_A_LIST:
        return _reader(
            dial,
            index,
            f"{field} must be a list of options",
            "write the options as list items, each as the command line has it, such as"
            f" {example}; to take none, leave the field out",
        )
    holds = f"{field} holds '{echoed(option)}'"
    if fault is OptionFault.WHITE_SPACE:
        return _reader(
            dial,
            index,
            f"{holds}, which holds white space, and an option is one word of the command line",
            f"write each option as an item of its own, such as {example}",
        )
    if fault is OptionFault.NO_SIGN:
        if dial is ReaderDial.WRAPPERS:
            return _reader(
                dial,
                index,
                f"{holds}, which does not start with '-', so it is no option",
                f"write it as the command line has it, with its dash, such as {example}",
            )
        return _reader(
            dial,
            index,
            f"{holds}, which starts with neither '-' nor '+', so it is no option",
            f"write it as the command line has it, with its sign, such as {example}",
        )
    if fault is OptionFault.LONE_SIGN:
        return _reader(
            dial,
            index,
            f"{holds}, which is no option, a lone sign naming nothing",
            "remove it; the reader already ends a program's options at '--'",
        )
    never = "which the reader never matches, since it"
    if fault is OptionFault.LETTERS:
        each, none = (
            ("each letter that takes a value", "a letter that takes none")
            if field is ReaderField.WITH_VALUE
            else ("each letter that is a command flag", "any other letter")
        )
        return _reader(
            dial,
            index,
            f"{holds}, a short option of more than one letter, {never} reads a short cluster one letter at"
            " a time",
            f"write as an option of its own, as '{option[0]}<letter>', {each}; {none} needs no entry; a long"
            " option is written --name",
        )
    return _reader(
        dial,
        index,
        f"{holds}, {never} compares a long option by its name before the '='",
        f"write '{escaped(option.partition('=')[0])}'",
    )


def c5_reader_count(dial: ReaderDial, index: int, field: ReaderField) -> Broken:
    return _reader(
        dial,
        index,
        f"{field} must be a whole number of words, 0 or more, and true and false are no number",
        f"write {field}: 1, or another whole number, or leave the field out for 0",
    )


def c5_reader_drop_value(dial: ReaderDial, index: int) -> Broken:
    return _reader(
        dial,
        index,
        "drop must be true, its one value",
        "write drop: true beside command to remove the default of that command, or leave the field out",
    )


def c5_reader_drop_beside(dial: ReaderDial, index: int, field: ReaderField) -> Broken:
    return _reader(
        dial,
        index,
        f"drop: true stands with command alone, and {field} stands beside it, which would be ignored in"
        " silence",
        f"remove {field} to drop the default, or remove drop to replace the default with the fields",
    )


def c5_reader_drop_unknown(
    dial: ReaderDial, index: int, command: Sequence[str], defaults: Sequence[str]
) -> Broken:
    return _reader(
        dial,
        index,
        f"drop names {_words(command, echoed)}, which is no default {_KINDS[dial]}, and a misspelt name would"
        " drop nothing in silence",
        f"write the command of a default {_KINDS[dial]} ({', '.join(defaults)}) or remove the entry",
    )


def c5_reader_twice(dial: ReaderDial, index: int, command: Sequence[str], first: int) -> Broken:
    return _reader(
        dial,
        index,
        f"command {_words(command, echoed)} stands in entry {first} already, and two entries of one command"
        " would leave one of them unread in silence",
        "keep one entry per command, with every field it needs; entries of one command are never merged",
    )


def c5_reader_both(word: str) -> Broken:
    return _c5(
        f"{_ns()}.wrappers and {_ns()}.shells both name '{echoed(word)}', and a word is a wrapper or a shell,"
        " never both: the reader strips a wrapper before it reads a shell",
        "give it to one of the two dials: remove its entry from the other, where a default is removed by an"
        f" entry with command: [{escaped(word)}] and drop: true",
    )


# ---------------------------------------------------------------- this module's own C12


def c12_event(name: str, tool: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"hook input names the event '{echoed(name)}' on tool '{echoed(tool)}', which this gate is not wired"
        " to",
        "wire the gate to PreToolUse with the matcher Bash, as the plugin's hooks file does; to see what"
        f" the dial does to a command by hand run it with --scan {COMMAND_FLAG} '<text>'",
    )


def c12_lists_hook() -> Broken:
    return Broken(
        SharedKey.C12,
        "this check has no hook mode: it scans a tree and judges no single write",
        "run it with --scan [<dir>]; the plugin wires it to no event",
    )
