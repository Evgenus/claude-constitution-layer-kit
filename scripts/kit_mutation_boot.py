"""Kit tooling, never shipped in a module: the start of a child that a test of the mutation report's line
map runs, where coverage.py alone would not measure it. `scripts/kit_mutation.py` copies this one file into a
folder of its own and runs it from the interpreter of the map's run, as
`<python> [-S] kit_mutation_boot.py <folder> <file> <argument>...`, for two kinds of child:

- `python3 -S <file>`: under `-S` Python reads no `.pth` file, and coverage.py's own start in a child is one.
  So this file does what `-S` skips for coverage.py alone: it puts `<folder>`, which holds coverage.py and
  nothing else, last on the path, and starts coverage.py when COVERAGE_PROCESS_START names its settings.
  Every other package stays as `-S` leaves it, out of reach.
- `python3 <file>` under a soft limit on the size of the files it writes, below the hard one: coverage.py
  has started already, through its `.pth` file, but could not write its data file under that limit.

In both, it registers a handler that lifts the soft limit on file size to the hard one. Python runs the
handlers of a process's exit last registered first, so this one runs after every handler `<file>` registers
and before coverage.py's, which saves the data. Then it runs `<file>` as Python would: as `__main__`, with
`<file>` and its arguments as sys.argv and the folder of `<file>`, links resolved, first on the path.
"""

import atexit
import os
import resource
import runpy
import sys


def lift_file_size_limit() -> None:
    """The soft limit on file size raised to the hard one, which a process may always do."""
    soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
    if soft != hard:
        resource.setrlimit(resource.RLIMIT_FSIZE, (hard, hard))


def main() -> None:
    lib, target = sys.argv[1], sys.argv[2]
    sys.argv = sys.argv[2:]
    sys.path[0] = os.path.dirname(os.path.realpath(target))
    if sys.flags.no_site:
        sys.path.append(lib)
        if os.environ.get("COVERAGE_PROCESS_START"):
            import coverage  # noqa: PLC0415 — found only once the folder is on the path

            coverage.process_startup()
    atexit.register(lift_file_size_limit)
    runpy.run_path(target, run_name="__main__")


main()
