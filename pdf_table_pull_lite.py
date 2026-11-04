#!/usr/bin/env python3
"""pdf-table-pull-lite: pull the tables out of a text PDF into CSV files.

Free, MIT-licensed lite edition. The paid version (pdf-table-pull) adds Excel and
JSON output, scanned-PDF OCR, joining tables across pages, and number cleanup:
https://tidybyte.gumroad.com/l/hkxqxh

Usage:
  pdf-table-pull-lite report.pdf
  pdf-table-pull-lite report.pdf -o out_dir/ --pages 2-5
"""
import argparse, csv, os, re, sys

__version__ = "1.2.1"
PRO_URL = "https://tidybyte.gumroad.com/l/hkxqxh"
PRO_LINE = f"Need Excel output, scanned PDFs or tables joined across pages? pdf-table-pull (paid): {PRO_URL}"


def parse_pages(spec, total):
    """'1,3-5' -> [1,3,4,5] (1-based). None means every page."""
    if not spec:
        return list(range(1, total + 1))
    pages = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a) if a else 1, (int(b) if b else total) + 1))
        else:
            pages.append(int(part))
    bad = [p for p in pages if p < 1 or p > total]
    if bad:
        raise ValueError(f"page {bad[0]} is out of range (PDF has {total} pages)")
    return sorted(set(pages))


def _clean_cell(c):
    return "" if c is None else re.sub(r"\s+", " ", str(c)).strip()


def _clean_table(rows):
    rows = [[_clean_cell(c) for c in r] for r in rows]
    rows = [r for r in rows if any(r)]
    if not rows:
        return []
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    keep = [i for i in range(width) if any(r[i] for r in rows)]
    return [[r[i] for i in keep] for r in rows]


def extract(pdf_path, pages=None, strategy="auto"):
    """Return (tables, scanned_pages). tables: list of {'page', 'index', 'rows'}.
    Pages with no text layer (scans) are skipped and listed in scanned_pages."""
    import pdfplumber
    if strategy not in ("auto", "lines", "text"):
        raise ValueError("strategy must be lines, text or auto")
    lines = {"vertical_strategy": "lines", "horizontal_strategy": "lines"}
    text = {"vertical_strategy": "text", "horizontal_strategy": "text"}
    out, scanned = [], []
    with pdfplumber.open(pdf_path) as pdf:
        for pno in parse_pages(pages, len(pdf.pages)):
            page = pdf.pages[pno - 1]
            if not page.chars:
                scanned.append(pno)
                continue
            if strategy == "auto":
                found = page.extract_tables(lines)
                if not any(_clean_table(t) for t in found):
                    found = page.extract_tables(text)
            else:
                found = page.extract_tables(lines if strategy == "lines" else text)
            k = 0
            for t in found:
                rows = _clean_table(t)
                if not rows or (len(rows) < 2 and strategy != "lines"):
                    continue
                k += 1
                out.append({"page": pno, "index": k, "rows": rows})
    return out, scanned


def write_csv(tables, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for t in tables:
        p = os.path.join(out_dir, f"page{t['page']}_table{t['index']}.csv")
        with open(p, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(t["rows"])
        paths.append(p)
    return paths


def run_mcp():
    """Start the stdio MCP server (needs the mcp package, which pip installs for you)."""
    try:
        import pdf_table_pull_lite_mcp
    except ImportError as e:
        print(f"error: the MCP server needs the mcp package ({e}). Run: pip install pdf-table-pull-lite", file=sys.stderr)
        return 1
    pdf_table_pull_lite_mcp.main()
    return 0

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["mcp"]:
        return run_mcp()
    ap = argparse.ArgumentParser(prog="pdf-table-pull-lite",
                                 description="Pull tables out of a text PDF into CSV files (one file per table).",
                                 epilog=PRO_LINE)
    ap.add_argument("pdf")
    ap.add_argument("-o", "--output", help="output folder (default: <pdf name>_tables next to the PDF)")
    ap.add_argument("-p", "--pages", help="pages to read, e.g. 1,3-5 (default: all)")
    ap.add_argument("-s", "--strategy", choices=["auto", "lines", "text"], default="auto",
                    help="lines = tables with ruled borders, text = tables lined up by spacing, auto = try lines then text")
    ap.add_argument("-q", "--quiet", action="store_true", help="don't print the one-line note about the paid version")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    try:
        if not os.path.isfile(a.pdf):
            raise FileNotFoundError(f"file not found: {a.pdf}")
        tables, scanned = extract(a.pdf, a.pages, a.strategy)
        files = write_csv(tables, a.output or os.path.splitext(a.pdf)[0] + "_tables")
        print(f"Found {len(tables)} table(s).")
        for t in tables:
            print(f"  page{t['page']}_table{t['index']}: {len(t['rows']) - 1} rows x {len(t['rows'][0])} columns")
        for p in files:
            print(f"Saved: {p}")
        if scanned:
            print(f"Skipped page(s) {', '.join(map(str, scanned))}: no text layer (scanned image). The lite version reads text PDFs only.")
        elif not tables:
            print("Tip: no tables found. Try --strategy text.")
        if not a.quiet and sys.stdout.isatty():
            print(PRO_LINE)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
