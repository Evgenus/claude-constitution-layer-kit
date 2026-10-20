"""The write-time guard of claimed territory, as a package beside its entry point.

The entry point in the parent directory is a thin file; Python puts that directory on the
import path, so this package and the shared one beside it, ``constitution_layer_kit``, are imported with
no path manipulation anywhere.

Modules, in reading order: ``model`` (the keys of this module's findings), ``messages`` (its
own texts), ``checks``, ``modes`` (hook and scan), ``start`` (which gate this is).
"""
