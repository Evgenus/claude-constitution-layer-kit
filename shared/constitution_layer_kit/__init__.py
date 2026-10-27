"""What every constitution gate shares: reading the hook event, the repository and the dials
file; territories, policies and resolution; the output log; the command line and its single
guard; the texts of every shared message.

The package has one source, and no plugin carries a copy or a link of it: pip installs it for python3 as
the distribution ``constitution-layer-kit``, and each entry file of a plugin imports ``cli`` from it and
asks ``cli.version_failure`` whether the installed release serves the plugin, before it imports anything
of its own. The tests of a module reach the source through links in their own folder. Nothing here knows
which plugin it serves until the guard of the entry point opens a scope that declares it (``identity``).

Modules, in reading order: ``identity``, ``model`` (enums and dataclasses), ``messages``,
``errors``, ``preflight``, ``output`` (screen plus log), ``repository`` (git and files),
``territory`` (pattern matching through git), ``envelope``, ``dials``, ``events`` (the hook
payload), ``index`` (policies and claims), ``resolution``, ``pipeline`` (event to target,
findings to verdict), ``cli`` (argparse, the single guard, and ``version_failure``, the check of the
installed release).
"""

# The package's version, major.minor.patch, and the one source of it: the distribution's metadata reads
# it from here when the package is built. A release keeps every module written for an earlier release
# of its major working.
__version__ = "2.0.0"
