-- Genres statistics
WITH movie_flags AS (
    SELECT
        m.id,
        m.rating,
        CASE 
            WHEN m.status IN ('completed', 'dropped') THEN 1 ELSE 0 
        END AS watched_flag
    FROM movie m
)
SELECT 
    g.id, 
    g.name, 
    COUNT(*) AS count, 
    SUM(mf.watched_flag) AS watched,
    ROUND(100.0 * SUM(mf.watched_flag) / COUNT(*), 2) || '%' AS watched_percent,
    ROUND(AVG(mf.rating), 2) AS avg_rating
FROM genre AS g
LEFT JOIN movie_genre mg ON mg.genre_id = g.id
LEFT JOIN movie_flags mf ON mf.id = mg.movie_id
GROUP BY g.name
ORDER BY count DESC;