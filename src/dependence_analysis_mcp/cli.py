"""CLI 命令行工具"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .scanner import scan_directory
from .report import generate_markdown_report, print_summary


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dependence-analysis",
        description="扫描前端项目并分析文件依赖关系，找出未被引用的文件。",
    )
    parser.add_argument(
        "directory",
        help="要扫描的目录路径",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        default=".hc/reports",
        help="报告输出目录（默认: .hc/reports）",
    )
    parser.add_argument(
        "-n", "--name",
        dest="report_name",
        help="报告文件名（不含扩展名，默认使用时间戳）",
    )
    parser.add_argument(
        "-e", "--extensions",
        dest="extensions",
        nargs="+",
        help="要扫描的文件扩展名（默认: .ts .tsx .js .jsx .vue）",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="不生成报告文件，只输出摘要到控制台",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式结果",
    )
    
    args = parser.parse_args()
    
    scan_path = Path(args.directory).resolve()
    if not scan_path.exists():
        print(f"❌ 目录不存在: {scan_path}", file=sys.stderr)
        sys.exit(1)
    
    if not scan_path.is_dir():
        print(f"❌ 路径不是目录: {scan_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"🔍 正在扫描目录: {scan_path}")
    print("   这可能需要一些时间...")
    
    # 执行扫描
    result = scan_directory(
        str(scan_path),
        roots=None,
        include_extensions=args.extensions,
    )
    
    # JSON 输出
    if args.json:
        import json
        print(result.model_dump_json(indent=2, by_alias=True))
        return
    
    # 打印摘要
    print_summary(result, str(scan_path))
    
    # 生成报告
    if not args.no_report:
        # 确定输出目录：如果是相对路径，则相对于当前工作目录
        output_dir = Path(args.output_dir)
        if not output_dir.is_absolute():
            output_dir = Path.cwd() / output_dir
        
        report_path = generate_markdown_report(
            result,
            scan_directory=str(scan_path),
            output_dir=output_dir,
            report_name=args.report_name,
        )
        print(f"\n📄 报告已生成: {report_path}")


if __name__ == "__main__":
    main()

