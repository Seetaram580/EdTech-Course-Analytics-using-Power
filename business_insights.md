# Insights

Numbers here are pulled from cleaned_data.csv (850 courses after cleaning) using the SQL queries in analysis_queries.sql. If you swap in a different dataset these will obviously change — just rerun the queries.

**IT & Software is doing the best out of all 8 categories.** 1.38M total views, ~11,900 avg views/course, and it's not even the biggest category by course count (116, basically middle of the pack). So it's not winning because there's more of it, it's just performing better per course.

**Design is kind of the opposite story.** 3rd most courses (113) but only 5th in avg views (~7,790). More supply than the demand really justifies — feels like a saturated category where new courses have to fight harder for attention.

**Development and Marketing look like the real gaps.** Both have above-average views per course but below-median course counts (91 and 103 vs a median of 106). Ran this properly as a query rather than eyeballing it — defined "opportunity" as below-median course count + above-average views, and these two categories are what came out. If I were pitching where to build new courses next, this is where I'd point.

**Duration doesn't matter.** Correlation between course length and views is -0.02. Basically zero. I went in expecting some relationship (either "people want quick wins" or "longer = more value") and got neither. Course length should probably just be set by however much content actually needs covering.

**Same story with skill count.** -0.016 correlation between number of skills tagged and views. Covering more skills in a course doesn't seem to help it get watched more.

**Subtitles actually do something though.** Courses with subtitles average ~9,372 views vs ~8,542 without (~10% bump), and enrollment jumps more — ~1,476 vs ~1,208, about 22% higher. Out of everything I tested this is one of the few attributes that actually moved the needle, and it's a cheap production cost compared to most other levers.

**Hindi courses do surprisingly well.** Largest language segment by course count (118, ~14% of catalog) AND highest avg views per language (~10,367). Normally you'd expect the biggest segment to regress toward the average since it's diluted across more courses, so seeing it lead on both counts is a bit unusual — I'd sanity check this against real platform data before using it to make a decision, since it could just be an artifact of how the synthetic data was generated.

**Some skills clearly pull more views than others.** SEO, Video Editing, and Cybersecurity Basics top the list (16k+, 15k+, 13k+ avg views respectively). Worth leading with these in course titles/marketing copy if you're trying to maximize views.

**Rating and price barely correlate with views** (+0.04 and +0.03). Kind of surprising but makes sense if you think about it — a 4.8-star course sitting quietly with nobody discovering it doesn't get more views just for being good. Views look driven more by discovery/marketing than by quality signals.

**A handful of instructors carry a disproportionate amount of the total views** — top instructor alone pulls 330K+ views off just 2 courses, while most instructors in the dataset only have 1-2 courses total and nowhere near that reach. If I were running this platform I'd want to understand what those top instructors are doing differently and see if it's replicable.

**Catalog's been growing steadily** — 269 courses in 2023, 259 in 2024, 292 in 2025 (2026 is only partial, 30 courses so far through January). Not explosive growth but consistent.

One honest caveat: this is a synthetic dataset I generated to have realistic structure and some intentional signal baked in for the demo, not real platform numbers. The math is all real and reproducible from the data, but don't quote these specific figures as if they came from an actual EdTech company. Swap in a real dataset (Udemy/Coursera exports on Kaggle work well) and rerun everything if you want insights you can actually present as findings.
