from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AliasRule:
    find: str
    replacement: str


def _strip_json_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(^|\n)\s*//.*", "\\1", text)
    return text


def load_tsconfig_aliases(project_root: Path) -> tuple[list[AliasRule], list[str]]:
    warnings: list[str] = []
    for name in ("tsconfig.json", "tsconfig.base.json", "tsconfig.app.json", "jsconfig.json"):
        p = project_root / name
        if p.exists():
            try:
                raw = _strip_json_comments(p.read_text(encoding="utf-8", errors="ignore"))
                data = json.loads(raw)
            except Exception as e:
                warnings.append(f"无法解析 {p}: {e}")
                continue

            co = (data.get("compilerOptions") or {})
            base_url = co.get("baseUrl")
            paths = co.get("paths") or {}
            if not base_url or not isinstance(paths, dict):
                return ([], warnings)

            base_dir = (project_root / base_url).resolve()
            rules: list[AliasRule] = []
            for k, v in paths.items():
                if not isinstance(v, list) or not v:
                    continue
                target = v[0]
                if not isinstance(target, str):
                    continue

                find = k
                repl = str((base_dir / target).resolve())
                rules.append(AliasRule(find=find, replacement=repl))

            return (rules, warnings)

    return ([], warnings)


_VITE_ALIAS_OBJ_RE = re.compile(
    r"alias\s*:\s*\{(?P<body>[^\}]+)\}", re.DOTALL
)
_VITE_ALIAS_PAIR_RE = re.compile(
    # Value may contain commas (e.g. path.resolve(__dirname, './src')), so capture until line end.
    r"['\"](?P<k>[^'\"]+)['\"]\s*:\s*(?P<v>[^\n]+)",
    re.DOTALL,
)
_VITE_ALIAS_ARRAY_RE = re.compile(
    r"alias\s*:\s*\[(?P<body>[\s\S]+?)\]",
    re.DOTALL,
)
_VITE_ALIAS_FIND_REPL_RE = re.compile(
    r"\{[\s\S]*?find\s*:\s*(['\"])(?P<find>.+?)\1[\s\S]*?replacement\s*:\s*(?P<repl>[\s\S]*?)\}\s*,?",
    re.DOTALL,
)


def load_vite_aliases(project_root: Path) -> tuple[list[AliasRule], list[str]]:
    warnings: list[str] = []
    candidates = list(project_root.glob("vite.config.*"))
    if not candidates:
        return ([], warnings)

    def _score(path: Path) -> int:
        s = 0
        if path.name == "vite.config.ts":
            s += 30
        if path.suffix == ".ts":
            s += 10
        if path.suffix in {".js", ".mjs", ".cjs"}:
            s += 5
        return s

    p = sorted(candidates, key=_score, reverse=True)[0]
    text = p.read_text(encoding="utf-8", errors="ignore")

    rules: list[AliasRule] = []

    m = _VITE_ALIAS_OBJ_RE.search(text)
    if m:
        body = m.group("body")
        for pm in _VITE_ALIAS_PAIR_RE.finditer(body):
            k = pm.group("k")
            v = pm.group("v").strip().rstrip(",").strip()
            repl = _eval_vite_replacement(v, project_root, warnings)
            if repl:
                rules.append(AliasRule(find=k, replacement=repl))

    m = _VITE_ALIAS_ARRAY_RE.search(text)
    if m:
        body = m.group("body")
        for am in _VITE_ALIAS_FIND_REPL_RE.finditer(body):
            find = am.group("find")
            repl_expr = am.group("repl").strip()
            if repl_expr.endswith(","):
                repl_expr = repl_expr[:-1].strip()
            repl = _eval_vite_replacement(repl_expr, project_root, warnings)
            if repl:
                rules.append(AliasRule(find=find, replacement=repl))

    return (rules, warnings)


_PATH_RESOLVE_RE = re.compile(
    r"path\.resolve\(\s*__dirname\s*,\s*(['\"])(?P<p>.+?)\1\s*\)"
)
_PATH_RESOLVE_META_DIRNAME_RE = re.compile(
    r"path\.resolve\(\s*import\.meta\.dirname\s*,\s*(['\"])(?P<p>.+?)\1\s*\)"
)
_PROCESS_CWD_RE = re.compile(
    r"process\.cwd\(\s*\)"
)
_URL_PATHNAME_RE = re.compile(
    r"new\s+URL\(\s*(['\"])(?P<p>.+?)\1\s*,\s*import\.meta\.url\s*\)\s*\.pathname"
)
_URL_RE = re.compile(
    r"new\s+URL\(\s*(['\"])(?P<p>.+?)\1\s*,\s*import\.meta\.url\s*\)"
)
_STRING_RE = re.compile(r"^(['\"])(?P<p>.+?)\1$")
_PATH_FILEURL_RE = re.compile(
    r"fileURLToPath\(\s*new\s+URL\(\s*(['\"])(?P<p>.+?)\1\s*,\s*import\.meta\.url\s*\)\s*\)"
)


def _eval_vite_replacement(expr: str, project_root: Path, warnings: list[str]) -> str | None:
    expr = expr.strip().rstrip()

    m = _STRING_RE.match(expr)
    if m:
        p = m.group("p")
        return str((project_root / p.lstrip("/")).resolve()) if p.startswith("/") else str(
            (project_root / p).resolve()
        )

    m = _PATH_RESOLVE_RE.search(expr)
    if m:
        p = m.group("p")
        return str((project_root / p).resolve())

    m = _PATH_RESOLVE_META_DIRNAME_RE.search(expr)
    if m:
        p = m.group("p")
        return str((project_root / p).resolve())

    if _PROCESS_CWD_RE.search(expr):
        m2 = re.search(r"process\.cwd\(\s*\)\s*,\s*(['\"])(?P<p>.+?)\1", expr)
        if m2:
            p = m2.group("p")
            return str((project_root / p).resolve())

    m = _PATH_FILEURL_RE.search(expr)
    if m:
        p = m.group("p")
        if p.startswith("./"):
            p = p[2:]
        return str((project_root / p).resolve())

    m = _URL_PATHNAME_RE.search(expr)
    if m:
        p = m.group("p")
        if p.startswith("./"):
            p = p[2:]
        return str((project_root / p).resolve())

    m = _URL_RE.search(expr)
    if m:
        p = m.group("p")
        if p.startswith("./"):
            p = p[2:]
        return str((project_root / p).resolve())

    warnings.append(f"无法解析 vite alias replacement 表达式: {expr[:120]}")
    return None


_EXTS = [".ts", ".tsx", ".js", ".jsx", ".vue"]


def resolve_import(
    importer: Path,
    source: str,
    project_root: Path,
    alias_rules: list[AliasRule],
) -> Path | None:
    source = source.strip()

    if source.startswith("http:") or source.startswith("https:"):
        return None

    if source.startswith("./") or source.startswith("../"):
        base = (importer.parent / source).resolve()
        return _resolve_as_file_or_dir(base)

    for rule in alias_rules:
        if "*" in rule.find:
            prefix = rule.find.split("*", 1)[0]
            if source.startswith(prefix):
                rest = source[len(prefix) :]
                repl_prefix = rule.replacement.split("*", 1)[0]
                base = Path(repl_prefix + rest).resolve()
                return _resolve_as_file_or_dir(base)
        else:
            if source == rule.find or source.startswith(rule.find + "/"):
                rest = source[len(rule.find) :].lstrip("/")
                base = (Path(rule.replacement) / rest).resolve()
                return _resolve_as_file_or_dir(base)

    return None


def _resolve_as_file_or_dir(base: Path) -> Path | None:
    if base.suffix in _EXTS and base.exists() and base.is_file():
        return base

    for ext in _EXTS:
        p = Path(str(base) + ext)
        if p.exists() and p.is_file():
            return p

    if base.exists() and base.is_dir():
        for name in ("index", "main"):
            for ext in _EXTS:
                p = base / f"{name}{ext}"
                if p.exists() and p.is_file():
                    return p

    return None
