#!/usr/bin/env python3
"""List files changed on the current branch vs a base ref.

Returns JSON: {base, head, files: [{path, status, adds, dels}]}

Base-ref resolution (when --base not supplied):
  1. origin/HEAD via `git symbolic-ref refs/remotes/origin/HEAD`
  2. Local branches in priority order: dev → main → master
  3. Error out if none exist.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def resolve_base(cwd: str) -> str | None:
    rc, out, _ = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=cwd)
    if rc == 0 and out.startswith("refs/remotes/origin/"):
        return out.removeprefix("refs/remotes/")

    for candidate in ("dev", "main", "master"):
        rc, _, _ = run(["git", "rev-parse", "--verify", candidate], cwd=cwd)
        if rc == 0:
            return candidate
        rc, _, _ = run(["git", "rev-parse", "--verify", f"origin/{candidate}"], cwd=cwd)
        if rc == 0:
            return f"origin/{candidate}"

    return None


def diff_files(cwd: str, base: str, paths_glob: str | None) -> list[dict]:
    rc, out, err = run(
        ["git", "diff", "--numstat", f"{base}...HEAD"],
        cwd=cwd,
    )
    if rc != 0:
        print(f"git diff failed: {err}", file=sys.stderr)
        sys.exit(1)

    results: list[dict] = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        adds_s, dels_s, path = parts
        if paths_glob and not fnmatch.fnmatch(path, paths_glob):
            continue
        adds = int(adds_s) if adds_s.isdigit() else 0
        dels = int(dels_s) if dels_s.isdigit() else 0

        rc_s, status_out, _ = run(
            ["git", "diff", "--name-status", f"{base}...HEAD", "--", path], cwd=cwd
        )
        status = "M"
        if rc_s == 0 and status_out:
            first = status_out.split()[0]
            status = first[0] if first else "M"

        results.append(
            {"path": path, "status": status, "adds": adds, "dels": dels}
        )
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None, help="base ref to diff against")
    ap.add_argument("--source", default=".", help="repo root (default: cwd)")
    ap.add_argument("--paths", default=None, help="fnmatch-style glob to filter paths")
    args = ap.parse_args()

    cwd = str(Path(args.source).resolve())

    rc, _, _ = run(["git", "rev-parse", "--git-dir"], cwd=cwd)
    if rc != 0:
        print(f"not a git repo: {cwd}", file=sys.stderr)
        return 1

    base = args.base or resolve_base(cwd)
    if not base:
        print(
            "could not auto-detect base ref. tried origin/HEAD, dev, main, master. "
            "pass --base=<ref> explicitly.",
            file=sys.stderr,
        )
        return 1

    rc, head_sha, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd=cwd)
    if rc != 0:
        head_sha = "unknown"

    rc, head_branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if rc != 0:
        head_branch = "HEAD"

    files = diff_files(cwd, base, args.paths)

    print(
        json.dumps(
            {
                "base": base,
                "head": head_sha,
                "head_branch": head_branch,
                "files": files,
                "count": len(files),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
