-- Status statistics
SELECT 
    status, 
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM movie), 2) || '%' AS percent,
    SUM(CASE WHEN type = 'movie' THEN 1 ELSE 0 END) AS movie_count,
    SUM(CASE WHEN type = 'series' THEN 1 ELSE 0 END) AS series_count,
    ROUND(AVG(rating), 2) AS avg_rating
FROM movie
GROUP BY status
ORDER BY count DESC