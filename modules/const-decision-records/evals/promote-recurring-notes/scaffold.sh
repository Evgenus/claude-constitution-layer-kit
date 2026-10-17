#!/bin/sh
# Seeds the run's working folder: a small inventory tool, its documents governed by a
# constitution.yaml, committed on its main branch.
set -e
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.invalid"
mkdir -p .
cat > constitution.yaml <<'END_OF_FILE'
root_policy: docs/policies/root-policy.md
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
echo "# one" >> src/inventory.py
git commit -q -am "Add helper one" -m "Routine: named the helper in snake_case, as the other helpers."
echo "# two" >> src/inventory.py
git commit -q -am "Add helper two" -m "Routine: named the helper in snake_case, as the other helpers."
echo "# three" >> src/inventory.py
git commit -q -am "Add helper three" -m "Routine: named the helper in snake_case, as the other helpers."
echo "# four" >> src/inventory.py
git commit -q -am "Add helper four" -m "Routine: named the helper in snake_case, as the other helpers."
