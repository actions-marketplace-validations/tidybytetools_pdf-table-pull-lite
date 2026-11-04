# Changelog

What changed in pdf-table-pull-lite, newest first.

## 1.2.0 - 2026-11-04

- MCP tool now has safety labels (tool annotations) so AI apps know what it does:
  readOnlyHint false, destructiveHint true, idempotentHint true, openWorldHint false.
- The tool description now says when to use it and when not to.
- Needs mcp 1.10 or newer.

## 1.1.0 - 2026-11-04

- New: a free MCP server, `pdf-table-pull-lite-mcp`. It gives AI apps one tool, `extract_pdf_tables`.
- New: `llms.txt` with short notes for AI agents.
- You can install it from PyPI with `pip install pdf-table-pull-lite`.

## 1.0.0 - 2026-11-04

- First release.
- Pulls the tables out of a text PDF and saves each one as a CSV file.
- Picks border or spacing mode for you, and tells you which pages are scans.
