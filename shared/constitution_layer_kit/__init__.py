"""What every constitution gate shares: reading the hook event, the repository and the dials
file; territories, policies and resolution; the output log; the command line and its single
guard; the texts of every shared message.

The package has one source, and each plugin that uses it reaches it through the link
`scripts/constitution_layer_kit`; an installed plugin carries the code. Nothing here knows which plugin
it serves until the entry point declares it (``identity``).

Modules, in reading order: ``identity``, ``model`` (enums and dataclasses), ``messages``,
``errors``, ``preflight``, ``output`` (screen plus log), ``repository`` (git and files),
``territory`` (pattern matching through git), ``envelope``, ``dials``, ``events`` (the hook
payload), ``index`` (policies and claims), ``resolution``, ``pipeline`` (event to target,
findings to verdict), ``cli`` (argparse and the single guard).
"""

# The package's version, major.minor.patch, and the one source of it: the distribution's metadata reads
# it from here when the package is built. A release keeps every module written for an earlier release
# of its major working.
__version__ = "1.0.0"
