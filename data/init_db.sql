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
    book_id     SERIAL PRIMARY KEY,
    work_id     VARCHAR(255) UNIQUE NOT NULL,
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
    username        VARCHAR(30) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    bio             TEXT,
    access_token    VARCHAR(255) UNIQUE     -- NULL when the user is disconnected
);

-----------------------------------------------------
-- Follow
-----------------------------------------------------
DROP TABLE IF EXISTS follow CASCADE;
CREATE TABLE follow (
    follower_id     INT NOT NULL REFERENCES user_table(user_id) ON DELETE CASCADE,
    followed_id     INT NOT NULL REFERENCES user_table(user_id) ON DELETE CASCADE,
    follow_date     DATE,
    PRIMARY KEY (follower_id, followed_id),
    CHECK (followed_id <> followed_id)
);

-----------------------------------------------------
-- Reading
-----------------------------------------------------
DROP TABLE IF EXISTS reading CASCADE;
CREATE TABLE reading (
    reading_id      SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES user_table(user_id) ON DELETE CASCADE,
    book_id         INT NOT NULL REFERENCES book(book_id),
    status          VARCHAR(50) NOT NULL,
    date_added      DATE,
    date_read       DATE,
    rating          INT CHECK (rating BETWEEN 0 AND 5),
    UNIQUE(user_id, book_id)            -- A book appears only once in the reading list of one user
);

-----------------------------------------------------
-- Review
-----------------------------------------------------
DROP TABLE IF EXISTS review CASCADE;
CREATE TABLE review (
    review_id           SERIAL PRIMARY KEY,
    reading_id          INT UNIQUE NOT NULL REFERENCES reading(reading_id) ON DELETE CASCADE,
    text                TEXT NOT NULL,
    publication_date    DATE DEFAULT CURRENT_DATE
);

-----------------------------------------------------
-- Like
-----------------------------------------------------
DROP TABLE IF EXISTS like_table CASCADE;
CREATE TABLE like_table (
    user_id         INT NOT NULL REFERENCES user_table(user_id) ON DELETE CASCADE,
    review_id       INT NOT NULL REFERENCES review(review_id) ON DELETE CASCADE,
    like_date       DATE DEFAULT CURRENT_DATE,
    liked           BOOLEAN NOT NULL,
    PRIMARY KEY (user_id, review_id)            -- Only one like possible for a user on one review
);


