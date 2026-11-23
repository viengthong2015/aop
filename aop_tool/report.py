"""
Writes the analysis outputs: Excel workbooks, CSV files and the HTML dashboard.
Nothing is ever written next to (or into) the source workbook.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from pipeline import CHECKS, SEVERITY_ORDER, SEVERITY_WEIGHT
import normalize as nz

HERE = os.path.dirname(os.path.abspath(__file__))

LINE_COLUMNS = [
    ("uid", "Line ID"), ("sheet", "Source sheet"), ("excel_row", "Excel row"), ("sheet_label", "Plan / department"),
    ("component", "Component"), ("modality", "Financing modality (sheet)"), ("section", "Section"),
    ("code", "Activity code"), ("level", "Code level"), ("name", "Activity name"), ("name_alt", "Activity name (2nd language)"),
    ("activity_type_raw", "Activity type (as typed)"), ("activity_category", "Activity category (standardised)"),
    ("activity_category_source", "Category source"), ("unit_raw", "Unit (as typed)"), ("unit", "Unit (standardised)"),
    ("unit_cost_usd", "Unit cost USD"), ("unit_cost_lak", "Unit cost LAK"), ("quantity", "Quantity"),
    ("mov_q1", "Activities Q1"), ("mov_q2", "Activities Q2"), ("mov_q3", "Activities Q3"), ("mov_q4", "Activities Q4"),
    ("mov_total", "Activities total"),
    ("budget_q1", "Budget Q1 USD"), ("budget_q2", "Budget Q2 USD"), ("budget_q3", "Budget Q3 USD"),
    ("budget_q4", "Budget Q4 USD"), ("budget_total", "Budget total USD"), ("quarterly_sum", "Q1–Q4 sum USD"),
    ("quarter_split_derived", "Quarters derived from activity counts"), ("total_lak", "Total LAK"),
    ("ia_raw", "Implementing agency (as typed)"), ("implementing_agency", "Implementing agency (standardised)"),
    ("implementation_level", "Implementation level"), ("financing_modality", "Financing modality (line)"),
    ("remark", "Remark"), ("total_is_formula", "Total is a formula"), ("total_formula", "Total formula"),
    ("row_kind", "Row type"), ("role", "Sheet role"), ("in_portfolio", "Counted in portfolio"),
    ("exclusion_reason", "Exclusion reason"), ("issue_count", "Issues"), ("max_severity", "Worst issue severity"),
    ("issue_checks", "Issue check IDs"), ("outlier_flags", "Outlier flags"),
]

ISSUE_COLUMNS = [("issue_id", "Issue ID"), ("severity", "Severity"), ("dimension", "Dimension"),
                 ("check_id", "Check"), ("check", "Check description"), ("sheet", "Sheet"), ("row", "Excel row"),
                 ("cell", "Cell"), ("code", "Activity code"), ("name", "Activity name"), ("role", "Sheet role"),
                 ("in_portfolio", "Line counted in portfolio"), ("value", "Value found"),
                 ("expected", "Expected / compared"), ("difference", "Difference"), ("message", "Detail"),
                 ("uid", "Line ID")]

HEADER_FILL = PatternFill("solid", fgColor="1C5CAB")
HEADER_FONT = Font(bold=True, color="FFFFFF")
SEV_FILL = {"Critical": "F6D5D5", "High": "FBE3D9", "Medium": "FEF0CF", "Low": "EFEFEC", "Info": "E4EEFB"}


def _write_table(wb, title, rows, columns, widths=None, sev_col=None, note=None):
    ws = wb.create_sheet(title[:31])
    start = 1
    if note:
        ws.cell(row=1, column=1, value=note).font = Font(italic=True, color="52514E")
        start = 3
    for j, (_, label) in enumerate(columns, 1):
        c = ws.cell(row=start, column=j, value=label)
        c.fill, c.font = HEADER_FILL, HEADER_FONT
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, r in enumerate(rows, start + 1):
        for j, (key, _) in enumerate(columns, 1):
            v = r.get(key)
            if isinstance(v, (list, dict)):
                v = json.dumps(v, ensure_ascii=False)
            c = ws.cell(row=i, column=j, value=v)
            if isinstance(v, float):
                c.number_format = "#,##0.00"
            elif isinstance(v, int) and not isinstance(v, bool):
                c.number_format = "#,##0"
        if sev_col and r.get(sev_col) in SEV_FILL:
            ws.cell(row=i, column=[k for k, _ in columns].index(sev_col) + 1).fill = \
                PatternFill("solid", fgColor=SEV_FILL[r[sev_col]])
    for j, (key, label) in enumerate(columns, 1):
        w = (widths or {}).get(key)
        if not w:
            sample = [len(str(r.get(key) or "")) for r in rows[:200]] + [len(label)]
            w = min(60, max(9, int(sum(sample) / len(sample) * 1.1) + 2))
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(row=start + 1, column=1)
    if rows:
        ws.auto_filter.ref = f"A{start}:{get_column_letter(len(columns))}{start + len(rows)}"
    return ws


def _cols(rows, order=None):
    keys = order or (list(rows[0].keys()) if rows else [])
    return [(k, k.replace("_", " ").capitalize()) for k in keys]


def _write_csv(path, rows, columns):
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow([label for _, label in columns])
        for r in rows:
            w.writerow(["" if r.get(k) is None else r.get(k) for k, _ in columns])


def _readme(wb, run, kind):
    ws = wb.active
    ws.title = "README"
    src = os.path.basename(run.path)
    port = [r for r in run.records if r["in_portfolio"]]
    lines = [
        (f"AOP 2027 – {kind}", True),
        (f"Source workbook: {src} (read-only; never modified)", False),
        (f"Generated: {dt.datetime.now():%Y-%m-%d %H:%M}", False),
        ("", False),
        (f"Counted budget lines: {len(port)}   Counted total (USD): {sum(r['budget_total'] or 0 for r in port):,.2f}", False),
        (f"Data-quality issues: {len(run.issues)}", False),
        ("", False),
        ("What is 'counted'?", True),
        ("Only budget lines (not subtotals) from primary sheets. Excluded: the English copy of IBF1, hidden older "
         "versions (1_QPS_DHR, 3.6_GESI, 2.5_IBF3_DHIS2_L), and the NCLE / DCDC sections of B_DCDC _IBF_QPS, which "
         "repeat the stand-alone 2.3.2_NCLE and 2.3.1 DCDC sheets.", False),
        ("Budget lines vs subtotals were separated using each sheet's own formulas (formula reference graph), "
         "falling back to activity-code hierarchy where subtotals were typed in.", False),
        ("2.1_PBC_DPF is in LAK; USD uses the sheet's own rate (22,500). Its quarters are allocated from activity counts.", False),
        ("", False),
        ("Severity", True),
        ("Critical – changes a total or breaks a formula; High – amount is likely wrong; Medium – needs review; "
         "Low – formatting / labelling; Info – for awareness.", False),
    ]
    for i, (t, bold) in enumerate(lines, 1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = Font(bold=bold, size=13 if i == 1 else 11)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 120


def aggregates(run):
    port = [r for r in run.records if r["in_portfolio"]]
    total = sum(r["budget_total"] or 0 for r in port)

    def group(key):
        g = defaultdict(lambda: dict(lines=0, budget=0.0, q=[0.0] * 4, issues=0))
        for r in port:
            k = r.get(key) or "(blank)"
            g[k]["lines"] += 1
            g[k]["budget"] += r["budget_total"] or 0
            for i in range(4):
                g[k]["q"][i] += r[f"budget_q{i + 1}"] or 0
            g[k]["issues"] += r.get("issue_count") or 0
        out = []
        for k, v in sorted(g.items(), key=lambda kv: -kv[1]["budget"]):
            out.append({key: k, "budget_lines": v["lines"], "budget_usd": round(v["budget"], 2),
                        "share_pct": round(100 * v["budget"] / total, 2) if total else None,
                        "q1_usd": round(v["q"][0], 2), "q2_usd": round(v["q"][1], 2),
                        "q3_usd": round(v["q"][2], 2), "q4_usd": round(v["q"][3], 2),
                        "issues": v["issues"]})
        return out
    top = sorted(port, key=lambda r: -(r["budget_total"] or 0))
    cum, pareto = 0.0, []
    for i, r in enumerate(top, 1):
        cum += r["budget_total"] or 0
        pareto.append(dict(rank=i, uid=r["uid"], sheet=r["sheet"], code=r["code"], name=r["name"],
                           activity_category=r["activity_category"], budget_usd=r["budget_total"],
                           share_pct=round(100 * (r["budget_total"] or 0) / total, 3),
                           cumulative_pct=round(100 * cum / total, 2)))
    return dict(by_sheet=group("sheet_label"), by_component=group("component"),
                by_modality=group("modality"), by_category=group("activity_category"),
                by_agency=group("implementing_agency"), by_level=group("implementation_level"),
                pareto=pareto)


def quality_score(run):
    """0-100 score: 100 minus severity-weighted issues per counted line (capped)."""
    port = [r for r in run.records if r["in_portfolio"]]
    w = sum(SEVERITY_WEIGHT[i["severity"]] for i in run.issues
            if i["in_portfolio"] or i["uid"] is None and i["role"] in ("primary", None, "summary"))
    per_line = w / max(1, len(port))
    clean = sum(1 for r in port if r.get("max_severity") not in ("Critical", "High", "Medium"))
    return dict(score=round(max(0, 100 - 20 * per_line), 1), weighted_points=w,
                clean_lines=clean, clean_pct=round(100 * clean / max(1, len(port)), 1))


def write_all(run, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    csv_dir = os.path.join(out_dir, "csv")
    os.makedirs(csv_dir, exist_ok=True)
    port = [r for r in run.records if r["in_portfolio"]]
    agg = aggregates(run)
    qs = quality_score(run)
    files = {}

    # ---------- 1. cleaned dataset
    wb = Workbook()
    _readme(wb, run, "Cleaned & standardised budget lines")
    _write_table(wb, "Budget_lines", port, LINE_COLUMNS, widths={"name": 60, "name_alt": 45},
                 sev_col="max_severity",
                 note="Counted budget lines in one standard layout. Raw values are kept beside standardised ones.")
    _write_table(wb, "All_parsed_rows", run.records, LINE_COLUMNS, widths={"name": 60},
                 sev_col="max_severity",
                 note="Every parsed row from every budget sheet, incl. subtotals, headings, copies and older versions.")
    maps = ([dict(field="Activity category", standard=k, raw_value=v) for k, vs in nz.ACTIVITY_CATEGORY.items() for v in vs] +
            [dict(field="Implementing agency", standard=k, raw_value=a, level=lvl) for k, (lvl, al) in nz.AGENCIES.items() for a in al] +
            [dict(field="Province", standard=k, raw_value=a) for k, al in nz.PROVINCES.items() for a in al] +
            [dict(field="Unit", standard=k, raw_value=a) for k, al in nz.UNITS.items() for a in al])
    _write_table(wb, "Mappings", maps, _cols(maps, ["field", "standard", "raw_value", "level"]))
    p = os.path.join(out_dir, "AOP2027_cleaned_dataset.xlsx")
    wb.save(p)
    files["cleaned_xlsx"] = p

    # ---------- 2. data-quality report
    wb = Workbook()
    _readme(wb, run, "Data-quality report")
    issues = sorted(run.issues, key=lambda i: (SEVERITY_ORDER.index(i["severity"]), i["check_id"], i["sheet"] or "", i["row"] or 0))
    sev_counts = defaultdict(lambda: defaultdict(int))
    for i in run.issues:
        sev_counts[i["check_id"]][i["severity"]] += 1
    cat = [dict(check_id=k, dimension=d, check=t, default_severity=s, explanation=e,
                **{sv.lower(): sev_counts[k].get(sv, 0) for sv in SEVERITY_ORDER},
                total=sum(sev_counts[k].values())) for k, (d, t, s, e) in CHECKS.items()]
    _write_table(wb, "Sheet_scorecard", run.sheet_rows, _cols(run.sheet_rows),
                 note=f"Overall data-quality score {qs['score']} / 100 · {qs['clean_pct']}% of counted lines have no Critical/High/Medium issue.")
    _write_table(wb, "Issues", issues, ISSUE_COLUMNS, widths={"message": 90, "name": 45, "check": 40}, sev_col="severity")
    _write_table(wb, "Check_catalogue", cat, _cols(cat), widths={"explanation": 70, "check": 45})
    _write_table(wb, "Summary_sheet_recon", run.summary_recon, _cols(run.summary_recon))
    _write_table(wb, "Version_comparison", run.versions, _cols(run.versions), widths={"name": 55})
    _write_table(wb, "Exchange_rates", run.fx, _cols(run.fx))
    links = [dict(n=i + 1, target=t) for i, t in enumerate(run.external_links)]
    _write_table(wb, "External_links", links, _cols(links), widths={"target": 120})
    p = os.path.join(out_dir, "AOP2027_data_quality_report.xlsx")
    wb.save(p)
    files["quality_xlsx"] = p

    # ---------- 3. analysis results
    wb = Workbook()
    _readme(wb, run, "Analysis results")
    for key, title in [("by_sheet", "By_plan"), ("by_component", "By_component"), ("by_modality", "By_modality"),
                       ("by_category", "By_activity_category"), ("by_agency", "By_implementing_agency"),
                       ("by_level", "By_implementation_level")]:
        _write_table(wb, title, agg[key], _cols(agg[key]))
    _write_table(wb, "Top_lines_Pareto", agg["pareto"], _cols(agg["pareto"]), widths={"name": 60})
    _write_table(wb, "Outliers", run.outlier_rows, _cols(run.outlier_rows), widths={"name": 55})
    bench = [dict(activity_category=k, **{kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()})
             for k, v in sorted(run.uc_stats.items())]
    _write_table(wb, "Unit_cost_benchmarks", bench, _cols(bench),
                 note="Unit-cost distribution per activity category (USD; fences = Tukey 1.5×IQR on log10).")
    _write_table(wb, "Data_profile", run.profile_rows, _cols(run.profile_rows), widths={"description": 50, "top_values": 70})
    p = os.path.join(out_dir, "AOP2027_analysis_results.xlsx")
    wb.save(p)
    files["analysis_xlsx"] = p

    # ---------- CSVs
    _write_csv(os.path.join(csv_dir, "budget_lines_counted.csv"), port, LINE_COLUMNS)
    _write_csv(os.path.join(csv_dir, "all_parsed_rows.csv"), run.records, LINE_COLUMNS)
    _write_csv(os.path.join(csv_dir, "issues.csv"), issues, ISSUE_COLUMNS)
    _write_csv(os.path.join(csv_dir, "outliers.csv"), run.outlier_rows, _cols(run.outlier_rows))
    _write_csv(os.path.join(csv_dir, "sheet_scorecard.csv"), run.sheet_rows, _cols(run.sheet_rows))
    _write_csv(os.path.join(csv_dir, "version_comparison.csv"), run.versions, _cols(run.versions))

    # ---------- dashboard
    keep = [k for k, _ in LINE_COLUMNS if k not in ("total_formula",)] + ["depth"]
    data = dict(
        meta=dict(source=os.path.basename(run.path), generated=f"{dt.datetime.now():%Y-%m-%d %H:%M}",
                  counted_total=round(sum(r["budget_total"] or 0 for r in port), 2),
                  counted_lines=len(port), parsed_rows=len(run.records),
                  sheets_total=len(run.wb.wf.worksheets),
                  sheets_counted=len({r["sheet"] for r in port}), quality=qs,
                  hidden=[ws.title for ws in run.wb.wf.worksheets if ws.sheet_state != "visible"]),
        records=[{k: r.get(k) for k in keep} | {"total_formula": r.get("total_formula")} for r in run.records],
        issues=issues, checks={k: dict(dimension=d, title=t, severity=s, explanation=e) for k, (d, t, s, e) in CHECKS.items()},
        sheets=run.sheet_rows, versions=run.versions, summary_recon=run.summary_recon, fx=run.fx,
        external_links=run.external_links, outliers=run.outlier_rows,
        uc_stats=run.uc_stats, total_stats=getattr(run, "total_stats", None), profile=run.profile_rows,
        files={k: os.path.relpath(v, out_dir).replace("\\", "/") for k, v in files.items()},
        layouts=_layout_doc(),
    )
    tpl = open(os.path.join(HERE, "dashboard_template.html"), encoding="utf-8").read()
    blob = json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/")
    html = tpl.replace("/*__AOP_DATA__*/null", blob)
    p = os.path.join(out_dir, "AOP2027_dashboard.html")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(html)
    files["dashboard"] = p
    return files, qs


def _layout_doc():
    from extract import LAYOUTS, SHEETS
    out = []
    for c in SHEETS:
        L = LAYOUTS[c["layout"]]
        m = {k: (", ".join(v) if isinstance(v, list) else (", ".join(f"{a}={b}" for a, b in v.items()) if isinstance(v, dict) else v))
             for k, v in L.items()}
        if c.get("ia_col"):
            m["ia"] = c["ia_col"]
        out.append(dict(sheet=c["sheet"], role=c["role"], layout=c["layout"], first_data_row=c["start"], **m))
    return out
