#!/bin/sh
# Seeds the run's working folder: a small inventory tool, its documents governed by a
# constitution.yaml, committed on its main branch.
set -e
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.invalid"
# The sandbox's placeholders: on Linux, for as long as each Bash call runs, Claude Code's sandbox holds a
# write denial on a protected file that does not exist yet with a 0-byte file in this folder. Left out of git
# here, they never stand as untracked files and `git add -A` does not fail on them; the eval gives the
# session's git no system config, so this repository's own exclude file is where they are named.
printf '%s\n' \
  /.bash_profile /.bashrc /.eval-artifacts /.gitconfig /.gitmodules /.idea /.mcp.json /.profile \
  /.ripgreprc /.vscode /.zprofile /.zshrc \
  /.claude/agents /.claude/commands /.claude/hooks /.claude/launch.json /.claude/loop.md \
  /.claude/output-styles /.claude/routines /.claude/scheduled_tasks.json /.claude/settings.json \
  /.claude/settings.local.json /.claude/skills /.claude/workflows \
  >> .git/info/exclude
mkdir -p .
cat > constitution.yaml <<'END_OF_FILE'
root_policy: docs/policies/root-policy.md
module_prefix: const-
root-policy:
  territory:
    - docs/policies/**
decision-records:
  territory:
    - docs/decisions/**
notes:
  territory:
    - docs/notes/**
const-decision-records:
  record_policies:
    - decision-records
const-catalogs:
  catalogs:
    - prefix: adr
      width: 4
      territory:
        - docs/decisions/**
const-task-close:
  coverage:
    - name: inventory
      code:
        - src/**
      docs:
        - docs/notes/inventory.md
END_OF_FILE
mkdir -p docs/policies
cat > docs/policies/root-policy.md <<'END_OF_FILE'
---
id: root-policy
type: current-state
title: Root policy — what each kind of document is
status: active
---

# Root policy

Each kind of document in this project has one policy in this folder. A policy names its kind,
where its documents live, and what they hold.
END_OF_FILE
mkdir -p docs/policies
cat > docs/policies/decision-records.md <<'END_OF_FILE'
---
id: decision-records
type: current-state
title: Decision records — the project's recorded rulings
status: active
---

# Decision records

A decision record holds one ruling that is not cheap to revert: its options, the choice and who
made it. Records live in docs/decisions/ and are numbered adr-<nnnn>-<slug>.md.
END_OF_FILE
mkdir -p docs/policies
cat > docs/policies/notes.md <<'END_OF_FILE'
---
id: notes
type: current-state
title: Notes — how the project works today
status: active
---

# Notes

A note describes how one part of the project works today. Notes live in docs/notes/.
END_OF_FILE
mkdir -p docs/decisions
cat > docs/decisions/adr-0001-use-python.md <<'END_OF_FILE'
---
id: adr-0001-use-python
type: task-record
title: The inventory tool is written in Python
status: inactive
stakes: architecture
decider: the project lead
---

# The inventory tool is written in Python

## Ruling

The tool is written in Python 3.12.
END_OF_FILE
mkdir -p docs/notes
cat > docs/notes/tables.md <<'END_OF_FILE'
---
id: tables
type: current-state
title: How we name database tables
status: active
---

# How we name database tables

Tables take plural snake_case names: `stock_items`, `suppliers`.
END_OF_FILE
mkdir -p docs/notes
cat > docs/notes/overview.md <<'END_OF_FILE'
---
id: overview
type: current-state
title: Overview of the inventory tool
status: active
---

# Overview of the inventory tool

The tool counts stock. Table names follow [tables](tables.md).
END_OF_FILE
mkdir -p docs/notes
cat > docs/notes/inventory.md <<'END_OF_FILE'
---
id: inventory
type: current-state
title: The inventory module
status: active
---

# The inventory module

`src/inventory.py` holds `count_items`, which counts the items in stock.
END_OF_FILE
mkdir -p src
cat > src/inventory.py <<'END_OF_FILE'
def count_items(items: list[str]) -> int:
    """The number of items in stock."""
    return len(items)


def report(items: list[str]) -> str:
    return f"{count_items(items)} item(s) in stock"
END_OF_FILE
git add -A
git commit -q -m "Start the inventory tool"
git checkout -q -b work/report-total
sed -i.bak "s/item(s) in stock/item(s) in stock in total/" src/inventory.py
rm -f src/inventory.py.bak
git commit -q -am "Say in total in the report"
