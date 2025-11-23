-- Return all animation in Japan
SELECT
    id,
    name,
    year,
    status,
    type,
    -- country,
    genres,
    rating,
    watched_date,
    note
FROM movie_detail
WHERE country = 'Japan' AND genres LIKE '%animation%'