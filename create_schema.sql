-- =====================================================================
-- create_schema.sql
-- Star-schema DDL for the EdTech Course Analytics project.
-- Grain of fact_courses: one row per course (Course_ID).
-- Compatible with SQLite / PostgreSQL / SQL Server (minor type tweaks
-- may be needed for SQL Server, e.g. VARCHAR -> NVARCHAR).
-- =====================================================================

-- ---------------------------------------------------------------------
-- DIMENSION: Category (Category + Subcategory combined; each
-- Subcategory rolls up into exactly one Category, so a single table
-- keeps the model simple without breaking normalization for BI use)
-- ---------------------------------------------------------------------
CREATE TABLE dim_category (
    Category_ID     INTEGER PRIMARY KEY,
    Category        VARCHAR(100) NOT NULL,
    Subcategory     VARCHAR(100) NOT NULL
);

-- ---------------------------------------------------------------------
-- DIMENSION: Instructor
-- ---------------------------------------------------------------------
CREATE TABLE dim_instructor (
    Instructor_ID   INTEGER PRIMARY KEY,
    Instructor      VARCHAR(150) NOT NULL
);

-- ---------------------------------------------------------------------
-- DIMENSION: Language
-- ---------------------------------------------------------------------
CREATE TABLE dim_language (
    Language_ID     INTEGER PRIMARY KEY,
    Language        VARCHAR(50) NOT NULL
);

-- ---------------------------------------------------------------------
-- DIMENSION: Course Level
-- ---------------------------------------------------------------------
CREATE TABLE dim_level (
    Level_ID        INTEGER PRIMARY KEY,
    Course_Level    VARCHAR(30) NOT NULL
);

-- ---------------------------------------------------------------------
-- DIMENSION: Date (standard BI date dimension)
-- ---------------------------------------------------------------------
CREATE TABLE dim_date (
    Date_ID         INTEGER PRIMARY KEY,
    Course_Date     DATE NOT NULL,
    Year            INTEGER NOT NULL,
    Month           INTEGER NOT NULL,
    Month_Name      VARCHAR(10) NOT NULL,
    Quarter         INTEGER NOT NULL
);

-- ---------------------------------------------------------------------
-- FACT: Courses (grain = 1 row per course)
-- ---------------------------------------------------------------------
CREATE TABLE fact_courses (
    Course_ID           VARCHAR(20) PRIMARY KEY,
    Course_Name          VARCHAR(255) NOT NULL,
    Category_ID          INTEGER REFERENCES dim_category(Category_ID),
    Instructor_ID         INTEGER REFERENCES dim_instructor(Instructor_ID),
    Language_ID           INTEGER REFERENCES dim_language(Language_ID),
    Level_ID              INTEGER REFERENCES dim_level(Level_ID),
    Date_ID                INTEGER REFERENCES dim_date(Date_ID),
    Duration_Hours        DECIMAL(5,1) NOT NULL,
    Views                  INTEGER NOT NULL,
    Ratings                 DECIMAL(2,1) NOT NULL,
    Number_of_Reviews      INTEGER NOT NULL,
    Skills                  VARCHAR(500),
    Skill_Count             INTEGER NOT NULL,
    Subtitles                VARCHAR(3) NOT NULL,   -- 'Yes' / 'No'
    Course_Price            DECIMAL(6,2) NOT NULL,
    Enrollment                INTEGER NOT NULL,
    Views_Outlier             BOOLEAN NOT NULL,
    Duration_Outlier          BOOLEAN NOT NULL
);

-- ---------------------------------------------------------------------
-- Recommended indexes (helps large-scale query performance; on a
-- ~850-row dataset these are optional but shown for completeness)
-- ---------------------------------------------------------------------
CREATE INDEX idx_fact_category   ON fact_courses(Category_ID);
CREATE INDEX idx_fact_instructor ON fact_courses(Instructor_ID);
CREATE INDEX idx_fact_language   ON fact_courses(Language_ID);
CREATE INDEX idx_fact_date       ON fact_courses(Date_ID);

-- =====================================================================
-- CARDINALITY / RELATIONSHIPS
-- dim_category   (1) ---- (many) fact_courses   [Category_ID]
-- dim_instructor (1) ---- (many) fact_courses   [Instructor_ID]
-- dim_language   (1) ---- (many) fact_courses   [Language_ID]
-- dim_level      (1) ---- (many) fact_courses   [Level_ID]
-- dim_date       (1) ---- (many) fact_courses   [Date_ID]
-- All relationships are one-to-many, single direction (dim -> fact),
-- filtering from dimension to fact -- the standard Power BI star-schema
-- pattern. No many-to-many relationships and no bidirectional filtering
-- are needed for this model.
-- =====================================================================
