# Install: know-check

This folder is a test fixture of the kit. It is not a module and it is never installed in a project.

It is a gate of a second layer. The kit's own check `scripts/check-layered-items.py` runs the shared
acceptance items against it. This shows that they hold for a gate whose dials file is not the constitution's.

The gate needs the Python package `constitution-layer-kit`, release 2.0.0 or a later 2.x release, installed
for `python3`. This note is the file that the gate's failure lines name.
