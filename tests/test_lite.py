import csv, io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
import pdf_table_pull_lite as lite
F = lambda n: os.path.join(HERE, "fixtures", n)

class Lite(unittest.TestCase):
    def test_pages(self):
        self.assertEqual(lite.parse_pages("1,3-4", 5), [1, 3, 4])
        self.assertEqual(lite.parse_pages(None, 2), [1, 2])
        with self.assertRaises(ValueError): lite.parse_pages("9", 3)
    def test_ruled_tables(self):
        tables, scanned = lite.extract(F("ruled.pdf"))
        self.assertEqual(scanned, [])
        self.assertEqual(tables[0]["rows"], [["Region", "Q1", "Q2"], ["North", "1,200", "1,350"], ["South", "980", "(40)"]])
        self.assertEqual(tables[1]["rows"][0], ["Item", "Qty"])
    def test_no_joining_across_pages(self):
        tables, _ = lite.extract(F("ruled.pdf"))
        self.assertEqual(sorted({t["page"] for t in tables}), [1, 2, 3])
    def test_text_table(self):
        tables, _ = lite.extract(F("plain.pdf"))
        self.assertEqual(tables[0]["rows"][0], ["Date", "Store", "Total"])
        self.assertEqual(len(tables[0]["rows"]), 4)
    def test_scanned_skipped(self):
        tables, scanned = lite.extract(F("scanned.pdf"))
        self.assertEqual((tables, scanned), ([], [1]))
    def test_empty(self):
        self.assertEqual(lite.extract(F("empty.pdf"), strategy="text")[0], [])
    def test_cli_writes_csv(self):
        with tempfile.TemporaryDirectory() as d:
            out = io.StringIO()
            with redirect_stdout(out): code = lite.main([F("ruled.pdf"), "-o", d, "-p", "1"])
            self.assertEqual(code, 0)
            self.assertEqual(sorted(os.listdir(d)), ["page1_table1.csv", "page1_table2.csv"])
            with open(os.path.join(d, "page1_table1.csv"), encoding="utf-8-sig") as f:
                self.assertEqual(list(csv.reader(f))[2], ["South", "980", "(40)"])
            self.assertIn("Found 2 table(s)", out.getvalue())
    def test_cli_scanned_message(self):
        with tempfile.TemporaryDirectory() as d:
            out = io.StringIO()
            with redirect_stdout(out): lite.main([F("scanned.pdf"), "-o", d])
            self.assertIn("text PDFs only", out.getvalue())
    def test_help_has_paid_link(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit): lite.main(["--help"])
        self.assertIn("https://tidybyte.gumroad.com/l/hkxqxh", out.getvalue())
    def test_missing_file(self):
        self.assertEqual(lite.main(["/nope.pdf"]), 1)

if __name__ == "__main__": unittest.main()
