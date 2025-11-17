-- List all watched k-drama
SELECT * FROM movie_detail
WHERE country = 'Korea' 
    AND status in ('completed', 'dropped')
ORDER BY watched_date;