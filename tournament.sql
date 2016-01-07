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

-- DROP VIEW IF EXISTS
DROP VIEW IF EXISTS standings;
DROP VIEW IF EXISTS opponent_standings;

-- DROP old Tables IF EXISTS
DROP TABLE IF EXISTS tournament;
DROP TABLE IF EXISTS match;
DROP TABLE IF EXISTS result;
DROP TABLE IF EXISTS player;


CREATE TABLE tournament (
  id serial PRIMARY KEY,
  name text NOT NULL
);

CREATE TABLE player (
    id serial PRIMARY KEY,
    name varchar(40) NOT NULL
);

CREATE TABLE match (
    id serial PRIMARY KEY,
    tournament_id integer REFERENCES tournament(id) NOT NULL,
    player1 integer REFERENCES player(id) NOT NULL,
    player2 integer REFERENCES player(id) NOT NULL,
    CONSTRAINT different CHECK (player1!=player2),
    winner integer REFERENCES player(id),
    CONSTRAINT winner in (player1 OR player2)
);

-- players standings
CREATE VIEW standings AS (
    SELECT t.id AS tournament_id, p.id AS player_id, p.name AS player_name,
      count(m.*) AS matches,
      count(w.*) AS wins,
      count(l.*) AS losses,
      count(m.*)-(count(w.*)+count(l.*)) AS draws,
      count(b.*) AS byes
    FROM tournament AS t
      CROSS JOIN player AS p
      LEFT JOIN match AS m ON m.tournament_id=t.id AND p.id IN (m.player1, m.player2)
      LEFT JOIN match AS w ON w.id=m.id AND w.winner=p.id
      LEFT JOIN match AS l ON l.id=m.id AND l.winner!=p.id
      LEFT JOIN match AS b ON b.id=m.id AND b.player2=NULL
    GROUP BY t.id, p.id
);

--opponent standings
CREATE VIEW opponent_standings AS
    SELECT t.id AS tournament_id,
        p.id AS player_id,
        sum(o.wins) AS wins,
        sum(o.losses) AS losses,
        sum(o.draws) AS draws
    FROM tournament AS t
        CROSS JOIN player AS p
        LEFT JOIN match AS m ON m.tournament_id=t.id AND p.id IN (m.player1, m.player2)
        LEFT JOIN standings AS o ON o.tournament_id=t.id AND o.player_id=case when p.id=m.player1 then m.player2 else m.player1 end
    GROUP BY t.id, p.id;
