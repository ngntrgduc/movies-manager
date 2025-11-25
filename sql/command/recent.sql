-- List 10 recent watched
SELECT * FROM (
    SELECT * FROM movie_detail 
    WHERE status in ('completed', 'dropped')
    ORDER BY id DESC 
    LIMIT (?)
) 
ORDER BY watched_date;