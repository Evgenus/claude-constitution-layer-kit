#!/bin/sh
# Kit tooling, never shipped in a module: the one list of the kit's checks. CI builds one job per
# job from it (.github/workflows/gates.yml), the gate-list-runner agent runs it locally, and
# scripts/check-gate-lists.py holds that every scan a module declares stands in it.
#   sh scripts/gate-list.sh --names [gate|extra|all|<job>]  the entries, one per line, in order (default all)
#   sh scripts/gate-list.sh --json                     every job as one JSON array, for CI's matrix
#   sh scripts/gate-list.sh --show <entry>             the commands of one entry, one per line
#   sh scripts/gate-list.sh --run <entry>|<job>        run one entry's commands, or every entry of a job, in turn, from the kit root
# The gates are the list the kit runs before a merge; the extras are the fixtures, lint and types.
# A CI job is a module — its scan, its install, its fixtures, its lint and its types — or `kit`, every
# entry no module holds; an entry is in exactly one job, and one no line of job() maps falls into `kit`.
# The jobs are read from the entries, never listed apart, so no entry is left out of CI. A module's scan
# reads the whole tree, so a red scan on a module's job means the tree breaks that module's rule, not
# that the module's code is broken; the annotation names the entry.
# The install-<module> gates need Claude Code's `claude` on PATH and no Claude account login; an install
# from a private remote needs git's credentials for it.
# --run runs every command of the entry, and every entry of the job, even after a red one and prints
# each command's exit; it exits 0 when every command did, else 2 when every failing command exited 2
# (a finding), else 1. A job's run in GitHub Actions folds each entry's log, annotates each entry that
# did not exit 0 and writes one summary line per entry. CI reruns a whole job; an entry is run alone
# with --run <entry>, where an install entry run by hand installs from the working folder unless
# CONSTITUTION_KIT_INSTALL_FROM names a source, as CI's does. The other modes exit 0, or 1 on a misinvocation.

MODULES="const-catalogs const-decision-records const-doc-budgets const-interaction const-language
const-locations const-meta-types const-questions const-referencing const-styling const-task-close"
GATES="references meta-types catalogs decision-records open-questions style language budgets
list-handles carry-lists shared-links yaml-style module-links aspects portability gate-lists
schema-mirror dials-schema bare-install $(for m in $MODULES; do printf 'install-%s ' "$m"; done)task-close"
EXTRAS="branch-gate $(for m in $MODULES; do printf 'fixtures-%s lint-%s types-%s ' "$m" "$m" "$m"; done)lint types"

job() {
    case "$1" in
        references) echo const-referencing ;;
        meta-types) echo const-meta-types ;;
        catalogs) echo const-catalogs ;;
        decision-records) echo const-decision-records ;;
        open-questions) echo const-questions ;;
        style) echo const-styling ;;
        language) echo const-language ;;
        budgets) echo const-doc-budgets ;;
        list-handles) echo const-interaction ;;
        task-close) echo const-task-close ;;
        install-* | fixtures-* | lint-* | types-*) echo "${1#*-}" ;;
        *) echo kit ;;
    esac
}

jobs() {
    for n in $GATES $EXTRAS; do job "$n"; done | sort -u
}

members() {
    for n in $GATES $EXTRAS; do [ "$(job "$n")" = "$1" ] && echo "$n"; done
}

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
        install-* | fixtures-* | lint-* | types-*)
            for m in $MODULES; do
                [ "${1#*-}" = "$m" ] || continue
                case "$1" in
                    install-*) echo "python3 scripts/check-bare-install.py --module $m" ;;
                    fixtures-*) echo "python3 modules/$m/tests/run.py" ;;
                    lint-*)
                        echo "python3 -m ruff format --check modules/$m"
                        echo "python3 -m ruff check modules/$m" ;;
                    types-*)
                        for p in modules/"$m"/scripts/*_gate; do
                            [ "${p##*/}" != const_gate ] && [ -d "$p" ] && echo "cd modules/$m/scripts && python3 -m mypy --strict ${p##*/}"
                        done
                        echo "cd modules/$m/tests && MYPYPATH=../scripts python3 -m mypy --strict *.py" ;;
                esac
                return 0
            done
            return 1 ;;
        task-close) echo "sh modules/const-task-close/scripts/check-task-close.sh --scan" ;;
        branch-gate) echo "sh scripts/git-hooks/tests/run.sh" ;;
        lint)
            echo "python3 -m ruff format --check scripts shared"
            echo "python3 -m ruff check scripts shared" ;;
        types)
            echo "cd shared && python3 -m mypy --strict const_gate"
            echo "cd scripts && python3 -m mypy --strict check-carry-lists.py check-shared-links.py check-yaml-style.py check-module-links.py check-aspects.py check-portability.py check-gate-lists.py check-bare-install.py check-dials-schema.py"
            echo "cd scripts && MYPYPATH=../modules/const-meta-types/scripts:../modules/const-decision-records/scripts python3 -m mypy --strict check-schema-mirror.py" ;;
        *) return 1 ;;
    esac
}

misuse() {
    printf 'BROKEN: %s — fix: sh scripts/gate-list.sh --names [gate|extra|all|<job>] | --json | --show <entry> | --run <entry>|<job>\n' "$1" >&2
    exit 1
}

# run_entry <entry>: run the entry's commands in turn, print each exit, and fold its worst into $worst.
run_entry() {
    list=$(commands "$1") && [ -n "$list" ] || {
        echo "BROKEN: entry $1 has no commands — fix: give it an arm in commands() of scripts/gate-list.sh"
        worst=1
        return
    }
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
}

top=$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ] && cd "$top" || misuse "not inside a git repository — run it from a clone of the kit"

case "$1" in
    --names)
        case "${2:-all}" in
            gate) set -- $GATES ;;
            extra) set -- $EXTRAS ;;
            all) set -- $GATES $EXTRAS ;;
            *)
                jobs | grep -qx -- "$2" || misuse "unknown group or job '$2'"
                set -- $(members "$2") ;;
        esac
        for n in "$@"; do echo "$n"; done ;;
    --json)
        sep=""; printf '['
        for j in $(jobs); do printf '%s"%s"' "$sep" "$j"; sep=","; done
        printf ']\n' ;;
    --show)
        [ -n "$2" ] || misuse "--show needs an entry"
        commands "$2" || misuse "no entry '$2' in the list" ;;
    --run)
        [ -n "$2" ] || misuse "--run needs an entry or a job"
        worst=0
        if commands "$2" >/dev/null; then
            run_entry "$2"
            exit "$worst"
        fi
        jobs | grep -qx -- "$2" || misuse "no entry or job '$2' in the list"
        all=0
        for n in $(members "$2"); do
            worst=0
            [ "$GITHUB_ACTIONS" = true ] && echo "::group::$n"
            run_entry "$n"
            [ "$GITHUB_ACTIONS" = true ] && echo "::endgroup::"
            echo "gate-list: entry $n — exit $worst"
            if [ "$GITHUB_ACTIONS" = true ]; then
                [ "$worst" -eq 0 ] || echo "::error title=$n::entry $n exited $worst — its log is the fold named $n; run it alone with sh scripts/gate-list.sh --run $n"
                [ -z "$GITHUB_STEP_SUMMARY" ] || echo "- \`$n\`: exit $worst" >>"$GITHUB_STEP_SUMMARY"
            fi
            case $worst in
                0) ;;
                2) [ "$all" -eq 1 ] || all=2 ;;
                *) all=1 ;;
            esac
        done
        exit "$all" ;;
    *) misuse "unknown mode '${1:-}'" ;;
esac
