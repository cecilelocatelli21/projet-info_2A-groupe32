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
-- Livre
-----------------------------------------------------
DROP TABLE IF EXISTS livre CASCADE;
CREATE TABLE livre (
    id_livre    SERIAL PRIMARY KEY,
    id_work     VARCHAR(255) UNIQUE,
    titre       VARCHAR(255) NOT NULL,
    auteurs     VARCHAR(255) NOT NULL
);

-----------------------------------------------------
-- Utilisateur
-----------------------------------------------------
DROP TABLE IF EXISTS utilisateur CASCADE;
CREATE TABLE utilisateur (
    id_user         SERIAL PRIMARY KEY,
    pseudo          VARCHAR(30),
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    bio             TEXT
);

-----------------------------------------------------
-- Utilisateur
-----------------------------------------------------
DROP TABLE IF EXISTS abonnement CASCADE;
CREATE TABLE abonnement (
    id_follower         SERIAL PRIMARY KEY,
    id_followed         INT UNIQUE NOT NULL,
    date_abonnement     DATE
);

-----------------------------------------------------
-- Lecture
-----------------------------------------------------
DROP TABLE IF EXISTS lecture CASCADE;
CREATE TABLE lecture (
    id_lecture      SERIAL PRIMARY KEY,
    id_user         INT UNIQUE REFERENCES utilisateur(id_user) NOT NULL,
    id_livre        INT UNIQUE REFERENCES livre(id_livre) NOT NULL,
    statut          VARCHAR(50) NOT NULL,
    date_ajout      DATE,
    date_lu         DATE,
    note            INT
);

-----------------------------------------------------
-- Critique
-----------------------------------------------------
DROP TABLE IF EXISTS critique CASCADE;
CREATE TABLE critique (
    id_critique         SERIAL PRIMARY KEY,
    id_lecture          INT UNIQUE REFERENCES lecture(id_lecture) NOT NULL,
    texte               TEXT NOT NULL,
    date_publication    DATE
);

-----------------------------------------------------
-- Like
-----------------------------------------------------
DROP TABLE IF EXISTS like CASCADE;
CREATE TABLE like_ (
    id_user         INT UNIQUE REFERENCES utilisateur(id_user) NOT NULL,
    id_critique     INT UNIQUE REFERENCES critique(id_critique) NOT NULL,
    date_like       DATE,
    aime            BOOLEAN NOT NULL
);


