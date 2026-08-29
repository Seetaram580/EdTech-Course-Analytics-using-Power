# Power BI Implementation Guide — Step by Step

This walks through building the actual `.pbix` in Power BI Desktop from the files in this repo. Since a `.pbix` can't be generated outside Power BI Desktop itself, this is the exact sequence to reproduce it.

## 1. Import the data
1. Open Power BI Desktop → **Get Data → Text/CSV**.
2. Import `data/cleaned_data.csv` (or, for the full star schema, import each table from `data/edtech.db` via **Get Data → ODBC/SQLite connector**, or simplest: run `python/build_star_schema.py` and export each SQLite table back to CSV, then import `fact_courses.csv`, `dim_category.csv`, `dim_instructor.csv`, `dim_language.csv`, `dim_level.csv`, `dim_date.csv` individually).
3. Click **Transform Data** (don't Load yet) to open Power Query Editor.

## 2. Clean data in Power Query
Even though `data_cleaning.py` already cleaned the source CSV, replicate the key transformations in Power Query so the pipeline is self-contained inside the `.pbix`:
1. On `fact_courses`: **Home → Use First Row as Headers** (if needed), set correct data types per column (Views/Enrollment → Whole Number, Ratings/Duration_Hours/Course_Price → Decimal Number, Course_Date → Date).
2. Right-click `Skills` column → **Split Column → By Delimiter → Comma → Split into Rows** to build the skill bridge table if you want per-skill DAX (see `dax_measures.md`).
3. **Remove Duplicates** on `Course_ID` (Home → Remove Rows → Remove Duplicates, after right-clicking the column).
4. **Trim/Clean** on any text column via Transform → Format → Trim / Clean, as a safety net.
5. Click **Close & Apply**.

## 3. Create relationships
1. Go to **Model view** (left rail icon).
2. Drag `Category_ID` from `dim_category` to `Category_ID` in `fact_courses` — Power BI auto-detects one-to-many, single direction. Repeat for `Instructor_ID`, `Language_ID`, `Level_ID`, `Date_ID`.
3. Confirm each relationship: double-click the line → cardinality = **One to Many**, cross-filter direction = **Single**, "Make this relationship active" checked.
4. Right-click `dim_date` → **Mark as Date Table** → choose `Course_Date` as the date column (required for the YoY DAX measure).

## 4. Create calculated columns
In `fact_courses` (Modeling tab → New Column):
```dax
Duration_Bucket =
SWITCH(
    TRUE(),
    fact_courses[Duration_Hours] < 2, "0-2 hrs",
    fact_courses[Duration_Hours] < 5, "2-5 hrs",
    fact_courses[Duration_Hours] < 10, "5-10 hrs",
    fact_courses[Duration_Hours] < 20, "10-20 hrs",
    "20+ hrs"
)
```
Used to power the duration-bucket bar chart on Page 3 without needing a measure-level `CASE` per visual.

## 5. Create DAX measures
1. Create a blank measure table: **Modeling → New Table** → type `_Measures = {BLANK()}` → Enter. Right-click the resulting column → **Hide in report view**.
2. Select `_Measures` table → **New Measure** for each formula in `documentation/dax_measures.md`. Paste the DAX exactly as given, rename to match the bold heading (e.g. `Total Courses`).
3. Repeat until all ~18 measures exist.

## 6. Create each visual
Follow the specs table-by-table in `documentation/dashboard_design.md`. General pattern per visual:
1. Insert a new page (bottom tab bar → `+`), rename to match (e.g. "Executive Overview").
2. From the **Visualizations** pane, pick the chart type listed in the spec table.
3. Drag the specified dimension field to **X-axis/Category** and the specified measure to **Y-axis/Values**.
4. Add the **Legend** field if listed.
5. Under the **Tooltip** well, add the extra fields listed in the spec (e.g. Course Count alongside Total Views).
6. Format via the paint-roller icon: enable data labels, set axis titles, apply the shared theme (Step 8).

## 7. Add slicers
1. Insert a **Slicer** visual for each field listed under each page's "Slicers" row in `dashboard_design.md` (Category, Language, Course_Level, Year, Subtitles).
2. Set slicer style to **Dropdown** for high-cardinality fields (Instructor) and **List**/**Buttons** for low-cardinality fields (Course_Level, Subtitles).
3. Use **Sync Slicers** (View → Sync Slicers) to make Category/Language/Year apply across all 4 pages consistently.

## 8. Format the dashboard
1. **View → Themes → Browse for themes** → import a custom `.json` theme (primary `#2E5EAA`, accent `#E8A33D`) for consistent colors across all visuals.
2. Set canvas size: **Format page → Canvas settings → 1920×1080 (16:9)**.
3. Add a consistent header rectangle + title text box at the top of each page; add page-navigation buttons (Insert → Buttons → Blank, with **Action → Page navigation** set) in the top-right corner of every page.
4. Turn off default visual borders/shadows for a cleaner enterprise look; enable **subtle shadow** only on KPI cards.

## 9. Publish the dashboard
1. **Home → Publish** → sign in with a Power BI (Microsoft) account → choose a workspace (e.g. "My Workspace" or a dedicated "Portfolio Projects" workspace).
2. Once published, open the report in the Power BI Service → **File → Embed report** or **Share** to generate a shareable/public link (Publish to Web, if you want it fully public for a portfolio site — note this makes the data public, so only do this with the synthetic/public dataset, not real proprietary data).
3. Optionally schedule a **Scheduled Refresh** if the underlying CSV/DB is hosted somewhere refreshable (e.g. OneDrive, a database) rather than a static local file.
4. Add the published link + a screenshot/GIF to your portfolio README and resume.
