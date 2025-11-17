-- Rating statistics
SELECT 
    rating, 
    COUNT(*) AS count,
    -- ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM movie), 2) || '%' AS percent
    -- MAX(watched_date) AS latest_watched
    SUM(CASE WHEN type = 'movie' THEN 1 ELSE 0 END) AS movie_count,
    SUM(CASE WHEN type = 'series' THEN 1 ELSE 0 END) AS series_count
FROM movie
-- WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY rating DESC;