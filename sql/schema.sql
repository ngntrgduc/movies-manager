-- name,year,status,type,country,genres,rating,watched_date,note
CREATE TABLE IF NOT EXISTS movie (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, 
    year INTEGER, 
    status TEXT NOT NULL,
    type TEXT,
    country TEXT,
    rating REAL,
    watched_date TEXT,
    note TEXT
);

CREATE TABLE IF NOT EXISTS genre (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS movie_genre (
    movie_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movie(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genre(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

-- view
CREATE VIEW IF NOT EXISTS movie_detail AS
SELECT
    m.id,
    m.name,
    m.year,
    m.status,
    m.type,
    m.country,
    GROUP_CONCAT(g.name, ',') AS genres,
    m.rating,
    m.watched_date,
    m.note
FROM movie AS m
LEFT JOIN movie_genre mg ON m.id = mg.movie_id
LEFT JOIN genre g ON g.id = mg.genre_id
GROUP BY m.id;