SELECT * FROM movie_detail
WHERE status in ('completed', 'dropped')
ORDER BY watched_date;