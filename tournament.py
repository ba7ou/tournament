#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteTournaments():
    """Remove all the tournament records from the database."""
    pg = connect()
    c = pg.cursor()
    c.execute("TRUNCATE tournament CASCADE")
    pg.commit()
    pg.close()

def deleteMatches():
    """Remove all the match records from the database."""
    pg = connect()
    c = pg.cursor()
    c.execute("TRUNCATE match CASCADE")
    #c.execute("DELETE FROM matches")
    pg.commit()
    pg.close()

def deletePlayers():
    """Remove all the player records and associated matches from the database."""
    pg = connect()
    c = pg.cursor()
    c.execute("TRUNCATE player CASCADE")
    #c.execute("DELETE FROM players")
    pg.commit()
    pg.close()

def countPlayers():
    """Returns the number of players currently registered."""
    pg = connect()
    c = pg.cursor()
    c.execute("SELECT COUNT(*) FROM player")
    nbplayers = c.fetchone()[0]
    pg.close()
    return nbplayers

def createTournament(name):
    """Adds a tournament to the tournament database.

    The database assigns a unique serial id number for the tournament.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the tournament full name (need not be unique).
    """
    pg = connect()
    c = pg.cursor()
    clean_content = bleach.clean(name)
    c.execute('INSERT INTO tournament (name) VALUES (%s) returning id;',
              (clean_content,)
              )
    tournament_id = c.fetchone()[0]
    pg.commit()
    pg.close()
    return tournament_id

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    pg = connect()
    c = pg.cursor()
    clean_content = bleach.clean(name)
    c.execute('INSERT INTO player (name) VALUES (%s)',
              (clean_content,)
              )
    pg.commit()
    pg.close()


def playerStandings(tournament):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    pg = connect()
    c = pg.cursor()
    clean_content = bleach.clean(tournament)
    c.execute('SELECT player_id, player_name, wins, draws, matches FROM standings where tournament_id=%s',
                (clean_content,)
             )
    playerStandings = c.fetchall()
    pg.close()
    return playerStandings

def reportMatch(t, p1, p2, w):
    """Records the outcome of a single match between two players.

    Args:
      t: tournament id
      p1:  player 1 id
      p2:  player 2 id
      w: id of winner
    """

    pg = connect()
    c = pg.cursor()
    clean_t = bleach.clean(t)
    clean_p1 = bleach.clean(p1)
    clean_p2 = bleach.clean(p2)
    c.execute("""INSERT INTO match (tournament_id, player1, player2) VALUES (%(tournament)s, %(player1)s, %(player2)s)
                returning id;""",
                {'tournament': clean_t, 'player1': clean_p1, 'player2': clean_p2}
             )
    match_id = c.fetchone()[0]
    clean_m = bleach.clean(match_id)
    clean_w = bleach.clean(w)
    if w:
        c.execute("""
                insert into result (match_id, winner)
                values(%(match_id)s, %(winner)s);""",
                {'match_id': clean_m, 'winner': clean_w}
                )
    pg.commit()
    pg.close()


def swissPairings(tournament):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    pg = connect()
    c = pg.cursor()
    c.execute("""select p.player_id, p.player_name, p.byes
                from standings p, opponent_standings o
                where p.tournament_id=%s
                and p.tournament_id=o.tournament_id
                and p.player_id=o.player_id
                order by p.wins, p.losses desc, o.wins, o.losses desc""",
                (tournament,))
    standings = c.fetchall()
    match = ()
    matches = []
    bye_needed = len(standings) % 2 != 0
    for player in standings:
        if bye_needed and player[2] == 0:
            matches.append(player[0:2] + (None, None))
        else:
            match = match + player[0:2]
            if len(match) == 4:
                matches.append(match)
                match = ()
    c.close()
    return list(set(matches))
