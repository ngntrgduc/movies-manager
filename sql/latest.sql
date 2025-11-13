-- get 10 latest added rows in the database
SELECT * FROM (
    SELECT * FROM movie_detail 
    ORDER BY id DESC 
    LIMIT 10
) 
ORDER BY id ASC;