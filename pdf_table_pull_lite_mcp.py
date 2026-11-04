"""Free MCP server for pdf-table-pull-lite (stdio).

Run:  uvx --from git+https://github.com/tidybytetools/pdf-table-pull-lite pdf-table-pull-lite-mcp
"""
import csv, io, os
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
import pdf_table_pull_lite as lite

mcp = FastMCP("pdf-table-pull-lite")


@mcp.tool(
    title="Extract PDF tables to CSV",
    annotations=ToolAnnotations(
        title="Extract PDF tables to CSV",
        readOnlyHint=False,      # writes CSV files when output_dir is set
        destructiveHint=True,    # may replace CSV files with the same names in output_dir
        idempotentHint=True,     # same input gives the same output
        openWorldHint=False,     # local files only, no network
    ),
)
def extract_pdf_tables(path: str, pages: str = "", strategy: str = "auto", output_dir: str = "") -> list[str]:
    """Pull the tables out of a local text PDF.

    Use this when you need the rows and columns of a table from a PDF on this
    computer, for example to load them into a spreadsheet, pandas or a database.
    Do not use it for scanned PDFs or photos (there is no OCR), for PDFs on the web
    (download the file first), or when you want the whole document as text
    (use a PDF-to-Markdown or text tool instead).

    path: full path to a PDF on this computer.
    pages: optional, like "1,3-5". Empty means all pages.
    strategy: "auto" (default, tries borders first, then spacing), "lines" (tables with
    ruled borders) or "text" (tables lined up by spacing). Try "text" if "auto" misses
    a table that has no border lines.
    output_dir: optional. If set, each table is saved there as a CSV and the file paths
    are returned. Files named pageN_tableM.csv that already exist there are replaced.
    If empty, nothing is written and the CSV text of each table is returned.

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
