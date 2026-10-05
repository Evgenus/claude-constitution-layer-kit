"""The texts of this module's own findings, notes, count lines, skip reasons and configuration
failures, as functions with typed parameters; the texts every gate shares live in the shared
package's messages module.

Error messages are a teaching surface: a finding states what failed, why the rule exists (one
clause), and the exact fix; a configuration failure is one self-sufficient line. Every function
name starts with the stable key of its text (l1_ to l6_, n2_, f9_, g1_, c2_, c5_, c12_), so a text
can be cited, reviewed and asserted by key. A reader must be able to act on a message without
holding any other document: no text here cites one.
"""

from __future__ import annotations

from const_gate import identity
from const_gate.messages import echoed, escaped
from const_gate.model import DIALS_FILE, Broken, Finding, SharedKey

from .model import VALE_FLOOR, Departure, Hit, Key, Level, Rule

INSTALL = "brew install vale (macOS, Linuxbrew), or the other routes at https://vale.sh/docs/install"


def _ns() -> str:
    return identity.current().namespace


def _floor() -> str:
    return ".".join(str(n) for n in VALE_FLOOR)


def _allow(rule: Rule) -> str:
    """The closing clause of a fix: how a document that must stand as it is written is declared."""
    return (
        f"; for a document that must stand as written, declare the departure with its reason: add to"
        f" {_ns()}.departures in {DIALS_FILE} an entry {{paths: [<the file, or a pattern of the documents"
        f" that stand>], allow: [{rule.value}], reason: <why they stand, in one line>}}"
    )


# ---------------------------------------------------------------- the findings


def finding(rel: str, hit: Hit, dials_grade: float, dials_words: int) -> Finding:
    """The finding of a hit, by its rule, for a rule at level error."""
    if hit.rule is Rule.GRADE:
        return l1_grade(rel, float(hit.message), dials_grade)
    if hit.rule is Rule.SENTENCE:
        return l2_sentence(rel, hit.line, int(float(hit.message)), dials_words, hit.match)
    if hit.rule is Rule.FORBIDDEN:
        return l3_forbidden(rel, hit.line, hit.match)
    if hit.rule is Rule.SIMPLER:
        return l4_simpler(rel, hit.line, hit.match, hit.message)
    return l5_passive(rel, hit.line, hit.match)


def l1_grade(rel: str, grade: float, ceiling: float) -> Finding:
    return Finding(
        Key.L1,
        f"{escaped(rel)}:1: the document reads at grade {grade:g} by Flesch–Kincaid, above the ceiling of"
        f" {ceiling:g}",
        "a reader whose first language is not English pays for every year of schooling the prose assumes,"
        " and the grade rises with words per sentence and syllables per word",
        "split the long sentences and prefer short words in the prose outside headings, code and tables"
        f" until the grade is at or under {ceiling:g}; the ceiling for this repository is"
        f" {_ns()}.grade_ceiling in {DIALS_FILE}" + _allow(Rule.GRADE),
    )


def l2_sentence(rel: str, line: int, words: int, limit: int, text: str) -> Finding:
    return Finding(
        Key.L2,
        f"{escaped(rel)}:{line}: a sentence of {words} words, over the limit of {limit} — {echoed(text)}",
        "a sentence longer than the limit carries more than one idea, and a non-native reader loses the"
        " first before reaching the last",
        f"split it at a clause into sentences of at most {limit} words; the limit for this repository is"
        f" {_ns()}.sentence_words in {DIALS_FILE}" + _allow(Rule.SENTENCE),
    )


def l3_forbidden(rel: str, line: int, text: str) -> Finding:
    return Finding(
        Key.L3,
        f"{escaped(rel)}:{line}: '{echoed(text)}' is a construction plain language avoids",
        "an idiom or a formal phrase says nothing a plain sentence does not, and a non-native reader must"
        " translate it before reading on",
        "say it in plain words, or drop it; a phrase this repository keeps on purpose is named in"
        f" {_ns()}.exceptions in {DIALS_FILE}" + _allow(Rule.FORBIDDEN),
    )


def l4_simpler(rel: str, line: int, text: str, plain: str) -> Finding:
    return Finding(
        Key.L4,
        f"{escaped(rel)}:{line}: '{echoed(text)}' where the plain word is '{echoed(plain)}'",
        "a long or formal word costs a non-native reader a dictionary where the plain one does not",
        f"write '{escaped(plain)}'; a word this repository keeps on purpose is named in {_ns()}.exceptions in"
        f" {DIALS_FILE}" + _allow(Rule.SIMPLER),
    )


def l5_passive(rel: str, line: int, text: str) -> Finding:
    return Finding(
        Key.L5,
        f"{escaped(rel)}:{line}: passive voice — '{echoed(text)}'",
        "the passive hides who acts, and a non-native reader must supply the actor to follow the sentence",
        "name who acts and put them first; a passive kept on purpose is a register the repository sets by"
        f" {_ns()}.levels.passive in {DIALS_FILE}" + _allow(Rule.PASSIVE),
    )


def l6_vale_comment(rel: str, line: int, text: str) -> Finding:
    return Finding(
        Key.L6,
        f"{escaped(rel)}:{line}: a Vale comment in the document — {echoed(text)}",
        "a comment that switches a rule off is a mark in the document, which the gate blanks before it"
        " reads; what departs from a rule is declared in the dials file, where every reader sees it",
        "remove the comment; to change a rule for this repository set its level or threshold under"
        f" {_ns()} in {DIALS_FILE}, or, for a document that must stand as written, declare the departure"
        f" with its reason in {_ns()}.departures there",
    )


# ---------------------------------------------------------------- notes: a rule at warning


def n2_warning(rel: str, rule: Rule, found: Finding) -> str:
    """A hit of a rule at level warning: the finding's first line as a note, not red."""
    return (
        f"note: {found.headline} — reported, not red, while {_ns()}.levels.{rule.value} is"
        f" {Level.WARNING.value}"
    )


def n3_stale_departure(index: int, departure: Departure) -> str:
    return (
        f"note: {_ns()}.departures entry {index} ({echoed(', '.join(departure.paths))}) matches no covered"
        " document; the documents it allowed were deleted or moved, or the pattern is wrong"
    )


# ---------------------------------------------------------------- count lines and skips


def f9_tail(documents: int, ceiling: float, words: int, departures: int, scanned: int) -> str:
    return (
        f"{documents} document(s) examined under a grade ceiling of {ceiling:g} and {words} words per"
        f" sentence and {departures} departure(s), {scanned} Markdown file(s) scanned"
    )


def f9_cut(findings: int, shown_first: int, rel: str) -> str:
    """The count line of a hook run whose findings did not all fit: the first so many are shown."""
    return (
        f"RED: {findings} finding(s), the first {shown_first} shown — the scan lists them all"
        f" — 1 document examined ({escaped(rel)})"
    )


def g1_covered() -> str:
    return f"covered by {_ns()}.territories"


def g1_skip_not_covered(rel: str) -> str:
    return f"{escaped(rel)} is not covered ({_ns()}.territories)"


# ---------------------------------------------------------------- the binary (C2, C12)


def c2_vale_missing() -> Broken:
    return Broken(
        SharedKey.C2,
        f"{_ns()} needs vale {_floor()} or newer on PATH",
        f"{INSTALL} — {identity.current().until_installed}",
    )


def c2_vale_too_old(found: str) -> Broken:
    return Broken(
        SharedKey.C2,
        f"{_ns()} needs vale {_floor()} or newer, found {found}",
        f"upgrade it: {INSTALL} — {identity.current().until_installed}",
    )


def c12_vale_version(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"vale did not report its version ({escaped(detail)})",
        f"run vale --version by hand and repair the installation — {identity.current().until_installed}",
    )


def c12_vale_version_exit(code: int, detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"vale --version failed (exit {code}: {escaped(detail)})",
        f"run vale --version by hand and repair the installation — {identity.current().until_installed}",
    )


def c12_vale_failed(detail: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"vale could not run: {escaped(detail)}",
        "repair what the message names — the binary, its permissions, the temporary directory — then"
        " run the check again",
    )


def c12_vale_too_slow(seconds: float) -> Broken:
    """The run's budget in a check after a write ran out: a document takes vale far less, so it hangs."""
    return Broken(
        SharedKey.C12,
        f"vale gave no answer in {seconds:g} s, the most a check after a write waits",
        "a document of normal size takes vale well under a second, so the likely cause is a vale that"
        " hangs; run vale by hand to repair it, and the scan waits for vale as long as it takes"
        f" — {identity.current().until_installed}",
    )


def c12_event(event: str) -> Broken:
    return Broken(
        SharedKey.C12,
        f"this check is wired to a tool event before or after a write, not to '{echoed(event)}'",
        "in hooks.json wire it to PostToolUse on Write|Edit, or run it with --scan [<dir>]",
    )


# ---------------------------------------------------------------- this module's dial failures (C5)


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{DIALS_FILE}: {detail}", fix)


def c5_territories() -> Broken:
    return _c5(
        f"{_ns()}.territories must be a non-empty list of path patterns",
        'write the patterns of the documents to check, one per line under "- ", or leave the key out to'
        " cover every Markdown file; an empty list would examine nothing in silence",
    )


def c5_grade_ceiling() -> Broken:
    return _c5(
        f"{_ns()}.grade_ceiling must be a finite number of 0 or more",
        "write the Flesch–Kincaid grade a document may reach, such as 10, or leave the key out for the"
        " default",
    )


def c5_sentence_words() -> Broken:
    return _c5(
        f"{_ns()}.sentence_words must be a whole number of 1 or more",
        "write the words a sentence may hold, such as 25, or leave the key out for the default",
    )


def c5_levels() -> Broken:
    return _c5(
        f"{_ns()}.levels must be a mapping of rule to level",
        "write it as levels: {grade: error, sentence: error, forbidden: error, simpler: error, passive:"
        " warning}, any subset; the levels are error, warning, off",
    )


def c5_level(rule: str, value: str) -> Broken:
    return _c5(
        f"{_ns()}.levels.{rule} is '{echoed(value)}', and the levels are error, warning, off",
        "set it to error (a finding, red), warning (reported, not red) or off, or remove the line; the"
        " rules are " + ", ".join(r.value for r in Rule),
    )


def c5_all_off() -> Broken:
    return _c5(
        f"{_ns()}.levels switches every rule off",
        "a gate that checks nothing would report green as if it had checked: set at least one rule to"
        " error or warning, or remove the plugin",
    )


def c5_phrases(key: str) -> Broken:
    return _c5(
        f"{_ns()}.{key} must be a list of phrases, each one non-empty line",
        'write one phrase per line under "- ", or leave the key out',
    )


def c5_simpler() -> Broken:
    return _c5(
        f"{_ns()}.simpler must be a mapping of phrase to plain word, each one non-empty line",
        "write one line per pair, the phrase as the key and the plain word as the value, such as"
        ' "prior to: before", or leave the key out',
    )


def c5_departures() -> Broken:
    return _c5(
        f"{_ns()}.departures must be a list of entries",
        'write one entry per "- " item with the fields paths (a list of patterns), allow (a list of rule'
        " keys) and reason (one line); leave the key out, or write [], for no departure",
    )


def c5_departure(index: int, detail: str) -> Broken:
    return _c5(
        f"{_ns()}.departures entry {index}: {detail}",
        "write the entry as paths: [<patterns>], allow: [<rule keys>], reason: <one line saying why these"
        " documents stand as written>; the keys are " + ", ".join(r.value for r in Rule),
    )


def c5_exception(phrase: str) -> Broken:
    return _c5(
        f"{_ns()}.exceptions names '{echoed(phrase)}', which no forbidden phrase and no simpler pair holds",
        "an exception removes a phrase the rules know; check its spelling against the rules' lists, or"
        " remove it",
    )
