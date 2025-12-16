from __future__ import annotations

import re
from dataclasses import dataclass

_IMPORT_RE = re.compile(
    r"(?:^|\n)\s*import\s+([^;\n]+?)\s+from\s+['\"]([^'\"]+)['\"]\s*;?",
    re.MULTILINE,
)

_EXPORT_FROM_RE = re.compile(
    r"(?:^|\n)\s*export\s+\*\s+from\s+['\"]([^'\"]+)['\"]\s*;?",
    re.MULTILINE,
)

_EXPORT_NAMED_FROM_RE = re.compile(
    r"(?:^|\n)\s*export\s+\{[^}]*\}\s+from\s+['\"]([^'\"]+)['\"]\s*;?",
    re.MULTILINE,
)


@dataclass(frozen=True)
class ImportItem:
    source: str
    clause: str | None


@dataclass(frozen=True)
class ParsedFile:
    imports: list[ImportItem]
    export_from: list[str]


def parse_imports(text: str) -> ParsedFile:
    items: list[ImportItem] = []
    for m in _IMPORT_RE.finditer(text):
        clause = m.group(1).strip()
        src = m.group(2).strip()
        items.append(ImportItem(source=src, clause=clause))

    export_from: list[str] = []
    for m in _EXPORT_FROM_RE.finditer(text):
        export_from.append(m.group(1).strip())
    for m in _EXPORT_NAMED_FROM_RE.finditer(text):
        export_from.append(m.group(1).strip())

    return ParsedFile(imports=items, export_from=export_from)


def parse_imported_names(clause: str) -> list[str]:
    clause = clause.strip()

    if clause.startswith("type "):
        clause = clause[len("type ") :].strip()

    if clause.startswith("*"):
        return ["*"]

    names: list[str] = []

    if "," in clause:
        left, right = clause.split(",", 1)
        left = left.strip()
        right = right.strip()
        if left and not left.startswith("{"):
            names.append(left)
        clause = right

    if clause.startswith("{") and "}" in clause:
        inner = clause[1 : clause.index("}")]
        for p in inner.split(","):
            p = p.strip()
            if not p:
                continue
            if " as " in p:
                p = p.split(" as ", 1)[1].strip()
            names.append(p)

    if not names and clause and not clause.startswith("{"):
        names.append(clause.split()[0])

    return [n for n in names if n]


def count_name_usages(text: str, name: str) -> int:
    if name == "*":
        return 1

    pat = re.compile(r"\b" + re.escape(name) + r"\b")
    return len(pat.findall(text))


_COMMENT_BLOCK_RE = re.compile(r"/\*[\s\S]*?\*/")
_COMMENT_LINE_RE = re.compile(r"(^|\n)\s*//.*?(?=\n|$)")
_STRING_RE = re.compile(
    r"('([^\\'\n]|\\.)*')|\"([^\\\"\n]|\\.)*\"|(`([^\\`]|\\.|\n)*?`)"
)


def strip_comments_and_strings(text: str) -> str:
    text = _COMMENT_BLOCK_RE.sub(" ", text)
    text = _COMMENT_LINE_RE.sub("\\1 ", text)
    return _STRING_RE.sub(" ", text)
