# Interview prep notes

## 30 sec version
"I built an end-to-end analytics project on an EdTech course catalog — around 850 courses, 8 categories, 9 languages. Cleaned the raw data in Python, modeled it into a star schema, wrote SQL for 18 business questions, then built a 4-page Power BI dashboard with DAX. The interesting finding was that duration and skill count basically don't affect views at all, but subtitles give a real ~10% views bump and ~22% enrollment bump — which actually changes what I'd recommend investing in."

## 1 min version
"Goal was to figure out what actually drives engagement on a course catalog, not just build a dashboard that looks nice. Started with a raw dataset that I deliberately made messy — duplicate rows, inconsistent category casing, mixed date formats, the kind of stuff you'd genuinely run into with a real export — and wrote a Pandas pipeline to clean it: standardized categories and languages, cleaned up instructor names, imputed missing ratings using category medians instead of just a global average, flagged outliers with IQR instead of just deleting them.

Then I modeled it as a star schema — fact table of courses, dimension tables for category, instructor, language, level, date — and validated the model by actually running 18 SQL queries against it, things like top instructors by views, category-wise ratings, and a query specifically designed to find categories with high demand but low course count.

In Power BI I built out DAX measures — the usual KPIs plus some RANKX-based leaderboards and a couple of share-of-total percentage measures — across 4 pages: overview, instructor analytics, course/engagement analytics, and a growth-opportunities page. The finding I'd lead with in an interview is that duration and skill count have almost zero correlation with views, while subtitles do noticeably help — that's the kind of thing that changes an actual content decision instead of just being a chart."

## Problem statement
EdTech platforms have huge catalogs but often don't have a structured way to know what's actually working — which categories, instructors, or course attributes drive engagement — so content decisions end up being gut calls instead of data-driven ones.

## Dataset
Synthetic, 850 courses after cleaning, across 8 categories / 34 subcategories, 9 languages, 500+ instructors, spanning Jan 2023 to Jan 2026. Built it with intentional messiness (dupes, casing issues, missing values, mixed date formats) so the cleaning step would be real work and not just for show. If asked, I'd mention it's synthetic and that a real Udemy/Coursera Kaggle dataset would drop into the same pipeline with minor column tweaks.

## Data cleaning
Removed duplicates at both the row level and Course_ID level, standardized text casing on categories/subcategories/instructors, mapped language variants to one canonical spelling, coerced Views out of comma-formatted and "k"-suffixed strings into clean integers, imputed missing ratings using the category median (not the overall median, since ratings differ meaningfully by category), defaulted ambiguous subtitle values to "No" as the conservative choice, parsed four different date formats down to ISO, and flagged (not deleted) outliers in views/duration using IQR.

## Data modeling
Star schema — one fact table (fact_courses, grain = 1 row per course) with FKs to category, instructor, language, level, and date dimensions. All one-to-many, single-direction filtering. Went with this over a flat table mainly for cleaner DAX filter context (RANKX/ALL() behave predictably) and because it's just how a real data warehouse would be set up.

## DAX
About 18 measures — core KPIs, some DIVIDE-safe ratios, share-of-total measures using ALL() to reset the denominator, a couple of TOPN-based "top instructor/category" text measures, RANKX leaderboards with dense ranking, and a YoY growth measure using SAMEPERIODLASTYEAR against a proper date table.

## Dashboard
4 pages — Overview, Instructor Analytics, Course & Engagement Analytics, and Market/Growth Opportunities. Kept the last page deliberately action-oriented rather than just more charts — it's meant to answer "where should we build next" directly.

## Key insights
IT & Software leads on both volume and engagement per course. Development and Marketing look under-supplied relative to how well they perform. Duration and skill count don't correlate with views at all. Subtitles give a real engagement lift. A small set of instructors account for a disproportionate share of total views. (Full writeup in business_insights.md.)

## Business impact
Basically reframes where content investment should go — instead of assuming "longer courses" or "more skills covered" helps, the data points at subtitles and specific under-supplied categories as the higher-leverage, cheaper moves. That's a recommendation someone could actually act on, not just a dashboard to look at.

## Challenges & how I solved them
- Skills column was comma-separated text, which makes per-skill ranking annoying in both SQL and DAX. Solved it with a recursive CTE in SQL to split it out, and documented the Power Query "split by delimiter into rows" approach for building a proper skill bridge table in Power BI.
- Raw dates came in four different formats. Wrote a small parser that tries each known format in order and falls back to a dayfirst guess, then checked afterward that nothing got silently dropped that shouldn't have been.
- Deciding what actually counts as a "growth opportunity" instead of just eyeballing a chart and calling it — ended up defining it as below-median course count + above-average views, which is something I could write as an actual query and defend, not just a vibe.
