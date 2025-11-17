-- Country statistics
SELECT
    country,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM movie), 2) || '%' AS percent,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'dropped' THEN 1 ELSE 0 END) AS dropped,
    -- SUM(CASE WHEN status in ('completed', 'dropped') THEN 1 ELSE 0 END) AS watched,
    ROUND(100.0 * SUM(CASE WHEN status IN ('completed', 'dropped') THEN 1 ELSE 0 END) / COUNT(*), 2) || '%' AS watched_percent,
    ROUND(AVG(rating), 2) AS avg_rating
FROM movie
GROUP BY country
ORDER BY count DESC;