# pdf-table-pull-lite

Free tool that pulls the tables out of a text PDF and saves each one as a CSV file.
Need Excel output, scanned PDFs or tables joined across pages? The paid version does that: **[pdf-table-pull on Gumroad](https://tidybyte.gumroad.com/l/hkxqxh)**

Runs on your own computer, so your PDFs are never uploaded anywhere. MIT license. Python 3.8 or newer, on Windows, Mac and Linux.

## Install

```
pip install pdf-table-pull-lite
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

## What the lite version does not do

- **Scanned PDFs.** Pages that are just an image (no text layer) are skipped, and the tool tells you which ones.
- **Tables that continue onto the next page** come out as separate CSVs, one per page.
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

## Tests

```
pip install pdfplumber
python3 -m unittest discover tests
```

## License

MIT. See `LICENSE`.
