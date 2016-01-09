#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect(database_name="tournament"):
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("<error message>")

def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor = connect()
    query = "TRUNCATE match CASCADE"
    cursor.execute(query)
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records and associated matches from the database."""
    db, cursor = connect()
    query = "TRUNCATE player CASCADE"
    cursor.execute(query)
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = connect()
    query = "SELECT COUNT(*) FROM player"
    cursor.execute(query)
    nbplayers = cursor.fetchone()[0]
    db.close()
    return nbplayers

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db, cursor = connect()
    clean_content = bleach.clean(name)
    query = 'INSERT INTO player (name) VALUES (%s)'
    params = (clean_content,)
    cursor.execute(query, params)
    db.commit()
    db.close()

def playerStandings():
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
    db, cursor = connect()
    query = 'SELECT * FROM standings'
    cursor.execute(query)
    playerStandings = cursor.fetchall()
    db.close()
    return playerStandings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  winner player 1 id
      loser:  loser player id
    """

    db, cursor = connect()
    clean_w = bleach.clean(winner)
    clean_l = bleach.clean(loser)
    query = """INSERT INTO match (winner_id, loser_id) VALUES (%(winner)s, %(loser)s)returning id;"""
    params = {'winner': clean_w, 'loser': clean_l}
    cursor.execute(query, params)
    id = cursor.fetchone()[0]
    db.commit()
    db.close()


def swissPairings():
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

    standings = playerStandings()
    swissPairings = list()

    #iterate over the list of two with python function zip()
    for player1, player2 in zip(standings[0::2], standings[1::2]):
        swissPairings.append((player1[0], player1[1], player2[0], player2[1]))
    return swissPairings
