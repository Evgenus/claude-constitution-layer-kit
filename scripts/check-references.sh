#!/usr/bin/env bash
# Interim reference gate (requirements A5.5–A5.7, decision reference-forms).
# Fails when a kit document cites another document by a bare handle instead of a link,
# or when any link or anchor does not resolve. Run from the repository root.
# Examines tracked and untracked (non-ignored) files, so a new document is checked before it is staged.
set -u
cd "$(dirname "$0")/.."
fail=0
docs=$(git ls-files --cached --others --exclude-standard '*.md' | wc -l | tr -d ' ')
links=0
red() { echo "RED: $1"; echo "  why: $2"; echo "  fix: $3"; fail=1; }

if [ "$docs" -eq 0 ]; then
  red "no documents examined" "a check that inspects nothing reports green vacuously" \
      "run from the root of a kit checkout whose markdown files are tracked by git"
else
  links=$(git ls-files --cached --others --exclude-standard '*.md' | xargs grep -ohE '\]\([^)]+\)' | wc -l | tr -d ' ')
fi

# Strip markdown links and frontmatter so only bare (unlinked) handles remain.
bare() { perl -0pe 's/\A---\n.*?\n---\n//s; s/\[[^\]]*\]\([^)]*\)//g' "$1"; }

for f in $(git ls-files --cached --others --exclude-standard '*.md'); do
  b="$(bare "$f")"
  case "$f" in docs/rollout-plan.md) ;; *)
    if grep -nE '\bM[0-9]+\b' <<<"$b" | grep -v '^[0-9]*:title:' >/dev/null; then
      red "$f cites a module as M<n>" "M<n> resolves only inside the rollout plan (docs/decisions/reference-forms.md#r7)" \
          "link the module's spec: [\`const-<name>\`](<rel>/docs/rollout-plan.md#const-<name>)"
    fi
    if grep -nE '\bA[0-9]+\.[0-9]+' <<<"$b" >/dev/null; then
      red "$f cites a requirement row bare" "rows resolve only inside the matrix (docs/decisions/reference-forms.md#r6)" \
          "link it: [requirement A5.3](<rel>/docs/rollout-plan.md#a5-3)"
    fi
  esac
  case "$f" in kernel/CONVENTIONS.md) ;; *)
    if grep -nE '§ ?[0-9]' <<<"$b" >/dev/null; then
      red "$f cites a kernel section bare" "§n is a local alias inside the kernel only (docs/decisions/reference-forms.md#r2)" \
          "link it: [kernel §4](<rel>/kernel/CONVENTIONS.md#k4)"
    fi
  esac
  case "$f" in CLAUDE.md) ;; *)
    if grep -nEi '\blaws? [0-9]' <<<"$b" >/dev/null; then
      red "$f cites a law bare" "laws are cited verbosely and linked (docs/decisions/reference-forms.md#r17)" \
          "link it: [law 4 of CLAUDE.md](<rel>/CLAUDE.md#law-4)"
    fi
  esac
  for id in $(git ls-files --cached --others --exclude-standard '*.md' | xargs grep -lE '^id: ' | xargs -n1 sed -n 's/^id: \([a-z0-9-]*\)$/\1/p'); do
    own="$(sed -n 's/^id: \([a-z0-9-]*\)$/\1/p' "$f" | head -1)"
    [ "$id" = "$own" ] && continue
    if grep -nF "\`$id\`" <<<"$b" >/dev/null; then
      red "$f cites governed document $id by bare id" "id references are links (docs/decisions/reference-forms.md#r1)" \
          "link it: [$id](<rel>/<path-of-$id>)"
    fi
  done
done

if [ "$docs" -eq 0 ]; then
  : # nothing to hand lychee; the red above already names the cause
elif command -v lychee >/dev/null; then
  lychee --offline --include-fragments --no-progress $(git ls-files --cached --others --exclude-standard '*.md') || \
    red "a link or anchor does not resolve" "no merge introduces a broken reference (requirement A5.3)" \
        "fix the target path or anchor named above"
else
  red "lychee not installed" "requirement A5.3 needs lychee >= 0.24.2" "install lychee and rerun"
fi
[ $fail -eq 0 ] && echo "GREEN: references resolve — $docs documents, $links links examined"
exit $fail
