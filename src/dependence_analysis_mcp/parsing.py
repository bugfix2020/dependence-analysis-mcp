from __future__ import annotations

import re
from dataclasses import dataclass, field


_IMPORT_RE = re.compile(
    r"(?:^|\n)\s*import\s+([^;\n]+?)\s+from\s+['\"]([^'\"]+)['\"]\s*;?",
    re.MULTILINE,
)

# export * from './xxx'
_EXPORT_STAR_FROM_RE = re.compile(
    r"(?:^|\n)\s*export\s+\*\s+from\s+['\"]([^'\"]+)['\"]\s*;?",
    re.MULTILINE,
)

# export { xxx, yyy } from './zzz'
# export { default as xxx } from './zzz'
# export type { xxx } from './zzz'
_EXPORT_NAMED_FROM_RE = re.compile(
    r"(?:^|\n)\s*export\s+(?:type\s+)?\{([^}]*)\}\s+from\s+['\"]([^'\"]+)['\"]\s*;?",
    re.MULTILINE,
)

# 动态导入: import('./xxx') 或 import("./xxx")
_DYNAMIC_IMPORT_RE = re.compile(
    r"import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
    re.MULTILINE,
)

# require('./xxx') 或 require("./xxx")
_REQUIRE_RE = re.compile(
    r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
    re.MULTILINE,
)

# import.meta.glob 模式 (Vite 特有)
# import.meta.glob(['../pages/**/*.tsx', '!**/__tests__/**'])
# import.meta.glob('../pages/**/*.tsx')
# import.meta.glob<{ default: FC }>(['../pages/**/*.tsx'])  -- with TypeScript generics
_IMPORT_META_GLOB_RE = re.compile(
    r"import\.meta\.glob(?:Eager)?(?:<[^>]*>)?\s*\(\s*(\[[\s\S]*?\]|['\"][^'\"]+['\"])",
    re.MULTILINE,
)


@dataclass(frozen=True)
class ImportItem:
    source: str
    clause: str | None


@dataclass(frozen=True)
class ExportFromItem:
    """重导出项"""
    source: str  # 来源模块
    names: list[str] = field(default_factory=list)  # 导出的名称列表，空列表表示 export *
    is_star: bool = False  # 是否是 export *


@dataclass(frozen=True)
class GlobPattern:
    """Vite import.meta.glob 模式"""
    pattern: str
    is_negation: bool = False  # 是否是排除模式 (以 ! 开头)


@dataclass(frozen=True)
class ParsedFile:
    imports: list[ImportItem]
    export_from: list[ExportFromItem]
    dynamic_imports: list[str]  # 动态导入的模块
    glob_patterns: list[GlobPattern] = field(default_factory=list)  # import.meta.glob 模式


def parse_imports(text: str) -> ParsedFile:
    items: list[ImportItem] = []
    for m in _IMPORT_RE.finditer(text):
        clause = m.group(1).strip()
        src = m.group(2).strip()
        items.append(ImportItem(source=src, clause=clause))

    export_from: list[ExportFromItem] = []
    
    # export * from './xxx'
    for m in _EXPORT_STAR_FROM_RE.finditer(text):
        src = m.group(1).strip()
        export_from.append(ExportFromItem(source=src, names=[], is_star=True))
    
    # export { xxx } from './xxx'
    for m in _EXPORT_NAMED_FROM_RE.finditer(text):
        names_str = m.group(1).strip()
        src = m.group(2).strip()
        names = parse_export_names(names_str)
        export_from.append(ExportFromItem(source=src, names=names, is_star=False))

    # 动态导入
    dynamic_imports: list[str] = []
    for m in _DYNAMIC_IMPORT_RE.finditer(text):
        src = m.group(1).strip()
        dynamic_imports.append(src)
    
    # require 调用
    for m in _REQUIRE_RE.finditer(text):
        src = m.group(1).strip()
        dynamic_imports.append(src)

    # import.meta.glob 模式
    glob_patterns: list[GlobPattern] = []
    for m in _IMPORT_META_GLOB_RE.finditer(text):
        raw = m.group(1).strip()
        patterns = parse_glob_patterns(raw)
        glob_patterns.extend(patterns)

    return ParsedFile(imports=items, export_from=export_from, dynamic_imports=dynamic_imports, glob_patterns=glob_patterns)


def parse_glob_patterns(raw: str) -> list[GlobPattern]:
    """解析 import.meta.glob 的参数"""
    patterns: list[GlobPattern] = []
    
    # 移除外层引号或方括号
    raw = raw.strip()
    
    if raw.startswith("["):
        # 数组形式: ['../pages/**/*.tsx', '!**/__tests__/**']
        # 简单提取字符串
        import json
        try:
            # 尝试用 JSON 解析
            arr = json.loads(raw.replace("'", '"'))
            for p in arr:
                if isinstance(p, str):
                    p = p.strip()
                    is_neg = p.startswith("!")
                    if is_neg:
                        p = p[1:]
                    patterns.append(GlobPattern(pattern=p, is_negation=is_neg))
        except Exception:
            # 降级：使用正则提取
            str_matches = re.findall(r"['\"]([^'\"]+)['\"]", raw)
            for p in str_matches:
                p = p.strip()
                is_neg = p.startswith("!")
                if is_neg:
                    p = p[1:]
                patterns.append(GlobPattern(pattern=p, is_negation=is_neg))
    else:
        # 单个字符串形式: '../pages/**/*.tsx'
        p = raw.strip("'\"")
        is_neg = p.startswith("!")
        if is_neg:
            p = p[1:]
        patterns.append(GlobPattern(pattern=p, is_negation=is_neg))
    
    return patterns


def parse_export_names(names_str: str) -> list[str]:
    """解析 export { xxx, yyy as zzz } 中的名称"""
    names: list[str] = []
    for part in names_str.split(","):
        part = part.strip()
        if not part:
            continue
        # 处理 "default as xxx" 或 "xxx as yyy"
        if " as " in part:
            # 取别名部分
            _, alias = part.split(" as ", 1)
            names.append(alias.strip())
        else:
            names.append(part)
    return names


def parse_imported_names(clause: str) -> list[str]:
    """
    解析 import 语句的 clause 部分，提取所有导入的本地绑定名称。
    
    支持的格式:
    - `Button` -> ['Button']
    - `{ Button }` -> ['Button']
    - `{ Button, Icon }` -> ['Button', 'Icon']
    - `{ Button as Btn }` -> ['Btn']
    - `{ type Button }` -> ['Button']
    - `{ type Button, Icon }` -> ['Button', 'Icon']
    - `* as Components` -> ['Components']
    - `Button, { Icon }` -> ['Button', 'Icon']
    - `type { Button }` -> ['Button']
    """
    clause = clause.strip()
    
    if not clause:
        return []
    
    # 处理 `type { ... }` 形式（整个导入是类型导入）
    if clause.startswith("type "):
        clause = clause[5:].strip()
    
    # 处理 `* as xxx` 命名空间导入
    if clause.startswith("*"):
        if " as " in clause:
            # `* as Components`
            alias = clause.split(" as ", 1)[1].strip()
            return [alias]
        return ["*"]
    
    names: list[str] = []
    
    # 分离默认导入和命名导入
    # 例如: `Button, { Icon, Text }` -> default_part="Button", named_part="{ Icon, Text }"
    default_part = ""
    named_part = ""
    
    if "{" in clause:
        brace_start = clause.index("{")
        default_part = clause[:brace_start].strip().rstrip(",").strip()
        # 提取 { ... } 内容
        brace_end = clause.rfind("}")
        if brace_end > brace_start:
            named_part = clause[brace_start + 1 : brace_end]
    else:
        # 没有 { }，整个是默认导入或简单导入
        default_part = clause
    
    # 处理默认导入部分
    if default_part:
        # 可能是 `Button` 或 `Button, Icon`（不带花括号的多个导入，虽然少见）
        for part in default_part.split(","):
            part = part.strip()
            if not part:
                continue
            # 处理 `type xxx` 前缀
            if part.startswith("type "):
                part = part[5:].strip()
            # 处理 `xxx as yyy`
            if " as " in part:
                part = part.split(" as ", 1)[1].strip()
            if part and part not in names:
                names.append(part)
    
    # 处理命名导入部分 { ... }
    if named_part:
        for part in named_part.split(","):
            part = part.strip()
            if not part:
                continue
            # 处理 `type xxx` 前缀
            if part.startswith("type "):
                part = part[5:].strip()
            # 处理 `xxx as yyy`
            if " as " in part:
                part = part.split(" as ", 1)[1].strip()
            if part and part not in names:
                names.append(part)
    
    return names


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
