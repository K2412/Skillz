#!/usr/bin/env python3
"""
init_workspace.py — scaffold a teaching workspace in the current directory.

Run ONCE at the start of a mission, before authoring the first lesson. It creates the
directory skeleton, drops stub state files, and copies the starter assets (shared
stylesheet, quiz widget, lesson template) so the very first lesson looks like part of a
coherent course instead of a hand-rolled one-off.

It is idempotent: existing files are never overwritten, so re-running in a live workspace
only fills in whatever is missing. Nothing here writes lesson *content* — that is the
teacher's job. This script only lays the table.

Usage:
    python3 <skill>/scripts/init_workspace.py [target_dir] [--topic "Solving a Rubik's cube"]

If target_dir is omitted, the current working directory is used.
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
STARTER = SKILL_ROOT / "assets" / "starter"

DIRS = ["lessons", "learning-records", "reference", "assets"]

MISSION_STUB = """# Mission: {topic}

## Why
<!-- 1-3 sentences. The concrete real-world goal. What changes when the learner has this
     skill? Push past "to understand X" to the underlying outcome. Interview the learner
     if this is not yet clear — a bad mission is worse than none. -->

## Success looks like
- <!-- a specific, observable thing the learner will be able to do -->

## Constraints
- <!-- time, budget, prior commitments, how they like to be taught -->

## Out of scope
- <!-- adjacent topics they explicitly do NOT want right now — protects the zone of proximal development -->
"""

RESOURCES_STUB = """# {topic} Resources

<!-- Curated, high-trust sources ONLY. Knowledge for lessons is drawn from here, never
     from parametric guesses. Annotate every entry with what it covers and when to reach
     for it. See references/RESOURCES-FORMAT.md. -->

## Knowledge

## Wisdom (Communities)
"""

REVIEW_QUEUE_STUB = """# Review Queue

<!-- The spaced-repetition schedule for this mission. Spacing + retrieval practice are the
     two highest-evidence ways to convert fluency into durable storage strength — but only
     if something SCHEDULES the re-surfacing. That is this file's whole job.
     See references/pedagogy/review-queue-format.md. -->

| Due | Item | Last seen | Interval | Notes |
|-----|------|-----------|----------|-------|
"""

NOTES_STUB = """# Notes

<!-- Teacher's scratchpad: the learner's stated preferences, watch-outs, and working notes.
     Refer back to this when designing lessons. -->
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a teaching workspace.")
    ap.add_argument("target_dir", nargs="?", default=".", help="Workspace dir (default: cwd)")
    ap.add_argument("--topic", default="<topic>", help="Topic name for stub headings")
    args = ap.parse_args()

    root = Path(args.target_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)

    created, skipped = [], []

    for d in DIRS:
        (root / d).mkdir(exist_ok=True)

    stubs = {
        "MISSION.md": MISSION_STUB.format(topic=args.topic),
        "RESOURCES.md": RESOURCES_STUB.format(topic=args.topic),
        "review-queue.md": REVIEW_QUEUE_STUB,
        "NOTES.md": NOTES_STUB,
    }
    for name, body in stubs.items():
        dest = root / name
        if dest.exists():
            skipped.append(name)
        else:
            dest.write_text(body, encoding="utf-8")
            created.append(name)

    # Copy starter assets (never clobber a customised one).
    for asset in ("teach.css", "quiz.js", "lesson-template.html"):
        src = STARTER / asset
        dest = root / "assets" / asset
        if dest.exists():
            skipped.append(f"assets/{asset}")
        elif src.exists():
            shutil.copy2(src, dest)
            created.append(f"assets/{asset}")

    print(f"Teaching workspace: {root}")
    if created:
        print("  created: " + ", ".join(created))
    if skipped:
        print("  kept (already present): " + ", ".join(skipped))
    print("\nNext: populate MISSION.md (interview the learner if the 'why' is unclear),")
    print("then find high-trust RESOURCES before authoring lessons/0001-*.html.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
