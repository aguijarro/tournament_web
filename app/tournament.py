#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def reportTournaments():
    """Returns a list of tournaments registered in database"""
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT * FROM tournament;
          '''
    c.execute(sql)
    tournaments = []

    for row in c.fetchall():
        tournaments.append(row)
    DB.close()
    return tournaments

def registerRound(name, id_tournament):
    """Adds a rounds to the tournament database.

    Args:
      name: the round's full name (needs be unique for each tournament).
      id_tournament: foreing key from table tournament.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''INSERT INTO round(name, id_tournament)
                VALUES (%s, %s) RETURNING id_round;'''
    c.execute(sql,(name,id_tournament,))
    DB.commit()
    id_round = c.fetchone()[0]
    DB.close()
    return id_round

def registerStandings(id_round, id_player, matches, win, lost, tied, action):
    """Adds a scoreboard to the tournament database by each Round.

    Args:
      name: the player's full name (need not be unique).
      id_round: foreing key from table round. Save scoreboard for each round
      id_player: foreing key from table player_tournament. Save scoreboard for each player
      matches: Save the number of matches for the player
      win: Save a win result
      lost: Save a lost result
      tied: Save tied result
      action: Define what action must be executed: Insert data or Update data
    """

    if action == 'Insert':
        DB = connect()
        c = DB.cursor()
        sql = '''INSERT INTO scoreboard(id_round, id_player, matches, win, lost, tied)
                VALUES (%s, %s, %s, %s, %s, %s);'''
        c.execute(sql,(id_round, id_player, matches, win, lost, tied,))
        DB.commit()
        DB.close()
    else:
        DB = connect()
        c = DB.cursor()
        sql = '''UPDATE scoreboard SET matches = %s, win = %s, lost = %s, tied = %s WHERE id_round = %s AND id_player = %s;'''
        c.execute(sql,(matches,win,lost,tied, id_round,id_player,))
        DB.commit()
        DB.close()


def registerTournament(name, description, tournamentPlayers, rounds):
    """Adds a tournament to the tournament database.

    Args:
      name: the tournament's full name (need not be unique).
      description: the tournament's description
      tournamentPlayers: define how many players will has the Tournament
      rounds: define how many rounds the Tournament will has depending the number of players.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''INSERT INTO tournament(name, description, tournamentPlayers, numberOfRounds)
                VALUES (%s, %s, %s, %s) RETURNING id_tournament;'''
    c.execute(sql,(name,description,tournamentPlayers,rounds,))
    DB.commit()
    id_tournament = c.fetchone()[0]
    DB.close()

    for x in range(0, rounds):
        name = 'Round %d' % x
        id_round = registerRound(name, id_tournament)


def reportRoundsTournament(id_tournament):
    """Returns the list of rounds registered per Tournament

    Args:
      id_tournament: foreing key from table tournament.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT r.name, r.id_round FROM round r WHERE r.id_tournament = %s;
          '''
    c.execute(sql,(id_tournament,))
    rounds = []

    for row in c.fetchall():
        rounds.append(row)
    DB.close()
    return rounds

def numberPlayerByTournament(id_tournament):
    """Returns the number of players by Tournament.
    Args:
      id_tournament: foreing key from table tournament.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT name, tournamentPlayers FROM tournament WHERE id_tournament = %s;'''
    c.execute(sql,(id_tournament,))
    numberPlayers = c.fetchone()[1]
    DB.close()
    return numberPlayers

def numberPlayerInTournament(id_tournament):
    """Returns the number of players already register in a Tournament.
    Args:
      id_tournament: foreing key from table tournament.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT count(*) FROM player_tournament WHERE id_tournament = %s;'''
    c.execute(sql,(id_tournament,))
    numberPlayers = c.fetchone()[0]
    DB.close()
    return numberPlayers


def registerPlayer(name):
    """Adds a player to the tournament database.

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    sql = '''INSERT INTO player(name) VALUES (%s);'''
    c.execute(sql,(name,))
    DB.commit()
    DB.close()

def reportPlayersTournaments(id_tournament):
    """Returns the list of players registered per Tournament
    Args:
      id_tournament: foreing key from table tournament.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT p.name, p.id_player, pt.id_player_tournament FROM player_tournament pt, player p
             WHERE p.id_player = pt.id_player
             AND pt.id_tournament = %s;
          '''
    c.execute(sql,(id_tournament,))
    players = []

    for row in c.fetchall():
        players.append(row)
    DB.close()
    return players

def assignPlayerTournament(id_tournament, id_player):
    """Assign a player to a one tournament.

    Args:
      id_tournament: foreing key from table tournament.
      id_player: foreing key from table player.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''INSERT INTO player_tournament(id_tournament, id_player) VALUES (%s,%s);'''
    c.execute(sql,(id_tournament,id_player,))
    DB.commit()
    DB.close()

def reportPlayers(id_tournament):
    """Returns the list of players currently registered.
    Args:
      id_tournament: foreing key from table tournament.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT * FROM player p WHERE p.id_player NOT IN
            (SELECT pt.id_player FROM player_tournament pt where pt.id_tournament = %s);
          '''
    c.execute(sql,(id_tournament))
    players = []

    for row in c.fetchall():
        players.append(row)
    DB.close()
    return players


def firstRoundTournament(id_tournament):
    """Returns the first round for each Tournament.
    Args:
      id_tournament: foreing key from table tournament.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT id_round FROM round WHERE name = 'Round 0' AND id_tournament = %s;'''
    c.execute(sql,(id_tournament,))
    id_round = c.fetchone()[0]
    DB.close()
    return id_round


def initTournament(id_tournament):
    """Initializes the Tournament and records the first scoreboard for the define the first
     matches.

    Args:
      id_tournament: foreing key from table tournament.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''UPDATE tournament SET stateTournament = True WHERE id_tournament = %s;'''
    c.execute(sql,(id_tournament,))
    DB.commit()
    DB.close()

    #Returns players already register in a tournament
    playersTournaments = reportPlayersTournaments(id_tournament)
    #Returns id for that round
    id_round = firstRoundTournament(id_tournament)

    for player in playersTournaments:
        #Save standing for first round
        registerStandings(id_round,player[2],0,0,0,0,'Insert')


def reportIdTournament(id_round):
    """Returns the id for each Tournament.
    Args:
      id_round: foreing key from table round.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT id_tournament FROM round WHERE id_round = %s;'''
    c.execute(sql,(id_round,))
    id_round = c.fetchone()[0]
    DB.close()
    return id_round

def roundStandings(id_round):
    """Returns a list of the players and their win records, sorted by wins

    Args:
      id_round: foreing key from table round.

    Returns:
      A list of tuples, each of which contains (id_player, name, matches, wins, lost, tied):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        matches: the number of matches the player has played
        wins: the number of matches the player has won
        lost: the number of matches the player has lost
        tied: the number of matches the player has tied
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT  s.id_player, p.name, s.matches, s.win, s.lost, s.tied
                FROM scoreboard s, player_tournament pt, player p
                WHERE s.id_player = pt.id_player_tournament
                AND pt.id_player = p.id_player
                AND s.id_round = %s
                ORDER BY 4 DESC;
          '''
    c.execute(sql,(id_round,))

    standings = []

    for row in c.fetchall():
        standings.append(row)
    DB.close()
    return standings

def reportMatchByRound(id_round):
    """ Returns true if there is a match already register for that round
    Args:
      id_round: foreing key from table round.
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT count(*) FROM match WHERE id_round = %s;'''
    c.execute(sql,(id_round,))
    numberMatch = c.fetchone()[0]
    DB.close()

    if numberMatch !=0:
        return False
    else:
        return True

def reportResultByMatch(id_round):
    """ Returns true if there is a result already registered for that round
    Args:
      id_round: foreing key from table round.
    """
    print "id_round"
    print id_round
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT result from match where id_round = %s;'''
    c.execute(sql,(id_round,))

    results = []
    for row in c.fetchall():
        results.append(row)
    DB.close()

    for result in results:
        if result[0]==None:
            return True

    return False


def roundMatches(id_round):
    """Returns a list of the matches per Round and Tournament.
    Args:
      id_round: foreing key from table round.

    Returns:
      A list of tuples, each of which contains (m.id_match, p1.name, p2.name, pt1.id_player_tournament, pt2.id_player_tournament):
        m.id_match: the matches' unique id (assigned by the database)
        p1.name: the player's 1 full name (as registered)
        p2.name: the player's 2 full name (as registered)
        pt1.id_player_tournament: the player's 1 unique id (assigned by the database)
        pt2.id_player_tournament: the player's 2 unique id (assigned by the database)
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT  m.id_match, p1.name, p2.name, pt1.id_player_tournament, pt2.id_player_tournament
                FROM match m, player_tournament pt1, player_tournament pt2, player p1, player p2
                WHERE m.player_1 = pt1.id_player_tournament
                AND m.player_2 = pt2.id_player_tournament
                AND pt1.id_player = p1.id_player
                AND pt2.id_player = p2.id_player
                AND m.id_round = %s;
          '''
    c.execute(sql,(id_round,))

    matches = []

    for row in c.fetchall():
        matches.append(row)
    DB.close()
    return matches

def saveMatch(id_round, player_1, player_2):
    """Records the match for a Round of Tournament.

    Args:
      id_round: the round's unique id (assigned by the database)
      player_1: the player's 1 id (as registered)
      player_2: the player's 2 id (as registered)
    """
    DB = connect()
    c = DB.cursor()
    sql = '''INSERT INTO match(id_round, player_1, player_2) VALUES (%s,%s,%s);'''
    c.execute(sql,(id_round,player_1,player_2,))
    DB.commit()
    DB.close()


def updateScoreboardBye(id_round, id_player):
    """Update scoreboard of a player which is in Bye state.

    Args:
      id_round: the round's unique id (assigned by the database)
      id_player: the player's 1 id (as registered)
    """
    DB = connect()
    c = DB.cursor()

    #get number of match
    sql_num_match = '''SELECT  get_num_match(%s,%s);'''
    c.execute(sql_num_match,(id_round,id_player))
    num_match = c.fetchone()[0]

    #get number of match for loser
    sql_win_num_match = '''SELECT  get_num_win(%s,%s);'''
    c.execute(sql_win_num_match,(id_round,id_player))
    win_num_match = c.fetchone()[0]

    DB.close()

    #Save standings
    registerStandings(id_round,id_player,num_match + 1,win_num_match + 1,0,0,'Update')


def saveBye(id_round, id_player):
    """Record a player which was selected for a Bye state.

    Args:
      id_round: the round's unique id (assigned by the database)
      id_player: the player's 1 id (as registered)
    """
    DB = connect()
    c = DB.cursor()
    sql = '''INSERT INTO bye(id_round, id_player) VALUES (%s,%s);'''
    c.execute(sql,(id_round,id_player,))
    DB.commit()
    DB.close()

def reportByePlayer(id_round):
    """Returns a player wihch is in Bye state.
    Args:
      id_round: the round's unique id (assigned by the database)
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT p.name FROM bye b, player_tournament pt, player p
             WHERE b.id_player = pt.id_player_tournament
             AND pt.id_player = p.id_player
             AND b.id_round = %s;
          '''
    c.execute(sql,(id_round,))
    namePlayerBye = c.fetchone()
    DB.close()

    return namePlayerBye

def reportIdByePlayer(id_round):
    """Returns value if the player is already saved in Bye table.
    Args:
      id_round: the round's unique id (assigned by the database)
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT pt.id_player_tournament FROM bye b, player_tournament pt, player p
             WHERE b.id_player = pt.id_player_tournament
             AND pt.id_player = p.id_player
             AND b.id_round = %s;
          '''
    c.execute(sql,(id_round,))
    idPlayerBye = c.fetchone()[0]
    DB.close()

    return idPlayerBye

def reportBye(id_round, id_player):
    """Returns value if the player is already saved in Bye table. Function use to control that a player
        must not save two times in a Bye table

    Args:
      id_round: the round's unique id (assigned by the database)
      id_player: the player's 1 id (as registered)

    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT count(*) FROM bye WHERE id_round = %s AND id_player = %s;'''
    c.execute(sql,(id_round,id_player,))
    bye = c.fetchone()[0]

    DB.close()
    return bye

def returnPairStandings(id_round,standings):
    """Return a even scoreboard whitout player which was saved in Bye Table.

    Args:
      id_round: the round's unique id (assigned by the database)
      standings: scoreboard belonging to a round
    """

    for index, standing in enumerate(standings):
        bye = reportBye(id_round, standing[0])
        if int(bye) == 0:
            #Save bye player
            saveBye(id_round,standing[0])
            standings.pop(index)
            break
    return standings

def validPairs(first_player, second_player):
    """Return True if the pair for the match is valid. That means that the players never play before

    Args:
        first_player: the player's 1 id (as registered)
        second_player: the player's 2 id (as registered)
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT  count(*) as num_match
                FROM match m
                WHERE (m.player_1 = %s and m.player_2 = %s)
                OR (m.player_1 = %s and m.player_2 = %s);
          '''
    c.execute(sql,(first_player,second_player,second_player,first_player))
    count = c.fetchone()[0]
    DB.close()

    if count == 0:
        return True
    else:
        return False

def makePairs(index_first_player, first_player, possiblePairs):
    """Return a player selected from the different alternatives

    Args:
        index_first_player: array position for a player_1
        first_player: the player's 1 id (as registered)
        possiblePairs: array of possible pairs for player 1
    """
    for index_second_player, second_player in enumerate(possiblePairs):
        if validPairs(first_player[0],second_player[0]):
            return index_second_player + (index_first_player + 1), second_player

def swissPairings(id_round):
    """Records a list of pairs of players for the next round of a match.
    Args:
      id_round: the round's unique id (assigned by the database)
    """

    pairs = []
    #Return standings for a round
    standings = roundStandings(id_round)
    #Returns the id of tournament to identify the number of players
    id_tournament = reportIdTournament(id_round)
    #Returns the number of players by tournament
    playersByTournament = numberPlayerByTournament(id_tournament)

    if (int(playersByTournament) % 2 != 0):
        #returns a standings with out bye player
        standings = returnPairStandings(id_round,standings)

    while len(standings) > 1:
        index_first_player = 0
        first_player = standings[0]
        # Make pair
        index_second_player, second_player = makePairs(index_first_player, first_player, standings[1:])
        # Take off the pairs which was proccess
        standings.pop(index_second_player)
        standings.pop(index_first_player)

        pairs.append((first_player[0],second_player[0]))

    for pair in pairs:
        #Save a new match
        saveMatch(id_round,pair[0],pair[1])


def saveResultMatch(id_round, id_match, winner, loser, tied):
    """Returns the number of players already register in a Tournament.
    Args:
      id_round: the round's unique id (assigned by the database)
      id_match: the matches' unique id (assigned by the database)
      winner: the winner's id (as registered)
      loser: the loser's 1 id (as registered)
      tied: condition that explain if the result of the match was tied
    """
    if tied == None:
        DB = connect()
        c = DB.cursor()
        sql = '''UPDATE match SET result = %s  WHERE id_match = %s;'''
        c.execute(sql,(winner,id_match,))
        DB.commit()
        DB.close()
        #Save match for save when there is not a tied
        reportMatch(id_round, winner, loser, tied)

    else:
        DB = connect()
        c = DB.cursor()
        sql = '''UPDATE match SET result = %s  WHERE id_match = %s;'''
        c.execute(sql,(tied,id_match,))
        DB.commit()
        DB.close()
        #Save match for save when there is a tied
        reportMatch(id_round, winner, loser, tied)

def reportMatch(id_round, winner, loser, tied):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()

    if tied == None:
        #get number of match for winners

        sql_win_num_match = '''SELECT  get_num_match(%s,%s);'''
        c.execute(sql_win_num_match,(id_round,winner))
        winner_num_match = c.fetchone()[0]


        #get number of match for loser
        sql_lost_num_match = '''SELECT  get_num_match(%s,%s);'''
        c.execute(sql_lost_num_match,(id_round,loser))
        loser_num_match = c.fetchone()[0]


        #get number of wins for winner
        sql_winner_num_win = '''SELECT  get_num_win(%s,%s);'''
        c.execute(sql_winner_num_win,(id_round,winner))
        winner_num_win = c.fetchone()[0]

        #get number of lost for winner
        sql_winner_num_lost = '''SELECT  get_num_lost(%s,%s);'''
        c.execute(sql_winner_num_lost,(id_round,winner))
        winner_num_lost = c.fetchone()[0]


        #get number of wins for loser
        sql_loser_num_win = '''SELECT  get_num_win(%s,%s);'''
        c.execute(sql_loser_num_win,(id_round,loser))
        loser_num_win = c.fetchone()[0]

        #get number of lost for loser
        sql_loser_num_lost = '''SELECT  get_num_lost(%s,%s);'''
        c.execute(sql_loser_num_lost,(id_round,loser))
        loser_num_lost = c.fetchone()[0]

        #get number of tied for winner
        sql_winner_num_tied = '''SELECT  get_num_tied(%s,%s);'''
        c.execute(sql_winner_num_tied,(id_round,winner))
        winner_num_tied = c.fetchone()[0]

        #get number of tied for loser
        sql_loser_num_tied = '''SELECT  get_num_tied(%s,%s);'''
        c.execute(sql_loser_num_tied,(id_round,loser))
        loser_num_tied = c.fetchone()[0]


        #update winner
        registerStandings(id_round,winner,winner_num_match + 1,winner_num_win + 1,winner_num_lost,winner_num_tied,'Update')

        #update loser
        registerStandings(id_round,loser,loser_num_match + 1,loser_num_win,loser_num_lost + 1,loser_num_tied,'Update')

    else:

        sql_player_1_num_match = '''SELECT  get_num_match(%s,%s);'''
        c.execute(sql_player_1_num_match,(id_round,winner))
        player_1_num_match = c.fetchone()[0]

        #get number of match for loser
        sql_player_2_num_match = '''SELECT  get_num_match(%s,%s);'''
        c.execute(sql_player_2_num_match,(id_round,loser))
        player_2_num_match = c.fetchone()[0]

        #get number of tied player 1
        sql_player_1_num_tied = '''SELECT  get_num_tied(%s,%s);'''
        c.execute(sql_player_1_num_tied,(id_round,winner))
        player_1_num_tied = c.fetchone()[0]

        #get number of tied player 2
        sql_player_2_num_tied = '''SELECT  get_num_tied(%s,%s);'''
        c.execute(sql_player_2_num_tied,(id_round,loser))
        player_2_num_tied = c.fetchone()[0]


        #get number of wins player 1
        sql_player_1_num_win = '''SELECT  get_num_win(%s,%s);'''
        c.execute(sql_player_1_num_win,(id_round,winner))
        player_1_num_win = c.fetchone()[0]

        #get number of wins player 2
        sql_player_2_num_win = '''SELECT  get_num_win(%s,%s);'''
        c.execute(sql_player_2_num_win,(id_round,loser))
        player_2_num_win = c.fetchone()[0]

        #get number of lost player 1
        sql_player_1_num_lost = '''SELECT  get_num_lost(%s,%s);'''
        c.execute(sql_player_1_num_lost,(id_round,winner))
        player_1_num_lost = c.fetchone()[0]

        #get number of lost player 2
        sql_player_2_num_lost = '''SELECT  get_num_lost(%s,%s);'''
        c.execute(sql_player_2_num_lost,(id_round,loser))
        player_2_num_lost = c.fetchone()[0]

        #update player_1
        registerStandings(id_round,winner,player_1_num_match + 1,player_1_num_win,player_1_num_lost,player_1_num_tied + 1,'Update')
        #update player_2
        registerStandings(id_round,loser,player_2_num_match + 1,player_2_num_win,player_2_num_lost,player_2_num_tied + 1,'Update')


def getNextRound(id_round, id_tournament):
    """Returns the next round for each tournament.

    Args:
        id_round: the round's unique id (assigned by the database)
        id_tournament: the tournament's unique id (assigned by the database)
    """
    DB = connect()
    c = DB.cursor()
    sql = '''SELECT id_round
            FROM round
            WHERE id_tournament = %s
            AND id_round > %s LIMIT 1;'''
    c.execute(sql,(id_tournament, id_round,))
    next_round = c.fetchone()

    DB.close()
    return next_round
