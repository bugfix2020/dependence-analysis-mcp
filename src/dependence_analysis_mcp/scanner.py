from __future__ import annotations

from collections import Counter
from pathlib import Path

from .ignore import default_pathspec, is_ignored
from .models import AnalysisResult, ReferencedFile, UnusedImport
from .parsing import count_name_usages, parse_imported_names, parse_imports, strip_comments_and_strings
from .ts_ast import collect_identifier_usages, collect_import_bindings
from .resolve import load_tsconfig_aliases, load_vite_aliases, resolve_import


_DEFAULT_EXTS = [".ts", ".tsx", ".js", ".jsx", ".vue"]


def scan_directory(directory: str, *, roots: list[str] | None, include_extensions: list[str] | None) -> AnalysisResult:
    root = Path(directory).resolve()
    spec = default_pathspec()

    exts = _DEFAULT_EXTS if not include_extensions else [
        e if e.startswith(".") else f".{e}" for e in include_extensions
    ]

    alias_rules = []
    warnings: list[str] = []

    ts_aliases, ts_warn = load_tsconfig_aliases(root)
    warnings.extend(ts_warn)
    alias_rules.extend(ts_aliases)

    vite_aliases, vite_warn = load_vite_aliases(root)
    warnings.extend(vite_warn)
    alias_rules.extend(vite_aliases)

    all_files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if is_ignored(p, root=root, spec=spec):
            continue
        if p.suffix not in exts:
            continue
        all_files.append(p)

    import_counts: Counter[str] = Counter()
    referenced_targets: set[str] = set()
    unused_imports: list[UnusedImport] = []

    for f in all_files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            warnings.append(f"无法读取 {f}: {e}")
            continue

        stripped_for_usage = strip_comments_and_strings(text)
        is_tsx = f.suffix in {".tsx", ".jsx"}
        ast_ident_counts: dict[str, int] | None = None
        ast_import_bindings = None
        if f.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            try:
                ast_ident_counts = collect_identifier_usages(text, is_tsx=is_tsx)
                ast_import_bindings = collect_import_bindings(text, is_tsx=is_tsx)
            except Exception as e:
                warnings.append(f"AST 解析失败（降级为词法计数） {f}: {e}")

        parsed = parse_imports(text)

        import_sources = [*parsed.imports]
        for src in parsed.export_from:
            import_sources.append(type("_X", (), {"source": src, "clause": None})())

        for item in import_sources:
            src = item.source
            target = resolve_import(f, src, root, alias_rules)
            if not target:
                continue

            if is_ignored(target, root=root, spec=spec):
                continue

            clause = getattr(item, "clause", None)
            if clause:
                names = parse_imported_names(clause)
                usage_total = 0
                if ast_ident_counts is not None and ast_import_bindings is not None:
                    for n in names:
                        usage_total += max(0, ast_ident_counts.get(n, 0) - 1)
                else:
                    for n in names:
                        usage_total += max(0, count_name_usages(stripped_for_usage, n) - 1)

                if usage_total <= 0:
                    unused_imports.append(
                        UnusedImport(
                            file=str(f),
                            importSource=src,
                            importedNames=names,
                        )
                    )
                    continue

            key = str(target)
            import_counts[key] += 1
            referenced_targets.add(key)

    referenced_files = [
        ReferencedFile(path=p, importCount=c) for p, c in import_counts.most_common()
    ]

    all_paths = {str(p) for p in all_files}
    unreferenced = sorted(all_paths - referenced_targets)

    __experimental = [
        p for p in unreferenced if any(s in Path(p).stem.lower() for s in ("inputv", "tmp", "temp", "ai_"))
    ]

    return AnalysisResult(
        referencedFiles=referenced_files,
        unreferencedFiles=unreferenced,
        unusedImports=unused_imports,
        experimentalUnusefulFiles=sorted(set(__experimental)),
        warnings=warnings,
    )
