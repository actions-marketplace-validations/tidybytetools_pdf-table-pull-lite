"""Starts the MCP server over stdio, lists tools, and calls extract_pdf_tables."""
import asyncio, os, sys, unittest
HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    ClientSession = None


async def _run():
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(ROOT, "pdf_table_pull_lite_mcp.py")], cwd=ROOT)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = [t.name for t in (await s.list_tools()).tools]
            res = await s.call_tool("extract_pdf_tables", {"path": os.path.abspath(os.path.join(HERE, "fixtures", "ruled.pdf")), "pages": "1"})
            return tools, res


@unittest.skipIf(ClientSession is None, "mcp not installed")
class MCP(unittest.TestCase):
    def test_lists_and_calls_tool(self):
        tools, res = asyncio.run(_run())
        self.assertEqual(tools, ["extract_pdf_tables"])
        self.assertFalse(res.isError)
        text = " ".join(c.text for c in res.content if getattr(c, "type", "") == "text")
        self.assertIn("Region,Q1,Q2", text)
        self.assertIn("South,980,(40)", text)


if __name__ == "__main__":
    unittest.main()
