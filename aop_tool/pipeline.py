"""
AOP 2027 analysis pipeline: cleaned records, data-quality checks, outliers,
version/summary reconciliation and a column profile.
"""
from __future__ import annotations

import math
import re
import statistics as st
from collections import Counter, defaultdict

from extract import (SHEETS, SUMMARY_SHEETS, SECTION_DUPLICATES, NUMCODE, extract, refs_of, clean_text)
import normalize as nz

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Info"]
SEVERITY_WEIGHT = {"Critical": 10, "High": 5, "Medium": 2, "Low": 0.5, "Info": 0}

# check catalogue: id -> (dimension, title, severity, explanation)
CHECKS = {
    "R1": ("Reconciliation", "Sheet total differs from the sum of its budget lines", "Critical",
           "The grand total shown on the sheet does not equal the sum of the individual budget lines."),
    "R2": ("Reconciliation", "Summary sheet differs from detail sheet", "High",
           "A roll-up/summary figure does not match the detail it summarises."),
    "R3": ("Reconciliation", "Language versions of the same plan differ", "Medium",
           "The Lao and English versions of the same plan carry different amounts."),
    "R4": ("Reconciliation", "Consolidated section differs from the stand-alone sheet", "High",
           "The same department plan appears twice with different line amounts."),
    "S1": ("Structure", "Budget line counted in more than one subtotal", "Critical",
           "The line's amount is pulled into two subtotals, so a subtotal is overstated."),
    "S2": ("Structure", "Budget line not included in the sheet total", "Critical",
           "No subtotal formula picks this line up, so it is missing from the sheet total."),
    "S3": ("Structure", "Subtotal row disconnected from the sheet total", "High",
           "A subtotal/check row is not linked to the sheet total (often a misplaced copy)."),
    "S4": ("Structure", "Amount copied from another line by formula", "Medium",
           "The line's value is a formula pointing at a sibling line - confirm it is a separate activity."),
    "S5": ("Structure", "Sub-line code does not sit under its subtotal's code", "Medium",
           "The subtotal formula sums a line whose code belongs to a different branch."),
    "S6": ("Structure", "Empty subtotal row", "Low",
           "The row has sub-activities with budget but shows 0 / blank itself."),
    "S7": ("Structure", "Subtotal typed in instead of calculated", "Medium",
           "A subtotal is a typed number, so it will not update when lines change."),
    "S9": ("Structure", "Left-over formula in a quarter cell", "Low",
           "A quarter cell of a budget line references another row."),
    "S10": ("Structure", "Total formula omits a quarter", "High",
            "The line's total formula does not sum all four quarters."),
    "S11": ("Structure", "Duplicate subtotal row", "Medium",
            "Two rows sum exactly the same lines."),
    "A1": ("Arithmetic", "Quarterly split does not add up to the annual total", "High",
           "Q1+Q2+Q3+Q4 differs from the annual total."),
    "A2": ("Arithmetic", "Unit cost × quantity does not match the total", "Medium",
           "None of unit cost × quantity (× movements) reproduces the line total."),
    "A3": ("Arithmetic", "Subtotal differs from the sum of its sub-lines", "High",
           "The subtotal amount is not equal to the sum of the rows it covers."),
    "A4": ("Arithmetic", "Budget phased in a quarter with no planned activity (or vice-versa)", "Medium",
           "Quarterly money and quarterly activity counts disagree."),
    "C1": ("Completeness", "Missing activity code", "Medium", "The budget line has no activity code."),
    "C2": ("Completeness", "Missing activity name", "High", "The budget line has no description."),
    "C3": ("Completeness", "Missing activity type", "Low", "No activity type was entered."),
    "C4": ("Completeness", "Missing unit cost / quantity / unit", "Medium",
           "Cost-build-up fields are blank, so the total cannot be verified."),
    "C5": ("Completeness", "Missing implementing agency", "Medium", "No implementing agency entered."),
    "C6": ("Completeness", "Budget line with zero / blank amount", "Low",
           "The line is coded and named but carries no budget."),
    "V1": ("Validity", "Text in a numeric field", "Medium", "A number was expected; text was found."),
    "V2": ("Validity", "Excel error value (#REF!, #VALUE!…)", "Critical", "A formula returns an error."),
    "V3": ("Validity", "Activity type not in the official dropdown list", "Low",
           "The value does not match the workbook's own Dropdownlist sheet."),
    "V4": ("Validity", "Unit of measure is malformed", "Low",
           "Number typed into the unit, currency used as unit, or misspelt unit."),
    "V5": ("Validity", "Implementing agency field is not an agency", "Medium",
           "A note/sentence or an unknown name was typed into the implementing-agency field."),
    "V6": ("Validity", "Negative amount", "High", "Budget amounts should not be negative."),
    "V7": ("Validity", "Activity code format is irregular", "Low", "Code is not of the form 1.2.3."),
    "V8": ("Validity", "Activity type is a programme tag or free text", "Low",
           "E.g. 'GESI' typed as the activity type; category was inferred from the name."),
    "K2": ("Consistency", "Hidden characters / stray spaces in text", "Low",
           "Zero-width characters or leading/trailing spaces break filtering and look-ups."),
    "K3": ("Consistency", "Non-round unit cost (looks back-calculated)", "Info",
           "Unit cost has many decimals - typically converted from LAK or allocated."),
    "K4": ("Consistency", "Different exchange rates used across sheets", "High",
           "LAK↔USD conversions use different rates in different sheets."),
    "K5": ("Consistency", "Line refers to another fiscal year", "Info",
           "Description mentions 2026 - confirm the amount belongs in the 2027 plan."),
    "U1": ("Uniqueness", "Duplicate activity code within a sheet", "Medium",
           "Two lines on the same sheet share a code."),
    "U2": ("Uniqueness", "Duplicate budget line within a sheet", "Medium",
           "Same description, unit cost and total appear twice on a sheet."),
    "U3": ("Uniqueness", "Same activity budgeted in two sheets", "High",
           "Identical description and amount in two counted sheets - possible double budgeting."),
    "U4": ("Uniqueness", "Possible cross-sheet duplicate (same amount & category)", "Medium",
           "Large lines with the same amount and category in two sheets - review for overlap."),
    "L1": ("Integrity", "Formula depends on another workbook", "High",
           "Values come from an external file and may be stale or break when files move."),
    "L2": ("Integrity", "Dormant external-link records", "Low",
           "The workbook stores links to many old files."),
    "L3": ("Integrity", "Hidden sheets present", "Info",
           "Hidden sheets hold older versions or templates; they are excluded from totals."),
    "L4": ("Integrity", "Sheet used-range / formatting bloat", "Low",
           "Formatting extends far beyond the data, slowing the file."),
}


def _r(x, n=2):
    return None if x is None else round(x, n)


def near(a, b, rel=0.001, abs_=1.0):
    if a is None or b is None:
        return False
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


class Run:
    def __init__(self, path):
        self.path = path
        self.wb, self.lines, self.declared = extract(path)
        self.cfg = {c["sheet"]: c for c in SHEETS}
        self.issues = []
        self.records = []
        self.by_uid = {}
        self.dropdown_types = self._dropdown_types()

    # ------------------------------------------------------------------ records
    def _dropdown_types(self):
        ws = self.wb.wv["Dropdownlist"]
        vals = set()
        for r in range(2, ws.max_row + 1):
            v = clean_text(ws[f"F{r}"].value)
            if v:
                vals.add(v)
        return vals

    def build_records(self):
        for ln in self.lines:
            f = ln.fields
            cfg = self.cfg[ln.sheet]
            cat, cat_src, cat_flag = nz.activity_category(f["activity_type"], f["name"], f["name_alt"])
            ag, lvl, ag_flag = nz.implementing_agency(f["ia"], f["ia_level_col"])
            un, un_flag = nz.unit(f["unit"])
            q = [x for x in f["q"]]
            qsum = sum(x or 0 for x in q) if any(x is not None for x in q) else None
            excl = None
            if f["role"] != "primary":
                excl = {"alternate": "alternate-language copy", "superseded": "hidden older version"}[f["role"]]
            elif f["section"] in SECTION_DUPLICATES:
                excl = f"duplicate of sheet '{SECTION_DUPLICATES[f['section']]}'"
            if f["kind"] != "line":
                excl = excl or f"{f['kind']} row"
            in_portfolio = excl is None
            rec = dict(
                uid=ln.uid, sheet=ln.sheet, sheet_short=f["sheet_short"], sheet_label=f["sheet_label"],
                role=f["role"], component=f["component"], modality=f["modality"], section=f["section"],
                excel_row=ln.row, code=f["code"], level=f["level"], depth=f["depth"],
                name=f["name"], name_alt=f["name_alt"], row_kind=f["kind"],
                activity_type_raw=f["activity_type"], activity_category=cat, activity_category_source=cat_src,
                unit_raw=f["unit"], unit=un,
                unit_cost_usd=_r(f["unit_cost"], 4), unit_cost_lak=f.get("unit_cost_lak"),
                quantity=f["qty"],
                mov_q1=(f["mov"] or [None] * 4)[0], mov_q2=(f["mov"] or [None] * 4)[1],
                mov_q3=(f["mov"] or [None] * 4)[2], mov_q4=(f["mov"] or [None] * 4)[3],
                mov_total=f["mov_total"],
                budget_q1=_r(q[0]), budget_q2=_r(q[1]), budget_q3=_r(q[2]), budget_q4=_r(q[3]),
                budget_total=_r(f["total"]), quarterly_sum=_r(qsum), quarter_split_derived=f["q_derived"],
                total_lak=f.get("total_lak"),
                ia_raw=f["ia"], implementing_agency=ag, implementation_level=lvl or ("Central" if ag else None),
                financing_modality=f["financing_modality"], remark=f["remark"],
                total_is_formula=f["total_is_formula"], total_formula=f["total_formula"],
                in_portfolio=in_portfolio, exclusion_reason=excl,
                _cat_flag=cat_flag, _ag_flag=ag_flag, _un_flag=un_flag,
            )
            self.records.append(rec)
            self.by_uid[ln.uid] = (rec, ln)
        return self.records

    # ------------------------------------------------------------------ issues
    def add(self, check, rec=None, sheet=None, row=None, cell=None, message="", value=None,
            expected=None, severity=None):
        dim, title, sev, _ = CHECKS[check]
        rec = rec or {}
        diff = None
        if isinstance(value, (int, float)) and isinstance(expected, (int, float)):
            diff = round(value - expected, 2)
        self.issues.append(dict(
            issue_id=f"Q{len(self.issues) + 1:04d}", check_id=check, check=title, dimension=dim,
            severity=severity or sev, sheet=rec.get("sheet", sheet), row=rec.get("excel_row", row),
            cell=cell, uid=rec.get("uid"), code=rec.get("code"), name=rec.get("name"),
            role=rec.get("role", self.cfg.get(sheet, {}).get("role") if sheet else None),
            in_portfolio=rec.get("in_portfolio", False),
            value=_r(value) if isinstance(value, float) else value,
            expected=_r(expected) if isinstance(expected, float) else expected,
            difference=diff, message=message))

    def run_checks(self):
        recs_by_sheet = defaultdict(list)
        for rec in self.records:
            recs_by_sheet[rec["sheet"]].append(rec)
        for rec in self.records:
            rec_ln = self.by_uid[rec["uid"]][1]
            self._row_checks(rec, rec_ln.fields, recs_by_sheet[rec["sheet"]])
        for sheet, recs in recs_by_sheet.items():
            self._sheet_checks(sheet, recs)
        self._cross_sheet_checks()
        self._workbook_checks()
        # attach to records
        per = defaultdict(list)
        for i in self.issues:
            if i["uid"]:
                per[i["uid"]].append(i)
        for rec in self.records:
            iss = per.get(rec["uid"], [])
            rec["issue_count"] = len(iss)
            rec["issue_checks"] = "; ".join(sorted({i["check_id"] for i in iss}))
            sev = [i["severity"] for i in iss if i["severity"] != "Info"]
            rec["max_severity"] = min(sev, key=SEVERITY_ORDER.index) if sev else None
        return self.issues

    def _row_checks(self, rec, f, sheet_recs):
        kind = rec["row_kind"]
        layout = f["layout"]
        idx = {r["excel_row"]: r for r in sheet_recs}
        tot = rec["budget_total"]
        q = [rec[f"budget_q{i}"] for i in range(1, 5)]
        # ---------------- error / invalid values (any row)
        for c in f["error_cells"]:
            self.add("V2", rec, cell=c, message=f"Cell {c} shows an Excel error value.")
        labels = {"mov0": "Q1 activity count", "mov1": "Q2 activity count", "mov2": "Q3 activity count",
                  "mov3": "Q4 activity count", "unit_cost": "unit cost", "qty": "quantity", "total": "total",
                  "mov_total": "activity count", "unit_cost_lak": "unit cost (LAK)", "total_lak": "total (LAK)"}
        for k, raw in f["invalid"].items():
            self.add("V1", rec, message=f"{labels.get(k, k)} contains text '{raw}' where a number is expected.",
                     value=raw)
        # ---------------- arithmetic: quarterly split (lines & subtotals)
        if kind in ("line", "subtotal", "grand_total") and tot is not None and not rec["quarter_split_derived"] \
                and any(x is not None for x in q):
            qs = sum(x or 0 for x in q)
            if not near(qs, tot):
                self.add("A1", rec, value=tot, expected=qs,
                         message=f"Annual total {tot:,.2f} vs Q1–Q4 sum {qs:,.2f}.")
        if kind in ("subtotal", "grand_total") and f["children_rows"]:
            ch_sum = sum((idx[c]["budget_total"] or 0) for c in f["children_rows"] if c in idx)
            if tot is not None and not near(tot, ch_sum):
                self.add("A3", rec, value=tot, expected=ch_sum,
                         message=f"Subtotal {tot:,.2f} vs sum of rows {f['children_rows'][:12]} = {ch_sum:,.2f}.")
            if not f["total_is_formula"] and tot:
                self.add("S7", rec, value=tot, message="Subtotal amount is typed in, not a formula.")
        if f["empty_subtotal"]:
            self.add("S6", rec, message="Row has budgeted sub-activities but shows no amount.")
        if f.get("stray_root"):
            self.add("S3", rec, value=tot,
                     message=f"Row {rec['excel_row']} ({tot or 0:,.0f}) is not linked to the sheet total.")
        if kind == "subtotal" and f["code_mismatch_children"]:
            bad = [f"{idx[c]['code']} (row {c})" for c in f["code_mismatch_children"] if c in idx]
            self.add("S5", rec, message=f"Subtotal {rec['code']} sums {', '.join(bad)}.")
        if kind != "line":
            return
        # ---------------- structure (lines)
        if f["rollup_paths"] > 1:
            self.add("S1", rec, value=tot, message=(f"Counted {f['rollup_paths']}× via subtotals rows "
                                                    f"{f['parent_rows']} – subtotal overstated by {tot or 0:,.0f}."))
        if f["rollup_paths"] == 0 and any(r["row_kind"] in ("subtotal", "grand_total") for r in sheet_recs):
            self.add("S2", rec, value=tot, message=f"{tot or 0:,.0f} is not picked up by any subtotal.")
        if f["linked_rows"] and not f["total_is_formula"]:
            self.add("S9", rec, message=f"Quarter cell formula points at sibling row {f['linked_rows'][0]}.")
        elif f["linked_rows"]:
            src = idx.get(f["linked_rows"][0], {})
            self.add("S4", rec, value=tot, message=(f"Total = formula {f['total_formula']} → copies line "
                                                    f"{src.get('code')} (row {f['linked_rows'][0]})."))
        if f["stray_q_refs"]:
            self.add("S9", rec, message=f"Quarter cell refers to row(s) {f['stray_q_refs']}.")
        tf = f["total_formula"] or ""
        qcols = self._qcols(layout)
        if tf and qcols:
            refs = {(c, r) for sh, c, r in refs_of(tf) if not sh}
            same_q = {c for c, r in refs if r == rec["excel_row"] and c in qcols}
            if same_q and len(same_q) < 4 and all(c in qcols for c, r in refs if r == rec["excel_row"]):
                miss = [f"Q{qcols.index(c) + 1}" for c in qcols if c not in same_q]
                self.add("S10", rec, message=f"Total formula {tf} leaves out {', '.join(miss)}.")
        # ---------------- arithmetic: cost build-up
        uc, qty, mt = rec["unit_cost_usd"], rec["quantity"], rec["mov_total"]
        if layout == "DPF":
            uc_l, tot_l = rec["unit_cost_lak"], rec["total_lak"]
            if uc_l and tot_l and mt and not near(uc_l * mt, tot_l):
                self.add("A2", rec, value=tot_l, expected=uc_l * mt,
                         message=(f"LAK {uc_l:,.0f} × {mt:g} movement(s) = {uc_l * mt:,.0f} but total is "
                                  f"{tot_l:,.0f} LAK (formula {f['total_formula'] or 'typed'})."))
        elif uc and tot:
            opts = [uc]
            if qty:
                opts.append(uc * qty)
            if mt:
                opts.append(uc * mt)
            if qty and mt:
                opts.append(uc * qty * mt)
            if not any(near(o, tot, rel=0.005) for o in opts):
                best = min(opts, key=lambda o: abs(o - tot))
                parts = f"unit cost {uc:,.2f}" + (f" × qty {qty:g}" if qty else "") + (
                    f" × movements {mt:g}" if mt else "")
                hint = ""
                if float(uc).is_integer() and uc <= 500 and tot / uc >= 50 and (tot / uc) % 50 == 0:
                    hint = (f" The unit-cost column seems to hold a count ({uc:g} {rec['unit_raw'] or ''}); "
                            f"implied unit cost {tot / uc:,.0f}.")
                self.add("A2", rec, value=tot, expected=best,
                         severity="High" if abs(best - tot) > 0.1 * tot else None,
                         message=f"{parts}; closest product {best:,.2f} vs total {tot:,.2f}.{hint}")
        # movement vs money by quarter
        movs = [rec[f"mov_q{i}"] for i in range(1, 5)]
        if f.get("mov") and layout in ("STD", "QPS") and any(m for m in movs):
            bad = []
            for i in range(4):
                has_m = (movs[i] or 0) > 0
                has_b = (q[i] or 0) > 0
                if has_m != has_b:
                    bad.append(f"Q{i + 1}: {'activity' if has_m else 'no activity'} / "
                               f"{'budget' if has_b else 'no budget'}")
            if bad:
                self.add("A4", rec, message="; ".join(bad))
        # ---------------- completeness
        if not rec["code"]:
            self.add("C1", rec, message="No activity code.")
        elif not NUMCODE.match(rec["code"]):
            self.add("V7", rec, value=rec["code"], message=f"Code '{rec['code']}'.")
        if not rec["name"]:
            self.add("C2", rec, message="No description.")
        if layout != "DPF" and not rec["activity_type_raw"]:
            self.add("C3", rec, message=f"Category inferred: {rec['activity_category']}.")
        missing = []
        if layout != "DPF" and rec["unit_cost_usd"] is None:
            missing.append("unit cost")
        if layout in ("QPS", "QPS_OLD", "IBF", "BIL") and rec["quantity"] is None:
            missing.append("quantity")
        if layout in ("STD", "QPS") and not rec["mov_total"]:
            missing.append("activity count")
        if not rec["unit_raw"] and layout != "DPF":
            missing.append("unit")
        if missing:
            self.add("C4", rec, message="Missing: " + ", ".join(missing) + ".")
        if layout != "DPF" and not rec["ia_raw"]:
            self.add("C5", rec, message="No implementing agency.")
        if not tot:
            self.add("C6", rec, value=tot, message="Line has no amount.")
        # ---------------- validity
        for x in [tot] + q + [uc]:
            if x is not None and x < 0:
                self.add("V6", rec, value=x, message=f"Negative amount {x:,.2f}.")
                break
        # V3 (dropdown conformity) is reported once per sheet in _sheet_checks
        if rec["_cat_flag"]:
            self.add("V8", rec, value=rec["activity_type_raw"],
                     message=f"{rec['_cat_flag']}; category → {rec['activity_category']} ({rec['activity_category_source']}).")
        if rec["_un_flag"]:
            self.add("V4", rec, value=rec["unit_raw"], message=rec["_un_flag"] + ".")
        if rec["_ag_flag"]:
            self.add("V5", rec, value=(rec["ia_raw"] or "")[:80], message=rec["_ag_flag"] + ".")
        # ---------------- consistency
        if f["text_flags"]:
            self.add("K2", rec, message="; ".join(f"{k}: {', '.join(v)}" for k, v in f["text_flags"].items()))
        if uc and abs(uc - round(uc, 2)) > 1e-6:
            hint = ""
            for rate in (21000, 22000, 22500):
                lak = uc * rate
                if abs(lak - round(lak, -3)) < 0.6:
                    hint = f" × {rate:,} = {round(lak):,} LAK (looks converted at {rate:,})"
                    break
            self.add("K3", rec, value=uc, message=f"Unit cost {uc:,.6f}{hint}.")
        txt = " ".join(x for x in (rec["name"], rec["name_alt"]) if x)
        if re.search(r"2026|2025", txt):
            self.add("K5", rec, value=tot, message="Description mentions " +
                     ", ".join(sorted(set(re.findall(r"202[56]", txt)))) + ".")

    @staticmethod
    def _qcols(layout):
        from extract import LAYOUTS
        return LAYOUTS[layout].get("q", [])

    def _sheet_checks(self, sheet, recs):
        lines = [r for r in recs if r["row_kind"] == "line"]
        # R1 declared total vs lines
        dec = self.declared.get(sheet)
        line_sum = sum(r["budget_total"] or 0 for r in lines)
        grand = [r for r in recs if self.by_uid[r["uid"]][1].fields.get("is_grand_root")
                 and r["row_kind"] in ("subtotal", "grand_total")]
        if len(grand) == 1:
            dec_total, dec = grand[0]["budget_total"], dict(row=grand[0]["excel_row"])
        else:
            dec_total = dec["total"] if dec else None
        if dec_total is not None and not near(dec_total, line_sum):
            self.add("R1", sheet=sheet, row=(dec or {}).get("row") or (grand[0]["excel_row"] if grand else None),
                     value=dec_total, expected=line_sum,
                     message=(f"Sheet total {dec_total:,.2f} vs sum of {len(lines)} budget lines "
                              f"{line_sum:,.2f}."))
        # V3 dropdown conformity (Lao-template sheets only)
        cfg = self.cfg.get(sheet, {})
        if cfg.get("layout") in ("STD", "QPS", "QPS_OLD") and self.dropdown_types:
            typed = [r for r in lines if r["activity_type_raw"] and not r["_cat_flag"]]
            off = [r for r in typed if r["activity_type_raw"] not in self.dropdown_types]
            if off:
                vals = Counter(r["activity_type_raw"] for r in off)
                self.add("V3", sheet=sheet, value=len(off), expected=len(typed),
                         message=(f"{len(off)} of {len(typed)} typed activity types are not in the Dropdownlist: "
                                  + ", ".join(f"'{k}' ×{v}" for k, v in vals.most_common(8))
                                  + (" …" if len(vals) > 8 else "") + "."))
        # U1 duplicate codes / U2 duplicate lines
        codes = Counter(r["code"] for r in lines if r["code"] and NUMCODE.match(r["code"]))
        for rr in lines:
            if rr["code"] in codes and codes[rr["code"]] > 1 and not rr["section"]:
                self.add("U1", rr, value=rr["code"], message=f"Code {rr['code']} used {codes[rr['code']]}× on this sheet.")
        sec_codes = defaultdict(Counter)
        for r in lines:
            if r["section"] and r["code"]:
                sec_codes[r["section"]][r["code"]] += 1
        for rr in lines:
            if rr["section"] and rr["code"] and sec_codes[rr["section"]][rr["code"]] > 1:
                self.add("U1", rr, value=rr["code"],
                         message=f"Code {rr['code']} used {sec_codes[rr['section']][rr['code']]}× in section {rr['section']}.")
        dk = lambda r: (r["name"], r["unit_cost_usd"], r["budget_total"], r["ia_raw"], r["section"])
        key = Counter(dk(r) for r in lines if r["name"])
        for rr in lines:
            k = dk(rr)
            if rr["name"] and key[k] > 1 and (rr["budget_total"] or 0) > 0:
                self.add("U2", rr, value=rr["budget_total"], message=f"Same description and amount appear {key[k]}× on the sheet.")
        # S11 duplicate subtotal rows
        seen = {}
        for r in recs:
            f = self.by_uid[r["uid"]][1].fields
            if r["row_kind"] == "subtotal" and len(f["children_rows"]) > 0:
                k = tuple(f["children_rows"])
                if k in seen:
                    self.add("S11", r, value=r["budget_total"],
                             message=f"Sums the same rows as row {seen[k]} ({r['budget_total'] or 0:,.0f}).")
                else:
                    seen[k] = r["excel_row"]
        # A_QPS_DHHP department allocation columns
        if sheet == "A_QPS_DHHP":
            ws = self.wb.wv[sheet]
            for r in lines:
                vals = [ws[f"{c}{r['excel_row']}"].value for c in "PQRST"]
                nums = [v for v in vals if isinstance(v, (int, float))]
                if r["budget_total"] and nums and not near(sum(nums), r["budget_total"]):
                    self.add("R2", r, value=r["budget_total"], expected=sum(nums),
                             message="Department allocation columns P–T do not add up to the line total.")
                elif r["budget_total"] and not nums:
                    self.add("R2", r, severity="Low", value=r["budget_total"], expected=0,
                             message="Line not allocated to any department in columns P–T (feeds A_QPS_DHHP_Sum).")

    # ------------------------------------------------------------------ cross-sheet
    def _section_recs(self, sheet, section=None, kind="line"):
        return [r for r in self.records if r["sheet"] == sheet and r["row_kind"] == kind
                and (section is None or r["section"] == section)]

    def compare(self, a_recs, b_recs, label_a, label_b, pair, key="code"):
        """Align two versions of a plan by activity code (with occurrence index)."""
        def keyed(recs):
            occ = Counter()
            out = {}
            for r in recs:
                k = r[key] or (r["name"] or "")[:40]
                occ[k] += 1
                out[(k, occ[k])] = r
            return out
        A, B = keyed(a_recs), keyed(b_recs)
        rows = []
        for k in sorted(set(A) | set(B), key=lambda x: (
                [int(p) if p.isdigit() else 0 for p in str(x[0]).split(".")], x[1])):
            a, b = A.get(k), B.get(k)
            ta = a["budget_total"] if a else None
            tb = b["budget_total"] if b else None
            if a and b:
                status = "same" if near(ta, tb) else "changed"
                qa = [a[f"budget_q{i}"] or 0 for i in range(1, 5)]
                qb = [b[f"budget_q{i}"] or 0 for i in range(1, 5)]
                if status == "same" and any(not near(x, y) for x, y in zip(qa, qb)):
                    status = "phasing changed"
            else:
                status = f"only in {label_a}" if a else f"only in {label_b}"
            rows.append(dict(pair=pair, code=k[0], occurrence=k[1],
                             name=(a or b)["name"], version_a=label_a, version_b=label_b,
                             total_a=ta, total_b=tb,
                             difference=None if ta is None or tb is None else round(ta - tb, 2),
                             q_a=" / ".join(f"{(a or {}).get(f'budget_q{i}') or 0:,.0f}" for i in range(1, 5)) if a else None,
                             q_b=" / ".join(f"{(b or {}).get(f'budget_q{i}') or 0:,.0f}" for i in range(1, 5)) if b else None,
                             status=status, row_a=a["excel_row"] if a else None, row_b=b["excel_row"] if b else None))
        return rows

    def _cross_sheet_checks(self):
        self.versions = []
        pairs = [
            ("IBF1 DCDC: Lao vs English", "2.3.1_IBF1_DCDC Lao 2027", None, "IBF1 (DCD) ENG 2027", None,
             "Lao", "English", "R3"),
            ("DCDC: stand-alone vs B_DCDC section", "2.3.1_IBF1_DCDC Lao 2027", None, "B_DCDC _IBF_QPS", "DCDC",
             "2.3.1 sheet", "B_DCDC section", "R4"),
            ("NCLE: stand-alone vs B_DCDC section", "2.3.2_NCLE", None, "B_DCDC _IBF_QPS", "NCLE",
             "2.3.2 sheet", "B_DCDC section", "R4"),
            ("QPS-DHR: V2 vs old (hidden)", "Com1_QPS_AOP2027_DHR(V2)", None, "1_QPS_DHR", None, "V2", "old", None),
            ("GESI: V2 vs old (hidden)", "3.6 GESI(V2)", None, "3.6_GESI", None, "V2", "old", None),
            ("IBF3 DHIS2: current vs hidden Lao draft", "2.5 IBF3_DPF_E", None, "2.5_IBF3_DHIS2_L", None,
             "current", "hidden draft", None),
        ]
        for pair, sa, seca, sb, secb, la, lb, chk in pairs:
            rows = self.compare(self._section_recs(sa, seca), self._section_recs(sb, secb), la, lb, pair)
            self.versions.extend(rows)
            if chk:
                diff = [r for r in rows if r["status"] != "same"]
                if diff:
                    ta = sum(r["total_a"] or 0 for r in rows)
                    tb = sum(r["total_b"] or 0 for r in rows)
                    n_ch = sum(r["status"] == "changed" for r in rows)
                    n_ph = sum(r["status"] == "phasing changed" for r in rows)
                    n_only = sum(r["status"].startswith("only") for r in rows)
                    self.add(chk, sheet=sb, message=(
                        f"{pair}: {n_ch} line amounts differ, {n_ph} differ only in quarterly phasing, "
                        f"{n_only} lines unmatched. Totals {ta:,.0f} ({la}) vs {tb:,.0f} ({lb})."),
                        value=ta, expected=tb)
        # summary sheet B_DCDC _IBF_QPS_SUM vs sections and stand-alone sheets
        self.summary_recon = []
        ws = self.wb.wv["B_DCDC _IBF_QPS_SUM"]
        wf = self.wb.wf["B_DCDC _IBF_QPS_SUM"]
        sec_total = {}
        for r in self.records:
            if r["sheet"] == "B_DCDC _IBF_QPS" and r["code"] and re.match(r"^[IVX]+\./?$", r["code"]):
                sec_total[r["section"]] = r
        standalone = {"NCLE": "2.3.2_NCLE", "DCDC": "2.3.1_IBF1_DCDC Lao 2027"}
        for row in range(4, 8):
            comp = ws[f"G{row}"].value
            vals = [ws[f"{c}{row}"].value for c in "BCDEF"]
            ext = any(isinstance(wf[f"{c}{row}"].value, str) and "[" in wf[f"{c}{row}"].value for c in "BCDEF")
            sec = sec_total.get(comp)
            targets = [("B_DCDC section", sec)]
            if comp in standalone:
                g = [r for r in self.records if r["sheet"] == standalone[comp]
                     and self.by_uid[r["uid"]][1].fields.get("is_grand_root")]
                targets.append((standalone[comp], g[0] if g else None))
            for tlabel, t in targets:
                if not t:
                    continue
                tv = [t[f"budget_q{i}"] or 0 for i in range(1, 5)] + [t["budget_total"] or 0]
                ok_total = near(vals[4], tv[4])
                ok_q = all(near(a or 0, b) for a, b in zip(vals[:4], tv[:4]))
                self.summary_recon.append(dict(
                    summary_sheet="B_DCDC _IBF_QPS_SUM", summary_row=row, component=comp,
                    compared_with=tlabel, summary_q=" / ".join(f"{v or 0:,.0f}" for v in vals[:4]),
                    detail_q=" / ".join(f"{v:,.0f}" for v in tv[:4]),
                    summary_total=_r(vals[4]), detail_total=_r(tv[4]),
                    difference=_r((vals[4] or 0) - tv[4]), external_link=ext,
                    status="match" if ok_total and ok_q else ("phasing differs" if ok_total else "total differs")))
                if not (ok_total and ok_q):
                    self.add("R2", sheet="B_DCDC _IBF_QPS_SUM", row=row,
                             value=vals[4], expected=tv[4],
                             severity="High" if not ok_total else "Medium",
                             message=(f"{comp}: summary Q1–Q4 {self.summary_recon[-1]['summary_q']} vs "
                                      f"{tlabel} {self.summary_recon[-1]['detail_q']}"
                                      + (" (summary values come from an external workbook)" if ext else "")))
        # A_QPS_DHHP_Sum
        ws = self.wb.wv["A_QPS_DHHP_Sum"]
        sumrow = 64
        dws = self.wb.wv["A_QPS_DHHP"]
        for row, col in zip(range(3, 8), "SPQTR"):
            v = ws[f"C{row}"].value
            alloc = sum((dws[f"{col}{r['excel_row']}"].value or 0) for r in self.records
                        if r["sheet"] == "A_QPS_DHHP" and r["row_kind"] == "line"
                        and isinstance(dws[f"{col}{r['excel_row']}"].value, (int, float)))
            self.summary_recon.append(dict(
                summary_sheet="A_QPS_DHHP_Sum", summary_row=row, component=ws[f"B{row}"].value,
                compared_with=f"A_QPS_DHHP column {col} (sum of budget lines)", summary_q=None, detail_q=None,
                summary_total=_r(v), detail_total=_r(alloc), difference=_r((v or 0) - alloc),
                external_link=False, status="match" if near(v, alloc) else "total differs"))
            if not near(v, alloc):
                self.add("R2", sheet="A_QPS_DHHP_Sum", row=row, value=v, expected=alloc,
                         message=f"{ws[f'B{row}'].value}: summary {v:,.0f} vs line allocations {alloc:,.0f}.")
        # U3/U4 cross-sheet duplicates among counted lines
        port = [r for r in self.records if r["in_portfolio"]]
        by_name = defaultdict(list)
        for r in port:
            if r["name"] and (r["budget_total"] or 0) > 0:
                by_name[(re.sub(r"\W+", "", r["name"].lower()), round(r["budget_total"]))].append(r)
        flagged = set()
        for (_, amt), rs in by_name.items():
            sheets = {r["sheet"] for r in rs}
            if len(sheets) > 1:
                for r in rs:
                    others = sorted(s for s in sheets if s != r["sheet"])
                    self.add("U3", r, value=r["budget_total"],
                             message=f"Same description and amount also in: {', '.join(others)}.")
                    flagged.add(r["uid"])
        by_amt = defaultdict(list)
        for r in port:
            big = (r["budget_total"] or 0) >= 100000 or (
                r["activity_category"] == "Procurement (goods)" and (r["budget_total"] or 0) >= 50000)
            if big and r["uid"] not in flagged:
                by_amt[(round(r["budget_total"]), r["activity_category"])].append(r)
        for (amt, cat), rs in by_amt.items():
            sheets = {r["sheet"] for r in rs}
            if len(sheets) > 1:
                for r in rs:
                    others = [f"{o['sheet_short']} {o['code'] or ''} (row {o['excel_row']})" for o in rs
                              if o["sheet"] != r["sheet"]]
                    self.add("U4", r, value=r["budget_total"],
                             message=f"{amt:,.0f} {cat} also in {', '.join(others)}.")

    def _workbook_checks(self):
        wf = self.wb.wf
        # exchange rates
        rates = defaultdict(lambda: defaultdict(list))
        for ws in wf.worksheets:
            for row in ws.iter_rows(max_col=min(ws.max_column, 70)):
                for c in row:
                    v = c.value
                    if isinstance(v, str) and v.startswith("="):
                        for m in re.findall(r"[/*]\s*\(?\s*(2[0-9]{4})\b", v):
                            rates[int(m)][ws.title].append(c.coordinate)
        tpl = self.wb.wv["ສັ່ງລວມ"]["D39"].value
        if isinstance(tpl, (int, float)):
            rates[int(tpl)]["ສັ່ງລວມ (template)"].append("D39")
        self.fx = [dict(rate=k, sheet=s, cells=", ".join(v[:6]) + (" …" if len(v) > 6 else ""), n_cells=len(v))
                   for k, d in sorted(rates.items()) for s, v in d.items()]
        if len(rates) > 1:
            self.add("K4", sheet="(workbook)", message="Rates in use: " + "; ".join(
                f"{k:,} LAK/USD in {', '.join(d)}" for k, d in sorted(rates.items())) +
                ". Implied 21,000 also appears in back-calculated unit costs (see K3).")
        # external links
        active = defaultdict(list)
        for ws in wf.worksheets:
            for row in ws.iter_rows(max_col=min(ws.max_column, 70)):
                for c in row:
                    v = c.value
                    if isinstance(v, str) and v.startswith("=") and re.search(r"\[\d+\]", v):
                        active[ws.title].append(c.coordinate)
        for s, cells in active.items():
            self.add("L1", sheet=s, cell=", ".join(cells[:8]),
                     message=f"{len(cells)} formula(s) read values from another workbook ({', '.join(cells[:6])}).")
        links = self.wb.external_links()
        self.external_links = links
        if links:
            self.add("L2", sheet="(workbook)", value=len(links),
                     message=f"{len(links)} external-link records stored (old GF / AOP 2026 files, OneDrive and local paths).")
        hidden = [ws.title for ws in wf.worksheets if ws.sheet_state != "visible"]
        if hidden:
            self.add("L3", sheet="(workbook)", value=len(hidden), message="Hidden: " + ", ".join(hidden) + ".")
        for ws in wf.worksheets:
            if ws.max_column > 200 or len(ws.merged_cells.ranges) > 300:
                self.add("L4", sheet=ws.title, message=(f"Used range {ws.dimensions} with "
                                                        f"{len(ws.merged_cells.ranges)} merged ranges."))
        # error cells anywhere (not only in parsed rows)
        seen = {(i["sheet"], i["cell"]) for i in self.issues if i["check_id"] == "V2"}
        for ws in self.wb.wv.worksheets:
            for row in ws.iter_rows(max_col=min(ws.max_column, 70)):
                for c in row:
                    if isinstance(c.value, str) and c.value.startswith("#") and (ws.title, c.coordinate) not in seen:
                        form = wf[ws.title][c.coordinate].value
                        self.add("V2", sheet=ws.title, row=c.row, cell=c.coordinate, value=c.value,
                                 message=f"{c.coordinate} = {form} → {c.value}.")

    # ------------------------------------------------------------------ outliers
    def outliers(self):
        port = [r for r in self.records if r["in_portfolio"]]
        out = []

        def iqr_flags(vals):
            xs = sorted(vals)
            n = len(xs)
            if n < 5:
                return None
            q1 = xs[int(0.25 * (n - 1))] + (xs[int(math.ceil(0.25 * (n - 1)))] - xs[int(0.25 * (n - 1))]) * ((0.25 * (n - 1)) % 1)
            q3 = xs[int(0.75 * (n - 1))] + (xs[int(math.ceil(0.75 * (n - 1)))] - xs[int(0.75 * (n - 1))]) * ((0.75 * (n - 1)) % 1)
            med = st.median(xs)
            mad = st.median([abs(x - med) for x in xs]) or None
            return q1, q3, med, mad

        # 1) unit cost within activity category (log10)
        groups = defaultdict(list)
        for r in port:
            if r["unit_cost_usd"] and r["unit_cost_usd"] > 0:
                groups[r["activity_category"]].append(r)
        self.uc_stats = {}
        for cat, rs in groups.items():
            logs = [math.log10(r["unit_cost_usd"]) for r in rs]
            s = iqr_flags(logs)
            if not s:
                continue
            q1, q3, med, mad = s
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            self.uc_stats[cat] = dict(n=len(rs), median=10 ** med, q1=10 ** q1, q3=10 ** q3,
                                      lower_fence=10 ** lo, upper_fence=10 ** hi)
            for r, lx in zip(rs, logs):
                z = 0.6745 * (lx - med) / mad if mad else 0
                if lx > hi or lx < lo or abs(z) > 3.5:
                    out.append(dict(uid=r["uid"], sheet=r["sheet"], sheet_short=r["sheet_short"], excel_row=r["excel_row"],
                                    code=r["code"], name=r["name"], metric="Unit cost (USD)",
                                    peer_group=cat, value=r["unit_cost_usd"], peer_median=round(10 ** med, 2),
                                    lower_fence=round(10 ** lo, 2), upper_fence=round(10 ** hi, 2),
                                    robust_z=round(z, 2), direction="high" if lx > med else "low",
                                    method=("Tukey IQR on log10" if (lx > hi or lx < lo) else "") +
                                           (" + " if (lx > hi or lx < lo) and abs(z) > 3.5 else "") +
                                           ("MAD robust z>3.5" if abs(z) > 3.5 else ""),
                                    budget_total=r["budget_total"]))
        # 2) line total across the portfolio (log10)
        rs = [r for r in port if (r["budget_total"] or 0) > 0]
        logs = [math.log10(r["budget_total"]) for r in rs]
        s = iqr_flags(logs)
        if s:
            q1, q3, med, mad = s
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            self.total_stats = dict(n=len(rs), median=10 ** med, q1=10 ** q1, q3=10 ** q3,
                                    lower_fence=10 ** lo, upper_fence=10 ** hi)
            for r, lx in zip(rs, logs):
                z = 0.6745 * (lx - med) / mad if mad else 0
                if lx > hi or lx < lo:
                    out.append(dict(uid=r["uid"], sheet=r["sheet"], sheet_short=r["sheet_short"], excel_row=r["excel_row"],
                                    code=r["code"], name=r["name"], metric="Line total (USD)",
                                    peer_group="All counted lines", value=r["budget_total"],
                                    peer_median=round(10 ** med, 2), lower_fence=round(10 ** lo, 2),
                                    upper_fence=round(10 ** hi, 2), robust_z=round(z, 2),
                                    direction="high" if lx > med else "low",
                                    method="Tukey IQR on log10", budget_total=r["budget_total"]))
        # 3) quarterly concentration: >= 90% of a large line in one quarter
        for r in port:
            q = [r[f"budget_q{i}"] or 0 for i in range(1, 5)]
            t = sum(q)
            if t >= 100000 and max(q) / t >= 0.999 and not r["quarter_split_derived"]:
                out.append(dict(uid=r["uid"], sheet=r["sheet"], sheet_short=r["sheet_short"], excel_row=r["excel_row"],
                                code=r["code"], name=r["name"], metric="Quarterly phasing",
                                peer_group="Lines ≥ 100,000", value=t, peer_median=None,
                                lower_fence=None, upper_fence=None, robust_z=None,
                                direction=f"100% in Q{q.index(max(q)) + 1}",
                                method="Single-quarter concentration", budget_total=r["budget_total"]))
        per = defaultdict(list)
        for o in out:
            per[o["uid"]].append(o["metric"])
        for r in self.records:
            r["outlier_flags"] = "; ".join(per.get(r["uid"], []))
        self.outlier_rows = out
        return out

    # ------------------------------------------------------------------ profile
    def profile(self):
        port = [r for r in self.records if r["in_portfolio"]]
        fields = [
            ("code", "text", "Activity code (hierarchical, e.g. 2.11.3.1)"),
            ("name", "text", "Activity description (Lao or English)"),
            ("name_alt", "text", "Second-language description (bilingual sheets)"),
            ("activity_type_raw", "text", "Activity type as typed"),
            ("activity_category", "category", "Standardised activity category"),
            ("unit_raw", "text", "Unit of measure as typed"),
            ("unit", "category", "Standardised unit"),
            ("unit_cost_usd", "number", "Unit cost in USD (DPF converted from LAK at 22,500)"),
            ("quantity", "number", "Quantity (units, people, facilities)"),
            ("mov_total", "number", "Number of activity movements in the year"),
            ("budget_q1", "number", "Q1 budget (USD)"), ("budget_q2", "number", "Q2 budget (USD)"),
            ("budget_q3", "number", "Q3 budget (USD)"), ("budget_q4", "number", "Q4 budget (USD)"),
            ("budget_total", "number", "Annual budget (USD)"),
            ("ia_raw", "text", "Implementing agency as typed"),
            ("implementing_agency", "category", "Standardised implementing agency"),
            ("implementation_level", "category", "Central / Province / District / Civil society"),
            ("financing_modality", "category", "IBF / PBF (bilingual & IBF sheets only)"),
            ("remark", "text", "Remarks"),
        ]
        prof = []
        n = len(port)
        for key, typ, desc in fields:
            vals = [r[key] for r in port]
            nn = [v for v in vals if v not in (None, "")]
            row = dict(field=key, type=typ, description=desc, records=n, non_missing=len(nn),
                       missing=n - len(nn), completeness_pct=round(100 * len(nn) / n, 1) if n else None,
                       unique=len(set(map(str, nn))))
            if typ == "number":
                xs = [float(v) for v in nn if isinstance(v, (int, float))]
                if xs:
                    row.update(min=min(xs), p25=_pct(xs, 25), median=st.median(xs), mean=st.mean(xs),
                               p75=_pct(xs, 75), max=max(xs), std=st.pstdev(xs) if len(xs) > 1 else 0,
                               sum=sum(xs), zeros=sum(1 for x in xs if x == 0))
            else:
                top = Counter(map(str, nn)).most_common(3)
                row["top_values"] = " | ".join(f"{k[:40]} ({v})" for k, v in top)
            prof.append(row)
        self.profile_rows = prof
        return prof

    def sheet_summary(self):
        inv = {s["sheet"]: s for s in self.wb.sheet_inventory()}
        rows = []
        cfgs = {c["sheet"]: c for c in SHEETS}
        for ws in self.wb.wf.worksheets:
            name = ws.title
            c = cfgs.get(name, {})
            recs = [r for r in self.records if r["sheet"] == name]
            lines = [r for r in recs if r["row_kind"] == "line"]
            port = [r for r in lines if r["in_portfolio"]]
            iss = [i for i in self.issues if i["sheet"] == name]
            sev = Counter(i["severity"] for i in iss)
            clean = sum(1 for r in lines if r.get("max_severity") not in ("Critical", "High", "Medium"))
            dec = self.declared.get(name)
            grand = [r for r in recs if self.by_uid[r["uid"]][1].fields.get("is_grand_root")
                     and r["row_kind"] in ("subtotal", "grand_total")]
            dec_total = grand[0]["budget_total"] if len(grand) == 1 else (dec["total"] if dec else None)
            role =c.get("role") or ("summary" if name in SUMMARY_SHEETS else "reference")
            rows.append(dict(
                sheet=name, short=c.get("short", name), label=c.get("label", {
                    "Dropdownlist": "Reference lists (types, provinces, districts, agencies)",
                    "ສັ່ງລວມ": "Blank consolidation template",
                    "A_QPS_DHHP_Sum": "Summary of A_QPS_DHHP by department",
                    "B_DCDC _IBF_QPS_SUM": "Summary of B_DCDC by component"}.get(name, name)),
                role=role, visibility=inv[name]["visibility"], layout=c.get("layout"),
                component=c.get("component"), modality=c.get("modality"),
                used_range=inv[name]["dimension"], merged_ranges=inv[name]["merged_ranges"],
                formulas=inv[name]["formulas"], numeric_constants=inv[name]["numeric_constants"],
                parsed_rows=len(recs), budget_lines=len(lines),
                subtotal_rows=sum(r["row_kind"] in ("subtotal", "grand_total") for r in recs),
                counted_lines=len(port), declared_total=_r(dec_total),
                lines_total=_r(sum(r["budget_total"] or 0 for r in lines)),
                counted_total=_r(sum(r["budget_total"] or 0 for r in port)),
                issues=len(iss), critical=sev["Critical"], high=sev["High"], medium=sev["Medium"],
                low=sev["Low"], info=sev["Info"],
                clean_line_pct=round(100 * clean / len(lines), 1) if lines else None))
        self.sheet_rows = rows
        return rows

    def run(self):
        self.build_records()
        self.run_checks()
        self.outliers()
        self.profile()
        self.sheet_summary()
        return self


def _pct(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    return xs[f] + (xs[c] - xs[f]) * (k - f)
