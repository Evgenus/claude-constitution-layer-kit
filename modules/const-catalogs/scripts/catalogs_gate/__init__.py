"""The gate on the items of numbered kinds, as a package beside its entry point.

The entry point in the parent directory is a thin file; Python puts that directory on the
import path, so this package and the shared one beside it, ``const_gate``, are imported with
no path manipulation anywhere.

Modules, in reading order: ``model`` (a catalog, an item, the keys of the findings),
``messages`` (this module's own texts), ``declarations`` (which policies declare a catalog),
``checks``, ``modes`` (hook and scan), ``start`` (which gate this is).
"""
