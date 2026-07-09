#!/usr/bin/env python3
"""Scaffold a course directory from combined lesson JSON.

Reads a JSON file of the shape `{"lessons": [...]}` (the combined output of all
per-chunk subagents) plus templates from `assets/`, and writes:

    <out>/
    ├── README.md
    ├── _TEACHER.md
    ├── _meta.json
    ├── .progress.json
    ├── 01-<chapter-slug>/        (one per group of consecutive lessons sharing a chapter)
    │   ├── README.md
    │   └── 01-<lesson-slug>/
    │       ├── README.md
    │       ├── exercises/
    │       │   └── 01-<exercise-slug>.<ext>
    │       ├── tests/
    │       │   └── 01-<exercise-slug>.test.<ext>
    │       └── .solutions/
    │           └── 01-<exercise-slug>.solution.<ext>
    └── ...

This is the boring file-IO glue. Everything subjective (lesson content, exercise
quality) was already decided by the subagents.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path

# Maps language → (file extension, test file extension, conventional test command)
LANGUAGE_PROFILES: dict[str, dict[str, str]] = {
    "python":     {"ext": "py", "test_ext": "py", "test_command": "python -m pytest"},
    "javascript": {"ext": "js", "test_ext": "js", "test_command": "node"},
    "typescript": {"ext": "ts", "test_ext": "ts", "test_command": "npx tsx"},
    "go":         {"ext": "go", "test_ext": "go", "test_command": "go test"},
    "terraform":  {"ext": "tf", "test_ext": "sh", "test_command": "bash"},
    "hcl":        {"ext": "tf", "test_ext": "sh", "test_command": "bash"},
    "php":        {"ext": "php", "test_ext": "php", "test_command": "./vendor/bin/pest"},
    "pest":       {"ext": "php", "test_ext": "php", "test_command": "./vendor/bin/pest"},
    "docker":     {"ext": "sh", "test_ext": "sh", "test_command": "bash"},
    "shell":      {"ext": "sh", "test_ext": "sh", "test_command": "bash"},
    "bash":       {"ext": "sh", "test_ext": "sh", "test_command": "bash"},
    "swift":      {"ext": "swift", "test_ext": "swift", "test_command": "swift"},
    "sql":        {"ext": "sql", "test_ext": "sh", "test_command": "bash"},
    "c":          {"ext": "c", "test_ext": "sh", "test_command": "bash"},
}

SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, fallback: str = "untitled") -> str:
    s = SLUG_RE.sub("-", text.lower()).strip("-")
    return s[:60] if s else fallback


def load_template(assets_dir: Path, name: str) -> str:
    return (assets_dir / name).read_text(encoding="utf-8")


def render(template: str, **kwargs: object) -> str:
    out = template
    for k, v in kwargs.items():
        out = out.replace(f"{{{{{k}}}}}", str(v))
    return out


def group_lessons_into_chapters(lessons: list[dict]) -> list[dict]:
    """Group consecutive lessons by chapter_title (set on each lesson by orchestrator).

    Lessons without a chapter_title get bucketed into a single 'Lessons' chapter.
    """
    chapters: list[dict] = []
    current: dict | None = None

    for lesson in lessons:
        chap_title = lesson.get("chapter_title") or "Lessons"
        if current is None or current["title"] != chap_title:
            current = {"title": chap_title, "lessons": []}
            chapters.append(current)
        current["lessons"].append(lesson)

    return chapters


def write_exercise_files(
    lesson_dir: Path,
    exercises: list[dict],
    profile: dict[str, str],
) -> None:
    ex_dir = lesson_dir / "exercises"
    test_dir = lesson_dir / "tests"
    sol_dir = lesson_dir / ".solutions"
    for d in (ex_dir, test_dir, sol_dir):
        d.mkdir(parents=True, exist_ok=True)

    ext = profile["ext"]
    test_ext = profile["test_ext"]

    for i, ex in enumerate(exercises, start=1):
        slug = slugify(ex.get("title", f"exercise-{i}"), f"exercise-{i}")
        prefix = f"{i:02d}-{slug}"

        (ex_dir / f"{prefix}.{ext}").write_text(ex["starter_code"], encoding="utf-8")
        (test_dir / f"{prefix}.test.{test_ext}").write_text(ex["test_code"], encoding="utf-8")
        (sol_dir / f"{prefix}.solution.{ext}").write_text(ex["solution_code"], encoding="utf-8")


def write_lesson(
    chapter_dir: Path,
    lesson: dict,
    lesson_index: int,
    assets_dir: Path,
    profile: dict[str, str],
) -> str:
    slug = slugify(lesson["title"], f"lesson-{lesson_index}")
    lesson_dir_name = f"{lesson_index:02d}-{slug}"
    lesson_dir = chapter_dir / lesson_dir_name
    lesson_dir.mkdir(parents=True, exist_ok=True)

    # Build exercise list for the README
    exercise_lines = []
    for i, ex in enumerate(lesson.get("exercises", []), start=1):
        ex_slug = slugify(ex.get("title", f"exercise-{i}"), f"exercise-{i}")
        exercise_lines.append(
            f"{i}. **{ex.get('title', f'Exercise {i}')}** — `exercises/{i:02d}-{ex_slug}.{profile['ext']}`\n"
            f"   {ex.get('instructions', '').splitlines()[0] if ex.get('instructions') else ''}"
        )

    template = load_template(assets_dir, "lesson-README.template.md")
    readme = render(
        template,
        title=lesson["title"],
        content=lesson["content"],
        exercise_list="\n".join(exercise_lines) if exercise_lines else "_(no exercises)_",
    )
    (lesson_dir / "README.md").write_text(readme, encoding="utf-8")

    write_exercise_files(lesson_dir, lesson.get("exercises", []), profile)

    return lesson_dir_name


def write_chapter(
    course_dir: Path,
    chapter: dict,
    chapter_index: int,
    assets_dir: Path,
    profile: dict[str, str],
) -> tuple[str, list[str]]:
    slug = slugify(chapter["title"], f"chapter-{chapter_index}")
    chapter_dir_name = f"{chapter_index:02d}-{slug}"
    chapter_dir = course_dir / chapter_dir_name
    chapter_dir.mkdir(parents=True, exist_ok=True)

    lesson_entries: list[str] = []
    lesson_dir_names: list[str] = []
    for i, lesson in enumerate(chapter["lessons"], start=1):
        lesson_dir_name = write_lesson(chapter_dir, lesson, i, assets_dir, profile)
        lesson_dir_names.append(lesson_dir_name)
        lesson_entries.append(f"{i}. [{lesson['title']}]({lesson_dir_name}/README.md)")

    template = load_template(assets_dir, "chapter-README.template.md")
    readme = render(
        template,
        title=chapter["title"],
        lesson_count=len(chapter["lessons"]),
        lesson_list="\n".join(lesson_entries),
    )
    (chapter_dir / "README.md").write_text(readme, encoding="utf-8")

    return chapter_dir_name, lesson_dir_names


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a course directory from lesson JSON.")
    parser.add_argument("course_json", type=Path, help="Combined lessons JSON")
    parser.add_argument("output_dir", type=Path, help="Course output directory")
    parser.add_argument("--language", required=True, help="Programming language (python, javascript, ...)")
    parser.add_argument("--source", default="(unknown)", help="Source markdown path. If it's a real file, it gets moved into the course root after scaffolding.")
    parser.add_argument("--no-move-source", action="store_true", help="Disable moving --source into the course root (default: move).")
    args = parser.parse_args()

    lang_key = args.language.strip().lower()
    profile = LANGUAGE_PROFILES.get(lang_key)
    if profile is None:
        # Unknown language — fall back to plain text extension and let the user fix it.
        profile = {"ext": "txt", "test_ext": "txt", "test_command": f"# TODO: set test command for {args.language}"}

    data = json.loads(args.course_json.read_text(encoding="utf-8"))
    lessons = data.get("lessons", [])
    if not lessons:
        print("error: course JSON contains no lessons", file=sys.stderr)
        return 1

    skill_dir = Path(__file__).resolve().parent.parent
    assets_dir = skill_dir / "assets"

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    chapters = group_lessons_into_chapters(lessons)

    chapter_entries: list[str] = []
    first_chapter_dir: str | None = None
    first_lesson_dir: str | None = None
    total_exercises = 0

    for ci, chapter in enumerate(chapters, start=1):
        chap_dir, lesson_dir_names = write_chapter(out, chapter, ci, assets_dir, profile)
        chapter_entries.append(f"{ci}. [{chapter['title']}]({chap_dir}/README.md)")
        if first_chapter_dir is None:
            first_chapter_dir = chap_dir
            if lesson_dir_names:
                first_lesson_dir = lesson_dir_names[0]
        for lesson in chapter["lessons"]:
            total_exercises += len(lesson.get("exercises", []))

    # Move source markdown into course root, if given a real path.
    moved_source: Path | None = None
    source_path = Path(args.source)
    if (
        not args.no_move_source
        and args.source != "(unknown)"
        and source_path.is_file()
    ):
        dest = out / source_path.name
        if source_path.resolve() != dest.resolve():
            shutil.move(str(source_path), str(dest))
            moved_source = dest
    source_label = moved_source.name if moved_source else args.source

    course_title = out.name.replace("-", " ").title()
    course_readme = render(
        load_template(assets_dir, "course-README.template.md"),
        title=course_title,
        language=args.language,
        source=source_label,
        chapter_count=len(chapters),
        lesson_count=sum(len(c["lessons"]) for c in chapters),
        exercise_count=total_exercises,
        chapter_list="\n".join(chapter_entries),
    )
    (out / "README.md").write_text(course_readme, encoding="utf-8")

    teacher = render(
        load_template(assets_dir, "_TEACHER.template.md"),
        language=args.language,
        test_command=profile["test_command"],
    )
    (out / "_TEACHER.md").write_text(teacher, encoding="utf-8")

    meta = {
        "language": args.language,
        "source_file": source_label,
        "test_command": profile["test_command"],
        "file_extension": profile["ext"],
        "test_extension": profile["test_ext"],
        "chapter_count": len(chapters),
        "lesson_count": sum(len(c["lessons"]) for c in chapters),
        "exercise_count": total_exercises,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    (out / "_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    progress = {
        "current_chapter": first_chapter_dir or "",
        "current_lesson": first_lesson_dir or "",
        "completed_exercises": [],
    }
    (out / ".progress.json").write_text(json.dumps(progress, indent=2) + "\n", encoding="utf-8")

    summary = {
        "course_path": str(out.resolve()),
        "chapters": len(chapters),
        "lessons": meta["lesson_count"],
        "exercises": total_exercises,
        "moved_source": str(moved_source) if moved_source else None,
        "next_step": (
            f"cd {out} && claude   then say: \"start lesson 1\""
        ),
    }
    json.dump(summary, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
