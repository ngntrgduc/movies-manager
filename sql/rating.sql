-- Rating statistics
SELECT 
    rating, 
    COUNT(*) AS count
    -- ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM movie), 2) || '%' AS percent
    -- MAX(watched_date) AS latest_watched
FROM movie
-- WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY rating DESC;