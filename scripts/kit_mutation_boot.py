"""Kit tooling, never shipped in a module: the start of a child that a test of the mutation report's line
map runs under `python3 -S <file>`. `scripts/kit_mutation.py` copies this one file into a folder of its own
and runs it, under `-S`, from the interpreter it hands the map's tests as sys.executable, as
`<python> -S kit_mutation_boot.py <folder> <file> <argument>...`.

Under `-S` Python reads no `.pth` file, and coverage.py's own start in a child is one. So this file does
what `-S` skips for coverage.py alone: it puts `<folder>`, which holds coverage.py and nothing else, last on
the path, starts coverage.py when COVERAGE_PROCESS_START names its settings, and runs `<file>` as Python
would: as `__main__`, with `<file>` and its arguments as sys.argv and the folder of `<file>`, links
resolved, first on the path. Every other package stays as `-S` leaves it, out of reach.
"""

import os
import runpy
import sys


def main() -> None:
    lib, target = sys.argv[1], sys.argv[2]
    sys.argv = sys.argv[2:]
    sys.path[0] = os.path.dirname(os.path.realpath(target))
    sys.path.append(lib)
    if os.environ.get("COVERAGE_PROCESS_START"):
        import coverage  # noqa: PLC0415 — found only once the folder is on the path

        coverage.process_startup()
    runpy.run_path(target, run_name="__main__")


main()
