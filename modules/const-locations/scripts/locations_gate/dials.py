"""This module's own dials, parsed once from its namespace as the shared reader hands it over."""

from __future__ import annotations

import os
from collections.abc import Mapping

from const_gate.dials import refuse_unknown_keys
from const_gate.errors import ConfigurationFailure

from . import messages
from .model import LocationsDials

KEYS = ("log_dir", "templates")  # log_dir is every gate's, read by the shared code
ENTRY_KEYS = ("policy", "template")


def parse(own: Mapping[str, object]) -> LocationsDials:
    if "severity" in own:  # the shared reader has accepted it by now; here it means nothing
        raise ConfigurationFailure(messages.c5_severity_here())
    refuse_unknown_keys(own, KEYS)
    return LocationsDials(templates=_templates(own.get("templates")))


def _templates(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, list):
        raise ConfigurationFailure(messages.c5_templates_shape())
    templates: dict[str, str] = {}
    for position, entry in enumerate(value):
        templates.update(_entry(position, entry, templates))
    return templates


def _entry(position: int, entry: object, seen: Mapping[str, str]) -> dict[str, str]:
    def refuse(what: str) -> ConfigurationFailure:
        return ConfigurationFailure(messages.c5_template_entry(position, what))

    if not isinstance(entry, dict):
        raise refuse(messages.entry_not_a_mapping())
    for key in entry:
        if str(key) not in ENTRY_KEYS:
            raise refuse(messages.entry_unknown_key(str(key)))
    values: dict[str, str] = {}
    for key in ENTRY_KEYS:
        found = entry.get(key)
        if not isinstance(found, str) or not found.strip():
            raise refuse(messages.entry_missing(key))
        values[key] = found
    if values["policy"] in seen:
        raise refuse(messages.entry_repeated(values["policy"]))
    path = values["template"]
    if os.path.isabs(path) or ".." in os.path.normpath(path).split(os.sep):
        raise refuse(messages.entry_outside())
    return {values["policy"]: os.path.normpath(path).replace(os.sep, "/")}
