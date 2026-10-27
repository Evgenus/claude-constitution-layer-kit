"""A throwaway consumer repository for the fixtures: three policies, two of them
overlapping on purpose so the multi-policy defect and its declaration escape can be shown.
Documents with an envelope are rendered through the YAML dumper, never typed as strings:
a hand-typed fixture can fail for a reason nobody intended.

The policies and the constitution's kernel keys stand in the constitution's file. A gate of this
kit keeps its own namespace there too; a gate of another layer keeps it in its own layer's file,
`own_file`, which then holds that layer's `module_prefix` and the gate's namespace, and
`write_dials` sends each key of a patch to the file it belongs in."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONSTITUTION_FILE = "constitution.yaml"  # the file the constitution's kernel names for its dials
CONSTITUTION_PREFIX = "const-"  # the prefix the consumer's constitution file declares for its modules
ROOT_POLICY = "docs/policies/root-policy.md"
POLICIES = ("root", "notes", "shared")
BASE_MARKDOWN = len(POLICIES)  # the Markdown files a fresh consumer holds, one per policy


def dump(dials: dict[str, object]) -> str:
    return yaml.safe_dump(dials, sort_keys=False)


def document(body: str = "# Fixture\n", **fields: str) -> str:
    return "---\n" + yaml.safe_dump(fields, sort_keys=False, allow_unicode=True) + "---\n\n" + body


def envelope(doc_id: str, meta_type: str = "non-authoritative", **extra: str) -> str:
    return document(id=doc_id, type=meta_type, title=f"Fixture {doc_id}", status="active", **extra)


def own_prefix(namespace: str) -> str:
    """The prefix of a module's layer: its namespace up to and including the first '-'."""
    head, dash, _ = namespace.partition("-")
    return head + dash


def split_patch(
    patch: dict[str, object], prefix: str, kernel_keys: tuple[str, ...]
) -> tuple[dict[str, object], dict[str, object]]:
    """A dials patch of a gate of another layer, cut in two: the keys of its own file — those its kernel keys
    list and those that start with its layer's prefix — and the rest, for the constitution's file."""
    own = {k: v for k, v in patch.items() if k in kernel_keys or k.startswith(prefix)}
    return own, {k: v for k, v in patch.items() if k not in own}


@dataclass
class Consumer:
    root: Path
    dials: dict[str, object] = field(
        default_factory=lambda: {
            "root_policy": ROOT_POLICY,
            "module_prefix": CONSTITUTION_PREFIX,
            "root-policy": {"territory": ["docs/policies/**"]},
            "notes-policy": {"territory": ["docs/notes/**"]},
            "shared-policy": {"territory": ["docs/notes/shared/**"]},  # overlaps notes-policy
        }
    )
    own_file: str = CONSTITUTION_FILE  # the gate's own dials file; another layer's names its own
    own_dials: dict[str, object] = field(default_factory=dict)  # that file's keys, when it is another
    kernel_keys: tuple[str, ...] = ()  # that file's kernel keys, which `write_dials` keeps in it

    @property
    def layered(self) -> bool:
        return self.own_file != CONSTITUTION_FILE

    def write_dials(
        self,
        patch: dict[str, object] | None = None,
        raw: str | None = None,
        raw_constitution: str | None = None,
    ) -> None:
        """The dials files with `patch` over them: in one file for a gate of this kit, its own file `raw`
        where given; cut by `split_patch` for a gate of another layer, its own file `raw` and the
        constitution's file `raw_constitution` where given."""
        patch = patch or {}
        if not self.layered:
            self.write(CONSTITUTION_FILE, raw if raw is not None else dump({**self.dials, **patch}))
            return
        prefix = str(self.own_dials.get("module_prefix", ""))
        own, rest = split_patch(patch, prefix, self.kernel_keys)
        constitution = raw_constitution if raw_constitution is not None else dump({**self.dials, **rest})
        self.write(CONSTITUTION_FILE, constitution)
        self.write(self.own_file, raw if raw is not None else dump({**self.own_dials, **own}))

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def build(self) -> Consumer:
        self.write_dials()
        for name in POLICIES:
            self.write(f"docs/policies/{name}-policy.md", envelope(f"{name}-policy", "current-state"))
        self.git("init", "-q")
        self.commit()
        return self

    def commit(self) -> None:
        self.git("add", "-A")
        self.git(
            "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"
        )

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)
