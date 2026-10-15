---
id: dec-0091-module-fixtures-run-as-pytest
type: task-record
title: The module fixtures run as native pytest tests, one test per acceptance item, and may run in parallel
status: active
stakes: process
decider: Eugene Chernyshov
---

# The module fixtures run as native pytest tests, one test per acceptance item, and may run in parallel

## Context

Each of the kit's eleven modules proves its gates with fixtures run by a runner of its own, `tests/run.py`, on a shared harness in `shared/tests/` — `harness.py`, `consumer.py` and `shared_items.py`, linked into each module. At the cut of this change the runners held 1,025 numbered items in 18,083 lines, and the shared files 2,890 lines; an item was a function returning a pair, `(ok, evidence)`, registered in one of three list forms, and the harness printed one line per item and a summary line that `scripts/check-aspects.py` parsed (R1 and R2 of [dec-0080-fixtures-run-through-check-aspects](dec-0080-fixtures-run-through-check-aspects.md#r1)). The custom runner cost the kit a parser of its own output, a selection flag of its own (`--item`) with its own messages, a collision check, and no way to run items side by side; a full pass of the eleven took about 18 minutes of runner time, measured four runners side by side.

Facts that settle the mechanism, from the official documentation as read on 2026-10-14 and from experiments on a copy of the kit at `fb30e75`:

1. pytest 9.1.1, pytest-xdist 3.8.0 and coverage.py 7.16.2 are the latest releases, each older than two weeks ([pytest on PyPI](https://pypi.org/project/pytest/9.1.1/), [pytest-xdist on PyPI](https://pypi.org/project/pytest-xdist/3.8.0/), [coverage.py changes](https://coverage.readthedocs.io/en/7.16.2/changes.html)).
2. pytest's default import mode, `prepend`, puts a test file's own folder first on the import path, so the linked files import by plain name with no edit of the path; `importlib` mode does not ([pytest, sys.path](https://docs.pytest.org/en/stable/explanation/pythonpath.html)).
3. pytest does not resolve a symbolic link during collection: a linked test file keeps the link's path ([pytest changelog, 6.0.0rc1](https://docs.pytest.org/en/stable/changelog.html)).
4. `fixtures` is the name of a pytest built-in plugin, so a shared file of that name cannot be loaded as a plugin; and a conftest that imports its module's test file before naming a plugin in `pytest_plugins` leaves that plugin without assertion rewriting, a warning that `-W error` makes fatal. Both were met in the experiment; a conftest that defines its own two hooks, each calling the shared file, has neither.
5. A marker reaches pytest's JUnit report only as a property added at collection; `record_property` warns under the default `junit_family` ([pytest, output](https://docs.pytest.org/en/stable/how-to/output.html)).
6. Under pytest every module reached exactly the lines and branches its old runner reached, serially and with `-n auto`; the report held every test and its number; three shuffled runs of each module, serial and with `-n auto`, were green; in the two modules timed, a parallel run took 10 to 15 s against 52 and 69 s serially.

The survey behind these facts, with its experiments, is the comparison [res-0013-fixture-runner](../research/res-0013-fixture-runner.md), cited here as provenance.

## Options

The session put five options to the decider on 2026-10-13, scored against eight weighted criteria; the ranking held under three weight profiles.

- **A. Leave as is.** The custom runner with `--item`, run through `check-aspects --run`.
  - **Pros:** no risk and no cost; every document and check already agrees with the code.
  - **Cons:** a module's full pass stays at one to two and a half minutes, all eleven at about twelve minutes serial; the harness stays a thing a model must learn from a long specification.
- **B. Improve the harness.** A thread pool in the harness's run, each item on its own fresh consumer, proven by a repeated run in a shuffled order.
  - **Pros:** the one measurable gain of pytest, speed, for about fifty lines, one record and two sentences in the shared specification; the gate list and CI unchanged.
  - **Cons:** item independence must be proven; the harness stays custom; the gain is local, since CI already runs modules in parallel jobs.
- **C. Full migration, serial.** Every item a native pytest test, the custom runner gone, no parallel runs.
  - **Pros:** a format every model and contributor knows; pytest's failure output and selection.
  - **Cons:** no speed gain, since the gates run in child processes; ten to eighteen million tokens over four to seven sessions; rulings, three readers of `scripts/check-aspects.py` and the shared specification rewritten, and a carry audit that has taken four to seven rounds.
- **D. Full migration, then parallel runs.** C, then the fixtures run side by side with pytest-xdist.
  - **Pros:** everything C gives, and the speed of B.
  - **Cons:** everything C costs, and the independence proof B needs; it scored below B under every weight profile.
- **E. Hybrid.** pytest for new modules only; the eleven runners stay.
  - **Pros:** no rewrite of what exists.
  - **Cons:** two specifications, two readers, two styles for every model; the lowest score under every profile.

## Recommendation

B, recommended by the session: it scored highest with A under the baseline weights and above D under the other two profiles, and it buys the speed for a small fraction of D's cost. The migration would overtake it if a second regular contributor who knows pytest joined, or if the kit adopted tooling that reads pytest's reports or plugins.

## Choice

D, chosen by the decider in chat on 2026-10-14, over the recommendation, with these conditions: one pull request; the plan approved before implementation; the work orchestrated by one session, with implementers and verifiers in parallel by module; type checking and coverage kept; stability and drift held by named checks; no code outside the tests touched but the kit tooling that reads the runner. Asked then whether CI runs the fixtures in parallel too, the decider chose that it does, in chat on 2026-10-14, once the shuffled runs are green for every module. Asked whether the change owes a research comparison, the decider chose one, in chat on 2026-10-14, over the session's recommendation of none: the survey is kept in the repository as [res-0013-fixture-runner](../research/res-0013-fixture-runner.md), and the research policy is widened to hold it.

## Ruling

<a id="r1"></a>**R1.** A module's fixtures are native pytest tests: its own items in `tests/test_<name>.py`, one test function or one row of a parametrized test per acceptance item, the module's red→green `Case` records, where it has them, the rows of its parametrized `test_case`; the items every gate shares in `shared/tests/test_shared_items.py`, linked into each module's `tests/`, each a test taking the module's `subject` fixture. Each test carries `item(<number>, <title>)` from `shared/tests/acceptance.py`; the numbers and titles are those the items held before.

<a id="r2"></a>**R2.** Each module's `tests/conftest.py` defines `pytest_configure` and `pytest_collection_modifyitems`, each calling `acceptance`, and the session fixture `subject`; no conftest names a plugin in `pytest_plugins`. A module's setup — its gate's identity, its harness, its subject — stays at the top of its test file.

<a id="r3"></a>**R3.** A run collects one module's folder: two modules' folders in one run stop at collection, each test file declaring its own gate in the one process. Before any test runs, a collected test without `item(…)` and a number two tests carry stop the run, one line per fault, in number order for the numbers, with a fix a person can follow; this replaces the closing line and the exit 1 of R2 of [dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders](dec-0078-landed-collisions-renumber-and-kit-checks-hold-numbers-descriptions-namespaces-and-folders.md#r2) with pytest's refusal of a usage error.

<a id="r4"></a>**R4.** The collection hands each test's number to pytest's JUnit report as the property `item`. `scripts/check-aspects.py --run` runs `python3 -m pytest modules/<module>/tests -p no:cacheprovider -W error` with a JUnit report, reads each item's result from it, takes the runner's total as the tests that ran, skips excluded, and prints pytest's whole output when it exits other than 0. R1 and R2 of [dec-0080-fixtures-run-through-check-aspects](dec-0080-fixtures-run-through-check-aspects.md#r1) stand, the runner now pytest; this replaces the parts of R6 of [dec-0054-acceptance-items-name-their-rows](dec-0054-acceptance-items-name-their-rows.md#r6) that rule the reading of a runner's printed item lines and its last line, its exits 0 and 2, and its harness unchanged; its handles of an item, `T12`, `12` and `S101`, stand.

<a id="r5"></a>**R5.** A shared item a gate does not run is skipped, its reason naming the `Subject` flag that leaves it out, and its number stays free in that module.

<a id="r6"></a>**R6.** The numbers of the shared items are read by `scripts/check-aspects.py` from the `item(…)` markers of `shared/tests/test_shared_items.py`, by syntax tree; this replaces the file R7 of [dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names](dec-0069-kit-checks-hold-module-lists-floor-clauses-shared-numbers-and-kit-names.md#r7) names, and its check each time the list is built: a number two tests carry is stopped at collection (R3), and the numbers' rising order is held by `scripts/check-aspects.py` alone.

<a id="r7"></a>**R7.** The shared test files a module links in its `tests/` are `harness.py`, `consumer.py`, `acceptance.py` and `test_shared_items.py`; this replaces the list of item 2 of [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md), whose principle stands.

<a id="r8"></a>**R8.** The checks a test calls assert: `check_case`, `expect` and `broken_first_line` in `acceptance.py`. Every message typed by hand once in a module's fixtures stays typed by hand once in its tests (rule 14 of [template §6](../../module-template/MODULE.md#t6)).

<a id="r9"></a>**R9.** The kit's gate list and CI run a module's tests only through `scripts/check-aspects.py --run --module`, as R1 of [dec-0080-fixtures-run-through-check-aspects](dec-0080-fixtures-run-through-check-aspects.md#r1) rules, which runs them whole and so selects none. `scripts/check-gate-lists.py` holds what their lines can show: no code line names pytest save in an exact pin `pytest==<version>`, passes `--item` or names `PYTEST_ADDOPTS`, and no pytest configuration file at the kit root, in `modules/`, in a module's folder or in its `tests/` sets `addopts`.

<a id="r10"></a>**R10.** Coverage stays `coverage run -m pytest` through `scripts/kit_coverage.py`; pytest-cov is not used. With `CONSTITUTION_KIT_JOBS` set, the run takes `-n <value>` from pytest-xdist; CI sets it to `auto` in every module's job.

<a id="r11"></a>**R11.** CI pins `pytest==9.1.1` and `pytest-xdist==3.8.0` on its tools line. A consumer verifies an install with `python3 -m pytest <plugin root>/tests -p no:cacheprovider`, pytest installed for it; a module's `requirements.txt` names none of them, since no gate needs them.

<a id="r12"></a>**R12.** No item depends on the order the items run in, or on running in the same process as another: each builds its own consumer and leaves nothing behind, so a module's tests may run in any order and side by side. A run with the collected tests shuffled by a seed, through a `pytest_collection_modifyitems` hook of the run's own, serial and with `-n auto`, three times each, is the proof a change to the fixtures keeps; review holds it, and no check runs it.

<a id="r13"></a>**R13.** A research comparison may survey a mechanism of the kit's own tooling as well as a module's: its slug names that mechanism, and it is frozen when the record that accepts its change is accepted. This widens R1 of [dec-0034-research-and-policies-numbered](dec-0034-research-and-policies-numbered.md#r1), R19 of [dec-0039-policies-state-their-kinds](dec-0039-policies-state-their-kinds.md#r19) and R6 of [dec-0040-rules-fit-their-documents](dec-0040-rules-fit-their-documents.md#r6), which stand for a module's survey.

## Carry list

1. R1 — item 8 of [kit-shared-gate-code §2](../../shared/GATE.md#g2), and [its §5](../../shared/GATE.md#g5); rule 14 of [template §6](../../module-template/MODULE.md#t6). That the numbers and titles are those the items held before is history.
2. R2 — item 8 of [kit-shared-gate-code §2](../../shared/GATE.md#g2); [the shared wiring](../../shared/tests/acceptance.py), its docstring.
3. R3 — [the shared wiring](../../shared/tests/acceptance.py), `collected`; rows H5 and H6 of [kit-shared-gate-code §3](../../shared/GATE.md#g3). The replacement of R2 of dec-0078's closing line and exit 1 is history.
4. R4 — [`scripts/check-aspects.py`](../../scripts/check-aspects.py), its docstring and `run_runner`; [CLAUDE.md](../../CLAUDE.md), "The gate list and CI". That R1 and R2 of dec-0080 stand, and the replacement of parts of R6 of dec-0054, are history; the handles of an item that R6 keeps stand in that docstring.
5. R5 — [the shared items](../../shared/tests/test_shared_items.py), their docstring.
6. R6 — [`scripts/check-aspects.py`](../../scripts/check-aspects.py), `shared_numbers` and its docstring; [the shared wiring](../../shared/tests/acceptance.py), `collected`. The replacement of the file and the check R7 of dec-0069 names is history.
7. R7 — item 7 of [kit-shared-gate-code §2](../../shared/GATE.md#g2); [`scripts/check-shared-links.py`](../../scripts/check-shared-links.py), `FLOOR`. The replacement of the list of item 2 of dec-0025 is history.
8. R8 — rule 14 of [template §6](../../module-template/MODULE.md#t6); [the shared wiring](../../shared/tests/acceptance.py), its docstring.
9. R9 — [`scripts/check-gate-lists.py`](../../scripts/check-gate-lists.py), its docstring.
10. R10 — [`scripts/kit_coverage.py`](../../scripts/kit_coverage.py), its docstring; [`scripts/check-aspects.py`](../../scripts/check-aspects.py), its docstring; [the workflow](../../.github/workflows/gates.yml), the module jobs' environment.
11. R11 — [the workflow](../../.github/workflows/gates.yml), the tools line; [the install guide](../../INSTALL.md), the prerequisites, step 4 of [its §3](../../INSTALL.md#s3) and step 8 of [its §2](../../INSTALL.md#s2); each module's `INSTALL.md`, the verify step.
12. R12 — item 8 of [kit-shared-gate-code §2](../../shared/GATE.md#g2).
13. R13 — [plc-0005-research](../policies/plc-0005-research.md#r6), its title, its opening line and rules 2, 5, 6, 7 and 9. That it widens R1 of dec-0034, R19 of dec-0039 and R6 of dec-0040 is history.
