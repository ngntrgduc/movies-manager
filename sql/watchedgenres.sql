-- Genres statistics for watched
SELECT 
    g.id, 
    g.name, 
    COUNT(*) AS count, 
    ROUND(AVG(rating), 2) AS avg_rating
FROM genre AS g
LEFT JOIN movie_genre mg ON mg.genre_id = g.id
LEFT JOIN movie m ON m.id = mg.movie_id
WHERE m.status IN ('completed', 'dropped')
GROUP BY g.name
ORDER BY count DESC;