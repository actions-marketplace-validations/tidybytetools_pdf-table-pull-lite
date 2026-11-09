# Changelog

What changed in pdf-table-pull-lite, newest first.

## 1.3.1 - 2026-11-09

- Point Homepage, Documentation, and the MCP Registry websiteUrl at the official product page on [tidybytetools.github.io](https://tidybytetools.github.io/tools/pdf-table-pull/).
- README: add a clear Links section (Website, Apify cloud version where it exists, Pro on Gumroad) and a short FAQ.

## 1.3.0 - 2026-11-09

- Fix: if the CSV files were saved under a hidden folder like `.github/`, the artifact upload said no files were found. The upload now includes those folders.
- New: a GitHub Action (`action.yml`). Add `uses: tidybytetools/pdf-table-pull-lite@v1` to a workflow to pull the tables out of PDFs into CSV files.
- The action can read many PDFs at once, upload the CSVs as an artifact, and show a preview of the first tables on the run page.
- It warns about scanned pages. Set `fail-on-scanned` or `fail-if-no-tables` to `"true"` to fail the step instead.
- The command-line tool and MCP server did not change.

## 1.2.1 - 2026-11-04

- Fix: installing from the MCP Registry now starts the MCP server. Before, it started the plain command-line tool by mistake.
- New: `pdf-table-pull-lite mcp` starts the MCP server. `uvx pdf-table-pull-lite mcp` works too. The old `pdf-table-pull-lite-mcp` command still works.
- To read a file that is named `mcp`, use `./mcp`.

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
