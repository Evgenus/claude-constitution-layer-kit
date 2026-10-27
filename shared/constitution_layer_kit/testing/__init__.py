"""The fixtures every gate's tests share: ``harness``, the case runner that drives a module's real entry point;
``consumer``, the throwaway repository a gate runs on; ``acceptance``, the pytest marker, the one-number rule and
the asserting checks; ``items``, the shared acceptance items, which a module's ``tests/test_shared_items.py``
brings into its own run with ``from constitution_layer_kit.testing.items import *``.

They ship in the distribution beside the gates' code, so that a module of another kit runs the same items at the
same release as the code they prove. They need pytest, the extra ``testing``; no gate imports this package, so a
project that only runs gates never needs it.
"""
