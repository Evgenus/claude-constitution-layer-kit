#!/usr/bin/env bash
# Fixtures of const-meta-types. Builds the fixture consumer (fixtures/repo) in a temporary git
# repository and drives the gate exactly as Claude Code does: a PreToolUse event on stdin.
# Case inputs are red.txt / green.txt: content the runner writes as Markdown into that consumer;
# they are not Markdown documents of any repository.
#
#   1-9   one red -> green pair per gate class (the red input is blocked with the designed
#         message, the green input passes), including the root policy itself (case 9)
#   10    an Edit is judged on the document as it will be after the edit
#   11-13 exit-code split: a configuration failure exits 1 with BROKEN, never 2, never 0
#   14-15 the examined count is printed on green and on a skip
#   16    a negated pattern (!path) excludes a file from a territory
#   17    severity warn: the finding is reported on stdout as JSON and the write proceeds
#   18-19 scan mode: reports the finding with counts, ignores severity warn
#
# Usage: tests/run.sh    (from the module root or anywhere; needs git, python3, PyYAML)
set -u
here="$(cd "$(dirname "$0")" && pwd)"
gate="$here/../scripts/check-governed-document.sh"
pass=0; fail=0

work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
repo="$work/consumer"
cp -R "$here/fixtures/repo" "$repo"
git -C "$repo" init -q && git -C "$repo" add -A && git -C "$repo" -c user.name=fixture -c user.email=f@x commit -qm fixture

# event <tool> <relative path> <content file> [<old> <new>]  -> PreToolUse JSON on stdout
event() {
  python3 - "$repo" "$@" <<'PY'
import json, os, sys
repo, tool, rel, content = sys.argv[1:5]
ti = {"file_path": os.path.join(repo, rel)}
if tool == "Write":
    ti["content"] = open(content, encoding="utf-8").read()
else:
    ti.update({"old_string": sys.argv[5], "new_string": sys.argv[6], "replace_all": False})
print(json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": repo, "tool_input": ti}))
PY
}

# run <expected exit> <must-match regex> -- <command...>  (stdin: $work/event, written by event)
run() {
  want=$1; pattern=$2; shift 3
  out="$("$@" 2>&1 <"$work/event")"; code=$?
  if [ "$code" -eq "$want" ] && grep -qE -- "$pattern" <<<"$out"; then
    pass=$((pass+1)); echo "ok   $name"
  else
    fail=$((fail+1)); echo "FAIL $name (exit $code, wanted $want, wanted /$pattern/)"; sed 's/^/     | /' <<<"$out"
  fi
}

n=0
for case in "$here"/fixtures/cases/*/; do
  n=$((n+1)); c="$(basename "$case")"; target="$(cat "$case/target")"
  name="$n $c red"; event Write "$target" "$case/red.txt" >"$work/event"; run 2 '^RED: ' -- /bin/sh "$gate"
  name="$n $c green"; event Write "$target" "$case/green.txt" >"$work/event"; run 0 '1 document examined, governed by' -- /bin/sh "$gate"
done

# 10. Edit: the result of the edit is judged, not the edit's strings
mkdir -p "$repo/docs/notes"; cp "$here/fixtures/cases/01-envelope-missing/green.txt" "$repo/docs/notes/a.md"
name="10 edit removing type red"; event Edit docs/notes/a.md - $'type: non-authoritative\n' '' >"$work/event"; run 2 'type missing' -- /bin/sh "$gate"
name="10 edit in the body green"; event Edit docs/notes/a.md - '# Note A' '# Note A, edited' >"$work/event"; run 0 'governed by notes-policy' -- /bin/sh "$gate"

# 11-13. exit-code split
cp "$repo/constitution.yaml" "$work/dials.bak"
printf 'root-policy: [\n' > "$repo/constitution.yaml"
name="11 malformed dials file is BROKEN, exit 1"; event Write docs/notes/a.md "$here/fixtures/cases/01-envelope-missing/green.txt" >"$work/event"; run 1 '^BROKEN: constitution.yaml is not valid YAML' -- /bin/sh "$gate"
cp "$work/dials.bak" "$repo/constitution.yaml"
printf 'ghost:\n  territory: ["docs/ghost/**"]\n' >> "$repo/constitution.yaml"
name="12 territory without a policy is BROKEN, exit 1"; event Write docs/ghost/g.md "$here/fixtures/cases/01-envelope-missing/red.txt" >"$work/event"; run 1 "^BROKEN: constitution.yaml: namespace 'ghost'" -- /bin/sh "$gate"
cp "$work/dials.bak" "$repo/constitution.yaml"
mkdir -p "$work/nopython"; ln -s "$(command -v dirname)" "$work/nopython/dirname"
name="13 missing python3 is BROKEN, exit 1"; event Write docs/notes/a.md "$here/fixtures/cases/01-envelope-missing/red.txt" >"$work/event"; run 1 '^BROKEN: const-meta-types needs python3' -- env PATH="$work/nopython" /bin/sh "$gate"

# 14-15. examined count
name="14 outside claimed territory: 0 examined, exit 0"; event Write README.md "$here/fixtures/cases/01-envelope-missing/red.txt" >"$work/event"; run 0 '0 documents examined — README.md is outside claimed territory' -- /bin/sh "$gate"
name="15 not Markdown: 0 examined, exit 0"; event Write docs/notes/a.txt "$here/fixtures/cases/01-envelope-missing/red.txt" >"$work/event"; run 0 '0 documents examined — .* is not a Markdown document' -- /bin/sh "$gate"

# 16. negation: a file-level !pattern carves one file out of a territory
printf 'notes-policy:\n  territory: ["docs/notes/**", "!docs/notes/secret.md"]\n' >> "$repo/constitution.yaml"
name="16 negated pattern excludes the file, exit 0"; event Write docs/notes/secret.md "$here/fixtures/cases/01-envelope-missing/red.txt" >"$work/event"; run 0 '0 documents examined — docs/notes/secret.md is outside claimed territory' -- /bin/sh "$gate"
cp "$work/dials.bak" "$repo/constitution.yaml"

# 17. severity warn
printf 'const-meta-types:\n  severity: warn\n' >> "$repo/constitution.yaml"
name="17 warn: finding reported as JSON, write proceeds, exit 0"; event Write docs/notes/a.md "$here/fixtures/cases/01-envelope-missing/red.txt" >"$work/event"; run 0 '"additionalContext": "RED: docs/notes/a.md: no frontmatter envelope' -- /bin/sh "$gate"

# 18-19. scan mode (severity still warn: the scan ignores it)
cp "$here/fixtures/cases/01-envelope-missing/red.txt" "$repo/docs/notes/a.md"; : >"$work/event"
name="18 scan reports the finding with counts, exit 2 despite warn"; run 2 'RED: 1 finding\(s\) — 4 governed document\(s\) examined, 4 Markdown file\(s\) scanned, 3 policies' -- python3 "$here/../scripts/check-governed-document.py" --scan "$repo"
cp "$here/fixtures/cases/01-envelope-missing/green.txt" "$repo/docs/notes/a.md"
name="19 scan green with counts"; run 0 'GREEN: const-meta-types: 4 governed document\(s\) examined' -- python3 "$here/../scripts/check-governed-document.py" --scan "$repo"

echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
