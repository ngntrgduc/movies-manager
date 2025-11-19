-- Year statistics
WITH year_stats AS (
    SELECT 
        year,
        COUNT(*) AS count,
        SUM(CASE WHEN status IN ('completed', 'dropped') THEN 1 ELSE 0 END) AS watched,
        ROUND(AVG(rating), 2) AS avg_rating
    FROM movie
    GROUP BY year
    -- HAVING avg_rating IS NOT NULL
)
SELECT 
    year,
    count,
    watched,
    ROUND(100.0 * watched / count, 2) || '%' AS percent, 
    avg_rating
FROM year_stats