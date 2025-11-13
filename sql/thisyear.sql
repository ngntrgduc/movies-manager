-- List all movies/series watched in this year
SELECT * FROM movie_detail
WHERE SUBSTR(watched_date, 1, 4) = SUBSTR(CURRENT_DATE, 1, 4)
-- WHERE strftime('%Y', watched_date) = strftime('%Y', CURRENT_DATE)
ORDER BY watched_date;