# Shortcuts for working in the kit. Kit tooling, never shipped in a module.

# Browse every gate's output log as one timeline; extra arguments go to lnav
logs *args:
    lnav {{args}} local/gate-logs

# Print the module metrics report, a report and never a check; extra arguments go to the script (--json <path>|-)
metrics *args:
    python3 scripts/metrics.py {{args}}

# List the most complex functions of the modules' own code, 20 unless a limit is given; extra arguments go to the script (--json <path>|-)
complexity limit="20" *args:
    python3 scripts/metrics.py --complexity {{limit}} {{args}}
