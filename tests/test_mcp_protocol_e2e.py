"""Validação opcional do servidor usando uma sessão MCP stdio real."""
from __future__ import annotations

import asyncio
import os
import sys
import unittest
from pathlib import Path


@unittest.skipUnless(os.getenv("BYTEBANK_RUN_PROTOCOL_E2E") == "1", "E2E MCP não habilitado")
class McpProtocolE2ETests(unittest.TestCase):
    def test_lists_tools_and_blocks_mutation_without_approval(self):
        async def exercise():
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            root = Path(__file__).resolve().parents[1]
            parameters = StdioServerParameters(
                command=sys.executable,
                args=["-m", "scripts.bytebank_mcp_server"],
                cwd=str(root),
                env={**os.environ, "PYTHONPATH": str(root)},
            )
            async with stdio_client(parameters) as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    names = {tool.name for tool in tools.tools}
                    result = await session.call_tool(
                        "criar_conta", {"cliente_referencia": "cliente-ficticio"}
                    )
                    return names, result

        names, result = asyncio.run(exercise())
        self.assertIn("consultar_politicas", names)
        self.assertIn("criar_conta", names)
        self.assertIn("approval_identity_required", str(result.content))