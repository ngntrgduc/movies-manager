-- List all movies/series watched in last month
SELECT * FROM movie_detail
WHERE SUBSTR(watched_date, 1, 7) = strftime('%Y-%m', CURRENT_DATE, '-1 month')
-- WHERE strftime('%Y-%m', watched_date) = strftime('%Y-%m', CURRENT_DATE, '-1 month')
ORDER BY watched_date;