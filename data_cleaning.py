"""
data_cleaning.py

Cleans raw_data.csv -> cleaned_data.csv. Kept the comments mostly on the
decisions that aren't obvious (why category median instead of overall
median, why "No" is the default for subtitles, etc) since those are the
things I'd actually get asked about later.

Run: python data_cleaning.py
"""

import pandas as pd
import numpy as np
import re

RAW_PATH = "/home/claude/EdTech-Course-Analytics/data/raw_data.csv"
CLEAN_PATH = "/home/claude/EdTech-Course-Analytics/data/cleaned_data.csv"

# load raw data
df = pd.read_csv(RAW_PATH)
print(f"Raw shape: {df.shape}")

# quick look at what's missing before touching anything
print("\nMissing values per column (before cleaning):")
print(df.isna().sum())

# Course_ID should be unique -- drop full-row dupes first, then any
# leftover duplicate Course_IDs, keeping the first one we see.
before = len(df)
df = df.drop_duplicates()
df = df.drop_duplicates(subset="Course_ID", keep="first")
print(f"\nRemoved {before - len(df)} duplicate rows.")

# categories come in as a mix of "Data Science" / "DATA SCIENCE" / " data science "
# -- trim + title-case so groupby doesn't split these into separate buckets
def clean_text_field(series):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

df["Category"] = clean_text_field(df["Category"])
df["Subcategory"] = clean_text_field(df["Subcategory"])
df["Course_Level"] = clean_text_field(df["Course_Level"])
df["Course_Name"] = df["Course_Name"].astype(str).str.strip()

# same idea for language, plus a couple of abbreviations ("Eng", "Hin") to map
language_map = {
    "eng": "English", "english": "English",
    "hin": "Hindi", "hindi": "Hindi",
    "espanol": "Spanish", "spanish": "Spanish",
    "french": "French", "german": "German",
    "portuguese": "Portuguese", "mandarin": "Mandarin",
    "arabic": "Arabic", "japanese": "Japanese",
}

def standardize_language(val):
    if pd.isna(val):
        return np.nan
    key = str(val).strip().lower()
    return language_map.get(key, key.title())

df["Language"] = df["Language"].apply(standardize_language)
# Fill missing language with the dataset mode (most common language) --
# a reasonable, defensible default for a categorical field used mainly
# for demand analysis.
df["Language"] = df["Language"].fillna(df["Language"].mode()[0])

# "carlos zhang", "CARLOS ZHANG ", "Carlos Zhang." need to collapse into
# one instructor or the ranking measures later get split across variants
def clean_instructor(name):
    name = str(name).strip()
    name = re.sub(r"\.$", "", name)          # trailing period
    name = re.sub(r"\s+", " ", name)          # collapse internal spaces
    return name.title()

df["Instructor"] = df["Instructor"].apply(clean_instructor)

# Views is a mess -- plain ints, "1,953", "9.1k". normalize all to int.
def parse_views(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip().lower().replace(",", "")
    if s.endswith("k"):
        try:
            return int(float(s[:-1]) * 1000)
        except ValueError:
            return np.nan
    try:
        return int(float(s))
    except ValueError:
        return np.nan

df["Views"] = df["Views"].apply(parse_views)
# Missing views are rare and central to the analysis -- rather than
# guessing, we drop rows with no usable view count.
df = df.dropna(subset=["Views"])
df["Views"] = df["Views"].astype(int)

df["Duration_Hours"] = pd.to_numeric(df["Duration_Hours"], errors="coerce")
df["Duration_Hours"] = df["Duration_Hours"].fillna(df["Duration_Hours"].median())
df["Duration_Hours"] = df["Duration_Hours"].round(1)

df["Ratings"] = pd.to_numeric(df["Ratings"], errors="coerce")
# Rating missing at random for ~4% of rows -- impute with the category
# median rating so we don't distort category-level rating comparisons.
df["Ratings"] = df.groupby("Category")["Ratings"].transform(
    lambda s: s.fillna(s.median())
)
df["Ratings"] = df["Ratings"].fillna(df["Ratings"].median()).round(1)
df["Ratings"] = df["Ratings"].clip(1.0, 5.0)

df["Number_of_Reviews"] = pd.to_numeric(df["Number_of_Reviews"], errors="coerce")
df["Number_of_Reviews"] = df["Number_of_Reviews"].fillna(0).astype(int)

df["Course_Price"] = pd.to_numeric(df["Course_Price"], errors="coerce")
df["Course_Price"] = df["Course_Price"].fillna(df["Course_Price"].median()).round(2)

df["Enrollment"] = pd.to_numeric(df["Enrollment"], errors="coerce").fillna(0).astype(int)

# clean up the comma-separated skills list -- "Python,  SQL ,Excel" -> "Python, SQL, Excel"
def clean_skills(val):
    if pd.isna(val):
        return ""
    parts = [p.strip() for p in str(val).split(",") if p.strip()]
    return ", ".join(parts)

df["Skills"] = df["Skills"].apply(clean_skills)
df["Skill_Count"] = df["Skills"].apply(lambda s: len(s.split(", ")) if s else 0)

# subtitles comes in as Yes/No/Y/N/blank/NaN -- collapsing to Yes/No.
# treating missing as "No" since that's the safer assumption if it's not confirmed
def clean_subtitles(val):
    if pd.isna(val):
        return "No"
    s = str(val).strip().lower()
    if s in ("yes", "y"):
        return "Yes"
    if s in ("no", "n", ""):
        return "No"
    return "No"

df["Subtitles"] = df["Subtitles"].apply(clean_subtitles)

# dates came in 4 different formats, normalizing to ISO
def parse_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(val, errors="coerce", dayfirst=True)

df["Course_Date"] = df["Course_Date"].apply(parse_date)
df = df.dropna(subset=["Course_Date"])
df["Course_Year"] = df["Course_Date"].dt.year
df["Course_Month"] = df["Course_Date"].dt.month
df["Course_Date"] = df["Course_Date"].dt.strftime("%Y-%m-%d")

# flagging outliers rather than deleting them -- want to keep the option
# to exclude them from trend charts without losing the actual records
def flag_outliers_iqr(series):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return (series < lower) | (series > upper)

df["Views_Outlier"] = flag_outliers_iqr(df["Views"])
df["Duration_Outlier"] = flag_outliers_iqr(df["Duration_Hours"])
print(f"\nViews outliers flagged: {df['Views_Outlier'].sum()}")
print(f"Duration outliers flagged: {df['Duration_Outlier'].sum()}")

# reorder columns and save
final_cols = [
    "Course_ID", "Course_Name", "Category", "Subcategory", "Language",
    "Instructor", "Duration_Hours", "Views", "Ratings", "Number_of_Reviews",
    "Skills", "Skill_Count", "Subtitles", "Course_Level", "Course_Price",
    "Enrollment", "Course_Date", "Course_Year", "Course_Month",
    "Views_Outlier", "Duration_Outlier",
]
df = df[final_cols].reset_index(drop=True)

print(f"\nCleaned shape: {df.shape}")
print("\nMissing values per column (after cleaning):")
print(df.isna().sum())

df.to_csv(CLEAN_PATH, index=False)
print(f"\nSaved cleaned dataset: {CLEAN_PATH}")
