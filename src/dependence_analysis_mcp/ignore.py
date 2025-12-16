from __future__ import annotations

from pathlib import Path

from pathspec import PathSpec

_DEFAULT_IGNORED_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "out",
    ".next",
    ".nuxt",
    ".angular",
    "coverage",
    ".cache",
    ".turbo",
    ".vercel",
}

_DEFAULT_IGNORED_DIRS_EXTRA = {
    "__tests__",
    "test",
    "tests",
    "e2e",
    "cypress",
    "__mocks__",
    "mocks",
    "mock",
    "fixtures",
    "fixture",
    "examples",
    "example",
    "demo",
    "demos",
    "stories",
}

_DEFAULT_IGNORED_FILE_GLOBS = [
    "**/*.d.ts",
    "**/*.test.*",
    "**/*.spec.*",
    "**/*.stories.*",
]


def default_pathspec() -> PathSpec:
    patterns: list[str] = []

    for d in sorted(_DEFAULT_IGNORED_DIRS | _DEFAULT_IGNORED_DIRS_EXTRA):
        patterns.append(f"{d}/")
        patterns.append(f"**/{d}/")

    patterns.extend(_DEFAULT_IGNORED_FILE_GLOBS)
    return PathSpec.from_lines("gitwildmatch", patterns)


def is_ignored(path: Path, *, root: Path, spec: PathSpec) -> bool:
    rel = path.relative_to(root).as_posix()
    if spec.match_file(rel):
        return True

    parts = set(path.relative_to(root).parts)
    if parts & (_DEFAULT_IGNORED_DIRS | _DEFAULT_IGNORED_DIRS_EXTRA):
        return True

    return False
