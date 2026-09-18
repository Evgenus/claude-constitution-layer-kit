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
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    import yaml
except ImportError:  # the shell wrapper reports this first; kept for direct invocation
    sys.stderr.write(
        "BROKEN: const-meta-types needs PyYAML — run: python3 -m pip install pyyaml"
        " — until then Markdown writes pass unchecked\n")
    sys.exit(1)

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


class Broken(Exception):
    """Configuration failure: the checker cannot run. args: (headline, fix)."""


# ---------------------------------------------------------------- git helpers

def git(args, cwd, stdin=None):
    try:
        return subprocess.run(["git"] + args, cwd=cwd, input=stdin,
                              capture_output=True, check=False)
    except FileNotFoundError:
        raise Broken("const-meta-types needs git on PATH",
                     "install git (https://git-scm.com/downloads)")


def repo_root(path):
    """Real path of the repository containing `path` (which need not exist), or None."""
    probe = os.path.dirname(os.path.abspath(path)) if not os.path.isdir(path) else path
    while not os.path.isdir(probe):
        parent = os.path.dirname(probe)
        if parent == probe:
            return None
        probe = parent
    r = git(["rev-parse", "--show-toplevel"], cwd=probe)
    if r.returncode != 0:
        return None
    return os.path.realpath(r.stdout.decode("utf-8", "replace").strip())


def list_markdown(root):
    """Tracked and untracked non-ignored Markdown files, repository-relative."""
    r = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    if r.returncode != 0:
        raise Broken("git ls-files failed in %s" % root,
                     "run the check from inside a git repository")
    out = r.stdout.decode("utf-8", "replace").split("\0")
    return sorted({p for p in out if p and p.lower().endswith(".md")})


class Matcher:
    """Evaluates gitignore-dialect patterns with git itself, in an isolated null repository."""

    def __init__(self):
        self.tmp = tempfile.mkdtemp(prefix="const-meta-types-")
        self.null = os.path.join(self.tmp, "null")
        self.tree = os.path.join(self.tmp, "tree")
        template = os.path.join(self.tmp, "template")
        os.makedirs(self.tree)
        os.makedirs(template)
        r = git(["init", "-q", "--template=" + template, self.null], cwd=self.tmp)
        if r.returncode != 0:
            raise Broken("git init of the scratch repository failed",
                         "check that git works: git --version")
        self.n = 0

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def match(self, patterns, paths):
        """{path: deciding pattern} for paths inside the territory; other paths absent."""
        if not patterns or not paths:
            return {}
        self.n += 1
        excludes = os.path.join(self.tmp, "territory-%d" % self.n)
        with open(excludes, "w", encoding="utf-8") as f:
            f.write("\n".join(patterns) + "\n")
        r = git(["--git-dir=" + os.path.join(self.null, ".git"), "--work-tree=" + self.tree,
                 "-c", "core.excludesfile=" + excludes, "-c", "core.ignorecase=false",
                 "check-ignore", "--no-index", "-v", "-n", "-z", "--stdin"],
                cwd=self.tree, stdin=("\0".join(paths) + "\0").encode("utf-8"))
        if r.returncode not in (0, 1):
            raise Broken("git check-ignore failed: %s" % r.stderr.decode("utf-8", "replace").strip(),
                         "territory patterns must be gitignore syntax; check " + DIALS_FILE)
        fields = r.stdout.decode("utf-8", "replace").split("\0")
        found = {}
        for i in range(0, len(fields) - 3, 4):
            source, _line, pattern, path = fields[i:i + 4]
            if source and not pattern.startswith("!"):
                found[path] = pattern
        return found


# ---------------------------------------------------------------- envelope

def read_frontmatter(text):
    """(state, mapping_or_None, detail). state: none | unterminated | invalid | ok."""
    text = text.lstrip("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "none", None, ""
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            block = "\n".join(lines[1:i])
            try:
                data = yaml.safe_load(block)
            except yaml.YAMLError as e:
                return "invalid", None, str(e).splitlines()[0]
            if data is None:
                data = {}
            if not isinstance(data, dict):
                return "invalid", None, "the block is not a mapping of field: value"
            return "ok", data, ""
    return "unterminated", None, ""


def field_errors(data):
    errs = []
    v = data.get("id")
    if v is None:
        errs.append("id missing")
    elif not isinstance(v, str) or not ID_RE.match(v):
        errs.append("id %r is not kebab-case" % (v,))
    v = data.get("type")
    if v is None:
        errs.append("type missing")
    elif v not in TYPES:
        errs.append("type %r not one of %s" % (v, " | ".join(TYPES)))
    v = data.get("title")
    if v is None:
        errs.append("title missing")
    elif not isinstance(v, str) or not v.strip():
        errs.append("title empty")
    elif len(v) > 200:
        errs.append("title longer than 200 characters")
    v = data.get("status")
    if v is None:
        errs.append("status missing")
    elif v not in STATUSES:
        errs.append("status %r not one of %s" % (v, " | ".join(STATUSES)))
    v = data.get(DECLARATION)
    if v is not None and (not isinstance(v, str) or not ID_RE.match(v)):
        errs.append("%s %r is not a kebab-case policy id" % (DECLARATION, v))
    return errs


def frontmatter_id(text):
    state, data, _ = read_frontmatter(text)
    if state == "ok" and isinstance(data.get("id"), str) and ID_RE.match(data["id"]):
        return data["id"]
    return None


def read_text(root, rel):
    try:
        with open(os.path.join(root, rel), "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


# ---------------------------------------------------------------- dials file

def load_dials(root):
    """The dials file as a mapping, or None when absent. Broken when malformed."""
    path = os.path.join(root, DIALS_FILE)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        raise Broken("%s is not valid YAML (%s)" % (DIALS_FILE, str(e).splitlines()[0]),
                     "fix the file; nothing is checked until it parses")
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise Broken("%s is not a mapping" % DIALS_FILE,
                     "the file holds top-level keys: root_policy, then one namespace per policy or module")
    return data


def validate_dials(d):
    """The keys this module reads, against the kernel schema. Broken on the first violation."""
    def bad(detail, fix):
        raise Broken("%s: %s" % (DIALS_FILE, detail), fix)
    if "root_policy" in d and (not isinstance(d["root_policy"], str) or not d["root_policy"].strip()):
        bad("root_policy must be a non-empty string", "root_policy: <repository-relative path of the root policy>")
    dialect = d.get("territory_dialect", DIALECT)
    if not isinstance(dialect, str) or not dialect.strip():
        bad("territory_dialect must be a non-empty string", "remove the key (default gitignore) or name a dialect")
    if dialect != DIALECT:
        bad("territory_dialect %r is not supported by %s (supports: %s)" % (dialect, NAMESPACE, DIALECT),
            "set territory_dialect: %s, or remove the key" % DIALECT)
    for key, ns in d.items():
        if key in KERNEL_KEYS:
            continue
        if not isinstance(ns, dict):
            bad("namespace %r must be a mapping" % key, "write it as a mapping: %s: {territory: [...]}, or the module's dials" % key)
        terr = ns.get("territory")
        if terr is not None and (not isinstance(terr, list)
                                 or not all(isinstance(p, str) and p.strip() for p in terr)):
            bad("%s.territory must be a list of non-empty strings" % key,
                "write it as %s: {territory: [\"docs/%s/**\"]}" % (key, key))
        cat = ns.get("catalog")
        if cat is not None:
            if (not isinstance(cat, dict) or not isinstance(cat.get("prefix"), str)
                    or not re.match(r"^[a-z0-9]+$", cat["prefix"])
                    or ("width" in cat and (not isinstance(cat["width"], int) or cat["width"] < 1))
                    or set(cat) - {"prefix", "width"}):
                bad("%s.catalog must be {prefix: <a-z0-9>, width: <integer >= 1>}" % key,
                    "write it as %s: {catalog: {prefix: dec, width: 4}}" % key)
    sev = (d.get(NAMESPACE) or {}).get("severity", "block")
    if sev not in SEVERITIES:
        bad("%s.severity must be block or warn" % NAMESPACE, "write %s: {severity: block} or {severity: warn}" % NAMESPACE)
    return sev


# ---------------------------------------------------------------- territory index

class Index:
    """Policies of the repository and which Markdown files each territory claims."""

    def __init__(self, root, dials, matcher, pending=None):
        """pending: (relpath, text) of a document about to be written, if any."""
        self.root, self.dials, self.pending = root, dials, pending
        self.notes = []
        md = set(list_markdown(root))
        if pending:
            md.add(pending[0])
        self.md = sorted(md)
        rp = dials["root_policy"]
        root_text = self.text(rp)
        if root_text is None:
            raise Broken("%s names root_policy %r but no such file exists" % (DIALS_FILE, rp),
                         "create it, or point root_policy at the policy for policies")
        root_id = frontmatter_id(root_text)
        if root_id is None:
            raise Broken("root policy %r carries no readable id in its envelope" % rp,
                         "give it the envelope (id, type, title, status); its id names its namespace")
        ns = dials.get(root_id)
        root_terr = ns.get("territory") if isinstance(ns, dict) else None
        if not root_terr:
            raise Broken("root policy %r claims no territory in %s" % (root_id, DIALS_FILE),
                         "write %s: {territory: [<where policies live, including the root itself>]}"
                         " — nothing is governed until then" % root_id)
        in_root = matcher.match(root_terr, self.md)
        if rp not in in_root:
            raise Broken("root policy %r lies outside its own territory %s" % (rp, root_terr),
                         "every chain of governance ends at the root; widen %s.territory to include it" % root_id)
        self.root_id, self.root_territory = root_id, root_terr
        # policies: every Markdown document in the root's territory that carries an id
        self.policies = {}          # id -> {"path", "territory", "claims": {path: pattern}}
        for p in sorted(in_root):
            pid = frontmatter_id(self.text(p) or "")
            if pid is None:
                self.notes.append("%s lies in the root policy's territory but carries no readable id;"
                                  " it claims nothing until it does" % p)
                continue
            if pid in self.policies:
                self.notes.append("%s and %s both carry id %r; the first claims, the second is ignored"
                                  % (self.policies[pid]["path"], p, pid))
                continue
            ns = dials.get(pid)
            terr = ns.get("territory") if isinstance(ns, dict) else None
            self.policies[pid] = {"path": p, "territory": terr or [], "claims": {}}
        for pid, pol in self.policies.items():
            pol["claims"] = matcher.match(pol["territory"], self.md)
        # namespaces carrying a territory with no policy behind them (module namespaces excepted)
        self.void = {}              # namespace -> {path: pattern}
        for key, ns in dials.items():
            if key in KERNEL_KEYS or key in self.policies or key.startswith("const-"):
                continue
            if isinstance(ns, dict) and ns.get("territory"):
                self.void[key] = matcher.match(ns["territory"], self.md)

    def text(self, rel):
        if self.pending and rel == self.pending[0]:
            return self.pending[1]
        return read_text(self.root, rel)

    def governed(self):
        """Every Markdown path claimed by at least one policy."""
        out = set()
        for pol in self.policies.values():
            out.update(pol["claims"])
        return sorted(out)


# ---------------------------------------------------------------- the check

def examine(index, rel, text):
    """Findings for one document. Returns (findings, policy_id_or_None).

    A finding is (headline, why, fix). policy_id is None when the document is
    outside claimed territory (nothing was checked)."""
    for ns, claims in index.void.items():
        if rel in claims:
            raise Broken("%s: namespace %r claims territory but no policy with id %r lies in the"
                         " root policy's territory" % (DIALS_FILE, ns, ns),
                         "create the policy document there first, or remove the namespace"
                         " — a claim without a policy behind it governs nothing")
    matches = [(pid, pol["claims"][rel]) for pid, pol in index.policies.items() if rel in pol["claims"]]
    state, data, detail = read_frontmatter(text)
    declared = data.get(DECLARATION) if state == "ok" and isinstance(data.get(DECLARATION), str) else None
    if not matches and declared is None:
        return [], None
    findings = []
    # --- resolution (kernel governance binding)
    policy = None
    if declared is not None and not ID_RE.match(declared):
        declared = None  # reported below as an envelope field error
    if len(matches) == 1 and (declared is None or declared == matches[0][0]):
        policy = matches[0][0]
    elif len(matches) == 1:
        findings.append((
            "%s: declares policy %r but its path is claimed by %r (%s)" % (rel, declared, matches[0][0], matches[0][1]),
            "the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never override it",
            "remove '%s: %s' from the envelope, or move the file into the territory of %r: %s"
            % (DECLARATION, declared, declared, index.policies[declared]["territory"] if declared in index.policies else "(no such policy)")))
    elif len(matches) > 1:
        ids = [m[0] for m in matches]
        if declared in ids:
            policy = declared
        elif declared is None:
            findings.append((
                "%s: matched by %d policy territories: %s" % (rel, len(matches), ", ".join("%s (%s)" % m for m in matches)),
                "a document resolves to exactly one governing policy, or two rule sets compete",
                "narrow one territory in %s so the patterns no longer overlap; during a move, declare the intended one"
                " with '%s: <id>' in the envelope while an active task-record covers it" % (DIALS_FILE, DECLARATION)))
        else:
            findings.append((
                "%s: declares policy %r but its path is claimed by %s" % (rel, declared, ", ".join("%s (%s)" % m for m in matches)),
                "the path mapping is primary; a declaration may resolve an absent or ambiguous mapping, never override it",
                "declare one of the policies that claim the path, or remove the declaration and narrow the territories in %s" % DIALS_FILE))
    else:  # no path match, a declaration present
        if declared in index.policies:
            policy = declared
        else:
            findings.append((
                "%s: declares policy %r but no policy with that id lies in the root policy's territory %s"
                % (rel, declared, index.root_territory),
                "a governed document resolves to exactly one governing policy, or its rules are undefined",
                "declare the id of a policy that exists there, or drop the declaration and place the file in a claimed territory"))
    # --- envelope
    if state == "none":
        findings.append((
            "%s: no frontmatter envelope" % rel,
            "a governed document declares its authority in its envelope, or sessions guess it",
            "start the file with a YAML block between two '---' lines carrying id: <kebab-id>,"
            " type: current-state | task-record | non-authoritative, title: <one line>, status: active | inactive"))
    elif state == "unterminated":
        findings.append((
            "%s: frontmatter opened with '---' but never closed" % rel,
            "an unclosed envelope is unreadable by machines and by the next session",
            "close the YAML block with a line holding only '---'"))
    elif state == "invalid":
        findings.append((
            "%s: frontmatter is not valid YAML (%s)" % (rel, detail),
            "the envelope is read by machines, so it must parse",
            "repair the YAML between the '---' lines; keep the four fields id, type, title, status"))
    else:
        errs = field_errors(data)
        if errs:
            findings.append((
                "%s: envelope field(s) invalid: %s" % (rel, "; ".join(errs)),
                "the envelope is the one place a document's authority is declared, and it is read by machines",
                "set each named field: id = stable kebab-case (never changed, never reused);"
                " type = current-state (reconciled truth) | task-record (change delta) | non-authoritative (explanation);"
                " title = one line; status = active | inactive"))
        elif policy is not None or declared is not None:
            doc_id = data["id"]
            for other in index.governed():
                if other == rel:
                    continue
                if frontmatter_id(index.text(other) or "") == doc_id:
                    findings.append((
                        "%s: id %r is already carried by %s" % (rel, doc_id, other),
                        "an id is a stable identifier: two documents sharing one break every reference to it",
                        "give this document its own id, never a retired one; if this is a move, delete the old file in the same change"))
                    break
    return findings, policy


def fmt(findings):
    return "".join("RED: %s\n  why: %s\n  fix: %s\n" % f for f in findings)


# ---------------------------------------------------------------- modes

def hook_mode():
    try:
        event = json.load(sys.stdin)
    except ValueError as e:
        raise Broken("hook input is not JSON (%s)" % e, "this script reads a PreToolUse event on stdin")
    tool = event.get("tool_name")
    ti = event.get("tool_input") or {}
    path = ti.get("file_path")
    if tool not in ("Write", "Edit") or not isinstance(path, str) or not path:
        return skip("tool %r carries no file to examine" % tool)
    cwd = event.get("cwd") or os.getcwd()
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    path = os.path.realpath(path)
    if not path.lower().endswith(".md"):
        return skip("%s is not a Markdown document" % path)
    root = repo_root(path)
    if root is None:
        return skip("%s is not inside a git repository; the constitution is silent there" % path)
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    if rel.startswith(".."):
        return skip("%s is outside the repository" % path)
    dials = load_dials(root)
    if dials is None:
        return skip("no %s in %s: nothing is claimed" % (DIALS_FILE, root))
    severity = validate_dials(dials)
    if "root_policy" not in dials:
        return skip("%s has no root_policy: nothing is claimed" % DIALS_FILE)
    # the document as it will be after the write
    if tool == "Write":
        text = ti.get("content")
        if not isinstance(text, str):
            return skip("Write carries no content")
    else:
        current = read_text(root, rel)
        old, new = ti.get("old_string"), ti.get("new_string")
        if current is None or not isinstance(old, str) or not isinstance(new, str) or old not in current:
            return skip("the Edit cannot be applied to %s; the tool will report it" % rel)
        text = current.replace(old, new) if ti.get("replace_all") else current.replace(old, new, 1)
    matcher = Matcher()
    try:
        index = Index(root, dials, matcher, pending=(rel, text))
        findings, policy = examine(index, rel, text)
    finally:
        matcher.close()
    if policy is None and not findings:
        return skip("%s is outside claimed territory" % rel)
    if not findings:
        print("GREEN: %s: 1 document examined, governed by %s" % (NAMESPACE, policy))
        return EXIT_GREEN
    body = fmt(findings) + "RED: %d finding(s) — 1 document examined (%s)\n" % (len(findings), rel)
    if severity == "warn":
        note = ("%s: severity is warn: the write proceeds, but the finding stands"
                " and recurs on every write until fixed" % NAMESPACE)
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "additionalContext": body + note},
            "systemMessage": "%s (warn): %s" % (NAMESPACE, findings[0][0]),
        }))
        return EXIT_GREEN
    sys.stderr.write(body)
    return EXIT_RED


def skip(reason):
    print("GREEN: %s: 0 documents examined — %s" % (NAMESPACE, reason))
    return EXIT_GREEN


def scan_mode(start):
    root = repo_root(os.path.abspath(start))
    if root is None:
        raise Broken("%s is not inside a git repository" % start, "run --scan from a repository, or pass its path")
    dials = load_dials(root)
    if dials is None:
        print("GREEN: %s: 0 documents examined — no %s in %s: nothing is claimed" % (NAMESPACE, DIALS_FILE, root))
        return EXIT_GREEN
    validate_dials(dials)          # the scan ignores severity and always reports
    if "root_policy" not in dials:
        print("GREEN: %s: 0 documents examined — %s has no root_policy: nothing is claimed" % (NAMESPACE, DIALS_FILE))
        return EXIT_GREEN
    matcher = Matcher()
    try:
        index = Index(root, dials, matcher)
        for ns in sorted(index.void):
            raise Broken("%s: namespace %r claims territory but no policy with id %r lies in the"
                         " root policy's territory" % (DIALS_FILE, ns, ns),
                         "create the policy document there first, or remove the namespace"
                         " — a claim without a policy behind it governs nothing")
        findings, examined = [], 0
        for rel in index.md:
            f, policy = examine(index, rel, index.text(rel) or "")
            if policy is None and not f:
                continue
            examined += 1
            findings.extend(f)
    finally:
        matcher.close()
    for n in index.notes:
        print("note: " + n)
    tail = "%d governed document(s) examined, %d Markdown file(s) scanned, %d policies" % (
        examined, len(index.md), len(index.policies))
    if findings:
        sys.stdout.write(fmt(findings))
        print("RED: %d finding(s) — %s" % (len(findings), tail))
        return EXIT_RED
    print("GREEN: %s: %s" % (NAMESPACE, tail))
    return EXIT_GREEN


def main(argv):
    try:
        if not argv:
            return hook_mode()
        if argv[0] == "--scan" and len(argv) <= 2:
            return scan_mode(argv[1] if len(argv) == 2 else os.getcwd())
        raise Broken("unknown invocation %r" % " ".join(argv), "run with no arguments (hook) or --scan [<dir>]")
    except Broken as b:
        headline, fix = b.args
        sys.stderr.write("BROKEN: %s — fix: %s\n" % (headline, fix))
        sys.stderr.write("BROKEN: the check could not run — 0 documents examined\n")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
