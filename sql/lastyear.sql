-- List all movies/series watched in last year
SELECT * FROM movie_detail
WHERE SUBSTR(watched_date, 1, 4) = strftime('%Y', CURRENT_DATE, '-1 year')
-- WHERE strftime('%Y', watched_date) = strftime('%Y', CURRENT_DATE, '-1 year')
-- WHERE watched_date >= date(CURRENT_DATE, 'start of year', '-1 year')
--   AND watched_date < date(CURRENT_DATE, 'start of year')
ORDER BY watched_date;