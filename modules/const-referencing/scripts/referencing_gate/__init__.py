"""The gate on references, as a package beside its entry points.

The entry points in the parent directory are thin files; Python puts that directory on the
import path, so this package and the shared one beside it, ``const_gate``, are imported with
no path manipulation anywhere.

Modules, in reading order: ``model`` (the dials, a link, the keys of the findings),
``messages`` (this module's own texts), ``dials`` (the module's namespace parsed),
``masking`` (the regions no check reads), ``links`` (the links of a document, with their
positions), ``lint`` (the forms a reference may not take), ``modes`` (hook and scan),
``start`` (which gate this is).
"""
