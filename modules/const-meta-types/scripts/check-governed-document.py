#!/usr/bin/env python3
"""const-meta-types: the write-time guard of claimed territory.

Two modes, one check:

  (hook)   no arguments: reads a PreToolUse event for Write or Edit on stdin,
           reconstructs the document as it will be after the write, and checks it.
  --scan   [<dir>]: checks every Markdown document in claimed territory of the
           repository containing <dir> (default: the current directory).

The check: a Markdown document in claimed territory carries the envelope
(id, type, title, status — valid values) and resolves to exactly one governing
policy: by path first; by a `policy: <id>` declaration only where the path
mapping is absent or ambiguous. Outside claimed territory nothing is checked.

Exit codes (identical meaning in both modes):
  0  green, or nothing to examine (the count says which)
  2  finding: the repository is wrong (hook mode: the write is blocked unless
     the dial severity is warn, then the finding is reported and the write proceeds)
  1  configuration failure: the checker could not run (dials file malformed,
     root policy missing, git missing). Never a silent pass.
Every exit prints how many documents were examined.

Territory patterns follow the gitignore dialect and are evaluated by git itself
(`git check-ignore`) against a fresh, empty repository whose only rules are one
policy's territory, so the project's own .gitignore never interferes.

Layout: constants and the message catalog first (every user-facing text, keyed as in
the module document), then data types, git and territory matching, the envelope, the
dials file, the territory index, the checks, output, and the two modes.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:  # the shell wrapper reports this first; kept for direct invocation
    sys.stderr.write(
        "BROKEN: const-meta-types needs PyYAML — run: python3 -m pip install pyyaml"
        " — until then Markdown writes pass unchecked\n"
        "BROKEN: the check could not run — 0 documents examined\n")
    sys.exit(1)

# ---------------------------------------------------------------- constants

EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
NAMESPACE = "const-meta-types"
DIALS_FILE = "constitution.yaml"
DECLARATION = "policy"          # the envelope field of the secondary binding
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TYPES = ("current-state", "task-record", "non-authoritative")
STATUSES = ("active", "inactive")
SEVERITIES = ("block", "warn")
DIALECT = "gitignore"
KERNEL_KEYS = ("root_policy", "territory_dialect")
FILE_TOOLS = ("Write", "Edit")

# ---------------------------------------------------------------- message catalog
# Every user-facing text, keyed as in the module document's section 6. A finding is
# (headline, why the rule exists, the exact fix); a BROKEN line is (headline, fix).
# Placeholders are filled with str.format; ids and paths are quoted in the text itself.

FIELD_FIX = ("set each named field: id = stable kebab-case (never changed, never reused);"
             " type = current-state (reconciled truth) | task-record (change delta) | non-authoritative (explanation);"
             " title = one line; status = active | inactive")
ENVELOPE_WHY = "the envelope is the one place a document's authority is declared, and it is read by machines"
DECLARATION_WHY = "the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never override it"

FINDINGS = {
    "F1": ("{rel}: no frontmatter envelope",
           "a governed document declares its authority in its envelope, or sessions guess it",
           "start the file with a YAML block between two '---' lines carrying id: <kebab-id>,"
           " type: current-state | task-record | non-authoritative, title: <one line>, status: active | inactive"),
    "F2": ("{rel}: frontmatter opened with '---' but never closed",
           "an unclosed envelope is unreadable by machines and by the next session",
           "close the YAML block with a line holding only '---'"),
    "F3": ("{rel}: frontmatter is not valid YAML ({detail})",
           "the envelope is read by machines, so it must parse",
           "repair the YAML between the '---' lines; keep the four fields id, type, title, status"),
    "F4": ("{rel}: envelope field(s) invalid: {errors}", ENVELOPE_WHY, FIELD_FIX),
    "F5": ("{rel}: id '{id}' is already carried by {other}",
           "an id is a stable identifier: two documents sharing one break every reference to it",
           "give this document its own id, never a retired one; if this is a move, delete the old file in the same change"),
    "F6": ("{rel}: declares policy '{declared}' but no policy with that id lies in the root policy's territory {root_territory}",
           "a governed document resolves to exactly one governing policy, or its rules are undefined",
           "declare the id of a policy that exists there, or drop the declaration and place the file in a claimed territory"),
    "F7": ("{rel}: matched by {n} policy territories: {matches}",
           "a document resolves to exactly one governing policy, or two rule sets compete",
           "narrow one territory in " + DIALS_FILE + " so the patterns no longer overlap; during a move, declare the intended one"
           " with '" + DECLARATION + ": <id>' in the envelope while an active task-record covers it"),
    "F8": ("{rel}: declares policy '{declared}' but its path is claimed by '{policy}' ({pattern})", DECLARATION_WHY,
           "remove '" + DECLARATION + ": {declared}' from the envelope, or move the file into the territory of '{declared}': {territory}"),
    "F8-no-such-policy": ("{rel}: declares policy '{declared}' but its path is claimed by '{policy}' ({pattern})", DECLARATION_WHY,
                          "remove '" + DECLARATION + ": {declared}' from the envelope — no policy with that id exists"),
    "F8b": ("{rel}: declares policy '{declared}' but its path is claimed by {matches}", DECLARATION_WHY,
            "declare one of the policies that claim the path, or remove the declaration and narrow the territories in " + DIALS_FILE),
    "F10": ("{rel}: lies in the root policy's territory but has type '{type}'",
            "a policy is a current-state document, and only policies lie where policies live",
            "set type: current-state, or move the file out of {root_territory}"),
    "F11": ("{rel}: the root policy has no readable envelope ({detail})",
            "the root policy's id names the namespace where policies live; without it nothing is governed",
            "keep the YAML block between two '---' lines with id, type: current-state, title, status: active"),
    "F12": ("{rel}: the root policy has type '{type}'",
            "a policy is a current-state document, and the root is the policy for policies",
            "set type: current-state"),
    "F13": ("{rel}: the root policy's id '{id}' has no territory under that id in " + DIALS_FILE,
            "the root's namespace is where policies live; changing the id orphans every policy",
            "keep the id that has the namespace, or rename the namespace in " + DIALS_FILE + " in the same change"),
}
COUNT_HOOK = "RED: {n} finding(s) — 1 document examined ({rel})"
COUNT_SCAN = "{examined} governed document(s) examined, {scanned} Markdown file(s) scanned, {policies} policies"
GREEN_HOOK = "GREEN: " + NAMESPACE + ": 1 document examined, governed by {policy}"
GREEN_SKIP = "GREEN: " + NAMESPACE + ": 0 documents examined — {reason}"
GREEN_SCAN = "GREEN: " + NAMESPACE + ": {tail}"
WARN_NOTE = (NAMESPACE + ": severity is warn: the write proceeds, but the finding stands"
             " and recurs on every write until fixed")
WARN_SYSTEM = NAMESPACE + " (warn): {headline}"
SKIPS = {
    "no-file": "tool '{tool}' carries no file to examine",
    "not-markdown": "{path} is not a Markdown document",
    "no-repo": "{path} is not inside a git repository; the constitution is silent there",
    "outside-repo": "{path} is outside the repository",
    "no-dials": "no " + DIALS_FILE + " in {root}: nothing is claimed",
    "no-root": DIALS_FILE + " has no root_policy: nothing is claimed",
    "no-content": "Write carries no content",
    "edit-unappliable": "the Edit cannot be applied to {rel}; the tool will report it",
    "outside-territory": "{rel} is outside claimed territory",
    "void-territory": "{rel} lies only in the territory of namespace {namespaces}, which has no policy document"
                      " behind it and so claims nothing",
}
NOTES = {
    "policy-without-id": "{rel} lies in the root policy's territory but carries no readable id; it claims nothing until it does",
    "policy-id-shared": "{first} and {second} both carry id '{id}'; the first claims, the second is ignored",
    "void-namespace": "namespace '{ns}' declares a territory but no policy with id '{ns}' lies in the root"
                      " policy's territory; it claims nothing until that policy exists",
}
BROKEN = {
    "C3": ("const-meta-types needs git on PATH", "install git (https://git-scm.com/downloads)"),
    "C4": (DIALS_FILE + " is not valid YAML ({detail})", "fix the file; nothing is checked until it parses"),
    "C4b": (DIALS_FILE + " is not a mapping", "the file holds top-level keys: root_policy, then one namespace per policy or module"),
    "C5": (DIALS_FILE + ": {detail}", "{fix}"),
    "C6": (DIALS_FILE + " names root_policy '{path}' but no such file exists", "create it, or point root_policy at the policy for policies"),
    "C7": ("root policy '{path}' carries no readable id in its envelope", "give it the envelope (id, type, title, status); its id names its namespace"),
    "C8": ("root policy '{id}' claims no territory in " + DIALS_FILE,
           "write {id}: {{territory: [<where policies live, including the root itself>]}} — nothing is governed until then"),
    "C9": ("root policy '{path}' lies outside its own territory {territory}",
           "every chain of governance ends at the root; widen {id}.territory to include it"),
    "C12-ls-files": ("git ls-files failed in {root}", "run the check from inside a git repository"),
    "C12-init": ("git init of the scratch repository failed", "check that git works: git --version"),
    "C12-check-ignore": ("git check-ignore failed: {detail}", "territory patterns must be gitignore syntax; check " + DIALS_FILE),
    "C12-input": ("hook input is not JSON ({detail})", "this script reads a PreToolUse event on stdin"),
    "C12-no-repo": ("{path} is not inside a git repository", "run --scan from a repository, or pass its path"),
    "C12-invocation": ("unknown invocation '{args}'", "run with no arguments (hook) or --scan [<dir>]"),
    "C12-unreadable": ("{rel} is listed by git but cannot be read", "check the file's permissions and encoding"),
}
BROKEN_LINE = "BROKEN: {headline} — fix: {fix}"
BROKEN_COUNT = "BROKEN: the check could not run — 0 documents examined"

# ---------------------------------------------------------------- data types


@dataclass
class Finding:
    headline: str
    why: str
    fix: str


def finding(key: str, **kw) -> Finding:
    headline, why, fix = FINDINGS[key]
    return Finding(headline.format(**kw), why.format(**kw), fix.format(**kw))


class Broken(Exception):
    """Configuration failure: the checker cannot run. Carries the catalog key and its values."""

    def __init__(self, key: str, **kw):
        headline, fix = BROKEN[key]
        super().__init__(headline.format(**kw), fix.format(**kw))


@dataclass
class Envelope:
    """A document's frontmatter as read. state: none | unterminated | invalid | ok."""
    state: str
    data: Dict = field(default_factory=dict)
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.state == "ok"

    @property
    def id(self) -> Optional[str]:
        v = self.data.get("id") if self.ok else None
        return v if isinstance(v, str) and ID_RE.match(v) else None

    @property
    def declared(self) -> Optional[str]:
        """The declaration, when present and well-formed; malformed ones are field errors."""
        v = self.data.get(DECLARATION) if self.ok else None
        return v if isinstance(v, str) and ID_RE.match(v) else None


@dataclass
class Policy:
    id: str
    path: str
    territory: List[str]
    claims: Dict[str, str] = field(default_factory=dict)   # path -> deciding pattern


@dataclass
class Index:
    """The repository's policies and what each territory claims."""
    root: str
    md: List[str]                       # every Markdown path considered
    root_id: str
    root_territory: List[str]
    in_root: Dict[str, str]             # paths in the root policy's territory
    policies: Dict[str, Policy]
    void: Dict[str, Dict[str, str]]     # non-policy namespace -> its would-be claims
    notes: List[str]
    pending: Optional[Tuple[str, str]]  # (path, text) of a document about to be written

    def text(self, rel: str) -> Optional[str]:
        if self.pending and rel == self.pending[0]:
            return self.pending[1]
        return read_text(self.root, rel)

    def matches(self, rel: str) -> List[Tuple[str, str]]:
        """(policy id, deciding pattern) for every policy whose territory claims rel."""
        return [(p.id, p.claims[rel]) for p in self.policies.values() if rel in p.claims]

    def governed(self) -> List[str]:
        out = set()
        for p in self.policies.values():
            out.update(p.claims)
        return sorted(out)


# ---------------------------------------------------------------- git and territory


def git(args: List[str], cwd: str, stdin: Optional[bytes] = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git"] + args, cwd=cwd, input=stdin, capture_output=True, check=False)
    except FileNotFoundError:
        raise Broken("C3")


def repo_root(path: str) -> Optional[str]:
    """Real path of the repository containing `path` (which need not exist), or None."""
    probe = path if os.path.isdir(path) else os.path.dirname(os.path.abspath(path))
    while not os.path.isdir(probe):
        parent = os.path.dirname(probe)
        if parent == probe:
            return None
        probe = parent
    r = git(["rev-parse", "--show-toplevel"], cwd=probe)
    if r.returncode != 0:
        return None
    return os.path.realpath(r.stdout.decode("utf-8", "replace").strip())


def list_markdown(root: str) -> List[str]:
    """Tracked and untracked non-ignored Markdown files, repository-relative."""
    r = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    if r.returncode != 0:
        raise Broken("C12-ls-files", root=root)
    out = r.stdout.decode("utf-8", "replace").split("\0")
    return sorted({p for p in out if p and p.lower().endswith(".md")})


def read_text(root: str, rel: str) -> Optional[str]:
    try:
        with open(os.path.join(root, rel), "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


class Matcher:
    """Evaluates gitignore-dialect patterns with git itself, in an isolated null repository.

    A fresh repository with an empty work tree and one policy's patterns as its only
    excludes file: paths need not exist, and the consumer's .gitignore never interferes."""

    def __init__(self):
        self.tmp = tempfile.mkdtemp(prefix=NAMESPACE + "-")
        self.git_dir = os.path.join(self.tmp, "null", ".git")
        self.tree = os.path.join(self.tmp, "tree")
        template = os.path.join(self.tmp, "template")
        os.makedirs(self.tree)
        os.makedirs(template)
        if git(["init", "-q", "--template=" + template, os.path.join(self.tmp, "null")], cwd=self.tmp).returncode != 0:
            raise Broken("C12-init")
        self.runs = 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def match(self, patterns: List[str], paths: List[str]) -> Dict[str, str]:
        """{path: deciding pattern} for the paths inside the territory; others absent.

        A deciding pattern that starts with '!' means the path is not in the territory."""
        if not patterns or not paths:
            return {}
        self.runs += 1
        excludes = os.path.join(self.tmp, "territory-%d" % self.runs)
        with open(excludes, "w", encoding="utf-8") as f:
            f.write("\n".join(patterns) + "\n")
        r = git(["--git-dir=" + self.git_dir, "--work-tree=" + self.tree,
                 "-c", "core.excludesfile=" + excludes, "-c", "core.ignorecase=false",
                 "check-ignore", "--no-index", "-v", "-n", "-z", "--stdin"],
                cwd=self.tree, stdin=("\0".join(paths) + "\0").encode("utf-8"))
        if r.returncode not in (0, 1):
            raise Broken("C12-check-ignore", detail=r.stderr.decode("utf-8", "replace").strip())
        fields = r.stdout.decode("utf-8", "replace").split("\0")
        found = {}
        for i in range(0, len(fields) - 3, 4):
            source, _line, pattern, path = fields[i:i + 4]
            if source and not pattern.startswith("!"):
                found[path] = pattern
        return found


# ---------------------------------------------------------------- envelope


def parse_envelope(text: str) -> Envelope:
    """The YAML block between the first line '---' and the next line '---'."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return Envelope("none")
    for i in range(1, len(lines)):
        if lines[i].strip() != "---":
            continue
        try:
            data = yaml.safe_load("\n".join(lines[1:i]))
        except yaml.YAMLError as e:
            return Envelope("invalid", detail=str(e).splitlines()[0])
        if data is None:
            data = {}
        if not isinstance(data, dict):
            return Envelope("invalid", detail="the block is not a mapping of field: value")
        return Envelope("ok", data)
    return Envelope("unterminated")


def envelope_errors(data: Dict) -> List[str]:
    """Field-level violations of the kernel's frontmatter schema, in reading order."""
    errs: List[str] = []

    def string(key: str) -> Optional[str]:
        v = data.get(key)
        if v is None:
            errs.append("%s missing" % key)
        elif not isinstance(v, str):
            errs.append("%s must be a quoted string (YAML read it as %s)" % (key, type(v).__name__))
        else:
            return v
        return None

    v = string("id")
    if v is not None and not ID_RE.match(v):
        errs.append("id '%s' is not kebab-case" % v)
    v = string("type")
    if v is not None and v not in TYPES:
        errs.append("type '%s' not one of %s" % (v, " | ".join(TYPES)))
    v = string("title")
    if v is not None and not v.strip():
        errs.append("title empty")
    elif v is not None and len(v) > 200:
        errs.append("title longer than 200 characters")
    v = string("status")
    if v is not None and v not in STATUSES:
        errs.append("status '%s' not one of %s" % (v, " | ".join(STATUSES)))
    v = data.get(DECLARATION)
    if v is not None and (not isinstance(v, str) or not ID_RE.match(v)):
        errs.append("%s '%s' is not a kebab-case policy id" % (DECLARATION, v))
    return errs


def frontmatter_id(text: Optional[str]) -> Optional[str]:
    return parse_envelope(text or "").id


# ---------------------------------------------------------------- dials file


def load_dials(root: str) -> Optional[Dict]:
    """The dials file as a mapping, or None when absent. Broken when malformed."""
    path = os.path.join(root, DIALS_FILE)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        raise Broken("C4", detail=str(e).splitlines()[0])
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise Broken("C4b")
    return data


def validate_dials(d: Dict) -> str:
    """Validate only the keys this module reads (kernel keys, policy territories, own
    namespace) against the kernel schema; normalise root_policy. Returns the severity."""
    def bad(detail: str, fix: str):
        raise Broken("C5", detail=detail, fix=fix)

    if "root_policy" in d:
        rp = d["root_policy"]
        if (not isinstance(rp, str) or not rp.strip() or os.path.isabs(rp)
                or ".." in os.path.normpath(rp).split("/")):
            bad("root_policy must be a repository-relative path", "root_policy: docs/policies/<root>.md")
        d["root_policy"] = os.path.normpath(rp).replace(os.sep, "/")
    dialect = d.get("territory_dialect", DIALECT)
    if not isinstance(dialect, str) or not dialect.strip():
        bad("territory_dialect must be a non-empty string", "remove the key (default gitignore) or name a dialect")
    if dialect != DIALECT:
        bad("territory_dialect '%s' is not supported by %s (supports: %s)" % (dialect, NAMESPACE, DIALECT),
            "set territory_dialect: %s, or remove the key" % DIALECT)
    for key, ns in d.items():
        if key in KERNEL_KEYS or (key.startswith("const-") and key != NAMESPACE):
            continue  # other modules' namespaces are not read
        if not isinstance(ns, dict):
            bad("namespace '%s' must be a mapping" % key, "write it as %s: {territory: [...]}" % key)
        terr = ns.get("territory")
        if terr is not None and (not isinstance(terr, list)
                                 or not all(isinstance(p, str) and p.strip() for p in terr)):
            bad("%s.territory must be a list of non-empty strings" % key,
                "write it as %s: {territory: [\"docs/%s/**\"]}" % (key, key))
    own = d.get(NAMESPACE) or {}
    if not isinstance(own, dict):
        bad("namespace '%s' must be a mapping" % NAMESPACE, "write it as %s: {severity: block}" % NAMESPACE)
    severity = own.get("severity", "block")
    if severity not in SEVERITIES:
        bad("%s.severity must be block or warn" % NAMESPACE, "write %s: {severity: block} or {severity: warn}" % NAMESPACE)
    return severity


def territory_of(dials: Dict, namespace: str) -> List[str]:
    ns = dials.get(namespace)
    return list(ns.get("territory") or []) if isinstance(ns, dict) else []


# ---------------------------------------------------------------- territory index


def build_index(root: str, dials: Dict, matcher: Matcher, pending: Optional[Tuple[str, str]] = None) -> Index:
    """Discover the root, the policies (id-bearing documents in the root's territory),
    what each claims, and the namespaces that claim without a policy behind them."""
    md = set(list_markdown(root))
    if pending:
        md.add(pending[0])
    index = Index(root=root, md=sorted(md), root_id="", root_territory=[], in_root={},
                  policies={}, void={}, notes=[], pending=pending)
    rp = dials["root_policy"]
    root_text = index.text(rp)
    if root_text is None:
        raise Broken("C6", path=rp)
    root_id = frontmatter_id(root_text)
    if root_id is None:
        raise Broken("C7", path=rp)
    root_territory = territory_of(dials, root_id)
    if not root_territory:
        raise Broken("C8", id=root_id)
    in_root = matcher.match(root_territory, index.md)
    if rp not in in_root:
        raise Broken("C9", path=rp, territory=root_territory, id=root_id)
    index.root_id, index.root_territory, index.in_root = root_id, root_territory, in_root

    for path in sorted(in_root):
        pid = frontmatter_id(index.text(path))
        if pid is None:
            index.notes.append(NOTES["policy-without-id"].format(rel=path))
        elif pid in index.policies:
            index.notes.append(NOTES["policy-id-shared"].format(first=index.policies[pid].path, second=path, id=pid))
        else:
            index.policies[pid] = Policy(pid, path, territory_of(dials, pid))
    for policy in index.policies.values():
        policy.claims = matcher.match(policy.territory, index.md)

    for key in dials:
        if key in KERNEL_KEYS or key in index.policies or key.startswith("const-"):
            continue  # module namespaces are never policies
        terr = territory_of(dials, key)
        if terr:
            index.void[key] = matcher.match(terr, index.md)
    return index


# ---------------------------------------------------------------- the checks


def resolve(index: Index, rel: str, env: Envelope) -> Tuple[Optional[str], List[Finding]]:
    """Kernel governance binding: path first, declaration where the path mapping is
    absent or ambiguous. Returns (governing policy id or None, resolution findings)."""
    matches = index.matches(rel)
    declared = env.declared
    if len(matches) == 1:
        policy, pattern = matches[0]
        if declared is None or declared == policy:
            return policy, []
        key = "F8" if declared in index.policies else "F8-no-such-policy"
        territory = index.policies[declared].territory if declared in index.policies else None
        return None, [finding(key, rel=rel, declared=declared, policy=policy, pattern=pattern, territory=territory)]
    if len(matches) > 1:
        listed = ", ".join("%s (%s)" % m for m in matches)
        if declared in [m[0] for m in matches]:
            return declared, []
        if declared is None:
            return None, [finding("F7", rel=rel, n=len(matches), matches=listed)]
        return None, [finding("F8b", rel=rel, declared=declared, matches=listed)]
    if declared is None:
        return None, []                      # outside claimed territory: silence
    if declared in index.policies:
        return declared, []
    return None, [finding("F6", rel=rel, declared=declared, root_territory=index.root_territory)]


def check_envelope(index: Index, rel: str, env: Envelope) -> List[Finding]:
    """The kernel envelope: shape, fields, the policy-type rule, id uniqueness in the tree."""
    if env.state == "none":
        return [finding("F1", rel=rel)]
    if env.state == "unterminated":
        return [finding("F2", rel=rel)]
    if env.state == "invalid":
        return [finding("F3", rel=rel, detail=env.detail)]
    errors = envelope_errors(env.data)
    if errors:
        return [finding("F4", rel=rel, errors="; ".join(errors))]
    findings = []
    if rel in index.in_root and env.data["type"] != "current-state":
        findings.append(finding("F10", rel=rel, type=env.data["type"], root_territory=index.root_territory))
    for other in index.governed():
        if other != rel and frontmatter_id(index.text(other)) == env.data["id"]:
            findings.append(finding("F5", rel=rel, id=env.data["id"], other=other))
            break
    return findings


def examine(index: Index, rel: str, text: str) -> Tuple[List[Finding], Optional[str]]:
    """One document: (findings, governing policy id). Both empty and None means the
    document is outside claimed territory and nothing was checked."""
    env = parse_envelope(text)
    policy, findings = resolve(index, rel, env)
    if policy is None and not findings:
        return [], None
    return findings + check_envelope(index, rel, env), policy


def check_root_policy(dials: Dict, rel: str, text: str) -> List[Finding]:
    """The root policy about to be written: a damaged envelope is a finding on this write,
    never a configuration failure (which would let the write through)."""
    env = parse_envelope(text)
    if not env.ok:
        return [finding("F11", rel=rel, detail=env.detail or env.state)]
    errors = envelope_errors(env.data)
    if errors:
        return [finding("F4", rel=rel, errors="; ".join(errors))]
    findings = []
    if env.data["type"] != "current-state":
        findings.append(finding("F12", rel=rel, type=env.data["type"]))
    if not territory_of(dials, env.data["id"]):
        findings.append(finding("F13", rel=rel, id=env.data["id"]))
    return findings


# ---------------------------------------------------------------- output


def red_lines(findings: List[Finding]) -> str:
    return "".join("RED: %s\n  why: %s\n  fix: %s\n" % (f.headline, f.why, f.fix) for f in findings)


def skip(key: str, **kw) -> int:
    print(GREEN_SKIP.format(reason=SKIPS[key].format(**kw)))
    return EXIT_GREEN


def report(findings: List[Finding], rel: str, severity: str) -> int:
    """Hook mode verdict on findings: block (exit 2, stderr) or warn (exit 0, JSON)."""
    body = red_lines(findings) + COUNT_HOOK.format(n=len(findings), rel=rel) + "\n"
    if severity == "warn":
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": body + WARN_NOTE},
            "systemMessage": WARN_SYSTEM.format(headline=findings[0].headline),
        }))
        return EXIT_GREEN
    sys.stderr.write(body)
    return EXIT_RED


# ---------------------------------------------------------------- modes


def document_after_write(event: Dict, root: str, rel: str) -> Optional[str]:
    """The document as it will be once the tool has run, or None when the tool itself
    will fail (missing file, absent old_string): nothing to judge then."""
    ti = event.get("tool_input") or {}
    if event.get("tool_name") == "Write":
        text = ti.get("content")
        return text if isinstance(text, str) else None
    current = read_text(root, rel)
    old, new = ti.get("old_string"), ti.get("new_string")
    if current is None or not isinstance(old, str) or not isinstance(new, str) or old not in current:
        return None
    return current.replace(old, new) if ti.get("replace_all") else current.replace(old, new, 1)


def hook_mode() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError as e:
        raise Broken("C12-input", detail=e)
    tool = event.get("tool_name")
    path = (event.get("tool_input") or {}).get("file_path")
    if tool not in FILE_TOOLS or not isinstance(path, str) or not path:
        return skip("no-file", tool=tool)
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(event.get("cwd") or os.getcwd(), path)
    path = os.path.realpath(path)
    if not path.lower().endswith(".md"):
        return skip("not-markdown", path=path)
    root = repo_root(path)
    if root is None:
        return skip("no-repo", path=path)
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    if rel.startswith(".."):
        return skip("outside-repo", path=path)
    dials = load_dials(root)
    if dials is None:
        return skip("no-dials", root=root)
    severity = validate_dials(dials)
    if "root_policy" not in dials:
        return skip("no-root")
    text = document_after_write(event, root, rel)
    if text is None:
        return skip("no-content") if tool == "Write" else skip("edit-unappliable", rel=rel)
    if rel == dials["root_policy"]:
        findings = check_root_policy(dials, rel, text)
        if findings:
            return report(findings, rel, severity)
    with Matcher() as matcher:
        index = build_index(root, dials, matcher, pending=(rel, text))
        findings, policy = examine(index, rel, text)
    if policy is None and not findings:
        void = [ns for ns, claims in index.void.items() if rel in claims]
        if void:
            return skip("void-territory", rel=rel, namespaces=", ".join("'%s'" % v for v in void))
        return skip("outside-territory", rel=rel)
    for note in index.notes:
        print("note: " + note)
    if not findings:
        print(GREEN_HOOK.format(policy=policy))
        return EXIT_GREEN
    return report(findings, rel, severity)


def scan_mode(start: str) -> int:
    root = repo_root(os.path.abspath(start))
    if root is None:
        raise Broken("C12-no-repo", path=start)
    dials = load_dials(root)
    if dials is None:
        return skip("no-dials", root=root)
    validate_dials(dials)               # the scan ignores severity and always reports
    if "root_policy" not in dials:
        return skip("no-root")
    with Matcher() as matcher:
        index = build_index(root, dials, matcher)
        for ns in sorted(index.void):
            index.notes.append(NOTES["void-namespace"].format(ns=ns))
        findings: List[Finding] = []
        examined = 0
        for rel in index.md:
            text = index.text(rel)
            if text is None:
                raise Broken("C12-unreadable", rel=rel)
            found, policy = examine(index, rel, text)
            if policy is None and not found:
                continue
            examined += 1
            findings.extend(found)
    for note in index.notes:
        print("note: " + note)
    tail = COUNT_SCAN.format(examined=examined, scanned=len(index.md), policies=len(index.policies))
    if findings:
        sys.stdout.write(red_lines(findings))
        print("RED: %d finding(s) — %s" % (len(findings), tail))
        return EXIT_RED
    print(GREEN_SCAN.format(tail=tail))
    return EXIT_GREEN


def main(argv: List[str]) -> int:
    try:
        if not argv:
            return hook_mode()
        if argv[0] == "--scan" and len(argv) <= 2:
            return scan_mode(argv[1] if len(argv) == 2 else os.getcwd())
        raise Broken("C12-invocation", args=" ".join(argv))
    except Broken as b:
        headline, fix = b.args
        sys.stderr.write(BROKEN_LINE.format(headline=headline, fix=fix) + "\n" + BROKEN_COUNT + "\n")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
