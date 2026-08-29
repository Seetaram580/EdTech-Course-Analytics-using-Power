# DAX Measures — EdTech Course Analytics

All measures assume the star schema from Part 3:
`fact_courses` (many) → `dim_category`, `dim_instructor`, `dim_language`, `dim_level`, `dim_date` (one each).

Create a dedicated **measure table** called `_Measures` (Modeling → New Table → `_Measures = {BLANK()}`, then hide the blank column) and put every measure below into it — this is standard practice so measures aren't scattered across fact/dim tables.

---

## Core KPIs

### Total Courses
```dax
Total Courses = DISTINCTCOUNT(fact_courses[Course_ID])
```
Counts unique courses in the current filter context.
**Where used:** KPI card, Page 1 (Executive Overview).

### Total Views
```dax
Total Views = SUM(fact_courses[Views])
```
Sums raw view counts.
**Where used:** KPI card, Page 1; base measure for share-% and ranking measures.

### Total Enrollments
```dax
Total Enrollments = SUM(fact_courses[Enrollment])
```
**Where used:** KPI card, Page 1; enrollment-vs-views scatter on Page 3.

### Average Views
```dax
Average Views = AVERAGE(fact_courses[Views])
```
**Where used:** KPI card; category/language comparison bar charts.

### Average Rating
```dax
Average Rating = AVERAGE(fact_courses[Ratings])
```
**Where used:** KPI card, Page 1; category-wise rating table, Page 2 instructor cards.

### Average Course Duration
```dax
Average Course Duration = AVERAGE(fact_courses[Duration_Hours])
```
**Where used:** Page 3 duration-vs-views context card.

### Total Reviews
```dax
Total Reviews = SUM(fact_courses[Number_of_Reviews])
```
**Where used:** KPI card; supporting context for rating credibility.

### Views per Course
```dax
Views per Course = DIVIDE([Total Views], [Total Courses])
```
`DIVIDE` avoids divide-by-zero errors when a filter returns no rows.
**Where used:** Category/instructor comparison tables — normalizes for instructors/categories with different course counts.

### Enrollment per Course
```dax
Enrollment per Course = DIVIDE([Total Enrollments], [Total Courses])
```
**Where used:** Page 3, alongside Views per Course, to compare "reach" vs "conversion."

---

## Leaders / Top-N Text Measures

### Top Instructor
```dax
Top Instructor =
VAR TopRow =
    TOPN(
        1,
        VALUES(dim_instructor[Instructor]),
        CALCULATE([Total Views]), DESC
    )
RETURN
    IF(
        HASONEVALUE(dim_instructor[Instructor]),
        SELECTEDVALUE(dim_instructor[Instructor]),
        CONCATENATEX(TopRow, dim_instructor[Instructor])
    )
```
Returns the instructor with the highest Total Views in the current filter context.
**Where used:** KPI card / callout, Page 2 (Instructor Analytics).

### Top Category
```dax
Top Category =
VAR TopRow =
    TOPN(
        1,
        VALUES(dim_category[Category]),
        CALCULATE([Total Views]), DESC
    )
RETURN
    CONCATENATEX(TopRow, dim_category[Category])
```
**Where used:** KPI card / callout, Page 1 & Page 4.

---

## Share-of-Total Measures

### Language Share %
```dax
Language Share % =
DIVIDE(
    [Total Views],
    CALCULATE([Total Views], ALL(dim_language[Language]))
)
```
Removes the Language filter (`ALL`) only from the denominator, so each language's views are shown as a % of the grand total views — classic 100% stacked bar / donut pattern.
**Where used:** Page 1 language-preference donut chart; Page 4 language demand chart.

### Category Share %
```dax
Category Share % =
DIVIDE(
    [Total Courses],
    CALCULATE([Total Courses], ALL(dim_category[Category]))
)
```
**Where used:** Page 1 category-distribution chart tooltip; Page 4 supply analysis.

---

## Time Intelligence

### Year-over-Year Growth
```dax
Courses Prior Year =
CALCULATE(
    [Total Courses],
    SAMEPERIODLASTYEAR(dim_date[Course_Date])
)

YoY Growth % =
DIVIDE(
    [Total Courses] - [Courses Prior Year],
    [Courses Prior Year]
)
```
Requires `dim_date[Course_Date]` to be marked as the model's **Date table** (Modeling → Mark as Date Table) with a continuous, gap-free calendar. `SAMEPERIODLASTYEAR` needs a contiguous date range, so build a full calendar dim_date (Jan 1–Dec 31 each year) rather than only the distinct course dates, if you plan to use true time-intelligence functions in production.
**Where used:** Page 1 trend line, YoY % label.

---

## Ranking Measures

### Instructor Rank
```dax
Instructor Rank =
RANKX(
    ALL(dim_instructor[Instructor]),
    CALCULATE([Total Views]),
    ,
    DESC,
    DENSE
)
```
`ALL(dim_instructor[Instructor])` re-establishes the full instructor list as the ranking universe regardless of slicers on other columns, so rank numbers stay meaningful even when a category/language slicer is applied.
**Where used:** Page 2 instructor ranking table; Top 10 instructor bar chart (filter visual to Rank ≤ 10).

### Category Rank
```dax
Category Rank =
RANKX(
    ALL(dim_category[Category]),
    CALCULATE([Total Views]),
    ,
    DESC,
    DENSE
)
```
**Where used:** Page 1 & Page 4 category tables.

### Course Rank
```dax
Course Rank =
RANKX(
    ALL(fact_courses[Course_ID]),
    CALCULATE([Total Views]),
    ,
    DESC,
    DENSE
)
```
**Where used:** "Top Courses" table, Page 3.

### Skill Rank
*(Skills is a comma-separated text field, not its own dimension table by default. To rank skills properly, first build a bridge table — see note below — then apply the same RANKX pattern.)*
```dax
Skill Rank =
RANKX(
    ALL(dim_skill[Skill]),
    CALCULATE([Total Views]),
    ,
    DESC,
    DENSE
)
```
**Where used:** Page 3/Page 4 skill-engagement chart.

> **Note on Skills / bridge table:** `Skills` in `fact_courses` holds multiple comma-separated values per course (many-to-many between courses and skills). For accurate skill-level DAX (Skill Rank, Skills vs. Views), unpivot it in Power Query first: split the `Skills` column by delimiter into rows (Home → Split Column → By Delimiter → Rows), load the result as a new `dim_skill_bridge` table with columns `Course_ID`, `Skill`, and relate it to `fact_courses` on `Course_ID` (one-to-many) and to a distinct `dim_skill` table on `Skill`. The Python `data_cleaning.py`/`build_star_schema.py` scripts already give you `Skill_Count` for quick use, but the bridge table is what makes true per-skill DAX possible.

---

## Supporting Measures (used inside visuals but worth naming)

### Subtitle Availability Views
```dax
Views With Subtitles = CALCULATE([Total Views], fact_courses[Subtitles] = "Yes")
Views Without Subtitles = CALCULATE([Total Views], fact_courses[Subtitles] = "No")
```
**Where used:** Page 3 subtitle-impact comparison chart.

### High Engagement Flag (calculated column, not a measure)
```dax
High Engagement Course =
IF(fact_courses[Views] > AVERAGE(fact_courses[Views]), "High", "Standard")
```
Used as a categorical column for conditional formatting / a slicer on Page 3, not a measure — note it needs `AVERAGE` in a calculated-COLUMN context, so in practice compute the dataset average once as a measure (`Average Views`) and reference `[Average Views]` inside a measure-based conditional format rule instead, which is the cleaner approach in Power BI.
