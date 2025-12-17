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
    # 生产部署更推荐无状态 + JSON 响应（更易扩展、更省资源）。
    stateless_http=True,
    json_response=True,
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
        description="Run dependence-analysis-mcp as an MCP Streamable HTTP server (endpoint: /mcp).",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Bind host (default: 0.0.0.0 or $HOST).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="Bind port (default: 8000 or $PORT).",
    )
    parser.add_argument(
        "--log-level",
        default=os.environ.get("LOG_LEVEL", "info"),
        help="Uvicorn log level (default: info or $LOG_LEVEL).",
    )
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)
