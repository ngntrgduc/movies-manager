-- get 15 latest rows in the database
SELECT * FROM (
    SELECT * FROM movie_detail 
    ORDER BY id DESC 
    LIMIT 15
) 
ORDER BY id ASC;