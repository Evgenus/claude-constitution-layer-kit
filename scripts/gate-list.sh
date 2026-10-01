#!/bin/sh
# Kit tooling, never shipped in a module: the one list of the kit's checks. CI builds one job per
# entry from it (.github/workflows/gates.yml), the gate-list-runner agent runs it locally, and
# scripts/check-gate-lists.py holds that every scan a module declares stands in it.
#   sh scripts/gate-list.sh --names [gate|extra|all]   the entries, one per line, in order (default all)
#   sh scripts/gate-list.sh --json                     every entry as one JSON array, for CI's matrix
#   sh scripts/gate-list.sh --show <entry>             the commands of one entry, one per line
#   sh scripts/gate-list.sh --run <entry>              run one entry's commands in turn, from the kit root
# The gates are the list the kit runs before a merge; the extras are the fixtures, lint and types.
# The install-<module> gates need Claude Code's `claude` on PATH and no Claude account login; an install
# from a private remote needs git's credentials for it.
# --run runs every command of the entry even after a red one and prints each command's exit; it
# exits 0 when every command did, else 2 when every failing command exited 2 (a finding), else 1.
# The other modes exit 0, or 1 on a misinvocation.

MODULES="const-catalogs const-decision-records const-doc-budgets const-interaction const-language
const-locations const-meta-types const-questions const-referencing const-styling const-task-close"
GATES="references meta-types catalogs decision-records open-questions style language budgets
list-handles carry-lists shared-links yaml-style module-links aspects portability gate-lists
schema-mirror dials-schema bare-install $(for m in $MODULES; do printf 'install-%s ' "$m"; done)task-close"
EXTRAS="branch-gate $(for m in $MODULES; do printf 'fixtures-%s ' "$m"; done)lint types"

commands() {
    case "$1" in
        references) echo "sh modules/const-referencing/scripts/check-references.sh --scan" ;;
        meta-types) echo "python3 modules/const-meta-types/scripts/check-governed-document.py --scan" ;;
        catalogs) echo "python3 modules/const-catalogs/scripts/check-catalog-item.py --scan" ;;
        decision-records) echo "python3 modules/const-decision-records/scripts/check-decision-record.py --scan" ;;
        open-questions) echo "sh modules/const-questions/scripts/check-open-questions.sh --scan" ;;
        style) echo "sh modules/const-styling/scripts/check-style.sh --scan" ;;
        language) echo "sh modules/const-language/scripts/check-language.sh --scan" ;;
        budgets) echo "sh modules/const-doc-budgets/scripts/check-budgets.sh --scan" ;;
        list-handles) echo "sh modules/const-interaction/scripts/check-list-handles.sh --scan" ;;
        carry-lists | shared-links | yaml-style | module-links | aspects | portability | gate-lists | dials-schema)
            echo "python3 scripts/check-$1.py"
            echo "python3 scripts/check-$1.py --self-test" ;;
        schema-mirror) echo "python3 scripts/check-schema-mirror.py" ;;
        bare-install) echo "python3 scripts/check-bare-install.py --self-test" ;;
        install-*)
            for m in $MODULES; do
                [ "$1" = "install-$m" ] && echo "python3 scripts/check-bare-install.py --module $m" && return 0
            done
            return 1 ;;
        task-close) echo "sh modules/const-task-close/scripts/check-task-close.sh --scan" ;;
        branch-gate) echo "sh scripts/git-hooks/tests/run.sh" ;;
        fixtures-*)
            for m in $MODULES; do
                [ "$1" = "fixtures-$m" ] && echo "python3 modules/$m/tests/run.py" && return 0
            done
            return 1 ;;
        lint)
            echo "python3 -m ruff format --check modules scripts shared"
            echo "python3 -m ruff check modules scripts shared" ;;
        types)
            echo "cd shared && python3 -m mypy --strict const_gate"
            for m in $MODULES; do
                for p in modules/"$m"/scripts/*_gate; do
                    [ "${p##*/}" != const_gate ] && [ -d "$p" ] && echo "cd modules/$m/scripts && python3 -m mypy --strict ${p##*/}"
                done
                echo "cd modules/$m/tests && MYPYPATH=../scripts python3 -m mypy --strict *.py"
            done
            echo "cd scripts && python3 -m mypy --strict check-carry-lists.py check-shared-links.py check-yaml-style.py check-module-links.py check-aspects.py check-portability.py check-gate-lists.py check-bare-install.py check-dials-schema.py"
            echo "cd scripts && MYPYPATH=../modules/const-meta-types/scripts:../modules/const-decision-records/scripts python3 -m mypy --strict check-schema-mirror.py" ;;
        *) return 1 ;;
    esac
}

misuse() {
    printf 'BROKEN: %s — fix: sh scripts/gate-list.sh --names [gate|extra|all] | --json | --show <entry> | --run <entry>\n' "$1" >&2
    exit 1
}

top=$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ] && cd "$top" || misuse "not inside a git repository — run it from a clone of the kit"

case "$1" in
    --names)
        case "${2:-all}" in
            gate) set -- $GATES ;;
            extra) set -- $EXTRAS ;;
            all) set -- $GATES $EXTRAS ;;
            *) misuse "unknown group '$2'" ;;
        esac
        for n in "$@"; do echo "$n"; done ;;
    --json)
        sep=""; printf '['
        for n in $GATES $EXTRAS; do printf '%s"%s"' "$sep" "$n"; sep=","; done
        printf ']\n' ;;
    --show)
        [ -n "$2" ] || misuse "--show needs an entry"
        commands "$2" || misuse "no entry '$2' in the list" ;;
    --run)
        [ -n "$2" ] || misuse "--run needs an entry"
        list=$(commands "$2") || misuse "no entry '$2' in the list"
        worst=0
        while IFS= read -r c; do
            (sh -c "$c") </dev/null; code=$?
            echo "gate-list: exit $code — $c"
            case $code in
                0) ;;
                2) [ "$worst" -eq 1 ] || worst=2 ;;
                *) worst=1 ;;
            esac
        done <<EOF
$list
EOF
        exit "$worst" ;;
    *) misuse "unknown mode '${1:-}'" ;;
esac
