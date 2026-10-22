"""A throwaway consumer repository for the fixtures: three policies, two of them
overlapping on purpose so the multi-policy defect and its declaration escape can be shown.
Documents with an envelope are rendered through the YAML dumper, never typed as strings:
a hand-typed fixture can fail for a reason nobody intended."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT_POLICY = "docs/policies/root-policy.md"
POLICIES = ("root", "notes", "shared")
BASE_MARKDOWN = len(POLICIES)  # the Markdown files a fresh consumer holds, one per policy


def document(body: str = "# Fixture\n", **fields: str) -> str:
    return "---\n" + yaml.safe_dump(fields, sort_keys=False, allow_unicode=True) + "---\n\n" + body


def envelope(doc_id: str, meta_type: str = "non-authoritative", **extra: str) -> str:
    return document(id=doc_id, type=meta_type, title=f"Fixture {doc_id}", status="active", **extra)


@dataclass
class Consumer:
    root: Path
    dials: dict[str, object] = field(
        default_factory=lambda: {
            "root_policy": ROOT_POLICY,
            "module_prefix": "const-",
            "root-policy": {"territory": ["docs/policies/**"]},
            "notes-policy": {"territory": ["docs/notes/**"]},
            "shared-policy": {"territory": ["docs/notes/shared/**"]},  # overlaps notes-policy
        }
    )

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def build(self) -> Consumer:
        self.write("constitution.yaml", yaml.safe_dump(self.dials, sort_keys=False))
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
