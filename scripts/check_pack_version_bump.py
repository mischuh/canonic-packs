#!/usr/bin/env python3
"""CI gate: fail a PR that changes a pack's content without bumping pack.yaml's version.

AMENDMENT-context-packs §2.3: "a version bump re-runs install and produces a new
reviewable diff" — that guarantee only holds if every content change to a pack is visible
as a version bump, not a silent edit a pinned install would never see.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import PurePosixPath

_VERSION_RE = re.compile(r"^version:\s*(.+?)\s*$", re.MULTILINE)


def changed_files(base_ref: str) -> list[str]:
    """Paths changed between base_ref and the current HEAD."""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def touched_packs(files: list[str]) -> set[str]:
    """Names of every pack with at least one file under packs/<name>/ in the diff."""
    packs: set[str] = set()
    for f in files:
        parts = PurePosixPath(f).parts
        if len(parts) >= 2 and parts[0] == "packs":
            packs.add(parts[1])
    return packs


def file_at_ref(ref: str, path: str) -> str | None:
    """Contents of path at ref, or None if it doesn't exist there."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def version_of(text: str | None) -> str | None:
    if text is None:
        return None
    match = _VERSION_RE.search(text)
    return match.group(1) if match else None


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <base-ref>", file=sys.stderr)
        return 2

    base_ref = sys.argv[1]
    packs = touched_packs(changed_files(base_ref))
    if not packs:
        print("no packs/*/ files changed — nothing to check.")
        return 0

    failures: list[str] = []
    for pack in sorted(packs):
        manifest_path = f"packs/{pack}/pack.yaml"
        before = file_at_ref(base_ref, manifest_path)
        after = file_at_ref("HEAD", manifest_path)

        if before is None:
            print(f"{pack}: new pack — nothing to check.")
            continue
        if after is None:
            print(f"{pack}: removed — nothing to check.")
            continue

        before_version, after_version = version_of(before), version_of(after)
        if before_version == after_version:
            failures.append(
                f"packs/{pack}/ changed but pack.yaml's version is still "
                f"{after_version!r} — bump it (AMENDMENT-context-packs §2.3)."
            )
        else:
            print(f"{pack}: version {before_version!r} -> {after_version!r} — OK.")

    if failures:
        for msg in failures:
            print(f"::error::{msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
