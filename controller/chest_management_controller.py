import datetime
import os

from tinydb import TinyDB

from helpers.notify_func import notify
from model.player import Player
from model.round import Round
from model.tournament import Tournament

gb_tournaments = []
gb_players = []


# Clears the console
def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


# Check if a player already fought another one
def did_player_already_gamed(player1, player2, tournament):
    for chess_round in tournament.rounds:
        for game in chess_round.games:
            if game[0][0] == player1 and game[1][0] == player2 \
                    or game[1][0] == player1 and game[0][0] == player2:
                return True
    return False


# Is the player already set for a match ?
def is_player_already_in_a_game(player, games):
    for game in games:
        if game[0][0] == player or game[1][0] == player:
            return True
    return False


# Let's use player pairing for our matches
def create_pairs(t):
    global gb_players
    if len(t.rounds) == 0:
        # Sorting players by points
        sorted_players = t.players
        length = len(sorted_players)
        middle = length // 2
        first_half = sorted_players[:middle]  # slice first half
        games = []
        for player_index in range(0, len(first_half)):
            match = ([sorted_players[player_index], 0],
                     [sorted_players[player_index + middle],
                      0])  # L'index + la moitié
            games.append(match)
        return games
    else:
        sorted_players = sorted(t.players, key=lambda ply: ply.classement,
                                # Trier en fonction du classement
                                reverse=True)
        games = []
        for player_index in range(0, len(sorted_players)):
            if is_player_already_in_a_game(sorted_players[player_index],
                                           games):
                continue
            for opposite_player_index in range(0, len(sorted_players)):
                # Not the same player
                # Opposite player not already in a game this round
                # Both player not already matched together
                if sorted_players[player_index] != sorted_players[
                    opposite_player_index] and not is_player_already_in_a_game(
                        sorted_players[opposite_player_index],
                        games) and not did_player_already_gamed(
                        sorted_players[player_index],
                        sorted_players[opposite_player_index], t):
                    games.append(
                        ([sorted_players[player_index], 0],
                         [sorted_players[opposite_player_index], 0]))

                    break
        return games


# Create & handle our round matches
def handle_match(games, tournoi):
    global gb_tournaments
    global gb_players
    now = datetime.datetime.now()
    round_idx = 'Round ' + str(len(tournoi.rounds) + 1)
    start_time = str(now.hour) + ':' + str(now.minute)
    chess_round = Round(round_idx, start_time)

    for i in range(0, len(games)):
        ply1_idx = (games[i][0][0])
        ply2_idx = (games[i][1][0])
        matchup = ([ply1_idx, False], [ply2_idx, False])
        chess_round.games.insert(i, matchup)
    return chess_round


# Validity checks & plays the tournament match
def play_tournament(tournoi):
    if tournoi is None:
        return None
    if len(tournoi.players) < 4:
        clear()
        notify("ERROR", 'Ce tournoi ne comporte que ' + str(
            len(tournoi.players)) + ' joueurs. Veuillez en '
                                    'ajouter pour continuer.')
        return None
    if (len(tournoi.players) % 2) != 0:
        notify("ERROR",
               "Impossible de commencer un tournoi "
               "comportant un nombre de joueurs impair ( " +
               str(len(tournoi.players)) + ' )')
        return None
    print('Vous jouez ' + tournoi.nom)
    chess_round = create_pairs(tournoi)
    if len(chess_round) < 2:
        notify("ERROR", "Tous les matchs de " + tournoi.nom + " ont été joué.")
        notify("SUCCESS", tournoi.nom + " est terminé")
        return None
    notify('SUCCESS',
           str(len(tournoi.rounds)) + " rounds trouvés dans le tournoi")
    return chess_round, tournoi


# Adds a round to a tournament
def add_round(tournoi, chess_round):
    tournoi.rounds.append(chess_round)


# Add a new player
def add_player(ply):
    ply_obj = Player(ply['nom'], ply['prenom'], ply['date'], ply['sexe'])
    gb_players.append(ply_obj)


# Add an existing player to a tournament
def add_player_to_tournament(tournoi, ply_picker):
    global gb_players
    # ply_picker = pick_player(gb_players, tournoi)
    ply = gb_players[ply_picker]
    if len(tournoi.players) > 7:
        notify("ERROR", "Ce tournoi comporte dèja 8 joueurs")
        return False
    else:
        tournoi.players.append(ply)
        return True


def get_all_tournaments():
    global gb_tournaments
    return gb_tournaments


def get_all_players():
    global gb_players
    return gb_players


# Retrieve the ID of a player from the gb_players list
def get_player_id_from_mapping(player):
    global gb_players
    for player_id, player_value in enumerate(gb_players):
        if player is player_value:
            return player_id


# Returns a dict copy of a tournament object,
# including serialized players & serialized rounds
def serialize(tournament):
    serialized_t = {
        'nom': tournament.nom,
        'lieu': tournament.lieu,
        'date': tournament.date,
        'tours': tournament.tours,
        'rounds': [],
        'players': [],
        'temps': tournament.temps,
        'desc': tournament.desc
    }

    if tournament.players is None:
        pass
    else:
        for ply in tournament.players:
            plyidx = get_player_id_from_mapping(ply)
            serialized_t['players'].append(plyidx)

    if tournament.rounds is not None:
        for chess_round in tournament.rounds:
            serialized_round = {}
            serialized_round['idx'] = chess_round.idx
            serialized_round['start'] = chess_round.start
            serialized_round['games'] = []
            serialized_round['end'] = chess_round.end
            for game in chess_round.games:
                matchup = (
                    [get_player_id_from_mapping(game[0][0]), game[0][1]],
                    [get_player_id_from_mapping(game[1][0]), game[1][1]])
                serialized_round['games'].append(matchup)
            serialized_t['rounds'].append(serialized_round)
    return serialized_t


# Returns a dict copy of a player object
def player_to_dict(ply):
    serialized_ply = {}
    for attr, value in vars(ply).items():
        serialized_ply[attr] = value
    return serialized_ply


# Saves our data & state
def save():
    global gb_players
    global gb_tournaments

    db = TinyDB('sauvegardes/sauvegarde.json')

    players_db = db.table('players_list')
    players_db.truncate()

    playerlist = []
    for ply in gb_players:
        playerlist.append(player_to_dict(ply))
    players_db.insert_multiple(playerlist)

    tournaments_db = db.table('tournaments')
    tournaments_db.truncate()

    tournaments_list = []
    for tournament in gb_tournaments:
        tournaments_list.append(serialize(tournament))

    tournaments_db.insert_multiple(tournaments_list)
    clear()
    notify("SUCCESS", str(len(gb_tournaments)) + ' tournoi(s) & '
           + str(len(gb_players)) + 'joueur(s) ont été enregistrés.')


# Loads our tournaments / players and try to load rounds if some are found
def load():
    global gb_players
    global gb_tournaments
    gb_players.clear()
    gb_tournaments.clear()
    db = TinyDB('sauvegardes/sauvegarde.json')
    players_db = db.table('players_list')
    tournaments_db = db.table('tournaments')

    if len(players_db) < 1:
        notify('ERROR', "Aucun joueur n'a été trouvé dans la base de données.")
    else:
        for pl in players_db:
            ply_obj = Player(pl['nom'], pl['prenom'], pl['date'], pl['sexe'])
            ply_obj.classement = pl['classement']
            gb_players.append(ply_obj)
        clear()
        notify("SUCCESS", str(len(gb_players)) + " joueurs ont été chargés.")

    if len(tournaments_db) < 1:
        notify('ERROR',
               "Aucun tournoi n'a été trouvé dans la base de données.")
    else:
        players_to_load = []
        for t in tournaments_db:
            for ply in t['players']:
                players_to_load.append(gb_players[ply])
            t_obj = Tournament(t['nom'], t['lieu'], t['date'], t['tours'],
                               t['rounds'], players_to_load, t['temps'],
                               t['desc'])
            if t_obj.rounds is not None:
                rounds_to_load = []
                for chess_round in t_obj.rounds:
                    round_obj = Round(chess_round['idx'], chess_round['start'])
                    round_obj.games = []
                    round_obj.end = chess_round['end']
                    for game in chess_round['games']:
                        game[0][0] = gb_players[game[0][0]]
                        game[1][0] = gb_players[game[1][0]]

                    round_obj.games = chess_round['games']
                    rounds_to_load.append(round_obj)

                t_obj.rounds = rounds_to_load
            # Add our loaded round object from the db to our tournament object
            gb_tournaments.append(t_obj)
        notify("SUCCESS",
               str(len(gb_tournaments)) + " tournois ont été chargés.")


def create_tournament(tournament):
    global gb_tournaments
    if tournament is None:
        return None
    tournament_obj = Tournament(tournament['nom'], tournament['lieu'],
                                tournament['date'], tournament['tours'],
                                tournament['rounds'], tournament['players'],
                                tournament['temps'], tournament['desc'])
    gb_tournaments.append(tournament_obj)
    notify("SUCCESS", tournament_obj.nom + ' a bien été crée !')


# valide debugged
def pick_tournament(tournoi_idx):
    global gb_tournaments
    if tournoi_idx is None:
        return None
    return gb_tournaments[tournoi_idx]


def quitter():
    notify('SUCCESS', 'Vous avez quitté le menu')
    quit()
    pass


# Loads every player found in the database into an actual object,
# appends it to gb_players
def init_players():
    global gb_players
    db = TinyDB(os.path.abspath(
        os.path.join(os.getcwd(), '../sauvegardes/sauvegarde.json')))
    if db is not None:
        if len((db.table('players_classement'))) < 1:
            notify("ERROR", "Il n'y a aucun joueur dans le classement.")

    for ply in db.table('players_classement'):
        ply_obj = Player(ply['nom'], ply['prenom'], ply['date'], ply['sexe'])
        gb_players.append(ply_obj)
    notify('SUCCESS',
           str(len(gb_players)) + ' joueurs ont été trouvés dans la db')
    pass
