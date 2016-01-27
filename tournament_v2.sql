-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create database

--psql
--vagrant=> \i tournament.sql

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

CREATE TABLE tournament(
  id_tournament serial primary key,
  name text,
  description text,
  tournamentPlayers text,
  numberOfRounds text,
  stateTournament boolean DEFAULT false
);

CREATE TABLE player(
  id_player serial primary key,
  name text
);

CREATE TABLE player_tournament(
  id_player_tournament serial primary key,
  id_tournament integer references tournament,
  id_player integer references player
);

CREATE TABLE round(
  id_round serial primary key,
  name text,
  id_tournament integer references tournament
);

CREATE TABLE bye(
  id_bye serial primary key,
  id_round integer references round,
  id_player integer references player_tournament
);

CREATE TABLE match(
  id_match serial primary key,
  id_round integer references round,
  player_1 integer references player_tournament,
  player_2 integer references player_tournament,
  result text
);

CREATE TABLE scoreboard(
  id_scoreboard serial primary key,
  id_round integer references round,
  id_player integer references player_tournament,
  matches integer,
  win integer,
  lost integer,
  tied  integer
);

-- Function that returns the number of match
CREATE OR REPLACE FUNCTION get_num_match(p_id_round integer, p_id_player integer)
RETURNS integer AS $num_match$
declare
  num_match integer;
BEGIN
    SELECT matches into num_match
    FROM scoreboard
    WHERE id_round = $1
    AND id_player = $2;
    RETURN num_match;
END;
$num_match$ LANGUAGE plpgsql;

-- Function that returns the number of wins
CREATE OR REPLACE FUNCTION get_num_win(p_id_round integer, p_id_player integer)
RETURNS integer AS $num_win$
DECLARE
  num_win integer;
BEGIN
    SELECT win into num_win
    FROM scoreboard
    WHERE id_round = p_id_round
    AND id_player = p_id_player;
    RETURN num_win;
END;
$num_win$ LANGUAGE plpgsql;

-- Function that returns the number of lost
CREATE OR REPLACE FUNCTION get_num_lost(p_id_round integer, p_id_player integer)
RETURNS integer AS $num_lost$
declare
  num_lost integer;
BEGIN
    SELECT lost into num_lost
    FROM scoreboard
    WHERE id_round = p_id_round
    AND id_player = p_id_player;
    RETURN num_lost;
END;
$num_lost$ LANGUAGE plpgsql;

-- Function that returns the number of tied
CREATE OR REPLACE FUNCTION get_num_tied(p_id_round integer, p_id_player integer)
RETURNS integer AS $num_tied$
declare
  num_tied integer;
BEGIN
    SELECT tied into num_tied
    FROM scoreboard
    WHERE id_round = p_id_round
    AND id_player = p_id_player;
    RETURN num_tied;
END;
$num_tied$ LANGUAGE plpgsql;

-- Insert data to support a tournament at a time
-- \d name_table
insert into tournament(name,description,tournamentPlayers,numberOfRounds) values ('Tournament 1','Tournament 1','7','3');
insert into tournament(name,description,tournamentPlayers,numberOfRounds) values ('Tournament 2','Tournament 2','5','2');
insert into tournament(name,description,tournamentPlayers,numberOfRounds) values ('Tournament 3','Tournament 3','7','3');

insert into player(name) values ('Player 1');
insert into player(name) values ('Player 2');
insert into player(name) values ('Player 3');
insert into player(name) values ('Player 4');
insert into player(name) values ('Player 5');
insert into player(name) values ('Player 6');
insert into player(name) values ('Player 7');

insert into round(name, id_tournament) values ('Round 0', 1);
insert into round(name, id_tournament) values ('Round 1', 1);
insert into round(name, id_tournament) values ('Round 2', 1);

insert into round(name, id_tournament) values ('Round 0', 2);
insert into round(name, id_tournament) values ('Round 1', 2);

insert into round(name, id_tournament) values ('Round 0', 3);
insert into round(name, id_tournament) values ('Round 1', 3);
insert into round(name, id_tournament) values ('Round 2', 3);

insert into player_tournament(id_tournament,id_player) values (1,1);
insert into player_tournament(id_tournament,id_player) values (1,2);
insert into player_tournament(id_tournament,id_player) values (1,3);
insert into player_tournament(id_tournament,id_player) values (1,4);
insert into player_tournament(id_tournament,id_player) values (1,5);
insert into player_tournament(id_tournament,id_player) values (1,6);
insert into player_tournament(id_tournament,id_player) values (1,7);

insert into player_tournament(id_tournament,id_player) values (2,1);
insert into player_tournament(id_tournament,id_player) values (2,2);
insert into player_tournament(id_tournament,id_player) values (2,3);
insert into player_tournament(id_tournament,id_player) values (2,4);
insert into player_tournament(id_tournament,id_player) values (2,5);

insert into player_tournament(id_tournament,id_player) values (3,1);
insert into player_tournament(id_tournament,id_player) values (3,2);
insert into player_tournament(id_tournament,id_player) values (3,3);
insert into player_tournament(id_tournament,id_player) values (3,4);
insert into player_tournament(id_tournament,id_player) values (3,5);
insert into player_tournament(id_tournament,id_player) values (3,6);
insert into player_tournament(id_tournament,id_player) values (3,7);
