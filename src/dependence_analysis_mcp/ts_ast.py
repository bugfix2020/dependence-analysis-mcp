from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from tree_sitter import Language, Node, Parser
from tree_sitter_typescript import language_tsx, language_typescript


@dataclass(frozen=True)
class ImportBinding:
    name: str
    start_byte: int
    end_byte: int


@lru_cache(maxsize=4)
def _parser_for(is_tsx: bool) -> Parser:
    lang = Language(language_tsx() if is_tsx else language_typescript())
    p = Parser()
    p.language = lang
    return p


def _iter_nodes(node: Node):
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        for c in reversed(n.children):
            stack.append(c)


def collect_import_bindings(code: str, *, is_tsx: bool) -> list[ImportBinding]:
    parser = _parser_for(is_tsx)
    tree = parser.parse(code.encode("utf-8", errors="ignore"))
    root = tree.root_node

    bindings: list[ImportBinding] = []

    for n in _iter_nodes(root):
        if n.type != "import_clause":
            continue

        for child in n.children:
            if child.type == "identifier":
                bindings.append(
                    ImportBinding(
                        name=code[child.start_byte : child.end_byte],
                        start_byte=child.start_byte,
                        end_byte=child.end_byte,
                    )
                )
            elif child.type == "named_imports":
                for g in child.children:
                    if g.type != "import_specifier":
                        continue
                    local_name = None
                    for gg in g.children:
                        if gg.type == "identifier":
                            local_name = code[gg.start_byte : gg.end_byte]
                        elif gg.type == "property_identifier":
                            local_name = code[gg.start_byte : gg.end_byte]
                    if local_name:
                        bindings.append(
                            ImportBinding(
                                name=local_name,
                                start_byte=g.start_byte,
                                end_byte=g.end_byte,
                            )
                        )
            elif child.type == "namespace_import":
                for g in child.children:
                    if g.type == "identifier":
                        bindings.append(
                            ImportBinding(
                                name=code[g.start_byte : g.end_byte],
                                start_byte=g.start_byte,
                                end_byte=g.end_byte,
                            )
                        )

    return bindings


def collect_identifier_usages(code: str, *, is_tsx: bool) -> dict[str, int]:
    parser = _parser_for(is_tsx)
    tree = parser.parse(code.encode("utf-8", errors="ignore"))
    root = tree.root_node

    counts: dict[str, int] = {}

    for n in _iter_nodes(root):
        if n.type not in {"identifier", "property_identifier"}:
            continue
        name = code[n.start_byte : n.end_byte]
        counts[name] = counts.get(name, 0) + 1

    return counts
