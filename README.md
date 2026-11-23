# AOP 2027 data-quality & analysis tool

Reads the HANSA II AOP workbook in `data/` **read-only**, standardises every budget sheet into one table, checks data quality, flags outliers, and builds an interactive dashboard plus Excel/CSV exports.

## Live dashboard (Streamlit)

```
pip install -r requirements.txt
streamlit run streamlit_app.py        # or double-click run_dashboard.bat
```

This opens http://localhost:8501.

**Language and look**

* **Language:** switch between ລາວ and English with the control at the top of the sidebar. Lao is the default. Filters and selections are kept when you switch.
* **What is translated:** menus, KPIs, chart titles, check names and explanations, activity categories, plan names and agency names.
* **What stays as typed:** values from the workbook (activity names, codes). The generated issue *detail* text is technical and stays in English.
* **UI mode:** the **Default / Crystal** switch at the top right toggles between the light mint theme and a dark emerald glass theme. Each mode has its own colour-blind-checked chart palette; filters and language are kept when you switch.
* **Styling:** the look is a green "mint glass" theme. It is set in `.streamlit/config.toml` and the CSS block at the top of `streamlit_app.py`. All interface text lives in `aop_tool/i18n.py`.

**Features**

* **Choosing a workbook:** pick any workbook in `data/` or upload one. Uploads are copied to a temp folder, never into `data/`.
* **Re-analysis:** results are cached for each file version. Saving the workbook triggers re-analysis on the next interaction. Switch on **Watch file for changes** to refresh automatically (checks every 5 s).
* **Filtering:** sidebar filters apply across tabs, and clicking a bar in *Budget by plan* filters to that plan.
* **Drill-down:** selecting a row in any line, issue or outlier table opens its full details: fields, Excel location, issues and outlier flags.
* **Exports:** the *Export* tab provides the three Excel workbooks, CSVs (all or filtered), JSON, and the standalone offline HTML dashboard.
* **Sharing on the office network:** `streamlit run streamlit_app.py --server.address 0.0.0.0`, then colleagues open `http://<this-pc>:8501`.

## Batch run (no server)

```
python run_aop_analysis.py                          # newest data/AOP*.xlsx
python run_aop_analysis.py "data/AOP2027(V4).xlsx"  # a specific version
```

Or double-click `run_analysis.bat`. Requires Python 3.10+ with `openpyxl`. The run takes about 3 seconds.

Then open `output/AOP2027_dashboard.html` in a browser. It works offline; only the Lao web font needs internet.

## Outputs (`output/`)

| File | Contents |
|---|---|
| `AOP2027_dashboard.html` | Overview KPIs, data quality, outliers, exploration, searchable line table, dataset structure, CSV downloads |
| `AOP2027_cleaned_dataset.xlsx` | Counted budget lines in one standard schema; all parsed rows with exclusion reasons; value mappings |
| `AOP2027_data_quality_report.xlsx` | Sheet scorecard, issue log (sheet, Excel row, values compared), check catalogue, summary-sheet and version reconciliation, exchange rates, external links |
| `AOP2027_analysis_results.xlsx` | Budget by plan, component, modality, category, agency and level; Pareto; outliers; unit-cost benchmarks; data profile |
| `csv/` | The same tables as UTF-8 CSV files |

## How the workbook is interpreted

* **Sheet roles** (`aop_tool/extract.py`, `SHEETS`).
  * *primary*: counted.
  * *alternate*: the English copy of IBF1.
  * *superseded*: hidden older versions.
  * *summary* and *reference*: not counted.
  * The NCLE and DCDC sections of `B_DCDC _IBF_QPS` repeat stand-alone sheets. They are compared with those sheets but not counted twice.
* **Layouts.** Six column layouts are mapped to one schema (`LAYOUTS`). The Dataset structure tab shows where each field was read from.
* **Lines vs subtotals** come from each sheet's own formulas (a formula reference graph). The same graph finds lines that are double-counted, left out of the total, or copied from a sibling line. Where subtotals are typed in, the activity-code hierarchy is used instead.
* **Currency.** `2.1_PBC_DPF` is in LAK and is converted at that sheet's own rate (22,500). Its quarterly amounts are allocated from the activity counts.
* **Outliers.** Tukey fences (1.5×IQR) on log10 values plus a MAD robust z-score above 3.5. Unit costs are compared only within the same activity category.

To support a new sheet or a changed layout, edit `SHEETS` / `LAYOUTS` in `aop_tool/extract.py`. To add spellings, edit the maps in `aop_tool/normalize.py`.
