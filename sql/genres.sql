-- List all genres in the database
-- SELECT * FROM genre;

-- Genres statistics
SELECT 
    g.id, 
    g.name, 
    COUNT(*) AS count, 
    SUM(
        CASE 
            WHEN m.status IN ('completed', 'dropped') THEN 1 ELSE 0 
        END
    ) AS watched,
    ROUND(AVG(rating), 2) AS avg_rating
FROM genre AS g
LEFT JOIN movie_genre mg ON mg.genre_id = g.id
LEFT JOIN movie m ON m.id = mg.movie_id
GROUP BY g.name
ORDER BY count DESC;