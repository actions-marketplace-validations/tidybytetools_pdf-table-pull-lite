"""Free MCP server for pdf-table-pull-lite (stdio).

Run:  uvx --from git+https://github.com/tidybytetools/pdf-table-pull-lite pdf-table-pull-lite-mcp
"""
import csv, io, os
from mcp.server.fastmcp import FastMCP
import pdf_table_pull_lite as lite

mcp = FastMCP("pdf-table-pull-lite")


@mcp.tool()
def extract_pdf_tables(path: str, pages: str = "", strategy: str = "auto", output_dir: str = "") -> list[str]:
    """Pull the tables out of a local text PDF.

    path: full path to a PDF on this computer.
    pages: optional, like "1,3-5". Empty means all pages.
    strategy: "auto" (default), "lines" (ruled borders) or "text" (lined up by spacing).
    output_dir: optional. If set, each table is saved there as a CSV and the file paths
    are returned. If empty, the CSV text of each table is returned.

    Scanned (image-only) pages have no text and are skipped. Returns [] if no tables.
    """
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"file not found: {path}")
    tables, _scanned = lite.extract(path, pages or None, strategy)
    if output_dir:
        return lite.write_csv(tables, os.path.expanduser(output_dir))
    out = []
    for t in tables:
        buf = io.StringIO()
        csv.writer(buf).writerows(t["rows"])
        out.append(buf.getvalue())
    return out


def main():
    mcp.run()


if __name__ == "__main__":
    main()
