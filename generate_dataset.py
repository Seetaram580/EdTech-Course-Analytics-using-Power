"""
generate_dataset.py

Builds a synthetic EdTech course catalog. Threw in the usual real-world
mess on purpose -- dupes, inconsistent casing, "9.1k" style view counts,
mixed date formats -- so data_cleaning.py actually has something to do.

Run: python generate_dataset.py
Output: ../data/raw_data.csv
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_ROWS = 850  # within the requested 500-1000 range

# ---------------------------------------------------------------------
# 1. Reference / dimension-style data
# ---------------------------------------------------------------------

categories = {
    "Development": ["Web Development", "Mobile Development", "Game Development",
                     "Programming Languages", "Database Design"],
    "Business": ["Entrepreneurship", "Finance", "Sales", "Business Strategy",
                 "Project Management"],
    "IT & Software": ["Data Science", "Cloud Computing", "Cybersecurity",
                       "Network & Security", "IT Certifications"],
    "Design": ["Graphic Design", "UX/UI Design", "3D & Animation", "Design Tools"],
    "Marketing": ["Digital Marketing", "Social Media Marketing", "SEO",
                  "Content Marketing"],
    "Personal Development": ["Productivity", "Leadership", "Career Development",
                              "Personal Finance"],
    "Photography & Video": ["Photography Basics", "Video Editing", "Videography"],
    "Music": ["Instruments", "Music Production", "Music Theory"],
}

# Some categories/subcategories will be deliberately entered with messy
# casing / spacing in a fraction of rows to simulate real dirty data.
def messy_variant(text):
    variants = [text.upper(), text.lower(), f" {text} ", text.title()]
    return random.choice(variants)

languages_clean = ["English", "Hindi", "Spanish", "French", "German",
                    "Portuguese", "Mandarin", "Arabic", "Japanese"]
def messy_language(lang):
    variants = {
        "English": ["English", "english", "ENGLISH", "Eng", " English"],
        "Hindi": ["Hindi", "hindi", "HINDI", "Hin"],
        "Spanish": ["Spanish", "spanish", "Espanol", "SPANISH"],
    }
    return random.choice(variants.get(lang, [lang, lang.lower()]))

first_names = ["Aarav", "Priya", "John", "Emily", "Wei", "Fatima", "Carlos",
               "Sofia", "Liam", "Aisha", "David", "Maria", "Kenji", "Olga",
               "Ahmed", "Grace", "Noah", "Isabella", "Rahul", "Elena",
               "Michael", "Sara", "Yusuf", "Anastasia", "Daniel", "Neha",
               "Thomas", "Wanjiru", "Hiro", "Lucia"]
last_names = ["Sharma", "Smith", "Johnson", "Zhang", "Khan", "Garcia",
              "Fernandez", "Patel", "Mueller", "Kim", "Rossi", "Nguyen",
              "Brown", "Silva", "Ali", "Kumar", "Novak", "Costa", "Ito",
              "Petrov", "Diaz", "Singh", "Weber", "Chen", "Reddy"]

def messy_instructor(name):
    """Occasionally add extra whitespace / lowercase / trailing dots."""
    r = random.random()
    if r < 0.1:
        return f"  {name}  "
    if r < 0.2:
        return name.lower()
    if r < 0.25:
        return name.upper()
    if r < 0.3:
        return name + "."
    return name

skills_pool = [
    "Python", "SQL", "Excel", "Power BI", "Tableau", "Machine Learning",
    "JavaScript", "React", "Java", "C++", "AWS", "Azure", "Docker",
    "Kubernetes", "Figma", "Photoshop", "After Effects", "SEO",
    "Google Ads", "Copywriting", "Public Speaking", "Negotiation",
    "Financial Modeling", "Accounting", "Statistics", "Deep Learning",
    "Data Visualization", "Git", "Agile", "Scrum", "Cybersecurity Basics",
    "Networking", "Video Editing", "Music Theory", "Guitar", "Piano",
    "3D Modeling", "Unity", "Unreal Engine", "HTML/CSS", "Node.js",
]

course_level_pool = ["Beginner", "Intermediate", "Advanced", "All Levels"]

# ---------------------------------------------------------------------
# 2. Build rows
# ---------------------------------------------------------------------

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%Y/%m/%d"]

rows = []
course_id_counter = 10000

for i in range(N_ROWS):
    course_id_counter += 1
    course_id = f"CRS{course_id_counter}"

    cat = random.choice(list(categories.keys()))
    subcat = random.choice(categories[cat])

    # Course name built from subcategory + a template, some noise added
    templates = [
        "Complete {sub} Bootcamp",
        "{sub}: Zero to Hero",
        "Mastering {sub} in 2025",
        "{sub} for Beginners",
        "Advanced {sub} Masterclass",
        "The Ultimate {sub} Course",
        "{sub} Crash Course",
        "Practical {sub} Projects",
    ]
    course_name = random.choice(templates).format(sub=subcat)

    lang_clean = random.choice(languages_clean)
    language = messy_language(lang_clean) if random.random() < 0.35 else lang_clean

    instructor_clean = f"{random.choice(first_names)} {random.choice(last_names)}"
    instructor = messy_instructor(instructor_clean)

    duration = round(np.random.gamma(shape=3.0, scale=2.0) + 0.5, 1)  # hours
    duration = min(duration, 80.0)

    # Views influenced loosely by category popularity + duration (slight
    # negative relationship at extremes) + randomness, with some outliers
    base_popularity = {
        "Development": 1.4, "IT & Software": 1.3, "Business": 1.1,
        "Design": 1.0, "Marketing": 1.15, "Personal Development": 0.8,
        "Photography & Video": 0.75, "Music": 0.6,
    }[cat]
    views = int(np.random.lognormal(mean=8.3, sigma=1.1) * base_popularity)
    # inject some extreme outliers
    if random.random() < 0.01:
        views *= random.randint(15, 40)

    rating = round(np.clip(np.random.normal(4.3, 0.4), 1.0, 5.0), 1)
    reviews = int(max(0, views * np.random.uniform(0.01, 0.06)))

    n_skills = random.randint(1, 5)
    skills = ", ".join(random.sample(skills_pool, n_skills))

    subtitles_options = ["Yes", "No", "yes", "no", "Y", "N", "", None]
    subtitles = random.choices(
        subtitles_options, weights=[35, 30, 10, 8, 5, 5, 5, 2], k=1
    )[0]

    level = random.choice(course_level_pool)

    price = round(random.choice([0, 0, 9.99, 12.99, 19.99, 24.99, 34.99,
                                  49.99, 59.99, 79.99, 99.99]), 2)

    enrollment = int(views * np.random.uniform(0.05, 0.25))

    course_date = random_date(datetime(2023, 1, 1), datetime(2026, 1, 31))
    course_date_str = course_date.strftime(random.choice(date_formats))

    # Randomly blank out category/subcategory casing consistency
    cat_field = messy_variant(cat) if random.random() < 0.25 else cat
    subcat_field = messy_variant(subcat) if random.random() < 0.25 else subcat

    rows.append({
        "Course_ID": course_id,
        "Course_Name": course_name,
        "Category": cat_field,
        "Subcategory": subcat_field,
        "Language": language,
        "Instructor": instructor,
        "Duration_Hours": duration,
        "Views": views,
        "Ratings": rating,
        "Number_of_Reviews": reviews,
        "Skills": skills,
        "Subtitles": subtitles,
        "Course_Level": level,
        "Course_Price": price,
        "Enrollment": enrollment,
        "Course_Date": course_date_str,
    })

df = pd.DataFrame(rows)

# ---------------------------------------------------------------------
# 3. Inject additional realistic dirtiness
# ---------------------------------------------------------------------

# Duplicate rows (~2%)
dup_frac = 0.02
dup_rows = df.sample(frac=dup_frac, random_state=SEED)
df = pd.concat([df, dup_rows], ignore_index=True)

# Missing values scattered across a few columns (~3-5%)
for col, frac in [("Ratings", 0.04), ("Number_of_Reviews", 0.03),
                   ("Language", 0.02), ("Subtitles", 0.05),
                   ("Course_Price", 0.02), ("Duration_Hours", 0.015)]:
    idx = df.sample(frac=frac, random_state=hash(col) % (2**32)).index
    df.loc[idx, col] = np.nan

# Some Views stored as strings with commas / "k" suffix to simulate
# scraped data inconsistency
def messy_views(v):
    if pd.isna(v):
        return v
    r = random.random()
    if r < 0.05:
        return f"{int(v):,}"
    if r < 0.08:
        return f"{v/1000:.1f}k"
    return v

df["Views"] = df["Views"].apply(messy_views)

# Shuffle rows so duplicates aren't all at the bottom
df = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

output_path = "/home/claude/EdTech-Course-Analytics/data/raw_data.csv"
df.to_csv(output_path, index=False)
print(f"Saved raw dataset: {output_path}")
print(f"Shape: {df.shape}")
print(df.head(10).to_string())
