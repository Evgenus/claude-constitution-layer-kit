"""The write-time guard of claimed territory, as a package beside its entry point.

The entry point in the parent directory is a thin file; Python puts that directory on
the import path, so ``import meta_types_gate`` needs no path manipulation anywhere.

Modules, in reading order: ``model`` (enums and dataclasses), ``messages`` (every
user-facing text), ``errors``, ``preflight``, ``output`` (screen plus log), ``repository``
(git and files), ``territory`` (pattern matching through git), ``envelope``, ``dials``,
``events`` (the hook payload), ``index`` (policies and claims), ``checks``, ``modes`` (hook and
scan), ``cli`` (argparse and the single guard).
"""
