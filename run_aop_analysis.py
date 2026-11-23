"""
AOP 2027 data-analysis tool – command-line entry point.

Usage:
    python run_aop_analysis.py                      # uses the newest AOP*.xlsx in ./data
    python run_aop_analysis.py "data/AOP2027(V4).xlsx" --out output

Outputs (in ./output by default; the source workbook is opened read-only):
    AOP2027_dashboard.html            interactive dashboard (open in a browser)
    AOP2027_cleaned_dataset.xlsx      standardised budget lines + all parsed rows + mappings
    AOP2027_data_quality_report.xlsx  scorecard, issue log, reconciliations, version comparison
    AOP2027_analysis_results.xlsx     aggregates, Pareto, outliers, unit-cost benchmarks, profile
    csv/                              the same tables as UTF-8 CSV
"""
import argparse
import glob
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "aop_tool"))

from pipeline import Run  # noqa: E402
from report import write_all  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="AOP 2027 data-quality & analysis tool")
    ap.add_argument("workbook", nargs="?", help="path to the AOP Excel workbook")
    ap.add_argument("--out", default=os.path.join(HERE, "output"), help="output folder")
    a = ap.parse_args()
    path = a.workbook
    if not path:
        cands = sorted(glob.glob(os.path.join(HERE, "data", "AOP*.xlsx")), key=os.path.getmtime)
        if not cands:
            sys.exit("No AOP*.xlsx found in ./data – pass the workbook path.")
        path = cands[-1]
    src = os.path.abspath(path)
    if os.path.abspath(a.out) == os.path.dirname(src):
        sys.exit("Refusing to write outputs into the source data folder.")
    before = (os.path.getsize(src), os.path.getmtime(src))
    t0 = time.time()
    print(f"Reading {os.path.basename(src)} (read-only) …")
    run = Run(src).run()
    files, qs = write_all(run, a.out)
    after = (os.path.getsize(src), os.path.getmtime(src))
    assert before == after, "source workbook changed – this should never happen"
    port = [r for r in run.records if r["in_portfolio"]]
    print(f"  parsed rows          {len(run.records)}")
    print(f"  counted budget lines {len(port)}   total USD {sum(r['budget_total'] or 0 for r in port):,.2f}")
    print(f"  issues               {len(run.issues)}   quality score {qs['score']}/100")
    print(f"  outlier flags        {len(run.outlier_rows)}")
    for k, v in files.items():
        print(f"  -> {os.path.relpath(v, HERE)}")
    print(f"done in {time.time() - t0:.1f}s; source workbook unchanged.")


if __name__ == "__main__":
    main()
