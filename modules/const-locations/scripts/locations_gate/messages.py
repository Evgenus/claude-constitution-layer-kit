"""The texts of this module's own lines, refusals and dial failures, as functions with typed
parameters; the texts every gate shares live in the shared package's messages module.

A refusal is one self-sufficient line — what was refused and the exact fix — followed by
the closing line that says nothing was written. Every function name starts with the stable
key of its text (l1_, l5_, c5_), so a text can be cited, reviewed and asserted by key. A
reader must be able to act on a message without holding any other document: no text here
cites one.
"""

from __future__ import annotations

from collections.abc import Sequence

from const_gate import identity
from const_gate.messages import echoed
from const_gate.model import DIALS_FILE, Broken, MetaType, SharedKey

from .model import ActKey

TYPES = ", ".join(t.value for t in MetaType)
TYPES_OR = " or ".join(TYPES.rsplit(", ", 1))  # "a, b or c"
_ENTRY = "{policy: <id>, template: <repository-relative path>}"


def _ns() -> str:
    return identity.current().namespace


# ---------------------------------------------------------------- the lines of a run


def l1_home(home: str, kind: str, pattern: str) -> str:
    return f"HOME: {home} — governed by {kind} (territory '{pattern}')"


def l2_template(path: str) -> str:
    return f"TEMPLATE: {path}"


def l2_no_template(kind: str) -> str:
    return (
        f"TEMPLATE: none — {kind} names no template in {_ns()}.templates; the envelope alone is"
        " written, and the body is the title's heading"
    )


def l3_created(home: str) -> str:
    return f"CREATED: {home}"


def l4_count(home: str) -> str:
    return f"1 document created ({home}) — fill the body where the template says, then commit"


def l4_dry_run() -> str:
    return "0 documents created — dry run: the lines above are what a write would use"


def l4_nothing_written() -> str:
    return "BROKEN: the document could not be created — nothing was written"


# ---------------------------------------------------------------- refusals

_USAGE = (
    "--kind <policy id> --stem <stem> --title <text> [--type <meta-type>] [--segment <segment>]"
    " [--id <id>] [--dry-run]"
)


def _refused(what: str, fix: str) -> Broken:
    return Broken(ActKey.L5, what, fix)


def l5_usage(detail: str) -> Broken:
    return _refused(f"misinvocation: {detail}", f"run it with {_USAGE}")


def l5_no_repository(directory: str) -> Broken:
    return _refused(
        f"{directory} is not inside a git repository",
        "run it from inside the repository the document belongs to",
    )


def l5_no_dials(root: str) -> Broken:
    return _refused(
        f"no {DIALS_FILE} in {root}: no kind is declared",
        "a document is created into a policy's territory; declare the root policy and the kind's"
        " policy first — the new-kind procedure",
    )


def l5_no_root_policy() -> Broken:
    return _refused(
        f"{DIALS_FILE} names no root_policy: no policy claims anything",
        "set root_policy: <path of the policy for policies>",
    )


def l5_not_a_policy(kind: str, ids: Sequence[str]) -> Broken:
    return _refused(
        f"'{kind}' is not a policy: no document in the root policy's territory carries that id",
        f"name one of: {', '.join(ids) or 'nothing — no policy is declared'}; for a new kind, create"
        " its policy first — the new-kind procedure",
    )


def l5_single_path(kind: str, pattern: str) -> Broken:
    return _refused(
        f"{kind}'s territory is the single path '{pattern}': nothing new is born there",
        "that document is created by hand at exactly that path, once; a kind that holds many"
        " documents claims a directory: <dir>/**",
    )


def l5_no_home(kind: str, patterns: Sequence[str]) -> Broken:
    shown = "[" + ", ".join(f"'{p}'" for p in patterns) + "]"
    return _refused(
        f"no home follows from {kind}'s territory {shown}",
        "a home follows from one pattern <dir>/** or <dir>/**/*.md, or from one with a single free"
        " segment, <dir>/*/NAME.md; write the document by hand inside the territory, or simplify the"
        " territory",
    )


def l5_no_territory(kind: str) -> Broken:
    return _refused(
        f"{kind} claims no territory: its namespace in {DIALS_FILE} has no territory, so no home follows",
        f"under {kind}: in {DIALS_FILE} write territory: ['<dir>/**'], <dir> being the directory its"
        " documents live in",
    )


def l5_segment_needed(kind: str, pattern: str) -> Broken:
    return _refused(
        f"{kind}'s territory '{pattern}' has a free segment, and --segment was not given: the pattern fixes"
        " the file name and leaves that one segment to be named",
        "run it with --segment <the segment>; the file name is the pattern's, so --stem is not taken",
    )


def l5_stem_not_taken(kind: str, pattern: str, name: str) -> Broken:
    return _refused(
        f"--stem was given, but {kind}'s territory '{pattern}' fixes the file name '{name}'",
        "drop --stem and give --segment",
    )


def l5_segment_not_taken(kind: str, pattern: str) -> Broken:
    return _refused(
        f"--segment was given, but {kind}'s territory '{pattern}' has no free segment: the home is the"
        " directory and the stem",
        "drop --segment and give --stem",
    )


def l5_not_kebab(value: str, what: str) -> Broken:
    return _refused(
        f"'{value}' is not a kebab-case name for {what}",
        "lower-case letters, digits and single hyphens between them: a-z, 0-9, no leading, trailing"
        " or double hyphen",
    )


def l5_exists(home: str) -> Broken:
    return _refused(
        f"{home} already exists: creating never overwrites, so the document that is there stays as it is",
        "choose another stem, or edit the document that is there",
    )


def l5_two_policies(home: str, other: str, pattern: str) -> Broken:
    return _refused(
        f"{home} would also lie in {other}'s territory ('{pattern}'): two policies would govern it",
        f"territories never overlap; narrow one of them in {DIALS_FILE} before creating documents there",
    )


def l5_type_needed(kind: str, policy_path: str) -> Broken:
    return _refused(
        f"{kind} has no template, and --type was not given: without a template nothing but the policy's"
        " prose says which meta-type the kind is",
        f"run it with --type {TYPES_OR} — {policy_path} says which its kind is",
    )


def l5_type_conflict(given: str, path: str, fixed: str) -> Broken:
    return _refused(
        f"--type {given} was given, but the template {path} fixes type: {fixed}, and a kind has one"
        " meta-type",
        "drop --type; the template decides",
    )


def l5_template_missing(kind: str, path: str) -> Broken:
    return _refused(
        f"the template of {kind}, {path}, does not exist",
        f"point {_ns()}.templates at a Markdown file of this repository, or remove the entry",
    )


def l5_template_unreadable(kind: str, path: str, error: str) -> Broken:
    return _refused(
        f"the template of {kind}, {path}, cannot be read ({error})",
        f"point {_ns()}.templates at a Markdown file of this repository, or remove the entry",
    )


def l5_template_no_envelope(path: str, detail: str) -> Broken:
    return _refused(
        f"the template {path} opens with no readable envelope ({detail})",
        "a template opens with the YAML block a document of its kind carries — id, type, title,"
        " status — with placeholders where the writer fills",
    )


def l5_template_bad_type(path: str, value: str) -> Broken:
    return _refused(
        f"the template {path} carries type '{value}', which is no meta-type",
        f"set type: {TYPES_OR} in the template",
    )


def l5_title_needed() -> Broken:
    return _refused(
        "--title was not given, and the envelope is written with the title as a value",
        "run it with --title '<the document's title>'; a dry run needs none",
    )


def l5_title_empty() -> Broken:
    return _refused(
        "--title is empty (or only whitespace), and the title is the envelope's one non-empty line",
        "run it with --title '<the document's title>'",
    )


def l5_title_multiline() -> Broken:
    return _refused("--title holds a line break, and a title is one line", "give the title on one line")


def l5_id_in_use(doc_id: str, path: str) -> Broken:
    return _refused(
        f"id '{doc_id}' is already carried by {path}",
        "ids are unique in the tree: choose another stem, or give --id",
    )


def l5_could_not_write(home: str, error: str) -> Broken:
    return _refused(
        f"{home} could not be written ({error}): the write is the last act, so the refusal leaves nothing"
        " behind",
        "remove what the system's error names — a denied permission, a file or link in the way at the"
        " home or a directory above it, a full or read-only disk — and run it again; nothing else was"
        " changed",
    )


# ---------------------------------------------------------------- this module's dial failures


def _c5(detail: str, fix: str) -> Broken:
    return Broken(SharedKey.C5, f"{DIALS_FILE}: {detail}", fix)


def c5_severity_here() -> Broken:
    return _c5(
        f"{_ns()}.severity has no meaning: this module blocks nothing, and a line that sets nothing misleads"
        " the next reader",
        "remove the line",
    )


def c5_templates_shape() -> Broken:
    return _c5(
        f"{_ns()}.templates must be a list of {_ENTRY}: one entry names one kind's template",
        "write it as templates: [{policy: <id>, template: <path>}, ...], or remove the key",
    )


def c5_template_entry(position: int, what: str) -> Broken:
    return _c5(
        f"{_ns()}.templates[{position}] {what}; an entry the command cannot read names no template",
        f"write the entry as {_ENTRY}",
    )


def entry_not_a_mapping() -> str:
    return "is not a mapping"


def entry_missing(key: str) -> str:
    return f"has no {key}"


def entry_unknown_key(key: str) -> str:
    return f"carries an unknown key '{echoed(key)}'"


def entry_repeated(policy: str) -> str:
    return f"names policy '{policy}' a second time"


def entry_outside() -> str:
    return "names a template outside the repository"
