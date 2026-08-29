# Power BI Dashboard Design — EdTech Course Analytics

4 pages, consistent theme (dark navy header bar, one accent color per page section, Segoe UI font), 1920×1080 canvas.

---

## PAGE 1 — Executive Overview

**Purpose:** one-glance health check of the whole course catalog.

| # | Visual | Type | X-axis | Y-axis / Values | Legend | Tooltip | Filters/Slicers | Why it's useful |
|---|--------|------|--------|------------------|--------|---------|------------------|------------------|
| 1 | KPI strip | 5× Card visuals | — | Total Courses, Total Views, Total Enrollments, Average Rating, Total Reviews | — | — | Page-level slicers below | Immediate top-line numbers for any stakeholder |
| 2 | Course distribution by category | Clustered bar chart | Category | Total Courses | — | Course Count, Category Share % | Category, Course Level | Shows catalog composition; spot thin categories |
| 3 | Views by category | Bar chart (horizontal) | Total Views | Category | — | Total Views, Views per Course | Category | Where the audience actually concentrates (vs. just course count) |
| 4 | Language preference | Donut chart | — | Total Courses (or Total Views) | Language | Language Share %, Course Count | Language | Learner-demand-by-language at a glance |
| 5 | Yearly/monthly trend | Line chart | Course_Date (Year-Month) | Total Courses / Total Views | — | Period, value, YoY Growth % | Year (slicer) | Growth trajectory and seasonality of catalog publishing |

**Slicers (top of page):** Category, Language, Course_Level, Year.

---

## PAGE 2 — Instructor Analytics

**Purpose:** who is driving engagement, and how consistently.

| # | Visual | Type | X-axis | Y-axis / Values | Legend | Tooltip | Filters/Slicers | Why it's useful |
|---|--------|------|--------|------------------|--------|---------|------------------|------------------|
| 1 | Top 10 instructors | Bar chart | Total Views | Instructor | — | Course Count, Instructor Rank | Category, Language | Identifies star performers to feature/partner with |
| 2 | Instructor ranking table | Table/Matrix | — | Instructor, Course Count, Total Views, Avg Rating, Instructor Rank | — | — | Category, Course Level | Sortable full leaderboard, not just Top 10 |
| 3 | Views by instructor (scatter) | Scatter chart | Course Count | Total Views | Instructor (as tooltip) | Avg Rating (size) | Category | Distinguishes "many small courses" vs "few blockbuster courses" instructors |
| 4 | Avg rating by instructor | Bar chart | Instructor (top 15 by views) | Average Rating | — | Total Views, Course Count | Category | Engagement (views) isn't always quality (rating) — flags mismatches |
| 5 | Course count by instructor | Column chart | Instructor (top 15) | Total Courses | — | — | Category | Volume/output view, complements views-based ranking |

**Slicers:** Category, Language, Course Level.

---

## PAGE 3 — Course & Engagement Analytics

**Purpose:** what course *attributes* actually move engagement.

| # | Visual | Type | X-axis | Y-axis / Values | Legend | Tooltip | Filters/Slicers | Why it's useful |
|---|--------|------|--------|------------------|--------|---------|------------------|------------------|
| 1 | Duration vs. views | Scatter chart | Duration_Hours | Views | Category | Course Name, Rating | Category, Course Level, exclude outlier toggle | Tests whether longer courses actually get more views (in this dataset: no strong relationship — correlation ≈ ‑0.02) |
| 2 | Skills vs. views | Bar chart (from dim_skill bridge) | Skill | Average Views | — | Course Count | Category | Surfaces which specific skills correlate with higher engagement |
| 3 | Enrollment vs. views | Scatter chart | Views | Enrollment | Category | Enrollment/Views ratio | Category | Checks if high-view courses convert to enrollments proportionally |
| 4 | Rating vs. views | Scatter chart | Ratings | Views | Category | Course Name | Category | Tests the "quality drives views" hypothesis (weak positive: ≈ +0.04) |
| 5 | Subtitle availability vs. engagement | Clustered column | Subtitles (Yes/No) | Average Views, Average Enrollment | Subtitles | — | Category, Language | Quantifies the subtitle "accessibility premium" |
| 6 | Course-level performance | Bar chart | Course_Level | Average Views, Average Rating | — | Course Count | Category | Beginner vs Advanced vs All Levels engagement comparison |

**Slicers:** Category, Course Level, Subtitles, exclude-outliers bookmark toggle.

---

## PAGE 4 — Market / Growth Opportunities

**Purpose:** where should new courses be built next.

| # | Visual | Type | X-axis | Y-axis / Values | Legend | Tooltip | Filters/Slicers | Why it's useful |
|---|--------|------|--------|------------------|--------|---------|------------------|------------------|
| 1 | High-demand / low-supply matrix | Scatter/quadrant chart | Course Count (per category) | Average Views (per category) | Category | Course Count, Avg Views | — | Quadrant with median lines identifies "high demand, low supply" = growth zone (SQL Q18 logic) |
| 2 | Popular languages | Bar chart | Language | Total Courses vs Average Views (dual) | — | Language Share % | — | Flags languages with strong per-course engagement but thin catalogs |
| 3 | High-performing skills | Bar chart | Skill | Average Views | — | Course Count | Category | Skill-level white space for new course topics |
| 4 | Emerging subcategories | Table | — | Subcategory, Course Count, Avg Views, YoY course growth | — | — | Category, Year | Subcategories growing fast but still small |
| 5 | Opportunity callout cards | Card visuals | — | Text-based takeaway (e.g. "Development: high demand, below-median supply") | — | — | — | Turns the analysis into a plain-English recommendation for stakeholders |

**Slicers:** Category, Language, Year.

---

## Formatting standards (applied to all pages)
- Theme: one imported `.json` theme file with a primary accent (`#2E5EAA`), a warning accent for "growth opportunity" highlights (`#E8A33D`), neutral greys for non-highlighted bars.
- All KPI cards: consistent font size (28pt value / 12pt label), thousands separator, no decimal on integer KPIs.
- All charts: data labels for the top 3–5 bars only (avoid clutter on 8+ category charts); axis titles present per Part 7 spec above.
- Consistent page navigation buttons (top-right) across all 4 pages.
- Tooltips use the report-page tooltip pattern (small dedicated tooltip page) for the quadrant chart on Page 4, since it needs more than one metric.
