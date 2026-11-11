#!/bin/sh
# Kit tooling, never shipped in a module: the one list of the kit's checks. CI builds one job per
# job from it (.github/workflows/gates.yml), the gate-list-runner agent runs it locally, and
# scripts/check-gate-lists.py holds that every scan a module declares stands in it, in that module's job,
# and that MODULES names exactly the module folders, each named const-<aspect>, named so by its
# manifest, listed once in the marketplace and enabled in the kit's settings, neither naming a plugin
# that is no module folder.
#   sh scripts/gate-list.sh --names [gate|extra|all|<job>]  the entries, one per line, in order (default all)
#   sh scripts/gate-list.sh --json                     every job as one JSON array, for CI's matrix
#   sh scripts/gate-list.sh --show <entry>             the commands of one entry, one per line
#   sh scripts/gate-list.sh --run <entry>|<job>        run one entry's commands, or every entry of a job, in turn, from the kit root
# The gates are the list the kit runs before a merge; the extras are the fixtures, lint and types: each
# module's, the branch gate's fixture, the fixture of scripts/setup-claude.sh, and the kit's own lint of scripts/ and shared/ and types of its
# checks and shared/constitution_layer_kit, whose subpackage testing holds the shared test files, typed with the package, and the fixture gate
# of another layer, scripts/layered-fixture/, which the gate `layered-items` runs the shared items against. A module's fixtures
# run through `check-aspects.py --run --module <module>`, which collects its tests under pytest, runs
# them once, prints pytest's own output whenever it exits other than 0, and holds the items against the
# module's acceptance table both ways (decision dec-0080-fixtures-run-through-check-aspects).
# A CI job is a module — its scan, its install, its session-load check, its fixtures, its lint and its types — or `install-guide`,
# the run of the install guide, or `kit`, every other entry no module holds; an entry is in exactly one job, and one no line of job() maps falls into `kit`.
# CI also measures a sample of each module's mutants, in jobs of the workflow that are no job of this list and
# hold no entry, since they judge nothing (scripts/module-mutation.py).
# The jobs are read from the entries, never listed apart, so no entry is left out of CI. A module's
# scan reads the whole tree, or for task-close the change's whole range, so a red scan on a module's
# job means the tree, or the change, breaks that module's rule, not that the module's code is broken;
# the annotation names the entry. The entry `profiles` of `kit` runs every module's scan too, on throwaway
# repositories that hold a profile: a module's scan red there means a profile breaks that module's rule.
# The install-<module> and session-<module> gates and the guide gate need the `claude` that scripts/claude-code.version pins on
# PATH and no Claude account login: on any other version they fail to run, unless CONSTITUTION_KIT_ANY_CLAUDE=1,
# when they run with a note naming both versions on every headline line of their report after the version
# check; each installs from the change's GitHub branch, which git reads with no credentials on the kit's
# public remote. A clone runs `sh scripts/setup-claude.sh` once, and again after the pin moves, which installs the
# pinned version into <main>/.claude-code-pinned, <main> the folder that holds git's common directory, so
# every worktree shares it; --run then puts that folder's node_modules/.bin first on PATH for the commands
# of the install-<module> and session-<module> entries and the guide alone, and only when its `claude` is executable. Every
# other entry, and every run where the folder does not exist, as in CI, runs as it would without it.
# --run runs every command of the entry, and every entry of the job, even after a red one and prints
# each command's exit; it exits 0 when every command did, else 2 when every failing command exited 2
# (a finding), else 1; an entry with no commands is a BROKEN line and exit 1. A job's run in GitHub
# Actions folds each entry's log, annotates each entry that did not exit 0 and writes one summary line
# per entry. CI reruns a whole job; an entry is run alone with --run <entry>, where an install entry
# run by hand installs from the working folder unless CONSTITUTION_KIT_INSTALL_FROM names a source, as
# CI's does. The other modes exit 0, or 1 on a misinvocation.

MODULES="const-catalogs const-change-cost const-decision-records const-doc-budgets const-interaction const-language
const-locations const-meta-types const-questions const-referencing const-styling const-task-close"
GATES="references meta-types catalogs decision-records open-questions style language budgets
list-handles carry-lists shared-links shared-package yaml-style module-links handle-forms aspects portability gate-lists
schema-mirror copies dials-schema profiles resolved-paths layered-items eval-receipts rollout-status run-evals module-mutation bare-install session-load guide $(for m in $MODULES; do printf 'install-%s session-%s ' "$m" "$m"; done)task-close"
EXTRAS="branch-gate setup-claude $(for m in $MODULES; do printf 'fixtures-%s lint-%s types-%s ' "$m" "$m" "$m"; done)lint types layered-fixture"

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
        guide) echo install-guide ;;
        install-* | session-const-* | fixtures-* | lint-* | types-*) echo "${1#*-}" ;;
        *) echo kit ;;
    esac
}

jobs() {
    for n in $GATES $EXTRAS; do job "$n"; done | sort -u
}

is_entry() {
    for n in $GATES $EXTRAS; do [ "$n" = "$1" ] && return 0; done
    return 1
}

members() {
    for n in $GATES $EXTRAS; do [ "$(job "$n")" = "$1" ] && echo "$n"; done
}

# scan <command>: a module's scan with the change's own shared code on PYTHONPATH. A plugin holds no shared
# code (decision dec-0099-shared-code-installed-as-a-pip-package, R7): its entry file imports the package that
# python3 finds, and a scan of the gate list must run the shared code of the change, never a release a person
# installed or none, so the kit's shared/ comes first on the path for the scan alone.
scan() { printf '%s\n' "PYTHONPATH=\"\$PWD/shared\" $*"; }

commands() {
    case "$1" in
        references) scan sh modules/const-referencing/plugin/scripts/check-references.sh --scan ;;
        meta-types) scan python3 modules/const-meta-types/plugin/scripts/check-governed-document.py --scan ;;
        catalogs) scan python3 modules/const-catalogs/plugin/scripts/check-catalog-item.py --scan ;;
        decision-records) scan python3 modules/const-decision-records/plugin/scripts/check-decision-record.py --scan ;;
        open-questions) scan sh modules/const-questions/plugin/scripts/check-open-questions.sh --scan ;;
        style) scan sh modules/const-styling/plugin/scripts/check-style.sh --scan ;;
        language) scan sh modules/const-language/plugin/scripts/check-language.sh --scan ;;
        budgets) scan sh modules/const-doc-budgets/plugin/scripts/check-budgets.sh --scan ;;
        list-handles) scan sh modules/const-interaction/plugin/scripts/check-list-handles.sh --scan ;;
        carry-lists | shared-links | shared-package | yaml-style | module-links | handle-forms | aspects | portability | gate-lists | copies | schema-mirror | dials-schema | profiles | resolved-paths | layered-items | eval-receipts | rollout-status)
            echo "python3 scripts/check-$1.py"
            echo "python3 scripts/check-$1.py --self-test" ;;
        bare-install) echo "python3 scripts/check-bare-install.py --self-test" ;;
        session-load) echo "python3 scripts/check-session-load.py --self-test" ;;
        run-evals) echo "python3 scripts/run-evals.py --self-test" ;;
        # the mutation report's own fixture; the report itself runs in jobs of the workflow and is no entry, since it judges nothing
        module-mutation) echo "python3 scripts/module-mutation.py --self-test" ;;
        guide)
            echo "python3 scripts/check-install-guide.py"
            echo "python3 scripts/check-install-guide.py --self-test" ;;
        install-* | session-const-* | fixtures-* | lint-* | types-*)
            for m in $MODULES; do
                [ "${1#*-}" = "$m" ] || continue
                case "$1" in
                    install-*) echo "python3 scripts/check-bare-install.py --module $m" ;;
                    session-*) echo "python3 scripts/check-session-load.py --module $m" ;;
                    fixtures-*) echo "python3 scripts/check-aspects.py --run --module $m" ;;
                    lint-*)
                        echo "python3 -m ruff format --check modules/$m"
                        echo "python3 -m ruff check modules/$m" ;;
                    types-*)
                        # the module's own packages, as own_packages of scripts/kit_module_doc.py derives them: each folder at
                        # the top of the plugin's scripts/, itself no link, that holds an __init__.py, whose name starts
                        # with neither . nor _ (the glob skips . already), save constitution_layer_kit. The plugin holds
                        # no shared code, so the shared package comes from the kit's shared/ on MYPYPATH.
                        for p in modules/"$m"/plugin/scripts/*; do
                            case "${p##*/}" in _* | constitution_layer_kit) continue ;; esac
                            [ -d "$p" ] && [ ! -L "$p" ] && [ -f "$p/__init__.py" ] && echo "cd modules/$m/plugin/scripts && MYPYPATH=../../../../shared python3 -m mypy --strict ${p##*/}"
                        done
                        echo "cd modules/$m/plugin/scripts && MYPYPATH=../../../../shared python3 -m mypy --strict *.py"
                        echo "cd modules/$m/tests && python3 -m mypy --strict *.py" ;;
                esac
                return 0
            done
            return 1 ;;
        task-close) scan sh modules/const-task-close/plugin/scripts/check-task-close.sh --scan ;;
        branch-gate) echo "sh scripts/git-hooks/tests/run.sh" ;;
        setup-claude) echo "sh scripts/tests/setup-claude.sh" ;;
        lint)
            echo "python3 -m ruff format --check scripts shared"
            echo "python3 -m ruff check scripts shared" ;;
        types)
            echo "cd shared && python3 -m mypy --strict constitution_layer_kit"
            echo "cd scripts && MYPYPATH=../modules/const-meta-types/plugin/scripts:../modules/const-decision-records/plugin/scripts:../shared python3 -m mypy --strict *.py" ;;
        layered-fixture)
            # the fixture gate of another layer, typed as a module is: its package, its entry files, its tests; its
            # lint is the kit's, since `lint` reads scripts/ whole. Not the `types` entry, whose MYPYPATH is the
            # schema mirror's folders and the shared package alone.
            echo "cd scripts/layered-fixture/plugin/scripts && MYPYPATH=../../../../shared python3 -m mypy --strict layered_gate"
            echo "cd scripts/layered-fixture/plugin/scripts && MYPYPATH=../../../../shared python3 -m mypy --strict *.py"
            echo "cd scripts/layered-fixture/tests && python3 -m mypy --strict *.py" ;;
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
        echo "BROKEN: entry $1 has no commands — why: an entry that runs nothing would pass unexamined — fix: give it an arm in commands() of scripts/gate-list.sh" >&2
        worst=1
        return
    }
    # the pinned claude of scripts/setup-claude.sh goes first on PATH for the install and session entries and the guide
    # alone, and only when it is there; <main> is derived as setup-claude.sh derives it
    pinned_bin=""
    case "$1" in
        install-* | session-const-* | guide)
            common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) && [ -n "$common" ] &&
                [ -x "$(dirname "$common")/.claude-code-pinned/node_modules/.bin/claude" ] &&
                pinned_bin="$(dirname "$common")/.claude-code-pinned/node_modules/.bin" ;;
    esac
    while IFS= read -r c; do
        (if [ -n "$pinned_bin" ]; then PATH="$pinned_bin:$PATH"; export PATH; fi; sh -c "$c") </dev/null; code=$?
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
        is_entry "$2" || misuse "no entry '$2' in the list"
        commands "$2" || {
            echo "BROKEN: entry $2 has no commands — why: an entry that runs nothing would pass unexamined — fix: give it an arm in commands() of scripts/gate-list.sh" >&2
            exit 1
        } ;;
    --run)
        [ -n "$2" ] || misuse "--run needs an entry or a job"
        worst=0
        if is_entry "$2"; then
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
