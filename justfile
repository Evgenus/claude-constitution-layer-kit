# Shortcuts for working in the kit. Kit tooling, never shipped in a module.

# Browse every gate's output log as one timeline; extra arguments go to lnav
logs *args:
    lnav {{args}} local/gate-logs

# Print the module metrics report, a report and never a check; extra arguments go to the script (--json <path>|-)
metrics *args:
    python3 scripts/metrics.py {{args}}

# List the most complex functions of the modules' own code, the script's default unless a limit is given; extra arguments go to the script (--json <path>|-)
complexity limit="" *args:
    python3 scripts/metrics.py --complexity {{limit}} {{args}}

# Print the fixture coverage of each module, a report and never a check: runs every fixtures entry under coverage.py, minutes in all, coverage.py and pytest installed for this python3; extra arguments go to the script (--module <name>, --from <folder>, --json <path>|-)
coverage *args:
    python3 scripts/module-coverage.py {{args}}
