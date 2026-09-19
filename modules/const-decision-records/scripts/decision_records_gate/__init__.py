"""The write-time gate on decision records, as a package beside its entry point.

The entry point in the parent directory is a thin file; Python puts that directory on the
import path, so this package and the shared one beside it, ``const_gate``, are imported with
no path manipulation anywhere.

Modules, in reading order: ``model`` (this module's vocabulary and dials), ``messages`` (its
own texts), ``dials`` (its own dials, parsed), ``checks``, ``modes`` (hook and scan),
``start`` (which gate this is).
"""
