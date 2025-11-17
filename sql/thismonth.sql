-- List all movies/series watched in this month
SELECT * FROM movie_detail
WHERE SUBSTR(watched_date, 1, 7) = SUBSTR(CURRENT_DATE, 1, 7)
-- WHERE strftime('%Y-%m', watched_date) = strftime('%Y-%m', CURRENT_DATE)
-- WHERE watched_date >= date(CURRENT_DATE, 'start of month')
--   AND watched_date < date(CURRENT_DATE, 'start of month', '+1 month')
ORDER BY watched_date;