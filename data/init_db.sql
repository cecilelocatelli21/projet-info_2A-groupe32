-----------------------------------------------------
-- Player
-----------------------------------------------------
DROP TABLE IF EXISTS player CASCADE;
CREATE TABLE player (
    id_player    SERIAL PRIMARY KEY,
    username     VARCHAR(30) UNIQUE,
    password     VARCHAR(256),
    elo          INTEGER,
    email        VARCHAR(50),
    pokemon_fan  BOOLEAN,
    access_token VARCHAR(255)
);

-----------------------------------------------------
-- Book
-----------------------------------------------------
DROP TABLE IF EXISTS book CASCADE;
CREATE TABLE book (
    book_id    SERIAL PRIMARY KEY,
    work_id     VARCHAR(255) UNIQUE,
    title       VARCHAR(255) NOT NULL,
    authors     VARCHAR(255) NOT NULL,
    cover_url   VARCHAR(255)
);

-----------------------------------------------------
-- User
-----------------------------------------------------
DROP TABLE IF EXISTS user_table CASCADE;
CREATE TABLE user_table (
    user_id         SERIAL PRIMARY KEY,
    username        VARCHAR(30),
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    bio             TEXT
);

-----------------------------------------------------
-- Follow
-----------------------------------------------------
DROP TABLE IF EXISTS follow CASCADE;
CREATE TABLE follow (
    follower_id     INT,
    followed_id     INT,
    follow_date     DATE,
    FOREIGN KEY (follower_id) REFERENCES user_table(user_id),
    FOREIGN KEY (followed_id) REFERENCES user_table(user_id)
);

-----------------------------------------------------
-- Reading
-----------------------------------------------------
DROP TABLE IF EXISTS reading CASCADE;
CREATE TABLE reading (
    reading_id      SERIAL PRIMARY KEY,
    user_id         INT UNIQUE REFERENCES user_table(user_id) NOT NULL,
    book_id         INT UNIQUE REFERENCES book(book_id) NOT NULL,
    status          VARCHAR(50) NOT NULL,
    date_added      DATE,
    date_read       DATE,
    rating          INT
);

-----------------------------------------------------
-- Review
-----------------------------------------------------
DROP TABLE IF EXISTS review CASCADE;
CREATE TABLE review (
    review_id           SERIAL PRIMARY KEY,
    reading_id          INT UNIQUE REFERENCES reading(reading_id) NOT NULL,
    text                TEXT NOT NULL,
    publication_date    DATE
);

-----------------------------------------------------
-- Like
-----------------------------------------------------
DROP TABLE IF EXISTS like_table CASCADE;
CREATE TABLE like_table (
    user_id         INT UNIQUE REFERENCES user_table(user_id) NOT NULL,
    review_id       INT UNIQUE REFERENCES review(review_id) NOT NULL,
    like_date       DATE,
    liked           BOOLEAN NOT NULL
);


