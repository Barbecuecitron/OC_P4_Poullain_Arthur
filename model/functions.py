# Saves our data & state
from tinydb import TinyDB
from model.player import Player
from helpers.clear_func import clear
from helpers.notify_func import notify
from model.tournament import Tournament
from model.round import Round


# Returns a dict copy of a tournament object,
# including serialized players & serialized rounds

# Retrieve the ID of a player from the gb_players list
def get_player_id_from_mapping(player, gb_players):
    for player_id, player_value in enumerate(gb_players):
        if player is player_value:
            return player_id


def serialize(tournament, gb_players):
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
            plyidx = get_player_id_from_mapping(ply, gb_players)
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
                    [get_player_id_from_mapping(game[0][0], gb_players), game[0][1]],
                    [get_player_id_from_mapping(game[1][0], gb_players), game[1][1]])
                serialized_round['games'].append(matchup)
            serialized_t['rounds'].append(serialized_round)
    return serialized_t


# Returns a dict copy of a player object
def player_to_dict(ply):
    serialized_ply = {}
    for attr, value in vars(ply).items():
        serialized_ply[attr] = value
    return serialized_ply


# Calls serialize and saves our tournaments & players
def save(gb_tournaments, gb_players):
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
        tournaments_list.append(serialize(tournament, gb_players))

    tournaments_db.insert_multiple(tournaments_list)
    clear()
    notify("SUCCESS", str(len(gb_tournaments)) + ' tournoi(s) & '
           + str(len(gb_players)) + ' joueur(s) ont été enregistrés.')


# Loads our tournaments / players and try to load rounds if some are found

def load(gb_tournaments, gb_players):
    gb_players.clear()
    gb_tournaments.clear()
    db = TinyDB('sauvegardes/sauvegarde.json')
    players_db = db.table('players_list')
    tournaments_db = db.table('tournaments')

    if len(players_db) < 1:
        notify('ERROR', "Aucun joueur n'a été trouvé dans la base de données.")
    else:
        for pl in players_db:
            ply_obj = Player(pl['nom'], pl['prenom'], pl['date'], pl['sexe'],
                             pl['points'])
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
                # Add our loaded round object from the db to our tournament
                # object
            gb_tournaments.append(t_obj)
        notify("SUCCESS",
               str(len(gb_tournaments)) + " tournois ont été chargés.")
