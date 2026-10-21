"""The act. Everything that can refuse is asked first — the command line, the repository, the
dials, the policy, the home and its proof, the template — so that a refusal finds the tree as
it was. Only then is one file written."""

from __future__ import annotations

import os
from pathlib import Path

from constitution_layer_kit import pipeline
from constitution_layer_kit.dials import load_dials
from constitution_layer_kit.envelope import id_of_text
from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.index import Index, build_index
from constitution_layer_kit.model import EXIT_GREEN, Dials, Policy
from constitution_layer_kit.output import Output
from constitution_layer_kit.repository import repo_root
from constitution_layer_kit.territory import Matcher

from . import dials as own_dials
from . import filling, homes, messages
from .model import HomeClass, Plan, Request


def act(output: Output, request: Request) -> int:
    """Refuses whatever can refuse, in order, then plans the document and writes it — or, on a
    dry run, prints the plan alone."""
    _refuse_bad_values(request)
    root = repo_root(Path.cwd())
    if root is None:
        raise ConfigurationFailure(messages.l5_no_repository(str(Path.cwd())))
    shared_dials = load_dials(root)
    if shared_dials is None:
        raise ConfigurationFailure(messages.l5_no_dials(str(root)))
    pipeline.route_log(output, root, shared_dials)  # before any refusal: a refusal belongs in the log too
    dials = own_dials.parse(shared_dials.own)
    if shared_dials.root_policy is None:
        raise ConfigurationFailure(messages.l5_no_root_policy())
    index, policy, (home, doc_id, pattern) = _locate(
        output, request, root, shared_dials, shared_dials.root_policy
    )
    if (root / home).exists():
        raise ConfigurationFailure(messages.l5_exists(home))
    _refuse_id_in_use(index, doc_id)
    plan = _plan(root, request, dials.templates.get(request.kind), policy.path, home, pattern, doc_id)
    output.out(messages.l1_home(plan.home, request.kind, plan.pattern))
    output.out(
        messages.l2_template(plan.template) if plan.template else messages.l2_no_template(request.kind)
    )
    if request.dry_run:
        output.out(messages.l4_dry_run())
        return EXIT_GREEN
    _write(root, plan)
    output.out(messages.l3_created(plan.home))
    output.out(messages.l4_count(plan.home))
    return EXIT_GREEN


def _refuse_bad_values(request: Request) -> None:
    """The command line's own refusals: a title missing, empty or of several lines; a stem, a
    segment or an id that is not kebab-case."""
    if request.title is None and not request.dry_run:
        raise ConfigurationFailure(messages.l5_title_needed())
    if request.title is not None and not request.title.strip():  # a dry run too: the title is a value
        raise ConfigurationFailure(messages.l5_title_empty())
    if request.title is not None and ("\n" in request.title or "\r" in request.title):
        raise ConfigurationFailure(messages.l5_title_multiline())
    for value, what in (
        (request.stem, "the stem"),
        (request.segment, "the segment"),
        (request.doc_id, "the id"),
    ):
        if value is not None and not homes.is_kebab(value):
            raise ConfigurationFailure(messages.l5_not_kebab(value, what))


def _locate(
    output: Output, request: Request, root: Path, shared_dials: Dials, root_policy: str
) -> tuple[Index, Policy, tuple[str, str, str]]:
    """The index, the kind's policy and the home it implies — the home, the id and the deciding
    pattern — or the refusal of a kind that is no policy, has no territory or no home of its own."""
    with Matcher() as matcher:
        index = build_index(root, shared_dials, root_policy, matcher)
        for note in index.notes:
            output.out(note)
        policy = index.policies.get(request.kind)
        if policy is None:
            raise ConfigurationFailure(messages.l5_not_a_policy(request.kind, sorted(index.policies)))
        if not policy.territory:  # a policy with no territory line: the fix is the line, not a simpler one
            raise ConfigurationFailure(messages.l5_no_territory(request.kind))
        located = _home_of(request, policy.territory)
        _refuse_other_claims(matcher, index, request.kind, policy.territory, located[0])
    return index, policy, located


def _refuse_other_claims(
    matcher: Matcher, index: Index, kind: str, territory: tuple[str, ...], home: str
) -> None:
    """Refuses a home another policy's territory claims too, or one the kind's own does not."""
    for other in index.policies.values():
        claimed = matcher.match(other.territory, [home])
        if other.id != kind and claimed:
            raise ConfigurationFailure(messages.l5_two_policies(home, other.id, claimed[home]))
        if other.id == kind and not claimed:  # the derivation and git disagree: no home
            raise ConfigurationFailure(messages.l5_no_home(kind, territory))


def _home_of(request: Request, territory: tuple[str, ...]) -> tuple[str, str, str]:
    """The home, the id and the deciding pattern, or the refusal the territory's shape earns."""
    rule = homes.rule_of(territory)
    kind = request.kind
    if rule.kind is HomeClass.SINGLE:
        raise ConfigurationFailure(messages.l5_single_path(kind, rule.pattern))
    if rule.kind is HomeClass.NONE:
        raise ConfigurationFailure(messages.l5_no_home(kind, territory))
    if rule.kind is HomeClass.SEGMENT:
        if request.stem is not None:
            raise ConfigurationFailure(messages.l5_stem_not_taken(kind, rule.pattern, rule.fixed_name))
        if request.segment is None:
            raise ConfigurationFailure(messages.l5_segment_needed(kind, rule.pattern))
        home = homes.segment_home(rule, request.segment)
        doc_id = request.doc_id or f"{rule.fixed_name.lower()}-{request.segment}"
    else:
        if request.segment is not None:
            raise ConfigurationFailure(messages.l5_segment_not_taken(kind, rule.pattern))
        if request.stem is None:
            raise ConfigurationFailure(messages.l5_usage("--stem was not given"))
        home = homes.directory_home(rule, request.stem)
        doc_id = request.doc_id or request.stem
    if not homes.is_kebab(doc_id):
        raise ConfigurationFailure(messages.l5_not_kebab(doc_id, "the id"))
    return home, doc_id, rule.pattern


def _refuse_id_in_use(index: Index, doc_id: str) -> None:
    for rel, text in index.documents():
        if id_of_text(text) == doc_id:
            raise ConfigurationFailure(messages.l5_id_in_use(doc_id, rel))


def _plan(
    root: Path, request: Request, template: str | None, policy_path: str, home: str, pattern: str, doc_id: str
) -> Plan:
    title = request.title or ""  # a dry run may have none: nothing is filled then
    if template is None:
        if request.meta_type is None and not request.dry_run:
            raise ConfigurationFailure(messages.l5_type_needed(request.kind, policy_path))
        text = filling.from_envelope_alone(doc_id, request.meta_type, title) if request.meta_type else ""
        return Plan(home, pattern, None, text)
    path = root / template
    if not path.is_file():
        raise ConfigurationFailure(messages.l5_template_missing(request.kind, template))
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigurationFailure(messages.l5_template_unreadable(request.kind, template, str(exc))) from exc
    return Plan(
        home, pattern, template, filling.from_template(source, template, doc_id, title, request.meta_type)
    )


def _write(root: Path, plan: Plan) -> None:
    """One new file, into a directory made for it where none exists — the file and the directories
    unmade when the write fails, part-way too."""
    made: list[Path] = []
    home = root / plan.home
    parent = home.parent
    while not parent.exists():
        made.append(parent)
        parent = parent.parent
    opened = False  # "x" creates the file or fails: once it opens, the file is this run's to remove
    try:
        for directory in reversed(made):
            directory.mkdir()
        with home.open("x", encoding="utf-8", newline="") as handle:
            opened = True
            handle.write(plan.text)
    except OSError as exc:
        if opened:  # a write that failed part-way leaves no truncated file
            home.unlink(missing_ok=True)
        for directory in made:
            if directory.is_dir() and not os.listdir(directory):
                directory.rmdir()
        raise ConfigurationFailure(messages.l5_could_not_write(plan.home, str(exc))) from exc
