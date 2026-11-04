# pdf-table-pull-lite

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![MCP server](https://img.shields.io/badge/MCP-stdio-purple.svg)](#use-it-from-claude-desktop-or-cursor-mcp)

Free tool that pulls the tables out of a text PDF and saves each one as a CSV file.
Need Excel output, scanned PDFs or tables joined across pages? The paid version does that: **[pdf-table-pull on Gumroad](https://tidybyte.gumroad.com/l/hkxqxh)**

Runs on your own computer, so your PDFs are never uploaded anywhere. MIT license. Python 3.10 or newer, on Windows, Mac and Linux.

## Install

```
pip install git+https://github.com/tidybytetools/pdf-table-pull-lite
```

## Use it

```
pdf-table-pull-lite statement.pdf                 # CSVs go in statement_tables/
pdf-table-pull-lite statement.pdf -o out/ -p 2-5  # only pages 2 to 5
pdf-table-pull-lite statement.pdf -s text         # tables with no border lines
```

Example run:

```
Found 2 table(s).
  page1_table1: 2 rows x 3 columns
  page1_table2: 2 rows x 2 columns
Saved: statement_tables/page1_table1.csv
Saved: statement_tables/page1_table2.csv
```

You get one CSV per table, named after its page. The CSVs open straight in Excel (they're saved as UTF-8 with a BOM so accents show correctly).

`--strategy` (`-s`): `lines` is for tables with ruled borders, `text` is for tables lined up by spacing, and `auto` (the default) tries lines first, then text.

When you run it in a terminal it ends with one short line about the paid version. `--quiet` turns it off, and it never shows when output is piped or redirected.

## Known limits

- **Scanned PDFs.** Pages that are just an image (no text layer) are skipped, and the tool tells you which ones.
- **Tables that continue onto the next page** come out as separate CSVs, one per page.
- **Odd layouts.** Tables with merged cells or no clear columns can come out with cells in the wrong spot. Check the CSV.
- **CSV only.** No Excel or JSON output, no number cleanup (so `(40)` stays as text), and no password-protected PDFs.

## Lite vs paid

| | lite (free) | [pdf-table-pull](https://tidybyte.gumroad.com/l/hkxqxh) |
|---|---|---|
| Text PDFs, ruled or spaced tables | yes | yes |
| CSV output | yes | yes |
| Excel (one sheet per table) and JSON output | no | yes |
| Scanned PDFs (OCR) | no | yes |
| Join tables across pages | no | yes |
| Numbers cleaned (`1,200` → 1200, `(40)` → -40) | no | yes |
| Password-protected PDFs | no | yes |

## How it compares to other free tools

All of these are free and open source. Pick what fits you.

| | pdf-table-pull-lite | [pdfplumber](https://github.com/jsvine/pdfplumber) | [Camelot](https://github.com/camelot-dev/camelot) | [tabula-py](https://github.com/chezou/tabula-py) |
|---|---|---|---|---|
| What it is | Command line tool | Python library | Python library + CLI | Python wrapper for Tabula |
| Needs Java | no | no | no | yes |
| One command to get CSVs | yes | no, you write code | yes | yes |
| Picks border or spacing mode for you | yes (`auto`) | no | no | yes (guess) |
| Tells you which pages are scans | yes | no | no | no |
| Built-in MCP server for AI apps | yes | no | no | no |
| Lots of tuning knobs | no | yes | yes | some |

This tool is built on pdfplumber. If you want full control in your own code, use pdfplumber or Camelot directly.

## Use it from Claude Desktop or Cursor (MCP)

There is a small free MCP server built in. It gives your AI app one tool, `extract_pdf_tables`. It needs [uv](https://docs.astral.sh/uv/).

Run it by hand to check it starts (it waits quietly for an app to talk to it):

```
uvx --from git+https://github.com/tidybytetools/pdf-table-pull-lite pdf-table-pull-lite-mcp
```

Claude Desktop (`claude_desktop_config.json`) or Cursor (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "pdf-table-pull-lite": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/tidybytetools/pdf-table-pull-lite", "pdf-table-pull-lite-mcp"]
    }
  }
}
```

Tool: `extract_pdf_tables(path, pages="", strategy="auto", output_dir="")`. It returns a list with the CSV text of each table. If you set `output_dir`, it saves the CSVs there and returns the file paths instead.

## For AI agents

- **Use when:** you have a local PDF with real text (you can select the words) and need its tables as rows.
- **Don't use when:** the PDF is a scan or photo, it has a password, or you need Excel. Those pages get skipped. Use the paid version for those.
- **Input:** a file path, plus optional `pages` like `1,3-5` and `strategy` (`auto`, `lines`, `text`).
- **Output:** a list of CSV strings, one per table, first row is the header. Empty list means no tables were found.
- CLI exit code is 0 on success and 1 on error (message on stderr). See also [`llms.txt`](llms.txt).

## Tests

```
pip install pdfplumber "mcp<2"
python3 -m unittest discover tests
```

## License

MIT. See `LICENSE`.
