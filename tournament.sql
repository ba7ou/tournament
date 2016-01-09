-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- DROP DATABASE IF EXISTS
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

--connect to database
\c tournament;


CREATE TABLE player (
    id serial PRIMARY KEY,
    name varchar(40) NOT NULL
);

CREATE TABLE match (
    id serial PRIMARY KEY,
    winner_id integer REFERENCES player(id) NOT NULL,
    loser_id integer REFERENCES player(id) NOT NULL,
    CONSTRAINT different CHECK (winner_id!=loser_id)
);

-- players standings
CREATE VIEW standings AS
  SELECT player.id, player.name, count(matches_won.id) as wins, count(matches_played.id) as played
  FROM player
    LEFT JOIN match as matches_won
         ON player.id = matches_won.winner_id
    LEFT JOIN match as matches_played
         ON player.id = matches_played.winner_id OR player.id = matches_played.loser_id
  GROUP BY player.id, player.name
  ORDER BY wins DESC
