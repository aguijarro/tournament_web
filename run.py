import web
import app.tournament as trn
from math import log

"""Define Urls."""

urls = (

    '/','index',
    '/new_tournament','new_tournament',
    '/new_player','new_player',
    '/init_tournament/(.+)','init_tournament',
    '/players_tournament/(.+)','players_tournament',
    '/rounds_tournament/(.+)','rounds_tournament',
    '/assign_players/(.+)','assign_players',
    '/player_standings/(.+)','player_standings',
    '/player_matches/(.+)','player_matches',
    '/new_match/(.+)','new_match',
    '/result_match/(.+)','result_match',
)

"""Determine location for templates"""
render = web.template.render('templates', base='layout')

#Define index web page.
class index:
    def GET(self):
        #get the list of tournaments to show in a web page
        tournaments = trn.reportTournaments()
        return render.index(tournaments)

#Define new tournament web page. Create new tournament
class new_tournament:
    #define a objects for the form to get information about tournament
    form = web.form.Form(
        web.form.Textbox('name', description='Name', class_="form-control"),
        web.form.Textbox('description', description='Description', class_="form-control"),
        web.form.Textbox('tournamentPlayers', description='TournamentPlayers', class_="form-control"),
        web.form.Button('process', type="submit", description="Register", class_="btn btn-lg btn-warning pull-right"),
    )

    def GET(self):
        form = self.form()
        return render.new_tournament(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new_tournament(form)
        #compute the rounds for a tournament based on the number of players
        rounds = round(log(int(form['tournamentPlayers'].value))/log(2))
        #records new tournament
        trn.registerTournament(form['name'].value, form['description'].value, form['tournamentPlayers'].value, int(rounds))
        raise web.seeother('/')

#Define new player web page. Create new player
class new_player:
    #define a objects for the form to get information about player
    form = web.form.Form(
        web.form.Textbox('name', description='Name', class_="form-control"),
        web.form.Button('save', type="submit", description="Save", class_="btn btn-lg btn-warning pull-right"),
    )

    def GET(self):
        form = self.form()
        return render.new_player(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new_player(form)
        #records new player
        trn.registerPlayer(form['name'].value)
        raise web.seeother('/')

#Define init tournament web page. Initialize standings for the first round
class init_tournament:

    #define a objects for the form to get information for Initializes the tournament
    form = web.form.Form(
        web.form.Checkbox('status', description='Statis', class_="form-control"),
        web.form.Button('save', type="submit", description="Save", class_="btn btn-lg btn-warning pull-right"),
    )

    def GET(self,id_tournament):
        form = self.form()
        #Returns players already register in a tournament
        playersTournaments = trn.reportPlayersTournaments(id_tournament)
        #Returns the number of players already register in a tournament
        numberPlayerInTournament = trn.numberPlayerInTournament(id_tournament)
        #Returns the number of players allowed by tournament
        numberPlayerByTournament = trn.numberPlayerByTournament(id_tournament)

        if int(numberPlayerInTournament) == int(numberPlayerByTournament):
            return render.init_tournament(form, id_tournament, 'True')
        else:
            return render.init_tournament(form, id_tournament, 'False')

    def POST(self,id_tournament):
        form = self.form()
        if not form.validates():
            return render.init_tournament(form)
        #Initializes the tournament. Save standings for the first round
        trn.initTournament(id_tournament)
        raise web.seeother('/')

#Define player tournament web page. Shows a list of players by tournament
class players_tournament:

    def GET(self,id_tournament):
        #Returns players already register in a tournament
        playersTournaments = trn.reportPlayersTournaments(id_tournament)
        #Returns the number of players already register in a tournament
        numberPlayerInTournament = trn.numberPlayerInTournament(id_tournament)
        #Returns the number of players allowed by tournament
        numberPlayerByTournament = trn.numberPlayerByTournament(id_tournament)

        return render.players_tournament(id_tournament, playersTournaments, numberPlayerInTournament, numberPlayerByTournament)


#Define rounds tournament web page. Show rounds for eache tournament
class rounds_tournament:

    def GET(self,id_tournament):
        #Returns rounds for a tournament
        roundsTournaments = trn.reportRoundsTournament(id_tournament)
        return render.rounds_tournament(id_tournament, roundsTournaments)


# Class uses to generate checkfield
# https://gist.github.com/simota/3300253 - Reference to this page to see how to implement an array of inputs in wep.py
class DynamicForm(web.form.Form):
    def add_input(self, new_input):
        list_inputs = list(self.inputs)
        list_inputs.append(new_input)
        self.inputs = tuple(list_inputs)


#Define assign players web page.
class assign_players:

    def __init__(self):
        self.dynamic = DynamicForm()

    def GET(self,id_tournament):
        #Returns the number of players already register in a tournament
        numberPlayerInTournament = trn.numberPlayerInTournament(id_tournament)
        #Returns the number of players allowed by tournament
        numberPlayerByTournament = trn.numberPlayerByTournament(id_tournament)

        #Validates if a number of players register in a tournament is less than a number
        #of players allowed in a tournament

        if int(numberPlayerInTournament) < int(numberPlayerByTournament):
            #Returns list of players register in the app
            players = trn.reportPlayers(id_tournament)
            #Create a list of Checkboxs uses to assign players to a tournament
            for player in players:
                name = 'player%d' % player[0]
                self.dynamic.add_input(web.form.Checkbox(name,description=player[1],value=player[0]))
            self.dynamic.add_input(web.form.Button('save', type="submit", description="Save", class_="btn btn-lg btn-warning pull-right"))
            return render.assign_players(id_tournament,self.dynamic)
        return render.assign_players(id_tournament,self.dynamic)

    def POST(self,id_tournament):
        list_inputs = web.input()
        #Returns the number of players already register in a tournament
        numberPlayerInTournament = trn.numberPlayerInTournament(id_tournament)
        #Returns the number of players allowed by tournament
        numberPlayerByTournament = trn.numberPlayerByTournament(id_tournament)
        #Get the number of inputs selected in form less one because of submit input
        numberOfInputs = len(list_inputs)-1


        if numberOfInputs + int(numberPlayerInTournament) <= int(numberPlayerByTournament):
            for value in list_inputs:
                if value != 'save':
                    #Records a player for each tournament
                    trn.assignPlayerTournament(int(id_tournament), int(value[6:]))
            url = '/players_tournament/%d' % int(id_tournament)
            raise web.seeother(url)

        #Returns the players for each tournament
        players = trn.reportPlayers(id_tournament)
            #Create a list of Checkboxs uses to assign players to a tournament
        for player in players:
            name = 'player%d' % player[0]
            self.dynamic.add_input(web.form.Checkbox(name,description=player[1],value=player[0]))
        self.dynamic.add_input(web.form.Button('save', type="submit", description="Save", class_="btn btn-lg btn-warning pull-right"))
        return render.assign_players(id_tournament,self.dynamic)

#Define player standings web page.
class player_standings:

    def GET(self,id_round):
        #Returns standings for round
        playerStandings = trn.roundStandings(id_round)
        #Returns id for a tournament
        id_tournament = trn.reportIdTournament(id_round)
        return render.player_standings(id_round, id_tournament, playerStandings)

#Define player matches page.
class player_matches:

    def GET(self,id_round):
        #Returns matches for a round
        playerMatches = trn.roundMatches(id_round)
        #Returns id for a tournament
        id_tournament = trn.reportIdTournament(id_round)
        #Returns true if exist a match for a round
        matchStatus = trn.reportMatchByRound(id_round)
        #Returns true if exist a result for match
        resultStatus = trn.reportResultByMatch(id_round)
        #Return a Bye Player
        byePlayer = trn.reportByePlayer(id_round)
        return render.player_matches(id_round, id_tournament, playerMatches, matchStatus, byePlayer, resultStatus)

#Define new match web page.
class new_match:

    #define a objects for the form to get information about matches
    form = web.form.Form(
        web.form.Checkbox('status', description='Statis', class_="form-control"),
        web.form.Button('save', type="submit", description="Save", class_="btn btn-lg btn-warning pull-right"),
    )

    def GET(self,id_round):
        form = self.form()
        return render.new_match(id_round, form)

    def POST(self,id_round):
        form = self.form()
        if not form.validates():
            return render.new_match(id_round, form)
            #Make a swiss paired system
        trn.swissPairings(id_round)
        url = '/player_matches/%d' % int(id_round)
        raise web.seeother(url)

#Define result match web page.
class result_match:

    def __init__(self):
        self.dynamic = DynamicForm()

    def GET(self,id_round):
        #Returns a matches for each round
        playerMatches = trn.roundMatches(id_round)
        #Returns id by tournament
        id_tournament = trn.reportIdTournament(id_round)
        #Returns if exist a match for a round
        matchState = trn.reportMatchByRound(id_round)

        #Create a list of inputs with information about matches to register the result
        for playerMatch in playerMatches:
            name = 'match%d' % playerMatch[0]
            self.dynamic.add_input(web.form.Dropdown(name,[(str(playerMatch[3])+'.'+str(playerMatch[4]),playerMatch[1]),(str(playerMatch[4])+'.'+str(playerMatch[3]),playerMatch[2]), (str(playerMatch[3])+'_'+str(playerMatch[4]),'Tied')]))

        self.dynamic.add_input(web.form.Button('save', type="submit", description="Save", class_="btn btn-lg btn-warning pull-right"))
        return render.result_match(id_round, id_tournament, playerMatches, matchState, self.dynamic)

    def POST(self,id_round):
        list_inputs = web.input()
        #get bye player
        byePlayer = trn.reportIdByePlayer(id_round)

        for key in list_inputs:
            if key != 'save':
                idPlayers = list_inputs[key].encode('ascii','ignore')
                #Split id for each input to get the id which will be record
                separatorPlayers = str.find(idPlayers,'.')
                if separatorPlayers != -1:
                    winner = idPlayers[:separatorPlayers]
                    loser = idPlayers[separatorPlayers+1:]
                    tied = None
                else:
                    separatorPlayers = str.find(idPlayers,'_')
                    winner = idPlayers[:separatorPlayers]
                    loser = idPlayers[separatorPlayers+1:]
                    tied =  idPlayers
                #Records match results.
                trn.saveResultMatch(id_round, int(key[5:]), winner, loser, tied)

        #Update result of bye player to sum a win according to the rules
        trn.updateScoreboardBye(id_round, byePlayer)

        # Returns id tournament
        id_tournament = trn.reportIdTournament(id_round)
        # Returns next round
        id_round_next = trn.getNextRound(id_round, id_tournament)


        if id_round_next != None:
            # Returns standings for actual round
            standings = trn.roundStandings(id_round)
            for standing in standings:
                #register standing for next round
                trn.registerStandings(id_round_next,standing[0],standing[2],standing[3],standing[4],standing[5],'Insert')

        url = '/player_matches/%d' % int(id_round)
        raise web.seeother(url)


#Executed the application.
def main():

    app = web.application(urls, globals())
    app.run()


if __name__ == '__main__':
    main()
