from __future__ import annotations

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server

from .models import AnalysisRequest
from .scanner import scan_directory


def build_server() -> Server:
    server = Server("dependence-analysis-mcp")

    async def run_dependence_analysis(request: AnalysisRequest) -> dict:
        result = await asyncio.to_thread(
            scan_directory,
            request.directory,
            roots=request.roots,
            include_extensions=request.includeExtensions,
        )
        return result.model_dump(by_alias=True)

    # MCP Python SDK compatibility:
    # We support multiple server APIs across mcp versions.
    tool_attr = getattr(server, "tool", None)
    if callable(tool_attr):
        tool_attr()(run_dependence_analysis)
        return server

    add_tool = getattr(server, "add_tool", None)
    if callable(add_tool):
        add_tool(
            name="run_dependence_analysis",
            description="Scan a directory and return referenced/unreferenced files and unused imports.",
            input_schema=AnalysisRequest,
            handler=run_dependence_analysis,
        )
        return server

    # Older API: implement list_tools + call_tool request handlers.
    # The SDK exposes request_handlers mapping internally.
    request_handlers = getattr(server, "request_handlers", None)
    if request_handlers is None:
        raise RuntimeError("Unsupported mcp Server API: no tool registration or request_handlers")

    async def _list_tools(_params: object | None = None) -> dict:
        return {
            "tools": [
                {
                    "name": "run_dependence_analysis",
                    "description": "Scan a directory and return referenced/unreferenced files and unused imports.",
                    "inputSchema": AnalysisRequest.model_json_schema(),
                }
            ]
        }

    async def _call_tool(params: dict) -> dict:
        name = params.get("name")
        arguments = params.get("arguments")
        if name != "run_dependence_analysis":
            raise ValueError(f"Unknown tool: {name}")
        req = AnalysisRequest.model_validate(arguments or {})
        result = await run_dependence_analysis(req)
        # Return a JSON payload as MCP tool content.
        return {
            "content": [
                {
                    "type": "text",
                    "text": __import__("json").dumps(result, ensure_ascii=False),
                }
            ]
        }

    # Register handlers; method names follow MCP JSON-RPC.
    request_handlers["tools/list"] = _list_tools
    request_handlers["tools/call"] = _call_tool

    return server


async def _amain() -> None:
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        try:
            await server.run(read_stream, write_stream)
        except TypeError as e:
            # Some mcp versions require an explicit `initialization_options` argument.
            # Provide a conservative default.
            if "initialization_options" not in str(e):
                raise
            await server.run(
                read_stream,
                write_stream,
                {
                    "capabilities": {},
                },
            )


def main() -> None:
    asyncio.run(_amain())
