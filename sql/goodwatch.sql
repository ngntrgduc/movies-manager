-- List all watched movies/series with rating >= 8
SELECT * FROM movie_detail
WHERE rating >= 8
ORDER BY 
    rating ASC,
    watched_date ASC;