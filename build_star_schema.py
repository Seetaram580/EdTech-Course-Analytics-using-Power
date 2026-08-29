"""
build_star_schema.py
---------------------
Transforms the flat cleaned_data.csv into a star schema (1 fact table +
5 dimension tables) and loads it into a local SQLite database
(data/edtech.db) so the SQL analysis queries can be run and verified.

This mirrors exactly what the Power BI data model (Part 3) will look
like -- Power BI's "Import" mode with Star Schema is essentially this
same structure, just modeled visually in Power BI's relationship view
instead of via foreign keys in SQL.

Run:
    python build_star_schema.py
"""

import pandas as pd
import sqlite3

CLEAN_PATH = "/home/claude/EdTech-Course-Analytics/data/cleaned_data.csv"
DB_PATH = "/home/claude/EdTech-Course-Analytics/data/edtech.db"

df = pd.read_csv(CLEAN_PATH)

# ---------------------------------------------------------------------
# DIM_CATEGORY  (Category + Subcategory, since Subcategory always rolls
# up into exactly one Category in this dataset -> safe to combine into
# one dimension with a single surrogate key)
# ---------------------------------------------------------------------
dim_category = (
    df[["Category", "Subcategory"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_category.insert(0, "Category_ID", range(1, len(dim_category) + 1))

# ---------------------------------------------------------------------
# DIM_INSTRUCTOR
# ---------------------------------------------------------------------
dim_instructor = pd.DataFrame({"Instructor": df["Instructor"].drop_duplicates()}).reset_index(drop=True)
dim_instructor.insert(0, "Instructor_ID", range(1, len(dim_instructor) + 1))

# ---------------------------------------------------------------------
# DIM_LANGUAGE
# ---------------------------------------------------------------------
dim_language = pd.DataFrame({"Language": df["Language"].drop_duplicates()}).reset_index(drop=True)
dim_language.insert(0, "Language_ID", range(1, len(dim_language) + 1))

# ---------------------------------------------------------------------
# DIM_LEVEL  (Course_Level)
# ---------------------------------------------------------------------
dim_level = pd.DataFrame({"Course_Level": df["Course_Level"].drop_duplicates()}).reset_index(drop=True)
dim_level.insert(0, "Level_ID", range(1, len(dim_level) + 1))

# ---------------------------------------------------------------------
# DIM_DATE  (one row per distinct Course_Date, with year/month parts)
# ---------------------------------------------------------------------
dim_date = pd.DataFrame({"Course_Date": pd.to_datetime(df["Course_Date"]).drop_duplicates()})
dim_date = dim_date.sort_values("Course_Date").reset_index(drop=True)
dim_date.insert(0, "Date_ID", range(1, len(dim_date) + 1))
dim_date["Year"] = dim_date["Course_Date"].dt.year
dim_date["Month"] = dim_date["Course_Date"].dt.month
dim_date["Month_Name"] = dim_date["Course_Date"].dt.strftime("%b")
dim_date["Quarter"] = dim_date["Course_Date"].dt.quarter
dim_date["Course_Date"] = dim_date["Course_Date"].dt.strftime("%Y-%m-%d")

# ---------------------------------------------------------------------
# FACT_COURSES  (grain: one row per course)
# ---------------------------------------------------------------------
fact = df.merge(dim_category, on=["Category", "Subcategory"], how="left") \
         .merge(dim_instructor, on="Instructor", how="left") \
         .merge(dim_language, on="Language", how="left") \
         .merge(dim_level, on="Course_Level", how="left") \
         .merge(dim_date.rename(columns={"Course_Date": "Course_Date_str"}),
                left_on="Course_Date", right_on="Course_Date_str", how="left")

fact_courses = fact[[
    "Course_ID", "Course_Name", "Category_ID", "Instructor_ID", "Language_ID",
    "Level_ID", "Date_ID", "Duration_Hours", "Views", "Ratings",
    "Number_of_Reviews", "Skills", "Skill_Count", "Subtitles",
    "Course_Price", "Enrollment", "Views_Outlier", "Duration_Outlier",
]].copy()

# ---------------------------------------------------------------------
# Load everything into SQLite
# ---------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
fact_courses.to_sql("fact_courses", conn, if_exists="replace", index=False)
dim_category.to_sql("dim_category", conn, if_exists="replace", index=False)
dim_instructor.to_sql("dim_instructor", conn, if_exists="replace", index=False)
dim_language.to_sql("dim_language", conn, if_exists="replace", index=False)
dim_level.to_sql("dim_level", conn, if_exists="replace", index=False)
dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)

print("Star schema loaded into", DB_PATH)
for t in ["fact_courses", "dim_category", "dim_instructor", "dim_language",
          "dim_level", "dim_date"]:
    n = pd.read_sql(f"SELECT COUNT(*) AS n FROM {t}", conn).iloc[0, 0]
    print(f"  {t}: {n} rows")

conn.close()
