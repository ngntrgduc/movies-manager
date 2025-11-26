-- Get latest added movies.
SELECT * FROM (
    SELECT * FROM movie_detail 
    ORDER BY id DESC 
    LIMIT ?
) 
ORDER BY id ASC;