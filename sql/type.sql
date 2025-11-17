SELECT 
    type, 
    COUNT(*) AS count,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'dropped' THEN 1 ELSE 0 END) AS dropped,
    -- ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) || '%' AS completed_percent
    ROUND(100.0 * SUM(CASE WHEN status IN ('completed', 'dropped') THEN 1 ELSE 0 END) / COUNT(*), 2) || '%' AS watched_percent,
    ROUND(AVG(rating), 2) AS avg_rating
FROM movie
GROUP BY type;