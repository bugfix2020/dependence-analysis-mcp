"""
路径搜索验证模块

使用文本搜索来验证文件是否被引用，作为 AST 分析的补充验证。
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from functools import lru_cache


def generate_import_patterns(file_path: Path, project_root: Path, alias_map: dict[str, str]) -> list[str]:
    """
    为一个文件生成所有可能的导入路径模式。
    
    Args:
        file_path: 目标文件的绝对路径
        project_root: 项目根目录
        alias_map: 别名映射，如 {"@": "/path/to/src"}
    
    Returns:
        可能的导入路径模式列表
    """
    patterns: list[str] = []
    
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        return patterns
    
    # 移除扩展名
    rel_str = str(rel_path)
    for ext in [".tsx", ".ts", ".jsx", ".js", ".vue"]:
        if rel_str.endswith(ext):
            rel_str = rel_str[:-len(ext)]
            break
    
    # 移除 /index 后缀（因为 import './Button' 可以指 './Button/index.tsx'）
    base_path = rel_str
    if base_path.endswith("/index"):
        base_path = base_path[:-6]
    
    # 1. 基于别名的路径
    for alias, alias_path in alias_map.items():
        try:
            alias_path_obj = Path(alias_path)
            if file_path.is_relative_to(alias_path_obj):
                rel_to_alias = file_path.relative_to(alias_path_obj)
                rel_to_alias_str = str(rel_to_alias)
                for ext in [".tsx", ".ts", ".jsx", ".js", ".vue"]:
                    if rel_to_alias_str.endswith(ext):
                        rel_to_alias_str = rel_to_alias_str[:-len(ext)]
                        break
                
                # @/components/Button
                patterns.append(f"{alias}/{rel_to_alias_str}")
                
                # 如果是 index 文件，也添加不带 /index 的版本
                if rel_to_alias_str.endswith("/index"):
                    patterns.append(f"{alias}/{rel_to_alias_str[:-6]}")
        except (ValueError, TypeError):
            continue
    
    # 2. 相对路径模式（文件名部分）
    # 用于匹配 from './Button' 或 from '../components/Button'
    file_name = file_path.stem
    if file_name != "index":
        patterns.append(f"/{file_name}'")
        patterns.append(f'/{file_name}"')
    
    # 添加目录名（用于 index.tsx 文件）
    parent_name = file_path.parent.name
    if file_path.stem == "index" and parent_name:
        patterns.append(f"/{parent_name}'")
        patterns.append(f'/{parent_name}"')
    
    # 3. 相对路径的更完整形式
    # components/Button 或 components/Button/index
    patterns.append(f"/{base_path}'")
    patterns.append(f'/{base_path}"')
    if base_path != rel_str:
        patterns.append(f"/{rel_str}'")
        patterns.append(f'/{rel_str}"')
    
    return list(set(patterns))


def search_pattern_in_files(
    pattern: str,
    search_dir: Path,
    exclude_file: Path | None = None,
) -> bool:
    """
    使用 grep 在目录中搜索模式。
    
    Args:
        pattern: 搜索模式
        search_dir: 搜索目录
        exclude_file: 排除的文件（通常是被检测的文件本身）
    
    Returns:
        是否找到匹配
    """
    try:
        cmd = [
            "grep",
            "-r",
            "-l",  # 只输出文件名
            "--include=*.ts",
            "--include=*.tsx",
            "--include=*.js",
            "--include=*.jsx",
            "--include=*.vue",
            "-F",  # 固定字符串匹配（非正则）
            pattern,
            str(search_dir),
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # 检查是否只有被排除的文件
            matched_files = result.stdout.strip().split("\n")
            if exclude_file:
                exclude_str = str(exclude_file)
                matched_files = [f for f in matched_files if f != exclude_str]
            return len(matched_files) > 0
        
        return False
    except (subprocess.TimeoutExpired, Exception):
        return False


def verify_file_is_referenced(
    file_path: Path,
    project_root: Path,
    search_dir: Path,
    alias_map: dict[str, str],
) -> tuple[bool, list[str]]:
    """
    验证文件是否被其他文件引用。
    
    Args:
        file_path: 要验证的文件路径
        project_root: 项目根目录（用于计算相对路径）
        search_dir: 搜索范围目录
        alias_map: 别名映射
    
    Returns:
        (是否被引用, 匹配到的模式列表)
    """
    patterns = generate_import_patterns(file_path, project_root, alias_map)
    matched_patterns: list[str] = []
    
    for pattern in patterns:
        if search_pattern_in_files(pattern, search_dir, exclude_file=file_path):
            matched_patterns.append(pattern)
            # 找到一个匹配就足够了
            return (True, matched_patterns)
    
    return (False, matched_patterns)


def batch_verify_files(
    files: list[Path],
    project_root: Path,
    search_dir: Path,
    alias_map: dict[str, str],
) -> dict[str, bool]:
    """
    批量验证多个文件是否被引用。
    
    Args:
        files: 要验证的文件列表
        project_root: 项目根目录
        search_dir: 搜索范围目录
        alias_map: 别名映射
    
    Returns:
        文件路径 -> 是否被引用 的映射
    """
    results: dict[str, bool] = {}
    
    for file_path in files:
        is_referenced, _ = verify_file_is_referenced(
            file_path, project_root, search_dir, alias_map
        )
        results[str(file_path)] = is_referenced
    
    return results

