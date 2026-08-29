-- =====================================================================
-- analysis_queries.sql
-- Business-question SQL queries for the EdTech Course Analytics project.
-- Written against the star schema (fact_courses + dim_* tables) created
-- by create_schema.sql / build_star_schema.py.
-- Tested against SQLite (data/edtech.db); portable to PostgreSQL / MySQL
-- / SQL Server with trivial syntax changes (e.g. LIMIT vs TOP).
-- =====================================================================

-- 1. Total number of courses
SELECT COUNT(*) AS Total_Courses
FROM fact_courses;

-- 2. Total views (across all courses)
SELECT SUM(Views) AS Total_Views
FROM fact_courses;

-- 3. Average views per course
SELECT ROUND(AVG(Views), 2) AS Avg_Views_Per_Course
FROM fact_courses;

-- 4. Top 10 instructors by total views
SELECT i.Instructor,
       SUM(f.Views) AS Total_Views,
       COUNT(*) AS Course_Count
FROM fact_courses f
JOIN dim_instructor i ON f.Instructor_ID = i.Instructor_ID
GROUP BY i.Instructor
ORDER BY Total_Views DESC
LIMIT 10;

-- 5. Top 10 categories by total views
SELECT c.Category,
       SUM(f.Views) AS Total_Views
FROM fact_courses f
JOIN dim_category c ON f.Category_ID = c.Category_ID
GROUP BY c.Category
ORDER BY Total_Views DESC
LIMIT 10;

-- 6. Course distribution by category
SELECT c.Category,
       COUNT(*) AS Course_Count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fact_courses), 2) AS Pct_Of_Total
FROM fact_courses f
JOIN dim_category c ON f.Category_ID = c.Category_ID
GROUP BY c.Category
ORDER BY Course_Count DESC;

-- 7. Course distribution by language
SELECT l.Language,
       COUNT(*) AS Course_Count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fact_courses), 2) AS Pct_Of_Total
FROM fact_courses f
JOIN dim_language l ON f.Language_ID = l.Language_ID
GROUP BY l.Language
ORDER BY Course_Count DESC;

-- 8. Average views by language
SELECT l.Language,
       ROUND(AVG(f.Views), 2) AS Avg_Views,
       COUNT(*) AS Course_Count
FROM fact_courses f
JOIN dim_language l ON f.Language_ID = l.Language_ID
GROUP BY l.Language
ORDER BY Avg_Views DESC;

-- 9. Average views by course duration (bucketed into ranges)
SELECT
    CASE
        WHEN Duration_Hours < 2   THEN '0-2 hrs'
        WHEN Duration_Hours < 5   THEN '2-5 hrs'
        WHEN Duration_Hours < 10  THEN '5-10 hrs'
        WHEN Duration_Hours < 20  THEN '10-20 hrs'
        ELSE '20+ hrs'
    END AS Duration_Bucket,
    ROUND(AVG(Views), 2) AS Avg_Views,
    COUNT(*) AS Course_Count
FROM fact_courses
GROUP BY Duration_Bucket
ORDER BY MIN(Duration_Hours);

-- 10. Duration vs. views (raw pairs for scatter-plot / correlation use
--     in Power BI or further Python/Excel correlation analysis)
SELECT Course_ID, Duration_Hours, Views
FROM fact_courses
WHERE Views_Outlier = 0   -- exclude extreme outliers for a cleaner view
ORDER BY Duration_Hours;

-- 11. Skills with the highest learner engagement (avg views per course
--     containing that skill). Uses one row per (course, skill) pair.
--     NOTE: Skills is stored as a comma-separated list in fact_courses;
--     this query works in SQLite via a recursive split. In PostgreSQL,
--     replace the recursive CTE with: unnest(string_to_array(Skills,', '))
WITH RECURSIVE split_skills(Course_ID, Views, Skill, Rest) AS (
    SELECT Course_ID, Views,
           TRIM(SUBSTR(Skills || ',', 1, INSTR(Skills || ',', ',') - 1)),
           SUBSTR(Skills || ',', INSTR(Skills || ',', ',') + 1)
    FROM fact_courses
    WHERE Skills IS NOT NULL AND Skills <> ''
    UNION ALL
    SELECT Course_ID, Views,
           TRIM(SUBSTR(Rest, 1, INSTR(Rest, ',') - 1)),
           SUBSTR(Rest, INSTR(Rest, ',') + 1)
    FROM split_skills
    WHERE Rest <> ''
)
SELECT Skill,
       COUNT(DISTINCT Course_ID) AS Course_Count,
       ROUND(AVG(Views), 2) AS Avg_Views
FROM split_skills
WHERE Skill <> ''
GROUP BY Skill
ORDER BY Avg_Views DESC
LIMIT 15;

-- 12. Courses with subtitles vs. without subtitles (avg views comparison)
SELECT Subtitles,
       COUNT(*) AS Course_Count,
       ROUND(AVG(Views), 2) AS Avg_Views,
       ROUND(AVG(Enrollment), 2) AS Avg_Enrollment
FROM fact_courses
GROUP BY Subtitles;

-- 13. Instructor ranking (by total views, with rank number)
SELECT i.Instructor,
       SUM(f.Views) AS Total_Views,
       RANK() OVER (ORDER BY SUM(f.Views) DESC) AS Instructor_Rank
FROM fact_courses f
JOIN dim_instructor i ON f.Instructor_ID = i.Instructor_ID
GROUP BY i.Instructor
ORDER BY Instructor_Rank
LIMIT 20;

-- 14. Category-wise average rating
SELECT c.Category,
       ROUND(AVG(f.Ratings), 2) AS Avg_Rating,
       COUNT(*) AS Course_Count
FROM fact_courses f
JOIN dim_category c ON f.Category_ID = c.Category_ID
GROUP BY c.Category
ORDER BY Avg_Rating DESC;

-- 15. Category-wise enrollment
SELECT c.Category,
       SUM(f.Enrollment) AS Total_Enrollment,
       ROUND(AVG(f.Enrollment), 2) AS Avg_Enrollment_Per_Course
FROM fact_courses f
JOIN dim_category c ON f.Category_ID = c.Category_ID
GROUP BY c.Category
ORDER BY Total_Enrollment DESC;

-- 16. Most popular skills (by number of courses that include them)
WITH RECURSIVE split_skills2(Course_ID, Skill, Rest) AS (
    SELECT Course_ID,
           TRIM(SUBSTR(Skills || ',', 1, INSTR(Skills || ',', ',') - 1)),
           SUBSTR(Skills || ',', INSTR(Skills || ',', ',') + 1)
    FROM fact_courses
    WHERE Skills IS NOT NULL AND Skills <> ''
    UNION ALL
    SELECT Course_ID,
           TRIM(SUBSTR(Rest, 1, INSTR(Rest, ',') - 1)),
           SUBSTR(Rest, INSTR(Rest, ',') + 1)
    FROM split_skills2
    WHERE Rest <> ''
)
SELECT Skill, COUNT(DISTINCT Course_ID) AS Course_Count
FROM split_skills2
WHERE Skill <> ''
GROUP BY Skill
ORDER BY Course_Count DESC
LIMIT 15;

-- 17. Highest-performing subcategories (by average views)
SELECT c.Category, c.Subcategory,
       ROUND(AVG(f.Views), 2) AS Avg_Views,
       COUNT(*) AS Course_Count
FROM fact_courses f
JOIN dim_category c ON f.Category_ID = c.Category_ID
GROUP BY c.Category, c.Subcategory
ORDER BY Avg_Views DESC
LIMIT 10;

-- 18. Categories with high demand (avg views) but low course availability
--     (course count below the median course count per category)
WITH category_stats AS (
    SELECT c.Category,
           COUNT(*) AS Course_Count,
           ROUND(AVG(f.Views), 2) AS Avg_Views
    FROM fact_courses f
    JOIN dim_category c ON f.Category_ID = c.Category_ID
    GROUP BY c.Category
),
medians AS (
    SELECT AVG(Course_Count) AS Median_Course_Count   -- approx. midpoint proxy
    FROM (
        SELECT Course_Count
        FROM category_stats
        ORDER BY Course_Count
        LIMIT 2 - (SELECT COUNT(*) FROM category_stats) % 2
        OFFSET (SELECT (COUNT(*) - 1) / 2 FROM category_stats)
    )
)
SELECT cs.Category, cs.Course_Count, cs.Avg_Views
FROM category_stats cs, medians m
WHERE cs.Course_Count < m.Median_Course_Count
  AND cs.Avg_Views > (SELECT AVG(Avg_Views) FROM category_stats)
ORDER BY cs.Avg_Views DESC;
