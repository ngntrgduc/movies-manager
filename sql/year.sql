-- Year statistics
SELECT 
    year, 
    COUNT(*) AS count,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    ROUND(AVG(rating), 2) AS avg_rating
FROM movie m
-- WHERE rating IS NOT NULL
GROUP BY year
-- HAVING avg_rating IS NOT NULL;