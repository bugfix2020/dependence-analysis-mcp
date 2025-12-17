from __future__ import annotations

import argparse
import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

from .models import AnalysisResult
from .scanner import scan_directory


_mcp = FastMCP(
    "dependence-analysis-mcp",
    instructions="扫描前端/Node 项目的 ESModule 依赖关系，找出未引用文件和未使用导入。",
)


@_mcp.tool()
async def run_dependence_analysis(
    directory: str,
    roots: list[str] | None = None,
    includeExtensions: list[str] | None = None,
) -> AnalysisResult:
    """Scan a directory and return referenced/unreferenced files and unused imports."""

    return await asyncio.to_thread(
        scan_directory,
        directory,
        roots=roots,
        include_extensions=includeExtensions,
    )


def create_app() -> Starlette:
    @asynccontextmanager
    async def lifespan(_app: Starlette):
        async with _mcp.session_manager.run():
            yield

    return Starlette(
        routes=[
            # FastMCP Streamable HTTP endpoint is /mcp
            Mount("/", app=_mcp.streamable_http_app()),
        ],
        lifespan=lifespan,
    )


# ASGI app for `uvicorn dependence_analysis_mcp.server:app`
app = create_app()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dependence-analysis-mcp",
        description="Run dependence-analysis-mcp as an MCP server.",
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default=os.environ.get("MCP_MODE", "stdio"),
        help="Server mode: stdio (default, for MCP clients) or http (for web deployment).",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Bind host for HTTP mode (default: 0.0.0.0 or $HOST).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="Bind port for HTTP mode (default: 8000 or $PORT).",
    )
    parser.add_argument(
        "--log-level",
        default=os.environ.get("LOG_LEVEL", "info"),
        help="Log level (default: info or $LOG_LEVEL).",
    )
    args = parser.parse_args()

    if args.mode == "stdio":
        # Stdio 模式：用于 MCP 客户端（如魔搭托管、Claude Desktop）
        _mcp.run(transport="stdio")
    else:
        # HTTP 模式：用于 Web 部署
        uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)
