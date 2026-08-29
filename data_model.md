# Power BI Data Model — EdTech Course Analytics

## Why a star schema (not one flat table)
The cleaned data starts as one flat table (`cleaned_data.csv`). Loading it into Power BI as-is would work for small dashboards, but it repeats Category/Instructor/Language text on every one of 850 rows, makes DAX filtering/ranking clumsier, and doesn't scale. A **star schema** — one fact table of measurable events (courses) surrounded by dimension tables of descriptive attributes — is the standard Power BI/Kimball pattern and is what `python/build_star_schema.py` and `sql/create_schema.sql` implement.

## Fact table
**`fact_courses`** — grain: **one row per course** (`Course_ID`).
Contains only foreign keys + numeric measures:
`Course_ID (PK), Course_Name, Category_ID (FK), Instructor_ID (FK), Language_ID (FK), Level_ID (FK), Date_ID (FK), Duration_Hours, Views, Ratings, Number_of_Reviews, Skills, Skill_Count, Subtitles, Course_Price, Enrollment, Views_Outlier, Duration_Outlier`

## Dimension tables

| Table | Primary Key | Description |
|---|---|---|
| `dim_category` | `Category_ID` | Category + Subcategory (combined into one dimension since each Subcategory maps to exactly one Category — a snowflake into two separate tables isn't necessary here) |
| `dim_instructor` | `Instructor_ID` | One row per unique cleaned instructor name |
| `dim_language` | `Language_ID` | One row per standardized language |
| `dim_level` | `Level_ID` | Beginner / Intermediate / Advanced / All Levels |
| `dim_date` | `Date_ID` | Standard calendar dimension (Year, Month, Month_Name, Quarter) — mark this as the model's official **Date Table** in Power BI for time intelligence |

*(A 6th table, `dim_skill_bridge`, is recommended — see the note in `dax_measures.md` — to properly model the many-to-many relationship between courses and skills, since `Skills` is stored as a comma-separated list.)*

## Relationships & cardinality

```
dim_category   (1) ────< (many) fact_courses   on Category_ID
dim_instructor (1) ────< (many) fact_courses   on Instructor_ID
dim_language   (1) ────< (many) fact_courses   on Language_ID
dim_level      (1) ────< (many) fact_courses   on Level_ID
dim_date       (1) ────< (many) fact_courses   on Date_ID
```

- All relationships are **one-to-many**, dimension → fact.
- **Cross-filter direction: Single** (dimension filters fact, not the reverse) — this is the default and correct choice for a star schema; bidirectional filtering isn't needed anywhere in this model and would risk ambiguous filter paths if added later.
- No many-to-many relationships in the core model (the Skills bridge table, if added, is the one place a many-to-many-like pattern exists, resolved via a bridge table rather than a direct M:N relationship).

## Why this matters for DAX/performance
- `RANKX`, `TOPN`, and share-of-total measures (see `dax_measures.md`) rely on `ALL()` clearing filters on a *dimension* column — this only behaves predictably in a proper star schema.
- Import-mode compression in Power BI works far better on a fact table of mostly numeric FK/measure columns than on one wide denormalized table with repeated text.
- It mirrors exactly how a real company's course-analytics data warehouse would be modeled, which is what makes this a credible portfolio piece rather than a "flat CSV in Power BI" tutorial.
