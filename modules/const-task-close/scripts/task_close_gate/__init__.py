"""The gate on task close, as a package beside its entry point.

The entry point in the parent directory is a thin file; Python puts that directory on the
import path, so this package and the shared one beside it, ``const_gate``, are imported with
no path manipulation anywhere.

Modules, in reading order: ``model`` (a coverage pair, the dials, a declaration, a range, the
keys of the findings), ``messages`` (this module's own texts), ``dials`` (the map, the trunk and
its remote, the declaration's key, the working files), ``history`` (the one place git is asked
about a range and about the working tree), ``checks`` (the range against the map, the
declarations against the pairs, the tree), ``modes`` (hook and scan), ``start`` (which gate
this is).
"""
