"""The tokens a session spent on each of its commits, as a package beside its entry points.

The entry points in the parent directory are thin files; Python puts that directory on the import path, so
this package and the shared one beside it, ``constitution_layer_kit``, are imported with no path
manipulation anywhere.

Modules, in reading order: ``model`` (the lines of the two logs and of the file of counts, a window, a count,
the keys), ``messages`` (this module's own texts), ``logs`` (the folder of the logs in git's common
directory, each file read a line at a time and appended whole, and the lock), ``windows`` (the cutter: one
session's records into the windows of its commits, copied into a throwaway folder), ``counter`` (the pinned
ccusage: where it stands, how it is installed, how it is run and read), ``counting`` (every complete
window not yet counted, under the lock), ``start`` (which entry this is).
"""
