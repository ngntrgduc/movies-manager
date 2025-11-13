SELECT 
    SUBSTR(watched_date, 1, 4) AS year, 
    SUM(CASE WHEN type = 'movie' THEN 1 ELSE 0 END) AS movie_count,
    SUM(CASE WHEN type = 'series' THEN 1 ELSE 0 END) AS series_count,
    ROUND(AVG(rating), 2) AS avg_rating
FROM movie
-- WHERE watched_date IS NOT NULL
GROUP BY SUBSTR(watched_date, 1, 4)
-- strftime('%Y', watched_date) -- Not work for year only data