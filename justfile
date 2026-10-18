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

# Run a module's tests natively, `coverage run -m pytest`: one line per test, then the coverage of the module's scripts and the shared const_gate, branches included. One module per run, since a run of two stops at collection; with no module, each in turn. Extra arguments go to pytest (-n auto, -k <expr>, -x), so a module must be named to pass them. Needs coverage.py and pytest, pytest-xdist for -n, installed for this python3; its data stays in a temporary folder
test module="" *args:
    #!/bin/sh
    set -u
    root="{{justfile_directory()}}"
    modules="{{module}}"
    [ -n "$modules" ] || modules=$(cd "$root/modules" && ls -d const-*)
    worst=0
    for m in $modules; do
        work=$(mktemp -d)
        printf '[run]\nbranch = true\nparallel = true\npatch = subprocess\ndata_file = %s/data\nsource =\n    %s/modules/%s/scripts\n    %s/shared/const_gate\n' "$work" "$root" "$m" "$root" > "$work/rc"
        echo "== $m"
        (cd "$root" && python3 -m coverage run --rcfile "$work/rc" -m pytest "modules/$m/tests" -p no:cacheprovider -W error -v {{args}})
        code=$?
        python3 -m coverage combine --quiet --rcfile "$work/rc" "$work" >/dev/null 2>&1
        (cd "$root" && python3 -m coverage report --rcfile "$work/rc")
        rm -rf "$work"
        [ "$code" -gt "$worst" ] && worst=$code
    done
    exit "$worst"

# Run the eval cases of the modules named, or of every module, through scripts/run-evals.py: each case in a throwaway container on the pinned Claude Code and model, logged in with a subscription token from `claude setup-token` and never billed by usage. The token file's path comes from KIT_EVAL_TOKEN_FILE; the file must be readable by its owner alone. Verbose: for each case, what the model is told and each grader's rule, the container's output as it comes, then per run the start hooks' text, every tool call and reply of the model, and each grader's verdict with its explanation. A module's attempt is added to scripts/eval-receipts.json, which you commit, unless its receipt already passes for these files and this run passed too; then nothing is written. Needs Docker running; the kit's tree must be committed
evals *modules:
    #!/bin/sh
    set -u
    token="${KIT_EVAL_TOKEN_FILE:-}"
    if [ -z "$token" ]; then
        echo "BROKEN: KIT_EVAL_TOKEN_FILE is not set — the evals log in with a subscription token, never an API key — fix: claude setup-token, save the token as CLAUDE_CODE_OAUTH_TOKEN=<token> in a file only you can read (chmod 600), then export KIT_EVAL_TOKEN_FILE=<that file>" >&2
        exit 1
    fi
    set --
    for m in {{modules}}; do set -- "$@" --module "$m"; done
    cd "{{justfile_directory()}}" && exec python3 scripts/run-evals.py --token-file "$token" --verbose "$@"

# Tell which modules' eval receipts are missing, stale or failing, as CI would: scripts/check-eval-receipts.py, no run and no token
eval-receipts:
    python3 scripts/check-eval-receipts.py
