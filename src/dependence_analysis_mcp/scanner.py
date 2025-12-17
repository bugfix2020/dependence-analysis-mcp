from __future__ import annotations

import fnmatch
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from .ignore import default_pathspec, is_ignored
from .models import AnalysisResult, ReferencedFile, UnusedImport
from .parsing import count_name_usages, parse_imported_names, parse_imports, strip_comments_and_strings, GlobPattern
from .ts_ast import collect_identifier_usages, collect_import_bindings
from .resolve import AliasRule, load_tsconfig_aliases, load_vite_aliases, resolve_import
from .path_search import verify_file_is_referenced


_DEFAULT_EXTS = [".ts", ".tsx", ".js", ".jsx", ".vue"]


_CONFIG_NAMES = (
    "tsconfig.json",
    "tsconfig.base.json",
    "tsconfig.app.json",
    "jsconfig.json",
)


@lru_cache(maxsize=4096)
def _find_nearest_project_root(start_dir: Path, stop_dir: Path) -> Path:
    """
    从 start_dir 向上查找项目根目录。
    
    会持续向上查找直到找到配置文件或到达文件系统根目录。
    stop_dir 作为最小返回值（如果找不到配置文件）。
    """
    cur = start_dir
    stop_dir = stop_dir.resolve()
    
    # 记录搜索过程中找到的 stop_dir（作为兜底）
    fallback = stop_dir
    
    while True:
        for name in _CONFIG_NAMES:
            if (cur / name).exists():
                return cur

        if any(cur.glob("vite.config.*")):
            return cur

        if (cur / "package.json").exists():
            return cur

        # 到达文件系统根目录
        if cur.parent == cur:
            return fallback

        cur = cur.parent


def _resolve_glob_patterns(
    importer: Path,
    patterns: list[GlobPattern],
    all_files_set: set[str],
) -> set[str]:
    """
    解析 import.meta.glob 模式，返回匹配的文件路径
    
    Args:
        importer: 包含 import.meta.glob 的文件路径
        patterns: glob 模式列表
        all_files_set: 所有扫描到的文件路径集合
    
    Returns:
        匹配的文件路径集合
    """
    if not patterns:
        return set()
    
    base_dir = importer.parent
    include_patterns: list[str] = []
    exclude_patterns: list[str] = []
    
    for p in patterns:
        # 将相对路径转换为绝对路径的 glob 模式
        pattern = p.pattern
        if pattern.startswith("./"):
            pattern = pattern[2:]
        elif pattern.startswith("../"):
            # 处理 ../pages/**/*.tsx 这种形式
            # 需要相对于 importer 的目录解析
            resolved_base = (base_dir / pattern.split("*")[0].rstrip("/")).resolve()
            # 重构 glob 模式
            glob_suffix = "*" + pattern.split("*", 1)[1] if "*" in pattern else ""
            pattern = str(resolved_base) + "/" + glob_suffix if glob_suffix else str(resolved_base)
        else:
            pattern = str(base_dir / pattern)
        
        if p.is_negation:
            exclude_patterns.append(pattern)
        else:
            include_patterns.append(pattern)
    
    matched: set[str] = set()
    
    for file_path in all_files_set:
        # 检查是否匹配 include 模式
        included = False
        for inc_pat in include_patterns:
            if fnmatch.fnmatch(file_path, inc_pat):
                included = True
                break
        
        if not included:
            continue
        
        # 检查是否被 exclude 模式排除
        excluded = False
        for exc_pat in exclude_patterns:
            if fnmatch.fnmatch(file_path, exc_pat):
                excluded = True
                break
        
        if not excluded:
            matched.add(file_path)
    
    return matched


@lru_cache(maxsize=1024)
def _load_alias_rules(project_root: Path) -> tuple[tuple[AliasRule, ...], tuple[str, ...]]:
    rules: list[AliasRule] = []
    warnings: list[str] = []

    ts_aliases, ts_warn = load_tsconfig_aliases(project_root)
    warnings.extend(ts_warn)
    rules.extend(ts_aliases)

    vite_aliases, vite_warn = load_vite_aliases(project_root)
    warnings.extend(vite_warn)
    rules.extend(vite_aliases)

    return (tuple(rules), tuple(warnings))


def scan_directory(directory: str, *, roots: list[str] | None, include_extensions: list[str] | None) -> AnalysisResult:
    root = Path(directory).resolve()
    spec = default_pathspec()

    exts = _DEFAULT_EXTS if not include_extensions else [
        e if e.startswith(".") else f".{e}" for e in include_extensions
    ]

    warnings: list[str] = []
    warned: set[str] = set()

    all_files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if is_ignored(p, root=root, spec=spec):
            continue
        if p.suffix not in exts:
            continue
        all_files.append(p)

    # ===========================================================================
    # 第一阶段：构建重导出图 (re-export graph)
    # 当 A 文件 export * from './B' 时，A -> B 的所有导出
    # ===========================================================================
    
    # re_export_graph[A] = set of files that A re-exports
    re_export_graph: dict[str, set[str]] = defaultdict(set)
    
    # 文件内容缓存
    file_contents: dict[str, str] = {}
    
    for f in all_files:
        project_root = _find_nearest_project_root(f.parent, root)
        alias_rules, alias_warnings = _load_alias_rules(project_root)
        for w in alias_warnings:
            if w not in warned:
                warnings.append(w)
                warned.add(w)

        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            file_contents[str(f)] = text
        except Exception as e:
            warnings.append(f"无法读取 {f}: {e}")
            continue

        parsed = parse_imports(text)
        
        # 构建重导出关系
        for export_item in parsed.export_from:
            target = resolve_import(f, export_item.source, project_root, list(alias_rules))
            if target and not is_ignored(target, root=root, spec=spec):
                re_export_graph[str(f)].add(str(target))
    
    # ===========================================================================
    # 展开重导出图：计算传递闭包
    # 如果 A -> B -> C，那么引用 A 也应该标记 B 和 C 为被引用
    # ===========================================================================
    
    def get_all_reexported(file_path: str, visited: set[str] | None = None) -> set[str]:
        """获取文件的所有重导出目标（包括传递性）"""
        if visited is None:
            visited = set()
        if file_path in visited:
            return set()
        visited.add(file_path)
        
        result = set()
        for target in re_export_graph.get(file_path, set()):
            result.add(target)
            result.update(get_all_reexported(target, visited))
        return result

    # ===========================================================================
    # 第二阶段：扫描引用关系
    # ===========================================================================
    
    import_counts: Counter[str] = Counter()
    referenced_targets: set[str] = set()
    unused_imports: list[UnusedImport] = []

    for f in all_files:
        project_root = _find_nearest_project_root(f.parent, root)
        alias_rules, _ = _load_alias_rules(project_root)

        text = file_contents.get(str(f))
        if text is None:
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

        # 处理常规 import
        for item in parsed.imports:
            src = item.source
            target = resolve_import(f, src, project_root, list(alias_rules))
            if not target:
                continue

            if is_ignored(target, root=root, spec=spec):
                continue

            clause = item.clause
            if clause:
                names = parse_imported_names(clause)
                usage_total = 0
                
                # 使用 AST 和正则计数中的较大值，以提高准确性
                # (tree-sitter 在某些复杂文件中可能漏掉 JSX 中的标识符)
                for n in names:
                    ast_count = ast_ident_counts.get(n, 0) if ast_ident_counts else 0
                    regex_count = count_name_usages(stripped_for_usage, n)
                    # 取两者中较大的值
                    effective_count = max(ast_count, regex_count)
                    usage_total += max(0, effective_count - 1)

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
            
            # 标记重导出的文件也为被引用
            for reexported in get_all_reexported(key):
                import_counts[reexported] += 1
                referenced_targets.add(reexported)

        # 处理 export ... from ... 也作为引用
        for export_item in parsed.export_from:
            target = resolve_import(f, export_item.source, project_root, list(alias_rules))
            if target and not is_ignored(target, root=root, spec=spec):
                key = str(target)
                import_counts[key] += 1
                referenced_targets.add(key)
        
        # 处理动态导入
        for dynamic_src in parsed.dynamic_imports:
            target = resolve_import(f, dynamic_src, project_root, list(alias_rules))
            if target and not is_ignored(target, root=root, spec=spec):
                key = str(target)
                import_counts[key] += 1
                referenced_targets.add(key)
        
        # 处理 import.meta.glob 模式
        if parsed.glob_patterns:
            all_files_set = {str(p) for p in all_files}
            glob_matches = _resolve_glob_patterns(f, list(parsed.glob_patterns), all_files_set)
            for matched_file in glob_matches:
                if not is_ignored(Path(matched_file), root=root, spec=spec):
                    import_counts[matched_file] += 1
                    referenced_targets.add(matched_file)

    referenced_files = [
        ReferencedFile(path=p, importCount=c) for p, c in import_counts.most_common()
    ]

    all_paths = {str(p) for p in all_files}
    unreferenced_initial = sorted(all_paths - referenced_targets)

    # ===========================================================================
    # 第三阶段：使用路径搜索验证未引用文件
    # 对于初步判断为"未引用"的文件，使用 grep 搜索进行二次验证
    # ===========================================================================
    
    # 构建别名映射（用于生成搜索模式）
    alias_map: dict[str, str] = {}
    # 获取第一个文件的项目根目录来加载别名（假设整个目录使用相同的别名配置）
    if all_files:
        sample_project_root = _find_nearest_project_root(all_files[0].parent, root)
        sample_rules, _ = _load_alias_rules(sample_project_root)
        for rule in sample_rules:
            # 移除通配符，如 "@/*" -> "@"
            alias_key = rule.find.rstrip("/*").rstrip("*")
            alias_value = rule.replacement.rstrip("/*").rstrip("*")
            alias_map[alias_key] = alias_value
    
    # 对未引用文件进行路径搜索验证
    unreferenced: list[str] = []
    for file_path_str in unreferenced_initial:
        file_path = Path(file_path_str)
        
        # 使用路径搜索验证
        is_referenced, _ = verify_file_is_referenced(
            file_path=file_path,
            project_root=root,
            search_dir=root,
            alias_map=alias_map,
        )
        
        if is_referenced:
            # 路径搜索发现被引用，添加到引用列表
            import_counts[file_path_str] += 1
            referenced_targets.add(file_path_str)
        else:
            # 确认未被引用
            unreferenced.append(file_path_str)
    
    # 更新引用文件列表
    referenced_files = [
        ReferencedFile(path=p, importCount=c) for p, c in import_counts.most_common()
    ]

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
