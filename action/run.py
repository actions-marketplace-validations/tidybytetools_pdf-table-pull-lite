#!/usr/bin/env python3
"""Runner for the PDF Table Pull Lite GitHub Action (Tidy Byte Tools, MIT).

Reads its settings from INPUT_* environment variables set by action.yml,
pulls the tables out of the matching PDFs with pdf_table_pull_lite.py from
this same tag, saves one CSV per table, and reports to the job summary.
"""
import glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import pdf_table_pull_lite as ptp  # noqa: E402

TITLE = "PDF Table Pull Lite"
PREVIEW_TABLES = 3
PREVIEW_ROWS = 5


def env(name, default=""):
    return os.environ.get("INPUT_" + name, default).strip()


def flag(name, default="false"):
    v = env(name, default).lower()
    if v not in ("true", "false"):
        raise ValueError(f"{name.lower().replace('_', '-')} must be true or false (got '{v}')")
    return v == "true"


def number(name, default, low):
    raw = env(name, str(default))
    try:
        n = int(raw)
    except ValueError:
        raise ValueError(f"{name.lower().replace('_', '-')} must be a whole number (got '{raw}')")
    if n < low:
        raise ValueError(f"{name.lower().replace('_', '-')} must be {low} or more (got {n})")
    return n


def patterns(raw):
    out = []
    for line in raw.replace(",", "\n").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def find_files(include, exclude):
    skip = set()
    for p in exclude:
        skip.update(os.path.normpath(x) for x in glob.glob(p, recursive=True))
    found = []
    for p in include:
        for x in sorted(glob.glob(p, recursive=True)):
            n = os.path.normpath(x)
            if os.path.isfile(n) and n not in skip and not any(n.startswith(s + os.sep) for s in skip) and n not in found:
                found.append(n)
    return found


def esc_prop(s):
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(":", "%3A").replace(",", "%2C")


def esc_msg(s):
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def annotate(kind, msg, file=None, line=None, title=None):
    props = []
    if file:
        props.append(f"file={esc_prop(file.replace(os.sep, '/'))}")
    if line:
        props.append(f"line={line}")
    if title:
        props.append(f"title={esc_prop(title)}")
    print(f"::{kind} {','.join(props)}::{esc_msg(msg)}" if props else f"::{kind}::{esc_msg(msg)}")


def write_outputs(values):
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        for k, v in values.items():
            fh.write(f"{k}={v}\n")


def write_summary(text):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(text)


def cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def preview(rows):
    head = rows[0]
    width = len(head)
    out = ["| " + " | ".join(cell(c) or " " for c in head) + " |", "|" + "---|" * width]
    for r in rows[1:PREVIEW_ROWS + 1]:
        out.append("| " + " | ".join(cell(c) or " " for c in r) + " |")
    if len(rows) > PREVIEW_ROWS + 1:
        out.append(f"\n...and {len(rows) - PREVIEW_ROWS - 1} more row(s).")
    return out


def main():
    try:
        include = patterns(env("FILES", "**/*.pdf"))
        exclude = patterns(env("EXCLUDE", ""))
        out_dir = env("OUTPUT_DIR", "pdf-tables")
        pages = env("PAGES", "") or None
        strategy = env("STRATEGY", "auto")
        if strategy not in ("auto", "lines", "text"):
            raise ValueError(f"strategy must be auto, lines or text (got '{strategy}')")
        fail_no_tables = flag("FAIL_IF_NO_TABLES")
        fail_on_scanned = flag("FAIL_ON_SCANNED")
        fail_if_none = flag("FAIL_IF_NO_FILES", "true")
        if not include:
            raise ValueError("files is empty. Give at least one pattern, like reports/**/*.pdf")
        if not out_dir:
            raise ValueError("output-dir is empty. Give a folder name, like pdf-tables")
        if os.path.isabs(out_dir):
            raise ValueError("output-dir must be a folder inside the repo, not a full path")
    except ValueError as e:
        annotate("error", str(e), title=TITLE)
        return 1

    files = [f for f in find_files(include, exclude) if f.lower().endswith(".pdf")]
    if not files:
        msg = f"No PDF files matched: {', '.join(include)}"
        write_outputs({"files": 0, "tables": 0, "scanned-files": 0, "output-dir": out_dir})
        write_summary(f"### {TITLE}\n\n{msg}\n")
        if fail_if_none:
            annotate("error", msg + ". Check the files input, or set fail-if-no-files to false.", title=TITLE)
            return 1
        annotate("warning", msg, title=TITLE)
        return 0

    rows, previews, errors, scanned_files, total = [], [], 0, [], 0
    for f in files:
        dest = os.path.normpath(os.path.join(out_dir, os.path.splitext(f)[0]))
        try:
            tables, scanned = ptp.extract(f, pages, strategy)
            paths = ptp.write_csv(tables, dest) if tables else []
        except Exception as e:  # one bad PDF should not stop the others
            errors += 1
            annotate("error", f"Could not read this PDF: {e}", file=f, title=TITLE)
            rows.append((f, dest, "error", "-"))
            continue
        total += len(tables)
        if scanned:
            scanned_files.append(f)
            annotate("error" if fail_on_scanned else "warning",
                     f"Page(s) {', '.join(map(str, scanned))} have no text layer (scanned image) and were skipped.",
                     file=f, title="Scanned pages")
        if not tables:
            annotate("error" if fail_no_tables else "notice",
                     "No tables found in this PDF." + (" Try strategy: text." if strategy == "lines" else ""),
                     file=f, title="No tables")
        rows.append((f, dest, len(tables), ", ".join(map(str, scanned)) or "-"))
        for t, p in zip(tables, paths):
            print(f"Saved: {p}  ({len(t['rows']) - 1} rows x {len(t['rows'][0])} columns)")
            if len(previews) < PREVIEW_TABLES:
                previews.append((p, t["rows"]))

    write_outputs({"files": len(rows), "tables": total, "scanned-files": len(scanned_files),
                   "output-dir": out_dir.replace(os.sep, "/")})

    lines = [f"### {TITLE}", "",
             f"**{total}** table(s) from **{len(rows)}** PDF(s). CSV files are in `{out_dir}`.", "",
             "| PDF | CSV folder | Tables | Scanned pages |", "|---|---|---:|---|"]
    for f, dest, n, sp in rows[:200]:
        lines.append(f"| `{cell(f)}` | `{cell(dest)}` | {n} | {sp} |")
    if len(rows) > 200:
        lines.append(f"| ...and {len(rows) - 200} more | | | |")
    for p, trows in previews:
        lines += ["", f"**Preview of `{cell(p)}`**", ""] + preview(trows)
    write_summary("\n".join(lines) + "\n\n")

    if errors:
        return 1
    if fail_no_tables and any(r[2] == 0 for r in rows):
        annotate("error", "Some PDFs had no tables.", title=TITLE)
        return 1
    if fail_on_scanned and scanned_files:
        annotate("error", f"{len(scanned_files)} PDF(s) have scanned pages with no text.", title=TITLE)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
