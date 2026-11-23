"""
AOP 2027 workbook extraction layer.

Reads the AOP workbook READ-ONLY (values + formulas), maps each sheet's own
layout onto one standard schema, and uses the formula reference graph to tell
budget lines (leaves) from subtotal rows (parents).

The source workbook is never written to.
"""
from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field

import openpyxl
from openpyxl.utils import column_index_from_string, get_column_letter

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Sheet registry: what each sheet IS, and where its columns are.
#   role:  primary      -> unique budget lines, counted in the portfolio
#          alternate    -> same plan in another language (cross-checked, not counted)
#          superseded   -> hidden older version (compared, not counted)
#          summary      -> roll-up sheet (reconciled against detail)
#          reference    -> lookup lists / blank templates
# ---------------------------------------------------------------------------
LAYOUTS = {
    # Com1 QPS (V2): unit cost x quantity x movement
    "QPS": dict(code="A", name="B", type="C", unit_cost="D", qty="E", unit="F",
                mov=["G", "H", "I", "J"], mov_total="K", q=["L", "M", "N", "O"],
                total="P", ia="Q"),
    # Older QPS / DHIS2 Lao layout: no movement columns
    "QPS_OLD": dict(code="A", name="B", type="C", unit_cost="D", qty="E", unit="F",
                    total="G", q=["H", "I", "J", "K"], ia="L"),
    # Standard Lao AOP template (most department sheets)
    "STD": dict(code="A", name="B", type="C", unit="D", unit_cost="E",
                mov=["F", "G", "H", "I"], mov_total="J", q=["K", "L", "M", "N"],
                total="O", ia="P"),
    # IBF template (Lao or English): central/province/district IA columns
    "IBF": dict(code="A", name="B", type="C", fin="D", unit_cost="E", qty="F",
                unit="G", total="H", q=["I", "J", "K", "L"],
                ia_levels={"Central": "M", "Province": "N", "District": "O"}, remark="P"),
    # Bilingual IBF template (EN + LA names)
    "BIL": dict(code="A", name="B", name_alt="C", type="D", fin="E", unit_cost="F",
                qty="G", unit="H", total="I", q=["J", "K", "L", "M"],
                ia_levels={"Central": "N", "Province": "O", "District": "P"}, remark="Q"),
    # DPF PBC1 sheet: LAK unit price, USD total, no quarterly amounts
    "DPF": dict(code="A", name="B", unit="C", unit_cost_lak="D",
                mov=["E", "F", "G", "H"], total_lak="I", total="J"),
}

SHEETS = [
    dict(sheet="Com1_QPS_AOP2027_DHR(V2)", role="primary", layout="QPS", start=15,
         label="QPS – Healthcare & Rehabilitation (DHR)", short="QPS-DHR",
         component="Component 1", modality="QPS"),
    dict(sheet="1_QPS_DHR", role="superseded", layout="QPS_OLD", start=15, of="Com1_QPS_AOP2027_DHR(V2)",
         label="QPS – DHR (old version)", short="QPS-DHR old", component="Component 1", modality="QPS"),
    dict(sheet="A_QPS_DHHP", role="primary", layout="STD", start=15, ia_col="U",
         label="QPS – Hygiene & Health Promotion (DHHP) and centres", short="QPS-DHHP",
         component="Component 1", modality="QPS"),
    dict(sheet="B_DCDC _IBF_QPS", role="primary", layout="STD", start=15, sectioned=True,
         label="HIV / TB / NCLE / DCDC consolidated (DCDC)", short="DCDC-GC8",
         component="Component 2", modality="GC8 / IBF1"),
    dict(sheet="2.1_PBC_DPF", role="primary", layout="DPF", start=15, currency="LAK", fx=22500,
         label="PBC1 – Planning & Finance (DPF)", short="PBC1-DPF",
         component="Component 2", modality="PBC1"),
    dict(sheet="2.2_PBC2_DHP", role="primary", layout="STD", start=15,
         label="PBC2 – Organisation & Personnel (DHP)", short="PBC2-DHP",
         component="Component 2", modality="PBC2"),
    dict(sheet="2.3.1_IBF1_DCDC Lao 2027", role="primary", layout="IBF", start=4,
         label="IBF1 – Communicable Disease Control (DCDC)", short="IBF1-DCDC",
         component="Component 2", modality="IBF1"),
    dict(sheet="IBF1 (DCD) ENG 2027", role="alternate", layout="IBF", start=5, of="2.3.1_IBF1_DCDC Lao 2027",
         label="IBF1 – DCDC (English version)", short="IBF1-DCDC EN",
         component="Component 2", modality="IBF1"),
    dict(sheet="2.3.2_NCLE", role="primary", layout="STD", start=15,
         label="IBF1 – Lab & Epidemiology Centre (NCLE)", short="IBF1-NCLE",
         component="Component 2", modality="IBF1"),
    dict(sheet="2.4_IBF2_FDD_V2", role="primary", layout="STD", start=15,
         label="IBF2 – Food & Drug Department (FDD)", short="IBF2-FDD",
         component="Component 2", modality="IBF2"),
    dict(sheet="2.5 IBF3_DPF_E", role="primary", layout="IBF", start=4,
         label="IBF3 – Health information / DHIS2 (DPF)", short="IBF3-DHIS2",
         component="Component 2", modality="IBF3"),
    dict(sheet="2.5_IBF3_DHIS2_L", role="superseded", layout="QPS_OLD", start=5, of="2.5 IBF3_DPF_E",
         label="IBF3 – DHIS2 (hidden Lao draft)", short="IBF3 old",
         component="Component 2", modality="IBF3"),
    dict(sheet="2.6_IOR_CN", role="primary", layout="STD", start=15,
         label="IOR – Centre of Nutrition (CN)", short="IOR-CN",
         component="Component 2", modality="IOR"),
    dict(sheet="2.11 IBF4_NHIB 2027", role="primary", layout="BIL", start=11,
         label="IBF4 – National Health Insurance Bureau (NHIB)", short="IBF4-NHIB",
         component="Component 2", modality="IBF4"),
    dict(sheet="3.4 ESF ", role="primary", layout="STD", start=5,
         label="ESF – Environmental & Social Framework (NPCO)", short="ESF",
         component="Component 3", modality="Input-based"),
    dict(sheet="3.6 GESI(V2)", role="primary", layout="BIL", start=16,
         label="GESI – Gender & Social Inclusion (Cabinet)", short="GESI",
         component="Component 3", modality="PBF"),
    dict(sheet="3.6_GESI", role="superseded", layout="BIL", start=16, of="3.6 GESI(V2)",
         label="GESI (old version)", short="GESI old", component="Component 3", modality="PBF"),
    dict(sheet="3.1.3.1-DOI_V2", role="primary", layout="STD", start=15,
         label="DOI – Internal Audit (DOI)", short="DOI",
         component="Component 3", modality="Input-based"),
]
SUMMARY_SHEETS = ["A_QPS_DHHP_Sum", "B_DCDC _IBF_QPS_SUM"]
REFERENCE_SHEETS = ["Dropdownlist", "ສັ່ງລວມ"]

# B_DCDC sections whose lines are ALSO budgeted in a standalone sheet
SECTION_DUPLICATES = {"NCLE": "2.3.2_NCLE", "DCDC": "2.3.1_IBF1_DCDC Lao 2027"}

STOP_PATTERNS = re.compile(
    r"^(ປະເພດກິດຈະກຳ\s*:|total|ລວມທັງໝົດ|ຫົວໜ້າ|ໝາຍເຫດ)", re.IGNORECASE)
ZW = re.compile(r"[​‌‍﻿]")
REF_RE = re.compile(
    r"(?:(?P<sheet>'[^']+'|\[[^\]]+\][^!]*|[A-Za-z0-9_\.]+)!)?\$?(?P<c1>[A-Z]{1,3})\$?(?P<r1>\d+)"
    r"(?::\$?(?P<c2>[A-Z]{1,3})\$?(?P<r2>\d+))?")


def clean_text(v):
    """Trim, drop zero-width characters, collapse whitespace."""
    if v is None:
        return None
    s = ZW.sub("", str(v)).replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def text_flags(v):
    """Formatting problems in a raw text cell."""
    if not isinstance(v, str):
        return []
    f = []
    if ZW.search(v):
        f.append("zero-width characters")
    if v != v.strip():
        f.append("leading/trailing spaces")
    if re.search(r"\S\s{2,}\S", v.strip()):
        f.append("repeated spaces")
    return f


def to_num(v):
    """Return (number|None, invalid_raw|None)."""
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None, None
    if isinstance(v, bool):
        return None, str(v)
    if isinstance(v, (int, float)):
        return float(v), None
    s = str(v).strip().replace(",", "")
    try:
        return float(s), None
    except ValueError:
        return None, str(v)


@dataclass
class Cell:
    value: object
    formula: str | None

    @property
    def is_formula(self):
        return self.formula is not None


@dataclass
class Line:
    uid: str
    sheet: str
    row: int
    fields: dict = field(default_factory=dict)


class Workbook:
    def __init__(self, path):
        self.path = path
        self.wf = openpyxl.load_workbook(path, data_only=False)  # formulas
        self.wv = openpyxl.load_workbook(path, data_only=True)   # cached values

    def cell(self, sheet, ref) -> Cell:
        f = self.wf[sheet][ref].value
        v = self.wv[sheet][ref].value
        formula = f if isinstance(f, str) and f.startswith("=") else None
        return Cell(v, formula)

    def sheet_inventory(self):
        out = []
        for ws in self.wf.worksheets:
            n_formula = n_num = n_text = n_err = 0
            wvs = self.wv[ws.title]
            max_col = min(ws.max_column, 70)
            for row in ws.iter_rows(max_col=max_col):
                for c in row:
                    v = c.value
                    cv = wvs[c.coordinate].value
                    if isinstance(v, str) and v.startswith("="):
                        n_formula += 1
                    elif isinstance(v, (int, float)):
                        n_num += 1
                    elif isinstance(v, str) and v.strip():
                        n_text += 1
                    if isinstance(cv, str) and cv.startswith("#"):
                        n_err += 1
            out.append(dict(sheet=ws.title, visibility=ws.sheet_state,
                            dimension=ws.dimensions, max_row=ws.max_row,
                            max_col=ws.max_column, merged_ranges=len(ws.merged_cells.ranges),
                            formulas=n_formula, numeric_constants=n_num, text_cells=n_text,
                            error_cells=n_err))
        return out

    def external_links(self):
        links = []
        for l in getattr(self.wf, "_external_links", []) or []:
            try:
                links.append(l.file_link.Target)
            except Exception:  # pragma: no cover
                pass
        return links


def refs_of(formula):
    """Yield (sheet_or_None, col_letter, row) for every cell in a formula (ranges expanded)."""
    if not formula:
        return
    body = re.sub(r'"[^"]*"', "", formula)
    for m in REF_RE.finditer(body):
        sh = m.group("sheet")
        c1, r1 = m.group("c1"), int(m.group("r1"))
        c2, r2 = m.group("c2"), m.group("r2")
        if c2:
            i1, i2 = column_index_from_string(c1), column_index_from_string(c2)
            for ci in range(min(i1, i2), max(i1, i2) + 1):
                for r in range(min(r1, int(r2)), max(r1, int(r2)) + 1):
                    yield sh, get_column_letter(ci), r
        else:
            yield sh, c1, r1


def extract(path):
    wb = Workbook(path)
    lines: list[Line] = []
    declared_totals = {}   # sheet -> dict(row, total, q)
    for cfg in SHEETS:
        lines.extend(_extract_sheet(wb, cfg, declared_totals))
    _build_hierarchy(wb, lines)
    return wb, lines, declared_totals


def _extract_sheet(wb, cfg, declared_totals):
    sh = cfg["sheet"]
    L = dict(LAYOUTS[cfg["layout"]])
    if cfg.get("ia_col"):
        L["ia"] = cfg["ia_col"]
    ws = wb.wv[sh]
    out = []
    section = None
    value_cols = [L["total"]] + L.get("q", []) + ([L["total_lak"]] if "total_lak" in L else [])
    for r in range(cfg["start"], ws.max_row + 1):
        get = lambda key: wb.cell(sh, f"{L[key]}{r}") if key in L else Cell(None, None)
        code_raw = get("code").value
        name_raw = get("name").value
        a_txt = clean_text(code_raw) or ""
        b_txt = clean_text(name_raw) or ""
        # stop at footnotes; grand-total rows become 'grand_total' records
        is_note = a_txt.startswith("ປະເພດກິດຈະກຳ") or a_txt.startswith("ຫົວໜ້າ") or b_txt.startswith("ຫົວໜ້າ")
        row_txt = " ".join(str(c.value) for c in ws[r][:20] if isinstance(c.value, str))
        if re.search(r"ວັນທີ|date\s*:", row_txt, re.IGNORECASE) and not re.match(r"^\d", a_txt):
            is_note = True  # signature / date footer
        if is_note:
            break
        is_grand = bool(STOP_PATTERNS.search(a_txt) or STOP_PATTERNS.search(b_txt))
        row_vals = [wb.cell(sh, f"{c}{r}").value for c in value_cols]
        if not a_txt and not b_txt and all(v in (None, "") for v in row_vals):
            continue
        # section markers in the consolidated DCDC sheet (I./, II./ ...)
        if cfg.get("sectioned") and re.match(r"^[IVX]+\./?$", a_txt):
            label = clean_text(wb.cell(sh, f"P{r}").value) or b_txt
            section = label.replace(" Component", "").strip()
        f = {}
        f["sheet"] = sh
        f["row"] = r
        f["role"] = cfg["role"]
        f["layout"] = cfg["layout"]
        f["sheet_label"] = cfg["label"]
        f["sheet_short"] = cfg["short"]
        f["component"] = cfg["component"]
        f["modality"] = cfg["modality"]
        f["section"] = section
        f["code_raw"] = code_raw
        f["code"] = a_txt or None
        f["name"] = b_txt or None
        f["name_alt"] = clean_text(get("name_alt").value) if "name_alt" in L else None
        f["activity_type_raw"] = get("type").value if "type" in L else None
        f["activity_type"] = clean_text(f["activity_type_raw"])
        f["unit_raw"] = get("unit").value if "unit" in L else None
        f["unit"] = clean_text(f["unit_raw"])
        f["financing_modality"] = clean_text(get("fin").value) if "fin" in L else None
        f["remark"] = clean_text(get("remark").value) if "remark" in L else None
        invalid = {}

        def num(key, col=None):
            c = wb.cell(sh, f"{col or L[key]}{r}")
            v, bad = to_num(c.value)
            if bad is not None:
                invalid[key] = bad
            return v, c

        fx = cfg.get("fx")
        if "unit_cost_lak" in L:
            uc_lak, _ = num("unit_cost_lak")
            f["unit_cost_lak"] = uc_lak
            f["unit_cost"] = uc_lak / fx if uc_lak is not None else None
        else:
            f["unit_cost"], _ = num("unit_cost") if "unit_cost" in L else (None, None)
        f["qty"], _ = num("qty") if "qty" in L else (None, None)
        movs = [num(f"mov{i}", c)[0] for i, c in enumerate(L.get("mov", []))]
        f["mov"] = movs if movs else None
        f["mov_total"] = num("mov_total")[0] if "mov_total" in L else (
            sum(m or 0 for m in movs) if movs else None)
        tot_v, tot_c = num("total")
        f["total"] = tot_v
        f["total_is_formula"] = tot_c.is_formula
        f["total_formula"] = tot_c.formula
        if "total_lak" in L:
            f["total_lak"], _ = num("total_lak")
        q_cells = [wb.cell(sh, f"{c}{r}") for c in L.get("q", [])]
        qs = []
        for i, c in enumerate(q_cells):
            v, bad = to_num(c.value)
            if bad is not None:
                invalid[f"Q{i+1}"] = bad
            qs.append(v)
        f["q_derived"] = False
        if not qs and movs:
            # DPF: no quarterly amounts -> allocate total by movement counts
            mt = sum(m or 0 for m in movs)
            if f["total"] and mt:
                qs = [f["total"] * (m or 0) / mt for m in movs]
                f["q_derived"] = True
            else:
                qs = [None] * 4
        f["q"] = qs or [None] * 4
        f["q_formula"] = [c.is_formula for c in q_cells] if q_cells else [False] * 4
        # implementing agency
        if "ia_levels" in L:
            ia, lvl = None, None
            for level, col in L["ia_levels"].items():
                v = clean_text(wb.cell(sh, f"{col}{r}").value)
                if v:
                    ia, lvl = v, level
                    break
            f["ia_raw"] = ia
            f["ia_level_col"] = lvl
        else:
            raw = wb.cell(sh, f"{L['ia']}{r}").value if "ia" in L else None
            f["ia_raw"] = raw
            f["ia_level_col"] = None
        f["ia"] = clean_text(f["ia_raw"])
        f["invalid"] = invalid
        f["text_flags"] = {k: text_flags(f[k + "_raw"]) for k in ("activity_type", "unit", "ia")
                           if text_flags(f.get(k + "_raw"))}
        f["value_cols"] = value_cols
        f["error_cells"] = [f"{c}{r}" for c in value_cols + [L.get("unit_cost", "A")]
                            if isinstance(wb.cell(sh, f"{c}{r}").value, str)
                            and str(wb.cell(sh, f"{c}{r}").value).startswith("#")]
        f["is_grand"] = is_grand
        if is_grand and f["total"] is not None:
            declared_totals.setdefault(sh, dict(row=r, total=f["total"], q=list(f["q"])))
        out.append(Line(uid=f"{cfg['short']}#{r}", sheet=sh, row=r, fields=f))
    return out


def _collect_child_rows(wb, sheet, row, start_cells, value_cols, seen=None, depth=0):
    """Other-row references reachable from a row's value cells (follows same-row refs)."""
    children, xsheet = set(), set()
    seen = seen or set()
    for col in start_cells:
        key = (col, row)
        if key in seen or depth > 6:
            continue
        seen.add(key)
        c = wb.cell(sheet, f"{col}{row}")
        for sh, cl, rr in refs_of(c.formula):
            if sh:
                xsheet.add(sh.strip("'"))
                continue
            if rr == row:
                if cl in value_cols:
                    ch, xs = _collect_child_rows(wb, sheet, row, [cl], value_cols, seen, depth + 1)
                    children |= ch
                    xsheet |= xs
            elif cl in value_cols:
                children.add(rr)
    return children, xsheet


NUMCODE = re.compile(r"^\d+(\.\d+)*$")


def norm_code(c):
    """'6.2.1.0' -> '6.2.1' so DPF-style codes compare like the others."""
    if not c or not NUMCODE.match(c):
        return c
    while c.endswith(".0") and c.count(".") > 0:
        c = c[:-2]
    return c


def _is_descendant(parent_code, child_code):
    """False when both codes are numeric and the child is NOT below the parent."""
    if not parent_code or not child_code:
        return True
    if not (NUMCODE.match(parent_code) and NUMCODE.match(child_code)):
        return True
    return norm_code(child_code).startswith(norm_code(parent_code) + ".")


def _is_sibling(a, b):
    if not a or not b or not (NUMCODE.match(a) and NUMCODE.match(b)):
        return False
    a, b = norm_code(a), norm_code(b)
    return a.count(".") == b.count(".") and a != b and a.rsplit(".", 1)[0] == b.rsplit(".", 1)[0]


def _build_hierarchy(wb, lines):
    by_sheet = {}
    for ln in lines:
        by_sheet.setdefault(ln.sheet, []).append(ln)
    for sheet, rows in by_sheet.items():
        idx = {ln.row: ln for ln in rows}
        for ln in rows:
            f = ln.fields
            ch, xs = _collect_child_rows(wb, sheet, ln.row, [f["value_cols"][0]], f["value_cols"])
            f["stray_q_refs"] = []
            if not ch and not f["total_is_formula"]:
                # total typed in -> the roll-up (if any) lives in the quarterly cells
                ch2, xs2 = _collect_child_rows(wb, sheet, ln.row, f["value_cols"][1:], f["value_cols"])
                ch |= ch2
                xs |= xs2
            elif not ch:
                ch2, _ = _collect_child_rows(wb, sheet, ln.row, f["value_cols"][1:], f["value_cols"])
                f["stray_q_refs"] = sorted(ch2)  # leftover formula in a quarter cell
            inside = sorted(r for r in ch if r in idx)
            f["linked_rows"], f["code_mismatch_children"] = [], []
            if len(inside) == 1 and _is_sibling(f["code"], idx[inside[0]].fields["code"]):
                f["linked_rows"] = inside            # value copied from a sibling line
                f["children_rows"] = []
            else:
                f["children_rows"] = inside
                f["code_mismatch_children"] = [r for r in inside
                                               if not _is_descendant(f["code"], idx[r].fields["code"])]
            f["children_outside"] = sorted(r for r in ch if r not in idx)
            f["xsheet_refs"] = sorted(xs)
            f["parent_by"] = "formula" if f["children_rows"] else None
        has_formula_parent = {c for ln in rows for c in ln.fields["children_rows"]}
        # code-hierarchy fallback for hard-coded subtotals
        ordered = sorted(rows, key=lambda x: x.row)
        for i, ln in enumerate(ordered):
            f = ln.fields
            code = f["code"]
            f["code_descendants"] = []
            if not code or not NUMCODE.match(code):
                continue
            desc = []
            for nxt in ordered[i + 1:]:
                nc = nxt.fields["code"]
                if nc and nc.startswith(code + "."):
                    desc.append(nxt.row)
                elif nc and NUMCODE.match(nc):
                    break
            f["code_descendants"] = desc
            if f["children_rows"] or not desc or not f["total"]:
                continue
            lvl = code.count(".") + 1
            cand = [k for k in desc if k not in has_formula_parent
                    and idx[k].fields["code"].count(".") == lvl]
            if not cand:
                continue
            # take children in order until they add up to the subtotal
            picked, acc = [], 0.0
            for k in cand:
                picked.append(k)
                acc += idx[k].fields["total"] or 0
                if abs(acc - f["total"]) < 0.5:
                    break
            f["children_rows"] = picked
            f["parent_by"] = "code"
        parents_of = {}
        for ln in rows:
            for c in ln.fields["children_rows"]:
                parents_of.setdefault(c, []).append(ln.row)
        for ln in rows:
            f = ln.fields
            f["parent_rows"] = parents_of.get(ln.row, [])
            has_value = any(v not in (None, 0) for v in [f["total"]] + list(f["q"]))
            if f.get("is_grand"):
                f["kind"] = "grand_total"
            elif f["children_rows"]:
                f["kind"] = "subtotal"
            elif has_value or f["unit_cost"] or f["qty"]:
                f["kind"] = "line"
            else:
                f["kind"] = "heading"
            f["empty_subtotal"] = (f["kind"] == "heading" and any(
                (idx[d].fields["total"] or 0) > 0 for d in f["code_descendants"]))
        # choose the grand root
        leaves = [ln.row for ln in rows if ln.fields["kind"] == "line"]

        def subtree(r, seen=None):
            seen = seen if seen is not None else set()
            for c in idx[r].fields["children_rows"]:
                if c not in seen:
                    seen.add(c)
                    subtree(c, seen)
            return seen
        roots = [ln.row for ln in rows if not ln.fields["parent_rows"]
                 and ln.fields["kind"] in ("subtotal", "grand_total", "line")]
        grand = []
        cands = [r for r in roots if idx[r].fields["kind"] in ("subtotal", "grand_total")]
        if cands and leaves:
            cover = {r: len(subtree(r) & set(leaves)) for r in cands}
            best = max(cands, key=lambda r: (cover[r], idx[r].fields["kind"] == "grand_total", r))
            if cover[best] >= 0.9 * len(leaves):
                grand = [best]
        grand_set = set(grand) if grand else set(roots)
        g_sub = subtree(grand[0]) if grand else set()
        g_tot = idx[grand[0]].fields["total"] if grand else None
        memo = {}

        def paths(r, stack=()):
            if r in grand_set:
                return 1
            if r in stack:
                return 0
            if r in memo:
                return memo[r]
            n = sum(paths(p, stack + (r,)) for p in idx[r].fields["parent_rows"])
            memo[r] = n
            return n
        for ln in rows:
            f = ln.fields
            f["is_grand_root"] = ln.row in grand_set
            f["rollup_paths"] = paths(ln.row)
            stray = (not f["parent_rows"] and ln.row not in grand_set and bool(grand)
                     and f["kind"] in ("subtotal", "line", "grand_total"))
            if stray and f["kind"] != "line":
                leafset = set(leaves)
                inside = (subtree(ln.row) & leafset) <= (g_sub & leafset)
                # a parallel top-level subtotal or a section check-total is harmless
                if inside and (f["kind"] == "grand_total" or
                               (g_tot is not None and abs((f["total"] or 0) - g_tot) < 1)):
                    stray = False
            f["stray_root"] = stray
            f["level"] = (f["code"].count(".") + 1) if f["code"] and NUMCODE.match(f["code"]) else None
        for ln in rows:
            d, cur, guard = 0, ln, 0
            while cur.fields["parent_rows"] and guard < 12:
                cur = idx[cur.fields["parent_rows"][0]]
                d += 1
                guard += 1
            ln.fields["depth"] = d
