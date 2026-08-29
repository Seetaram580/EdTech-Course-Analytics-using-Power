# EdTech Course Analytics using Power BI

## Objective
Analyze EdTech course data to identify demand patterns, learner preferences, instructor performance, skill relevance, and growth opportunities.

## Tech Stack
- Python
- Pandas
- NumPy
- SQL
- Power BI
- DAX

## Project Pipeline
Raw CSV → Python Cleaning → Cleaned Dataset → SQL Analysis → Power BI Data Model → DAX → Dashboard → Insights

## Files
- `data/raw_data.csv` — intentionally contains a few missing values and duplicate records for cleaning practice.
- `data/cleaned_data.csv` — cleaned analysis-ready dataset.
- `data/fact_courses.csv` — fact table for a star-schema version.
- `data/dim_course.csv` — course dimension.
- `data/dim_instructor.csv` — instructor dimension.
- `python/data_cleaning.py` — reproducible Pandas cleaning workflow.
- `sql/analysis_queries.sql` — business analysis queries.
- `powerbi/DAX_Measures.txt` — DAX measures.
- `documentation/PowerBI_Implementation_Guide.md` — dashboard build instructions.

## Dataset
The dataset contains 1,200 generated course records before cleaning, plus a few intentionally duplicated/missing records. The final cleaned file contains one row per Course_ID.

## Interview-ready summary
"I built an EdTech analytics project using Python, SQL and Power BI. I cleaned and standardized course-level data, modeled it for reporting, created DAX measures for KPIs and rankings, and designed a dashboard covering category demand, language preferences, instructor performance, course duration, skill diversity and learner engagement. I then used the analysis to identify high-demand and potential growth areas."

## Important
This is a synthetic portfolio dataset. It is designed to demonstrate the workflow and analytical methods rather than represent a real company's proprietary data.
