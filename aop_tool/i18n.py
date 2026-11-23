"""
Lao / English interface text for the AOP 2027 dashboard.

Data values typed in the workbook (activity names, codes, remarks) are shown
as they are. Generated issue *detail* messages are technical and stay in English.
"""

LANGS = {"lo": "ລາວ", "en": "English"}

UI = {
    # ---- app / sidebar
    "app_title": ("AOP 2027 · Data quality & budget analysis", "AOP 2027 · ຄຸນນະພາບຂໍ້ມູນ ແລະ ການວິເຄາະງົບປະມານ"),
    "app_sub": ("Annual Operational Plan of the HANSA II project: checks data quality, flags outliers and explores the 2027 budget.",
                "ແຜນປະຕິບັດງານປະຈຳປີ ຂອງໂຄງການ HANSA II: ກວດຄຸນນະພາບຂໍ້ມູນ, ຊອກຄ່າຜິດປົກກະຕິ ແລະ ວິເຄາະງົບປະມານປີ 2027."),
    "lang": ("Language", "ພາສາ"),
    "busy": ("Calculating…", "ກຳລັງຄຳນວນ…"),
    "sb_head": ("Data & analysis", "ຂໍ້ມູນ ແລະ ການວິເຄາະ"),
    "sb_workbook": ("Workbook", "ໄຟລ໌ຂໍ້ມູນ"),
    "sb_live": ("Live update", "ອັບເດດອັດຕະໂນມັດ"),
    "sb_filters": ("Filters", "ຕົວກອງ"),
    "src_folder": ("From data folder", "ຈາກໂຟນເດີ data"),
    "src_upload": ("Upload a file", "ອັບໂຫຼດໄຟລ໌"),
    "pick_wb": ("Workbook in ./data", "ໄຟລ໌ໃນ ./data"),
    "upload_wb": ("AOP workbook (.xlsx)", "ໄຟລ໌ AOP (.xlsx)"),
    "no_xlsx": ("No .xlsx file in ./data", "ບໍ່ພົບໄຟລ໌ .xlsx ໃນ ./data"),
    "choose_wb": ("Choose or upload an AOP workbook in the sidebar to start.", "ກະລຸນາເລືອກ ຫຼື ອັບໂຫຼດໄຟລ໌ AOP ໃນແຖບຂ້າງ ເພື່ອເລີ່ມ."),
    "reanalyse": ("Re-analyse now", "ວິເຄາະຄືນໃໝ່"),
    "reanalyse_help": ("Clear the cache and read the workbook again", "ລ້າງຂໍ້ມູນທີ່ເກັບໄວ້ ແລະ ອ່ານໄຟລ໌ໃໝ່"),
    "watch": ("Watch file for changes", "ຕິດຕາມການປ່ຽນແປງຂອງໄຟລ໌"),
    "watch_help": ("Checks every 5 s and re-analyses automatically when the workbook is saved",
                   "ກວດທຸກ 5 ວິນາທີ ແລະ ວິເຄາະຄືນອັດຕະໂນມັດ ເມື່ອໄຟລ໌ຖືກບັນທຶກ"),
    "watching": ("watching · checked", "ກຳລັງຕິດຕາມ · ກວດເມື່ອ"),
    "changed": ("Workbook changed – re-analysing…", "ໄຟລ໌ມີການປ່ຽນແປງ – ກຳລັງວິເຄາະຄືນ…"),
    "analysing": ("Analysing {f} (read-only)…", "ກຳລັງວິເຄາະ {f} (ອ່ານຢ່າງດຽວ)…"),
    "status": ("Saved {m} · analysed {a} in {s} s", "ບັນທຶກ {m} · ວິເຄາະ {a} ໃຊ້ເວລາ {s} ວິນາທີ"),
    "f_sheet": ("Plan / sheet", "ແຜນ / ແຜ່ນງານ"),
    "f_comp": ("Component", "ອົງປະກອບ"),
    "f_cat": ("Activity category", "ປະເພດກິດຈະກຳ"),
    "f_level": ("Implementation level", "ຂັ້ນຈັດຕັ້ງປະຕິບັດ"),
    "f_qual": ("Quality", "ຄຸນນະພາບ"),
    "f_q": ("Search", "ຄົ້ນຫາ"),
    "f_q_ph": ("code, name, agency…", "ລະຫັດ, ຊື່, ພາກສ່ວນ…"),
    "all_plans": ("All counted plans", "ທຸກແຜນທີ່ນັບ"),
    "all_comp": ("All components", "ທຸກອົງປະກອບ"),
    "all_cat": ("All categories", "ທຸກປະເພດ"),
    "all_level": ("All levels", "ທຸກຂັ້ນ"),
    "q_all": ("All lines", "ທຸກລາຍການ"),
    "q_issues": ("With material issues", "ມີບັນຫາສຳຄັນ"),
    "q_clean": ("Without material issues", "ບໍ່ມີບັນຫາສຳຄັນ"),
    "q_outlier": ("Flagged as outlier", "ຖືກໝາຍເປັນຄ່າຜິດປົກກະຕິ"),
    "reset": ("Reset filters", "ລ້າງຕົວກອງ"),
    "lines_total": ("{n} lines · {v}", "{n} ລາຍການ · {v}"),
    # ---- steps (main tabs)
    "t_overview": ("Overview", "ພາບລວມ"),
    "t_quality": ("Data quality", "ຄຸນນະພາບຂໍ້ມູນ"),
    "t_outliers": ("Outliers", "ຄ່າຜິດປົກກະຕິ"),
    "t_explore": ("Explore", "ສຳຫຼວດຂໍ້ມູນ"),
    "t_table": ("Data table", "ຕາຕະລາງຂໍ້ມູນ"),
    "t_structure": ("Dataset structure", "ໂຄງສ້າງຂໍ້ມູນ"),
    "t_export": ("Export", "ດາວໂຫຼດ"),
    # ---- overview
    "ov_title": ("Budget overview", "ພາບລວມງົບປະມານ"),
    "ov_desc": ("Counted 2027 budget lines after removing subtotals, language copies, hidden older versions and repeated sections.",
                "ລາຍການງົບປະມານປີ 2027 ທີ່ນັບ ຫຼັງຈາກຕັດຍອດຍ່ອຍ, ສະບັບແປພາສາ, ສະບັບເກົ່າທີ່ເຊື່ອງໄວ້ ແລະ ພາກສ່ວນທີ່ຊ້ຳກັນອອກ."),
    "k_budget": ("Counted 2027 budget", "ງົບປະມານປີ 2027 ທີ່ນັບ"),
    "k_budget_sel": ("Selected 2027 budget", "ງົບປະມານປີ 2027 ທີ່ເລືອກ"),
    "k_budget_help": ("Budget lines only, each counted once: excludes subtotals, the English copy, hidden older versions and the B_DCDC sections that repeat stand-alone sheets.",
                      "ນັບສະເພາະລາຍການງົບປະມານ ເທື່ອລະຄັ້ງ: ບໍ່ລວມຍອດຍ່ອຍ, ສະບັບພາສາອັງກິດ, ສະບັບເກົ່າທີ່ເຊື່ອງໄວ້ ແລະ ພາກສ່ວນໃນ B_DCDC ທີ່ຊ້ຳກັບແຜ່ນງານສະເພາະ."),
    "k_lines": ("Budget lines", "ລາຍການງົບປະມານ"),
    "k_lines_d": ("of {n} parsed rows", "ຈາກ {n} ແຖວທີ່ອ່ານ"),
    "k_plans": ("Plans", "ແຜນ"),
    "k_plans_d": ("of {n} sheets", "ຈາກ {n} ແຜ່ນງານ"),
    "k_clean": ("Without material issues", "ບໍ່ມີບັນຫາສຳຄັນ"),
    "k_clean_d": ("{c} of {n} lines", "{c} ຈາກ {n} ລາຍການ"),
    "k_crit": ("Critical + high findings", "ບັນຫາຮ້າຍແຮງ + ສູງ"),
    "k_crit_d": ("on these lines", "ໃນລາຍການເຫຼົ່ານີ້"),
    "k_dup": ("Possible double budgeting", "ງົບປະມານທີ່ອາດຊ້ຳກັນ"),
    "k_dup_d": ("{g} groups of lines in 2+ plans", "{g} ກຸ່ມລາຍການ ທີ່ຢູ່ໃນ 2 ແຜນຂຶ້ນໄປ"),
    "view_all": ("View all ›", "ເບິ່ງທັງໝົດ ›"),
    "dlg_crit": ("Critical & high findings", "ບັນຫາລະດັບຮ້າຍແຮງ ແລະ ສູງ"),
    "dlg_crit_d": ("{n} critical/high findings on the {l} selected budget lines, plus {w} that concern a whole sheet or the workbook. Select a row to see the line, its Excel location and all its issues.",
                   "ບັນຫາລະດັບຮ້າຍແຮງ/ສູງ {n} ລາຍການ ໃນ {l} ລາຍການງົບປະມານທີ່ເລືອກ, ແລະ {w} ບັນຫາ ທີ່ກ່ຽວກັບທັງແຜ່ນງານ ຫຼື ທັງໄຟລ໌. ເລືອກແຖວ ເພື່ອເບິ່ງລາຍການ, ຕຳແໜ່ງໃນ Excel ແລະ ບັນຫາທັງໝົດ."),
    "dlg_on_lines": ("On selected budget lines", "ໃນລາຍການທີ່ເລືອກ"),
    "dlg_wb": ("Sheet / workbook level", "ລະດັບແຜ່ນງານ / ໄຟລ໌"),
    "dlg_dup": ("Possible double budgeting", "ງົບປະມານທີ່ອາດຊ້ຳກັນ"),
    "dlg_dup_d": ("{g} groups of budget lines appear in more than one plan. Amount at risk {v}: the extra copies if each activity should be budgeted only once. Agree with the departments which plan keeps the activity.",
                  "ມີ {g} ກຸ່ມລາຍການງົບປະມານ ທີ່ປາກົດໃນຫຼາຍກວ່າໜຶ່ງແຜນ. ຈຳນວນເງິນທີ່ອາດຊ້ຳ {v}: ສ່ວນທີ່ເກີນ ຖ້າແຕ່ລະກິດຈະກຳຄວນມີງົບປະມານພຽງບ່ອນດຽວ. ຄວນຕົກລົງກັບພາກສ່ວນກ່ຽວຂ້ອງ ວ່າແຜນໃດຈະເກັບກິດຈະກຳນີ້ໄວ້."),
    "dup_u3": ("Identical description and amount", "ຊື່ ແລະ ຈຳນວນເງິນຄືກັນ"),
    "dup_u4": ("Same amount and activity category", "ຈຳນວນເງິນ ແລະ ປະເພດກິດຈະກຳຄືກັນ"),
    "at_risk": ("at risk", "ອາດຊ້ຳ"),
    "group": ("Group", "ກຸ່ມ"),
    "no_items": ("Nothing in the current selection.", "ບໍ່ມີໃນການເລືອກປັດຈຸບັນ."),
    "dl_csv": ("Download (CSV)", "ດາວໂຫຼດ (CSV)"),
    "k_dup_help": ("Lines flagged by checks U3/U4: identical description & amount, or same large amount & category, in two counted plans.",
                   "ລາຍການທີ່ຖືກໝາຍໂດຍການກວດ U3/U4: ຊື່ ແລະ ຈຳນວນເງິນຄືກັນ ຫຼື ຈຳນວນເງິນໃຫຍ່ ແລະ ປະເພດຄືກັນ ໃນສອງແຜນ."),
    "c_plan": ("Budget by plan", "ງົບປະມານຕາມແຜນ"),
    "c_plan_d": ("Counted budget lines, USD · click a bar to filter", "ລາຍການທີ່ນັບ, ໂດລາ · ກົດທີ່ແທ່ງເພື່ອກອງ"),
    "c_quarter": ("Quarterly phasing", "ການແບ່ງງົບປະມານຕາມໄຕມາດ"),
    "c_quarter_d": ("Share of the annual budget per quarter", "ສັດສ່ວນງົບປະມານປະຈຳປີ ໃນແຕ່ລະໄຕມາດ"),
    "c_comp": ("Composition", "ໂຄງສ້າງງົບປະມານ"),
    "c_comp_d": ("By project component and implementation level", "ຕາມອົງປະກອບໂຄງການ ແລະ ຂັ້ນຈັດຕັ້ງປະຕິບັດ"),
    "c_comp_1": ("Project component", "ອົງປະກອບໂຄງການ"),
    "c_comp_2": ("Implementation level", "ຂັ້ນຈັດຕັ້ງປະຕິບັດ"),
    "c_cat": ("Budget by activity category", "ງົບປະມານຕາມປະເພດກິດຈະກຳ"),
    "c_cat_d": ("Standardised from the typed activity types", "ປັບໃຫ້ເປັນມາດຕະຖານຈາກປະເພດທີ່ພິມໃສ່"),
    "c_find": ("Key data-quality findings", "ບັນຫາຫຼັກດ້ານຄຸນນະພາບຂໍ້ມູນ"),
    "c_find_d": ("Critical & high, whole workbook (not filtered)", "ລະດັບຮ້າຍແຮງ ແລະ ສູງ, ທັງໄຟລ໌ (ບໍ່ຂຶ້ນກັບຕົວກອງ)"),
    "lines_word": ("lines", "ລາຍການ"),
    # ---- quality
    "dq_title": ("Data-quality assessment", "ການປະເມີນຄຸນນະພາບຂໍ້ມູນ"),
    "dq_desc": ("{n} findings from {c} automated checks across 8 dimensions · {p}% of counted lines have no Critical/High/Medium issue.",
                "{n} ບັນຫາ ຈາກການກວດອັດຕະໂນມັດ {c} ແບບ ໃນ 8 ດ້ານ · {p}% ຂອງລາຍການທີ່ນັບ ບໍ່ມີບັນຫາລະດັບຮ້າຍແຮງ/ສູງ/ປານກາງ."),
    "dq_heat": ("Issues by sheet and dimension", "ບັນຫາຕາມແຜ່ນງານ ແລະ ດ້ານ"),
    "dq_heat_d": ("Number of findings", "ຈຳນວນບັນຫາ"),
    "dq_checks": ("Most frequent checks", "ການກວດທີ່ພົບເລື້ອຍທີ່ສຸດ"),
    "dq_log": ("Issue log", "ບັນທຶກບັນຫາ"),
    "dq_log_d": ("Every finding with its sheet, Excel row and the values compared · select a row for details",
                 "ທຸກບັນຫາ ພ້ອມແຜ່ນງານ, ແຖວ Excel ແລະ ຄ່າທີ່ປຽບທຽບ · ເລືອກແຖວເພື່ອເບິ່ງລາຍລະອຽດ"),
    "severity": ("Severity", "ລະດັບ"),
    "dimension": ("Dimension", "ດ້ານ"),
    "sheet": ("Sheet", "ແຜ່ນງານ"),
    "check": ("Check", "ການກວດ"),
    "scope": ("Scope", "ຂອບເຂດ"),
    "sc_all": ("All sheets & roles", "ທຸກແຜ່ນງານ"),
    "sc_counted": ("Counted lines + workbook-level", "ລາຍການທີ່ນັບ + ລະດັບໄຟລ໌"),
    "sc_primary": ("Primary sheets only", "ສະເພາະແຜ່ນງານຫຼັກ"),
    "search_detail": ("Search in detail", "ຄົ້ນຫາໃນລາຍລະອຽດ"),
    "all": ("All", "ທັງໝົດ"),
    "shown": ("{n} findings shown", "ສະແດງ {n} ບັນຫາ"),
    "dl_issues": ("Filtered issues (CSV)", "ບັນຫາທີ່ກອງ (CSV)"),
    "recon": ("Reconciliation", "ການກວດທຽບຍອດ"),
    "recon_d": ("Do totals, summaries and versions of the same plan agree?", "ຍອດລວມ, ແຜ່ນສັງລວມ ແລະ ສະບັບຕ່າງໆຂອງແຜນດຽວກັນ ກົງກັນບໍ?"),
    "scorecard": ("Sheet scorecard", "ຜົນການປະເມີນແຕ່ລະແຜ່ນງານ"),
    "scorecard_d": ("Sheet total vs sum of budget lines; clean = no Critical/High/Medium issue",
                    "ຍອດລວມແຜ່ນງານ ທຽບກັບຜົນບວກລາຍການ; ລາຍການສະອາດ = ບໍ່ມີບັນຫາຮ້າຍແຮງ/ສູງ/ປານກາງ"),
    "summ": ("Summary sheets vs detail", "ແຜ່ນສັງລວມ ທຽບກັບລາຍລະອຽດ"),
    "vers": ("Versions & duplicates of the same plan", "ສະບັບ ແລະ ສຳເນົາຂອງແຜນດຽວກັນ"),
    "vers_d": ("Line-by-line by activity code", "ທຽບເທື່ອລະລາຍການ ຕາມລະຫັດກິດຈະກຳ"),
    "comparison": ("Comparison", "ການປຽບທຽບ"),
    "diff_only": ("Differences only", "ສະເພາະທີ່ຕ່າງກັນ"),
    "no_diff": ("No differences – the versions agree.", "ບໍ່ມີຄວາມແຕກຕ່າງ – ທຸກສະບັບກົງກັນ."),
    "about_check": ("What this check means", "ຄວາມໝາຍຂອງການກວດນີ້"),
    # ---- outliers
    "ol_title": ("Outlier detection", "ການກວດຫາຄ່າຜິດປົກກະຕິ"),
    "ol_desc": ("Amounts are strongly right-skewed, so tests run on a log₁₀ scale. Unit costs are compared only with lines of the same activity category (Tukey fences 1.5×IQR + robust z-score on the MAD, |z| > 3.5); line totals across all counted lines. A flag means “check this”, not “wrong”.",
                "ຈຳນວນເງິນມີການກະຈາຍອຽງຂວາຫຼາຍ ຈຶ່ງທົດສອບໃນມາດຕາສ່ວນ log₁₀. ລາຄາຕໍ່ຫົວໜ່ວຍ ທຽບສະເພາະກັບລາຍການປະເພດກິດຈະກຳດຽວກັນ (ເກນ Tukey 1.5×IQR + ຄ່າ z ແບບທົນທານ ຈາກ MAD, |z| > 3.5); ຍອດລວມລາຍການ ທຽບກັບທຸກລາຍການທີ່ນັບ. ການໝາຍ ໝາຍເຖິງ “ຄວນກວດເບິ່ງ” ບໍ່ແມ່ນ “ຜິດ”."),
    "ol_strip": ("Unit cost by activity category", "ລາຄາຕໍ່ຫົວໜ່ວຍ ຕາມປະເພດກິດຈະກຳ"),
    "ol_strip_d": ("Each dot = budget line · band = normal range · | = median", "ແຕ່ລະຈຸດ = ລາຍການ · ແຖບ = ຂອບເຂດປົກກະຕິ · | = ຄ່າກາງ"),
    "within": ("Within range", "ຢູ່ໃນຂອບເຂດ"),
    "outlier": ("Outlier", "ຄ່າຜິດປົກກະຕິ"),
    "ol_hist": ("Distribution of line totals", "ການກະຈາຍຂອງຍອດລວມລາຍການ"),
    "ol_hist_d": ("Log scale · dashed = outlier fences", "ມາດຕາສ່ວນ log · ເສັ້ນປະ = ເກນຄ່າຜິດປົກກະຕິ"),
    "lower_fence": ("lower fence", "ເກນຕ່ຳ"),
    "upper_fence": ("upper fence", "ເກນສູງ"),
    "ol_bench": ("Unit-cost benchmarks", "ມາດຕະຖານລາຄາຕໍ່ຫົວໜ່ວຍ"),
    "ol_bench_d": ("Per activity category, USD", "ຕາມປະເພດກິດຈະກຳ, ໂດລາ"),
    "ol_flag": ("Flagged lines", "ລາຍການທີ່ຖືກໝາຍ"),
    "ol_flag_d": ("Respects the sidebar filters · select a row for details", "ຂຶ້ນກັບຕົວກອງ · ເລືອກແຖວເພື່ອເບິ່ງລາຍລະອຽດ"),
    "test": ("Test", "ການທົດສອບ"),
    "no_uc": ("No unit costs in this selection.", "ບໍ່ມີລາຄາຕໍ່ຫົວໜ່ວຍ ໃນການເລືອກນີ້."),
    "dl_out": ("Outliers (CSV)", "ຄ່າຜິດປົກກະຕິ (CSV)"),
    "m_uc": ("Unit cost (USD)", "ລາຄາຕໍ່ຫົວໜ່ວຍ (ໂດລາ)"),
    "m_tot": ("Line total (USD)", "ຍອດລວມລາຍການ (ໂດລາ)"),
    "m_phase": ("Quarterly phasing", "ການແບ່ງຕາມໄຕມາດ"),
    # ---- explore
    "ex_title": ("Exploratory analysis", "ການວິເຄາະສຳຫຼວດຂໍ້ມູນ"),
    "ex_desc": ("Concentration, distribution, phasing and who implements the budget.", "ຄວາມເຂັ້ມຂຸ້ນ, ການກະຈາຍ, ການແບ່ງໄຕມາດ ແລະ ພາກສ່ວນຈັດຕັ້ງປະຕິບັດ."),
    "ex_pareto": ("Budget concentration", "ຄວາມເຂັ້ມຂຸ້ນຂອງງົບປະມານ"),
    "ex_pareto_d": ("Top 10 lines hold {p}% of {v}", "10 ລາຍການໃຫຍ່ສຸດ ກວມ {p}% ຂອງ {v}"),
    "ex_pareto_x": ("lines, largest first", "ລາຍການ, ຈາກໃຫຍ່ຫານ້ອຍ"),
    "ex_80": ("{k} lines = 80%", "{k} ລາຍການ = 80%"),
    "ex_bands": ("Line size distribution", "ການກະຈາຍຕາມຂະໜາດລາຍການ"),
    "ex_bands_d": ("Number of lines per size band", "ຈຳນວນລາຍການ ໃນແຕ່ລະຂະໜາດ"),
    "ex_catq": ("Phasing by activity category", "ການແບ່ງໄຕມາດ ຕາມປະເພດກິດຈະກຳ"),
    "ex_catq_d": ("Share of each category's budget per quarter", "ສັດສ່ວນງົບປະມານແຕ່ລະປະເພດ ໃນແຕ່ລະໄຕມາດ"),
    "ex_ag": ("Top implementing agencies", "ພາກສ່ວນຈັດຕັ້ງປະຕິບັດ ທີ່ມີງົບປະມານຫຼາຍສຸດ"),
    "ex_ag_d": ("Standardised agency names, USD", "ຊື່ພາກສ່ວນທີ່ປັບເປັນມາດຕະຖານ, ໂດລາ"),
    "ex_pivot": ("Breakdown table", "ຕາຕະລາງແຍກລາຍລະອຽດ"),
    "group_by": ("Group by", "ຈັດກຸ່ມຕາມ"),
    "dl_pivot": ("Breakdown (CSV)", "ຕາຕະລາງແຍກ (CSV)"),
    "g_plan": ("Plan / department", "ແຜນ / ກົມ"),
    "g_cat": ("Activity category", "ປະເພດກິດຈະກຳ"),
    "g_ag": ("Implementing agency", "ພາກສ່ວນຈັດຕັ້ງປະຕິບັດ"),
    "g_level": ("Implementation level", "ຂັ້ນຈັດຕັ້ງປະຕິບັດ"),
    "g_mod": ("Financing modality", "ຮູບແບບການເງິນ"),
    "g_comp": ("Component", "ອົງປະກອບ"),
    "g_unit": ("Unit", "ຫົວໜ່ວຍ"),
    # ---- table
    "tb_title": ("Budget lines", "ລາຍການງົບປະມານ"),
    "tb_desc": ("Searchable line-level data · select a row for all fields, issues and the original Excel location",
                "ຂໍ້ມູນລະດັບລາຍການ · ເລືອກແຖວເພື່ອເບິ່ງທຸກຊ່ອງ, ບັນຫາ ແລະ ຕຳແໜ່ງໃນ Excel"),
    "rows": ("Rows", "ແຖວ"),
    "r_counted": ("Counted budget lines", "ລາຍການທີ່ນັບ"),
    "r_all": ("All parsed rows", "ທຸກແຖວທີ່ອ່ານ"),
    "r_excl": ("Excluded rows only", "ສະເພາະແຖວທີ່ບໍ່ນັບ"),
    "tb_count": ("{n} rows · {v} counted", "{n} ແຖວ · ນັບ {v}"),
    "select_hint": ("Select a row to see all fields, its issues and outlier flags.", "ເລືອກແຖວ ເພື່ອເບິ່ງທຸກຊ່ອງ, ບັນຫາ ແລະ ການໝາຍຄ່າຜິດປົກກະຕິ."),
    "dl_rows": ("Filtered rows (CSV)", "ແຖວທີ່ກອງ (CSV)"),
    # ---- structure
    "st_title": ("Dataset structure", "ໂຄງສ້າງຊຸດຂໍ້ມູນ"),
    "st_desc": ("{f} holds {s} sheets ({h} hidden). Budget sheets use {l} column layouts in Lao, English or both. Parsed {p} rows; {c} lines are counted once. Lines vs subtotals are identified from each sheet's own formulas.",
                "{f} ມີ {s} ແຜ່ນງານ (ເຊື່ອງໄວ້ {h}). ແຜ່ນງົບປະມານໃຊ້ຮູບແບບຖັນ {l} ແບບ ເປັນພາສາລາວ, ອັງກິດ ຫຼື ທັງສອງ. ອ່ານໄດ້ {p} ແຖວ; ນັບ {c} ລາຍການ ເທື່ອລະຄັ້ງ. ແຍກລາຍການ ແລະ ຍອດຍ່ອຍ ຈາກສູດຂອງແຕ່ລະແຜ່ນງານເອງ."),
    "st_inv": ("Sheet inventory", "ລາຍການແຜ່ນງານ"),
    "st_schema": ("Standard schema & completeness", "ໂຄງສ້າງມາດຕະຖານ ແລະ ຄວາມຄົບຖ້ວນ"),
    "st_stats": ("Summary statistics", "ສະຖິຕິສະຫຼຸບ"),
    "st_fx": ("Exchange rates found", "ອັດຕາແລກປ່ຽນທີ່ພົບ"),
    "st_links": ("{n} external-link records stored in the workbook", "ໄຟລ໌ເກັບການເຊື່ອມໂຍງພາຍນອກ {n} ລາຍການ"),
    "st_map": ("Column mapping per sheet", "ການຈັບຄູ່ຖັນ ຂອງແຕ່ລະແຜ່ນງານ"),
    "st_cat": ("Check catalogue", "ລາຍການການກວດທັງໝົດ"),
    # ---- export
    "xp_title": ("Download results", "ດາວໂຫຼດຜົນການວິເຄາະ"),
    "xp_desc": ("CSV files are UTF-8 with BOM so Lao text opens correctly in Excel. ‘Filtered’ respects the sidebar filters.",
                "ໄຟລ໌ CSV ເປັນ UTF-8 (BOM) ເພື່ອໃຫ້ພາສາລາວເປີດໃນ Excel ໄດ້ຖືກຕ້ອງ. ‘ທີ່ກອງ’ ຂຶ້ນກັບຕົວກອງໃນແຖບຂ້າງ."),
    "xp_clean": ("Cleaned dataset", "ຊຸດຂໍ້ມູນທີ່ປັບປຸງແລ້ວ"),
    "xp_clean_d": ("Counted budget lines in one standard schema, raw and standardised values side by side; all parsed rows; mappings.",
                   "ລາຍການທີ່ນັບ ໃນໂຄງສ້າງມາດຕະຖານດຽວ, ມີຄ່າເດີມ ແລະ ຄ່າທີ່ປັບແລ້ວ; ທຸກແຖວທີ່ອ່ານ; ຕາຕະລາງຈັບຄູ່."),
    "xp_q": ("Data-quality report", "ລາຍງານຄຸນນະພາບຂໍ້ມູນ"),
    "xp_q_d": ("{n} findings, sheet scorecard, check catalogue, summary-sheet & version reconciliation, FX, links.",
               "{n} ບັນຫາ, ຜົນປະເມີນແຕ່ລະແຜ່ນ, ລາຍການການກວດ, ການທຽບແຜ່ນສັງລວມ ແລະ ສະບັບ, ອັດຕາແລກປ່ຽນ, ການເຊື່ອມໂຍງ."),
    "xp_a": ("Analysis results", "ຜົນການວິເຄາະ"),
    "xp_a_d": ("Budget by plan, component, modality, category, agency and level; Pareto; outliers; benchmarks; profile.",
               "ງົບປະມານຕາມແຜນ, ອົງປະກອບ, ຮູບແບບການເງິນ, ປະເພດ, ພາກສ່ວນ ແລະ ຂັ້ນ; Pareto; ຄ່າຜິດປົກກະຕິ; ມາດຕະຖານ; ໂປຣໄຟລ໌."),
    "xp_rows": ("All parsed rows", "ທຸກແຖວທີ່ອ່ານ"),
    "xp_rows_d": ("Every row from every budget sheet incl. subtotals, copies and hidden versions, with exclusion reason.",
                  "ທຸກແຖວຈາກທຸກແຜ່ນງົບປະມານ ລວມທັງຍອດຍ່ອຍ, ສຳເນົາ ແລະ ສະບັບທີ່ເຊື່ອງ ພ້ອມເຫດຜົນທີ່ບໍ່ນັບ."),
    "xp_html": ("Offline dashboard", "ແຜງຄວບຄຸມອອບລາຍ"),
    "xp_html_d": ("Single-file HTML snapshot (English) – opens in any browser, no Python needed.",
                  "ໄຟລ໌ HTML ດຽວ (ພາສາອັງກິດ) – ເປີດໃນເບຣົາເຊີໃດກໍໄດ້ ບໍ່ຕ້ອງມີ Python."),
    "xp_json": ("Everything as JSON", "ທັງໝົດເປັນ JSON"),
    "xp_json_d": ("Records, issues, outliers, reconciliation and profile for other tools.", "ຂໍ້ມູນ, ບັນຫາ, ຄ່າຜິດປົກກະຕິ, ການທຽບຍອດ ແລະ ໂປຣໄຟລ໌ ສຳລັບເຄື່ອງມືອື່ນ."),
    "b_excel": ("Excel workbook", "ໄຟລ໌ Excel"),
    "b_counted": ("Counted lines (CSV)", "ລາຍການທີ່ນັບ (CSV)"),
    "b_filtered": ("Filtered lines (CSV)", "ລາຍການທີ່ກອງ (CSV)"),
    "b_issues": ("Issues (CSV)", "ບັນຫາ (CSV)"),
    # ---- detail card
    "d_counted": ("counted", "ນັບ"),
    "d_notcounted": ("not counted", "ບໍ່ນັບ"),
    "d_row": ("Excel row", "ແຖວ Excel"),
    "d_plan": ("Plan", "ແຜນ"),
    "d_cat": ("Category", "ປະເພດ"),
    "d_typed": ("Type as typed", "ປະເພດທີ່ພິມ"),
    "d_unit": ("Unit", "ຫົວໜ່ວຍ"),
    "d_uc": ("Unit cost", "ລາຄາຕໍ່ຫົວໜ່ວຍ"),
    "d_qty": ("Quantity", "ຈຳນວນ"),
    "d_mov": ("Activities Q1–Q4", "ຈຳນວນກິດຈະກຳ Q1–Q4"),
    "d_bud": ("Budget Q1–Q4", "ງົບປະມານ Q1–Q4"),
    "d_total": ("Annual total", "ຍອດລວມປະຈຳປີ"),
    "d_formula": ("Formula", "ສູດ"),
    "d_typed_val": ("typed value", "ຄ່າທີ່ພິມໃສ່"),
    "d_agency": ("Agency", "ພາກສ່ວນ"),
    "d_level": ("Level", "ຂັ້ນ"),
    "d_issues": ("Issues", "ບັນຫາ"),
    "d_noissue": ("No issues found.", "ບໍ່ພົບບັນຫາ."),
    "d_outlier": ("Outlier", "ຄ່າຜິດປົກກະຕິ"),
    "d_value": ("value", "ຄ່າ"),
    "d_peer": ("peer median", "ຄ່າກາງຂອງກຸ່ມ"),
    # ---- column labels
    "col_plan": ("Plan", "ແຜນ"),
    "col_row": ("Row", "ແຖວ"),
    "col_code": ("Code", "ລະຫັດ"),
    "col_activity": ("Activity", "ກິດຈະກຳ"),
    "col_cat": ("Category", "ປະເພດ"),
    "col_uc": ("Unit cost", "ລາຄາ/ຫົວໜ່ວຍ"),
    "col_qty": ("Qty", "ຈຳນວນ"),
    "col_total": ("Total USD", "ລວມ (ໂດລາ)"),
    "col_agency": ("Agency", "ພາກສ່ວນ"),
    "col_worst": ("Worst issue", "ບັນຫາສູງສຸດ"),
    "col_issues": ("Issues", "ບັນຫາ"),
    "col_kind": ("Row type", "ປະເພດແຖວ"),
    "col_excl": ("Exclusion reason", "ເຫດຜົນທີ່ບໍ່ນັບ"),
    "col_desc": ("Description", "ຄຳອະທິບາຍ"),
    "col_detail": ("Detail (EN)", "ລາຍລະອຽດ (EN)"),
    "col_sheet": ("Sheet", "ແຜ່ນງານ"),
    "col_role": ("Role", "ບົດບາດ"),
    "col_lines": ("Lines", "ລາຍການ"),
    "col_sheet_total": ("Sheet total", "ຍອດລວມແຜ່ນ"),
    "col_sum_lines": ("Σ lines", "Σ ລາຍການ"),
    "col_diff": ("Difference", "ສ່ວນຕ່າງ"),
    "col_counted": ("Counted", "ທີ່ນັບ"),
    "col_clean": ("Clean lines", "ລາຍການສະອາດ"),
    "col_summary": ("Summary", "ສັງລວມ"),
    "col_detail_v": ("Detail", "ລາຍລະອຽດ"),
    "col_item": ("Item", "ລາຍການ"),
    "col_compared": ("Compared with", "ທຽບກັບ"),
    "col_status": ("Status", "ສະຖານະ"),
    "col_value": ("Value", "ຄ່າ"),
    "col_peer": ("Peer median", "ຄ່າກາງຂອງກຸ່ມ"),
    "col_z": ("Robust z", "ຄ່າ z"),
    "col_dir": ("Direction", "ທິດທາງ"),
    "col_group": ("Peer group", "ກຸ່ມທຽບ"),
    "col_method": ("Method", "ວິທີ"),
    "col_test": ("Test", "ການທົດສອບ"),
    "col_share": ("Share", "ສັດສ່ວນ"),
    "col_mat": ("Lines w/ material issues", "ລາຍການມີບັນຫາສຳຄັນ"),
    "col_field": ("Field", "ຊ່ອງຂໍ້ມູນ"),
    "col_type": ("Type", "ປະເພດ"),
    "col_complete": ("Complete", "ຄົບຖ້ວນ"),
    "col_missing": ("Missing", "ຂາດ"),
    "col_unique": ("Distinct", "ຄ່າບໍ່ຊ້ຳ"),
    "col_top": ("Most frequent", "ພົບເລື້ອຍສຸດ"),
    "col_content": ("Content", "ເນື້ອໃນ"),
    "col_visible": ("Visibility", "ການສະແດງ"),
    "col_layout": ("Layout", "ຮູບແບບ"),
    "col_used": ("Used range", "ຂອບເຂດທີ່ໃຊ້"),
    "col_formulas": ("Formulas", "ສູດ"),
    "col_parsed": ("Rows parsed", "ແຖວທີ່ອ່ານ"),
    "col_sub": ("Subtotals", "ຍອດຍ່ອຍ"),
    "col_counted_usd": ("Counted USD", "ທີ່ນັບ (ໂດລາ)"),
    "col_findings": ("Findings", "ຈຳນວນບັນຫາ"),
    "col_expl": ("Explanation", "ຄຳອະທິບາຍ"),
    "col_title": ("Check", "ການກວດ"),
    "hv_lines": ("lines", "ລາຍການ"),
    "hv_findings": ("findings", "ບັນຫາ"),
    "hv_unit_cost": ("Unit cost", "ລາຄາຕໍ່ຫົວໜ່ວຍ"),
    "hv_of_year": ("of the year", "ຂອງປີ"),
}

SEVERITY = {"Critical": ("Critical", "ຮ້າຍແຮງ"), "High": ("High", "ສູງ"), "Medium": ("Medium", "ປານກາງ"),
            "Low": ("Low", "ຕ່ຳ"), "Info": ("Info", "ຂໍ້ມູນ")}

DIMENSION = {"Reconciliation": ("Reconciliation", "ການທຽບຍອດ"), "Structure": ("Structure", "ໂຄງສ້າງ"),
             "Arithmetic": ("Arithmetic", "ການຄິດໄລ່"), "Completeness": ("Completeness", "ຄວາມຄົບຖ້ວນ"),
             "Validity": ("Validity", "ຄວາມຖືກຕ້ອງ"), "Consistency": ("Consistency", "ຄວາມສອດຄ່ອງ"),
             "Uniqueness": ("Uniqueness", "ຄວາມບໍ່ຊ້ຳ"), "Integrity": ("Integrity", "ຄວາມໝັ້ນຄົງໄຟລ໌")}

LEVEL = {"Central": "ສູນກາງ", "Province": "ແຂວງ", "District": "ເມືອງ", "Civil society": "ອົງການສັງຄົມ",
         "Multiple": "ຫຼາຍພາກສ່ວນ", "(blank)": "(ຫວ່າງ)"}

COMPONENT = {"Component 1": "ອົງປະກອບ 1", "Component 2": "ອົງປະກອບ 2", "Component 3": "ອົງປະກອບ 3"}

ROLE = {"primary": "ຫຼັກ", "alternate": "ສະບັບແປ", "superseded": "ສະບັບເກົ່າ", "summary": "ສັງລວມ", "reference": "ອ້າງອີງ"}

CATEGORY = {
    "Meeting / workshop": "ກອງປະຊຸມ / ສຳມະນາ", "Training": "ການຝຶກອົບຮົມ",
    "Monitoring & supervision": "ການຕິດຕາມຊຸກຍູ້", "Administration & operating costs": "ຄ່າບໍລິຫານ ແລະ ດຳເນີນງານ",
    "Field implementation": "ການຈັດຕັ້ງປະຕິບັດພາກສະໜາມ", "Procurement (goods)": "ການຈັດຊື້ (ສິນຄ້າ)",
    "Contracting / technical assistance": "ການຈັດຈ້າງ / ວິຊາການ", "Systems & tools development": "ພັດທະນາລະບົບ ແລະ ເຄື່ອງມື",
    "Personnel / salaries": "ບຸກຄະລາກອນ / ເງິນເດືອນ", "Incentives & subsidies": "ເງິນຈູງໃຈ ແລະ ເງິນອຸດໜູນ",
    "Patient support": "ຊ່ວຍເຫຼືອຄົນເຈັບ", "Performance payments (QPS)": "ຈ່າຍຕາມຜົນງານ (QPS)",
    "Assessment & evaluation": "ການປະເມີນ", "Audit & inspection": "ການກວດສອບ ແລະ ກວດກາ",
    "Printing / IEC": "ການພິມ / ເຜີຍແຜ່", "Data collection": "ການເກັບກຳຂໍ້ມູນ",
    "Transfers to sub-national level": "ໂອນເງິນໃຫ້ຂັ້ນທ້ອງຖິ່ນ", "Unclassified": "ບໍ່ໄດ້ຈັດປະເພດ",
}

PLAN = {
    "Com1_QPS_AOP2027_DHR(V2)": "QPS – ກົມປິ່ນປົວ ແລະ ຟື້ນຟູໜ້າທີ່ການ (DHR)",
    "1_QPS_DHR": "QPS – ກົມປິ່ນປົວ (ສະບັບເກົ່າ)",
    "A_QPS_DHHP": "QPS – ກົມອະນາໄມ ແລະ ສົ່ງເສີມສຸຂະພາບ (DHHP) ແລະ ສູນຕ່າງໆ",
    "B_DCDC _IBF_QPS": "HIV / TB / NCLE / DCDC ລວມ (ກົມຄວບຄຸມພະຍາດຕິດຕໍ່)",
    "2.1_PBC_DPF": "PBC1 – ກົມແຜນການ ແລະ ການເງິນ (DPF)",
    "2.2_PBC2_DHP": "PBC2 – ກົມຈັດຕັ້ງ ແລະ ພະນັກງານ",
    "2.3.1_IBF1_DCDC Lao 2027": "IBF1 – ກົມຄວບຄຸມພະຍາດຕິດຕໍ່ (DCDC)",
    "IBF1 (DCD) ENG 2027": "IBF1 – DCDC (ສະບັບພາສາອັງກິດ)",
    "2.3.2_NCLE": "IBF1 – ສູນວິເຄາະ ແລະ ລະບາດວິທະຍາ (NCLE)",
    "2.4_IBF2_FDD_V2": "IBF2 – ກົມອາຫານ ແລະ ຢາ (FDD)",
    "2.5 IBF3_DPF_E": "IBF3 – ຂໍ້ມູນຂ່າວສານສຸຂະພາບ / DHIS2 (DPF)",
    "2.5_IBF3_DHIS2_L": "IBF3 – DHIS2 (ຮ່າງເກົ່າ)",
    "2.6_IOR_CN": "IOR – ສູນໂພຊະນາການ (CN)",
    "2.11 IBF4_NHIB 2027": "IBF4 – ຫ້ອງການປະກັນສຸຂະພາບແຫ່ງຊາດ (NHIB)",
    "3.4 ESF ": "ESF – ກອບສິ່ງແວດລ້ອມ ແລະ ສັງຄົມ (NPCO)",
    "3.6 GESI(V2)": "GESI – ຄວາມສະເໝີພາບຍິງຊາຍ ແລະ ການມີສ່ວນຮ່ວມ",
    "3.6_GESI": "GESI (ສະບັບເກົ່າ)",
    "3.1.3.1-DOI_V2": "DOI – ການກວດສອບພາຍໃນ (ກົມກວດກາ)",
}

AGENCY = {
    "NCLE (Lab & Epidemiology Centre)": "ສູນວິເຄາະ ແລະ ລະບາດວິທະຍາ (NCLE)",
    "DCDC (Communicable Disease Control)": "ກົມຄວບຄຸມພະຍາດຕິດຕໍ່ (DCDC)",
    "CHAS (HIV/AIDS & STI Centre)": "ສູນຕ້ານເອດ ແລະ ພຕພ (CHAS)",
    "NTC (National TB Centre)": "ສູນຄວບຄຸມວັນນະໂລກ (NTC)",
    "NHIB (Health Insurance Bureau)": "ຫ້ອງການປະກັນສຸຂະພາບແຫ່ງຊາດ (NHIB)",
    "DHR (Healthcare & Rehabilitation)": "ກົມປິ່ນປົວ ແລະ ຟື້ນຟູໜ້າທີ່ການ (DHR)",
    "DHHP (Hygiene & Health Promotion)": "ກົມອະນາໄມ ແລະ ສົ່ງເສີມສຸຂະພາບ (DHHP)",
    "Cabinet (MoH)": "ຫ້ອງການກະຊວງ",
    "DO (Organisation & Personnel)": "ກົມຈັດຕັ້ງ ແລະ ພະນັກງານ (DO)",
    "DIO (Inspection)": "ກົມກວດກາ (DIO)",
    "MCHC (Mother & Child Health Centre)": "ສູນສຸຂະພາບແມ່ ແລະ ເດັກ (MCHC)",
    "CHIS (Health Statistics & Information)": "ສູນສະຖິຕິ ແລະ ຂ່າວສານສາທາລະນະສຸກ",
    "CN (Centre of Nutrition)": "ສູນໂພຊະນາການ (CN)",
    "FDD (Food & Drug Department)": "ກົມອາຫານ ແລະ ຢາ (FDD)",
    "DPF (Planning & Finance)": "ກົມແຜນການ ແລະ ການເງິນ (DPF)",
    "MPSC (Medical Products Supply Centre)": "ສູນສະໜອງຜະລິດຕະພັນການແພດ (MPSC)",
    "NPCO (Project Coordination Office)": "ຫ້ອງການປະສານງານໂຄງການ (NPCO)",
    "Consultant firm / DPF": "ບໍລິສັດທີ່ປຶກສາ / ກົມແຜນການ",
    "PHO (Provincial Health Office)": "ພະແນກສາທາລະນະສຸກແຂວງ (PHO)",
    "DHO (District Health Office)": "ຫ້ອງການສາທາລະນະສຸກເມືອງ (DHO)",
    "DHO / Health centres": "ຫ້ອງການສາທາລະນະສຸກເມືອງ / ສຸກສາລາ",
}

CHECK = {
    "R1": ("ຍອດລວມແຜ່ນງານ ບໍ່ກົງກັບຜົນບວກລາຍການງົບປະມານ", "ຍອດລວມທີ່ສະແດງໃນແຜ່ນງານ ບໍ່ເທົ່າກັບຜົນບວກຂອງແຕ່ລະລາຍການ."),
    "R2": ("ແຜ່ນສັງລວມ ບໍ່ກົງກັບແຜ່ນລາຍລະອຽດ", "ຕົວເລກສັງລວມ ບໍ່ກົງກັບລາຍລະອຽດທີ່ມັນສັງລວມ."),
    "R3": ("ສະບັບລາວ ແລະ ອັງກິດ ຂອງແຜນດຽວກັນ ບໍ່ກົງກັນ", "ສະບັບພາສາລາວ ແລະ ອັງກິດ ຂອງແຜນດຽວກັນ ມີຈຳນວນເງິນຕ່າງກັນ."),
    "R4": ("ພາກສ່ວນໃນແຜ່ນລວມ ບໍ່ກົງກັບແຜ່ນງານສະເພາະ", "ແຜນຂອງພາກສ່ວນດຽວກັນປາກົດສອງບ່ອນ ດ້ວຍຈຳນວນເງິນຕ່າງກັນ."),
    "S1": ("ລາຍການຖືກນັບໃນຫຼາຍກວ່າໜຶ່ງຍອດຍ່ອຍ", "ຈຳນວນເງິນຂອງລາຍການຖືກດຶງເຂົ້າສອງຍອດຍ່ອຍ ເຮັດໃຫ້ຍອດຍ່ອຍສູງເກີນ."),
    "S2": ("ລາຍການບໍ່ໄດ້ຖືກລວມເຂົ້າຍອດລວມແຜ່ນງານ", "ບໍ່ມີສູດຍອດຍ່ອຍໃດດຶງລາຍການນີ້ ຈຶ່ງຂາດຈາກຍອດລວມ."),
    "S3": ("ແຖວຍອດຍ່ອຍ ບໍ່ເຊື່ອມກັບຍອດລວມ", "ແຖວຍອດຍ່ອຍ ຫຼື ແຖວກວດສອບ ບໍ່ເຊື່ອມກັບຍອດລວມ (ມັກເປັນສຳເນົາທີ່ວາງຜິດບ່ອນ)."),
    "S4": ("ຈຳນວນເງິນສຳເນົາຈາກລາຍການອື່ນດ້ວຍສູດ", "ຄ່າຂອງລາຍການເປັນສູດທີ່ຊີ້ໄປຫາລາຍການຂ້າງຄຽງ – ໃຫ້ຢືນຢັນວ່າເປັນກິດຈະກຳແຍກຕ່າງຫາກ."),
    "S5": ("ລະຫັດລາຍການຍ່ອຍ ບໍ່ຢູ່ພາຍໃຕ້ລະຫັດຍອດຍ່ອຍ", "ສູດຍອດຍ່ອຍ ລວມເອົາລາຍການທີ່ລະຫັດຢູ່ໃນກິ່ງອື່ນ."),
    "S6": ("ແຖວຍອດຍ່ອຍຫວ່າງເປົ່າ", "ແຖວມີກິດຈະກຳຍ່ອຍທີ່ມີງົບປະມານ ແຕ່ສະແດງ 0 ຫຼື ຫວ່າງ."),
    "S7": ("ຍອດຍ່ອຍພິມໃສ່ດ້ວຍມື ແທນການຄິດໄລ່", "ຍອດຍ່ອຍເປັນຕົວເລກທີ່ພິມ ຈຶ່ງບໍ່ປ່ຽນຕາມເມື່ອລາຍການປ່ຽນ."),
    "S9": ("ສູດທີ່ເຫຼືອຄ້າງ ໃນຊ່ອງໄຕມາດ", "ຊ່ອງໄຕມາດຂອງລາຍການ ອ້າງອີງແຖວອື່ນ."),
    "S10": ("ສູດຍອດລວມ ຂາດໄຕມາດ", "ສູດຍອດລວມຂອງລາຍການ ບໍ່ໄດ້ບວກທັງສີ່ໄຕມາດ."),
    "S11": ("ແຖວຍອດຍ່ອຍຊ້ຳກັນ", "ສອງແຖວ ບວກລາຍການດຽວກັນທັງໝົດ."),
    "A1": ("ການແບ່ງໄຕມາດ ບໍ່ເທົ່າກັບຍອດລວມປະຈຳປີ", "Q1+Q2+Q3+Q4 ຕ່າງຈາກຍອດລວມປະຈຳປີ."),
    "A2": ("ລາຄາຕໍ່ຫົວໜ່ວຍ × ຈຳນວນ ບໍ່ກົງກັບຍອດລວມ", "ບໍ່ມີການຄູນ ລາຄາຕໍ່ຫົວໜ່ວຍ × ຈຳນວນ (× ຄັ້ງ) ໃດ ທີ່ໄດ້ເທົ່າກັບຍອດລວມ."),
    "A3": ("ຍອດຍ່ອຍ ຕ່າງຈາກຜົນບວກຂອງລາຍການຍ່ອຍ", "ຍອດຍ່ອຍ ບໍ່ເທົ່າກັບຜົນບວກຂອງແຖວທີ່ມັນຄຸມ."),
    "A4": ("ມີງົບປະມານໃນໄຕມາດທີ່ບໍ່ມີກິດຈະກຳ (ຫຼື ກົງກັນຂ້າມ)", "ເງິນຕາມໄຕມາດ ແລະ ຈຳນວນກິດຈະກຳຕາມໄຕມາດ ບໍ່ສອດຄ່ອງກັນ."),
    "C1": ("ຂາດລະຫັດກິດຈະກຳ", "ລາຍການງົບປະມານບໍ່ມີລະຫັດກິດຈະກຳ."),
    "C2": ("ຂາດຊື່ກິດຈະກຳ", "ລາຍການງົບປະມານບໍ່ມີຄຳອະທິບາຍ."),
    "C3": ("ຂາດປະເພດກິດຈະກຳ", "ບໍ່ໄດ້ໃສ່ປະເພດກິດຈະກຳ."),
    "C4": ("ຂາດລາຄາຕໍ່ຫົວໜ່ວຍ / ຈຳນວນ / ຫົວໜ່ວຍ", "ຊ່ອງຄິດໄລ່ຄ່າໃຊ້ຈ່າຍຫວ່າງ ຈຶ່ງກວດສອບຍອດລວມບໍ່ໄດ້."),
    "C5": ("ຂາດພາກສ່ວນຈັດຕັ້ງປະຕິບັດ", "ບໍ່ໄດ້ໃສ່ພາກສ່ວນຈັດຕັ້ງປະຕິບັດ."),
    "C6": ("ລາຍການທີ່ງົບປະມານເປັນ 0 ຫຼື ຫວ່າງ", "ລາຍການມີລະຫັດ ແລະ ຊື່ ແຕ່ບໍ່ມີງົບປະມານ."),
    "V1": ("ມີຂໍ້ຄວາມໃນຊ່ອງຕົວເລກ", "ຄວນເປັນຕົວເລກ ແຕ່ພົບຂໍ້ຄວາມ."),
    "V2": ("ຄ່າຜິດພາດຂອງ Excel (#REF!, #VALUE!…)", "ສູດໃຫ້ຜົນເປັນຄ່າຜິດພາດ."),
    "V3": ("ປະເພດກິດຈະກຳ ບໍ່ຢູ່ໃນລາຍການເລືອກທາງການ", "ຄ່າບໍ່ກົງກັບແຜ່ນ Dropdownlist ຂອງໄຟລ໌ເອງ."),
    "V4": ("ຫົວໜ່ວຍວັດແທກ ບໍ່ຖືກຮູບແບບ", "ພິມຕົວເລກໃສ່ຫົວໜ່ວຍ, ໃຊ້ສະກຸນເງິນເປັນຫົວໜ່ວຍ ຫຼື ສະກົດຜິດ."),
    "V5": ("ຊ່ອງພາກສ່ວນຈັດຕັ້ງປະຕິບັດ ບໍ່ແມ່ນຊື່ພາກສ່ວນ", "ພິມໝາຍເຫດ, ປະໂຫຍກ ຫຼື ຊື່ທີ່ບໍ່ຮູ້ຈັກ ໃນຊ່ອງພາກສ່ວນ."),
    "V6": ("ຈຳນວນເງິນຕິດລົບ", "ຈຳນວນເງິນງົບປະມານ ບໍ່ຄວນຕິດລົບ."),
    "V7": ("ຮູບແບບລະຫັດກິດຈະກຳ ບໍ່ປົກກະຕິ", "ລະຫັດບໍ່ຢູ່ໃນຮູບແບບ 1.2.3."),
    "V8": ("ປະເພດກິດຈະກຳ ເປັນຊື່ແຜນງານ ຫຼື ຂໍ້ຄວາມອິດສະຫຼະ", "ເຊັ່ນ ພິມ 'GESI' ເປັນປະເພດ; ໄດ້ອະນຸມານປະເພດຈາກຊື່ກິດຈະກຳ."),
    "K2": ("ຕົວອັກສອນເຊື່ອງ / ຍະຫວ່າງເກີນ ໃນຂໍ້ຄວາມ", "ຕົວອັກສອນທີ່ເບິ່ງບໍ່ເຫັນ ຫຼື ຍະຫວ່າງເກີນ ເຮັດໃຫ້ການກອງ ແລະ ຄົ້ນຫາຜິດພາດ."),
    "K3": ("ລາຄາຕໍ່ຫົວໜ່ວຍ ບໍ່ເປັນຕົວເລກມົນ (ຄືຄິດໄລ່ກັບຄືນ)", "ມີທົດສະນິຍົມຫຼາຍ – ມັກແປງມາຈາກກີບ ຫຼື ແບ່ງສັນ."),
    "K4": ("ໃຊ້ອັດຕາແລກປ່ຽນຕ່າງກັນ ໃນແຕ່ລະແຜ່ນງານ", "ການແປງ ກີບ↔ໂດລາ ໃຊ້ອັດຕາຕ່າງກັນ ໃນແຕ່ລະແຜ່ນງານ."),
    "K5": ("ລາຍການກ່າວເຖິງປີງົບປະມານອື່ນ", "ຄຳອະທິບາຍກ່າວເຖິງປີ 2026 – ໃຫ້ຢືນຢັນວ່າເປັນງົບປະມານປີ 2027."),
    "U1": ("ລະຫັດກິດຈະກຳຊ້ຳກັນ ໃນແຜ່ນດຽວກັນ", "ສອງລາຍການໃນແຜ່ນດຽວກັນ ໃຊ້ລະຫັດດຽວກັນ."),
    "U2": ("ລາຍການງົບປະມານຊ້ຳກັນ ໃນແຜ່ນດຽວກັນ", "ຊື່, ລາຄາຕໍ່ຫົວໜ່ວຍ ແລະ ຍອດລວມຄືກັນ ປາກົດສອງເທື່ອ."),
    "U3": ("ກິດຈະກຳດຽວກັນ ມີງົບປະມານໃນສອງແຜ່ນງານ", "ຊື່ ແລະ ຈຳນວນເງິນຄືກັນ ໃນສອງແຜ່ນທີ່ນັບ – ອາດຕັ້ງງົບປະມານຊ້ຳ."),
    "U4": ("ອາດຊ້ຳກັນລະຫວ່າງແຜ່ນງານ (ຈຳນວນເງິນ ແລະ ປະເພດຄືກັນ)", "ລາຍການໃຫຍ່ ທີ່ມີຈຳນວນເງິນ ແລະ ປະເພດຄືກັນ ໃນສອງແຜ່ນ – ຄວນກວດເບິ່ງ."),
    "L1": ("ສູດອີງໃສ່ໄຟລ໌ Excel ອື່ນ", "ຄ່າມາຈາກໄຟລ໌ພາຍນອກ ອາດບໍ່ທັນສະໄໝ ຫຼື ເສຍເມື່ອຍ້າຍໄຟລ໌."),
    "L2": ("ມີການເຊື່ອມໂຍງພາຍນອກທີ່ບໍ່ໃຊ້ແລ້ວ", "ໄຟລ໌ເກັບການເຊື່ອມໂຍງໄປຫາໄຟລ໌ເກົ່າຫຼາຍໄຟລ໌."),
    "L3": ("ມີແຜ່ນງານທີ່ເຊື່ອງໄວ້", "ແຜ່ນທີ່ເຊື່ອງ ເກັບສະບັບເກົ່າ ຫຼື ແບບຟອມ; ບໍ່ນັບເຂົ້າຍອດລວມ."),
    "L4": ("ຂອບເຂດ / ຮູບແບບຂອງແຜ່ນງານ ໃຫຍ່ເກີນ", "ຮູບແບບຂະຫຍາຍໄກເກີນຂໍ້ມູນ ເຮັດໃຫ້ໄຟລ໌ຊ້າ."),
}


class Tr:
    """Translator bound to one language."""

    def __init__(self, lang: str):
        self.lang = lang if lang in LANGS else "lo"
        self.i = 1 if self.lang == "lo" else 0

    def __call__(self, key: str, **kw) -> str:
        s = UI[key][self.i] if key in UI else key
        return s.format(**kw) if kw else s

    # pandas 3 stores missing text as NaN (a float), pandas 2 as None: only translate real strings
    @staticmethod
    def _ok(v):
        return isinstance(v, str) and v != ""

    def sev(self, s):
        return SEVERITY.get(s, (s, s))[self.i] if self._ok(s) else s

    def dim(self, d):
        return DIMENSION.get(d, (d, d))[self.i] if self._ok(d) else d

    def level(self, v):
        return LEVEL.get(v, v) if self.i and self._ok(v) else v

    def comp(self, v):
        return COMPONENT.get(v, v) if self.i and self._ok(v) else v

    def role(self, v):
        return ROLE.get(v, v) if self.i and self._ok(v) else v

    def cat(self, v):
        return CATEGORY.get(v, v) if self.i and self._ok(v) else v

    def plan(self, sheet, default):
        return PLAN.get(sheet, default) if self.i else default

    def agency(self, v):
        if not self.i or not self._ok(v):
            return v
        if v in AGENCY:
            return AGENCY[v]
        if v.startswith("Multiple agencies: "):
            return "ຫຼາຍພາກສ່ວນ: " + v.split(": ", 1)[1]
        if v.startswith("PHO – "):
            return "ພະແນກສາທາລະນະສຸກແຂວງ – " + v.split("– ", 1)[1]
        return v

    def check(self, cid, en_title, en_expl):
        if self.i and cid in CHECK:
            return CHECK[cid]
        return en_title, en_expl
