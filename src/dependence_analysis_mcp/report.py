"""报告生成模块"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import AnalysisResult


def generate_markdown_report(
    result: AnalysisResult,
    *,
    scan_directory: str,
    output_dir: Path,
    report_name: str | None = None,
) -> Path:
    """
    生成 Markdown 格式的分析报告
    
    Args:
        result: 分析结果
        scan_directory: 扫描的目录
        output_dir: 输出目录
        report_name: 报告文件名（不含扩展名），默认使用时间戳
    
    Returns:
        生成的报告文件路径
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if report_name is None:
        report_name = f"unused_files_{timestamp}"
    
    report_path = output_dir / f"{report_name}.md"
    
    # 生成报告内容
    lines: list[str] = []
    
    lines.append(f"# 依赖分析报告")
    lines.append("")
    lines.append(f"**扫描目录**: `{scan_directory}`")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # 统计摘要
    lines.append("## 📊 统计摘要")
    lines.append("")
    total_files = len(result.referencedFiles) + len(result.unreferencedFiles)
    lines.append(f"- **总文件数**: {total_files}")
    lines.append(f"- **被引用文件数**: {len(result.referencedFiles)}")
    lines.append(f"- **未被引用文件数**: {len(result.unreferencedFiles)}")
    lines.append(f"- **未使用的导入数**: {len(result.unusedImports)}")
    lines.append("")
    
    # 未被引用的文件（主要关注）
    lines.append("## 🔴 未被引用的文件")
    lines.append("")
    lines.append("> ⚠️ 以下文件在项目中没有被其他文件直接或间接引用，请手动确认是否需要保留。")
    lines.append("> 入口文件（如 main.tsx, App.tsx）通常不会被其他文件引用，这是正常的。")
    lines.append("")
    
    if result.unreferencedFiles:
        # 按目录分组
        by_dir: dict[str, list[str]] = {}
        scan_path = Path(scan_directory).resolve()
        
        for file_path in result.unreferencedFiles:
            try:
                rel_path = Path(file_path).relative_to(scan_path)
                dir_parts = rel_path.parent.parts
                if dir_parts:
                    dir_key = str(Path(*dir_parts[:2])) if len(dir_parts) > 1 else str(dir_parts[0])
                else:
                    dir_key = "根目录"
            except ValueError:
                dir_key = "其他"
            
            if dir_key not in by_dir:
                by_dir[dir_key] = []
            by_dir[dir_key].append(file_path)
        
        for dir_name, files in sorted(by_dir.items()):
            lines.append(f"### 📁 {dir_name} ({len(files)} 个文件)")
            lines.append("")
            for file_path in sorted(files):
                try:
                    rel_path = Path(file_path).relative_to(scan_path)
                    lines.append(f"- [ ] `{rel_path}`")
                except ValueError:
                    lines.append(f"- [ ] `{file_path}`")
            lines.append("")
    else:
        lines.append("✅ 没有发现未被引用的文件！")
        lines.append("")
    
    # 未使用的导入
    lines.append("## 🟡 未使用的导入")
    lines.append("")
    lines.append("> 以下导入语句在文件中没有被使用。")
    lines.append("")
    
    if result.unusedImports:
        # 按文件分组
        by_file: dict[str, list[tuple[str, list[str]]]] = {}
        for item in result.unusedImports:
            if item.file not in by_file:
                by_file[item.file] = []
            by_file[item.file].append((item.importSource, item.importedNames))
        
        for file_path, imports in sorted(by_file.items()):
            try:
                rel_path = Path(file_path).relative_to(scan_path)
                lines.append(f"#### `{rel_path}`")
            except ValueError:
                lines.append(f"#### `{file_path}`")
            lines.append("")
            for src, names in imports:
                names_str = ", ".join(names) if names else "*"
                lines.append(f"- `{names_str}` from `{src}`")
            lines.append("")
    else:
        lines.append("✅ 没有发现未使用的导入！")
        lines.append("")
    
    # 警告信息
    if result.warnings:
        lines.append("## ⚠️ 警告信息")
        lines.append("")
        for w in result.warnings:
            lines.append(f"- {w}")
        lines.append("")
    
    # 被引用最多的文件 (Top 20)
    lines.append("## 📈 被引用最多的文件 (Top 20)")
    lines.append("")
    lines.append("| 文件 | 引用次数 |")
    lines.append("|------|----------|")
    
    for ref in result.referencedFiles[:20]:
        try:
            rel_path = Path(ref.path).relative_to(scan_path)
            lines.append(f"| `{rel_path}` | {ref.importCount} |")
        except ValueError:
            lines.append(f"| `{ref.path}` | {ref.importCount} |")
    lines.append("")
    
    # 写入文件
    report_path.write_text("\n".join(lines), encoding="utf-8")
    
    return report_path


def print_summary(result: AnalysisResult, scan_directory: str) -> None:
    """打印分析结果摘要到控制台"""
    total_files = len(result.referencedFiles) + len(result.unreferencedFiles)
    
    print("\n" + "=" * 60)
    print("📊 依赖分析结果摘要")
    print("=" * 60)
    print(f"扫描目录: {scan_directory}")
    print(f"总文件数: {total_files}")
    print(f"被引用文件数: {len(result.referencedFiles)}")
    print(f"未被引用文件数: {len(result.unreferencedFiles)}")
    print(f"未使用的导入数: {len(result.unusedImports)}")
    print("=" * 60)
    
    if result.unreferencedFiles:
        print("\n🔴 未被引用的文件（前 10 个）:")
        scan_path = Path(scan_directory).resolve()
        for file_path in result.unreferencedFiles[:10]:
            try:
                rel_path = Path(file_path).relative_to(scan_path)
                print(f"  - {rel_path}")
            except ValueError:
                print(f"  - {file_path}")
        if len(result.unreferencedFiles) > 10:
            print(f"  ... 还有 {len(result.unreferencedFiles) - 10} 个文件")
    
    if result.warnings:
        print(f"\n⚠️ 有 {len(result.warnings)} 条警告信息")

