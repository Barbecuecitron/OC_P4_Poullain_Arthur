from view.chest_management_view import *
from model.tournament import *
import os.path
from os import listdir
from tinydb import TinyDB, Query
import random
import datetime

gb_tournaments = []
gb_players = []



def create_pairs(t, phase):
    global gb_players
    # print("Le tournoi en est à la phase :" + str(phase))
    if phase == 1:
        # Sorting players by points
        #  sorted_ply = sorted(t.players, key = lambda ply: ply.points)
        # Trier selon le rank
        sorted_players = t.players
        length = len(sorted_players)
        middle = length // 2
        first_half = sorted_players[:middle]  # slice first half
        second_half = sorted_players[middle:]  # slice 2nd half
        #matches_from_round = []
        games = []
        for player_index in range(0,len(first_half)):
            match = ([sorted_players[player_index].GetID(gb_players),0], [sorted_players[player_index + middle].GetID(gb_players),0]) # L'index + la moitié
            id = sorted_players[player_index].GetID(gb_players)
            id2 = sorted_players[player_index + middle].GetID(gb_players)
            print("DANS LA LISTE GLOBALE DES JOUEURS, QUI DOIT ETRE PAREIL :")
            print(gb_players[id].nom + ' VS ' + gb_players[id2].nom)

            games.append(match)
        return games
    else:
        sorted_players = sorted(t.players, key=lambda ply: (ply.points, ply.classement), reverse=True) #/!\ Recalculer les points à partir de l'historique des matchs
        games = []
        for player_index in range(0, len(sorted_players)):
            if is_player_already_in_a_game(sorted_players[player_index], games):
                continue

            for opposite_player_index in range(0, len(sorted_players)):
                # Not the same player
                # Opposite player not already in a game this round
                # Both player not already games together
                if sorted_players[player_index] != sorted_players[opposite_player_index] \
                        and not is_player_already_in_a_game(sorted_players[opposite_player_index], games) \
                        and not did_player_already_gamed(sorted_players[player_index],sorted_players[opposite_player_index], t):
                    games.append(
                        ([sorted_players[player_index], 0], [sorted_players[opposite_player_index], 0]))

                    break
               # t.rounds[int(phase)] = games
        return games


def play_tournament():
    #playing_tournament = True
    #while playing_tournament:
    tournoi_idx = pick_tournament()
    if tournoi_idx is None:
        return None
    tournoi = gb_tournaments[tournoi_idx]
    if len(tournoi.players) < 4:
        display("ERROR",'Ce tournoi ne comporte que ' + str(len(tournoi.players)) + ' joueurs. Veuillez en '
                                                                                    'ajouter pour continuer.')
        return None
    if (len(tournoi.players) % 2) != 0:
        display("ERROR", "Impossible de commencer un tournoi comportant un nombre de joueurs impair ( " +
                str(len(tournoi.players)) + ' )' )
        return None
    print('Vous jouez ' + tournoi.nom)
    print(tournoi.rounds)
    newgames = create_pairs(tournoi, tournoi.phase)
    print(newgames)
    #handle_match(newgames, t)

def add_player():
    ply = enter_new_player()
    ply_obj = Player(ply['nom'], ply['prenom'], ply['date'], ply['sexe'])
    gb_players.append(ply_obj)

def add_player_to_tournament():
    global gb_players
    global gb_tournaments
    tournoi_picker = pick_tournament()
    if tournoi_picker is None:
        return False
    tournoi = gb_tournaments[tournoi_picker]

    ply_picker = pick_player(gb_players,tournoi)
    print(ply_picker)
    if ply_picker is None:
        return False
    else:
        ply = gb_players[ply_picker]
    if len(tournoi.players) > 7:
        print("Ce tournoi comporte dèja 8 joueurs")
        return False
    else:
        print('Vous avez ajouté ' + ply.prenom  + ' ' + ply.nom + "" + ' au tournoi : ' + tournoi.nom)
        tournoi.players.append(ply)
        print('Le tournoi ' + tournoi.nom + ' comporte désormais ' + str(len(tournoi.players)) + ' / 8 ' + ' joueurs.' )



def save():
    global gb_players
    spark_home = os.path.abspath(os.path.join(os.getcwd(), '../joueurs'))
    db_file_name = 'classement'
    db = TinyDB(spark_home + '/' + db_file_name + '.json')
    #ply = enter_new_player()
    players_db = db.table('players_classement')
    players_db.truncate()
    for player_to_save in gb_players:
        serialized_player = player_to_save.Serialize()
        players_db.insert(serialized_player)

def get_menu_option():
    pass

def create_and_save_tournament():
    tournament = tournament_creator_view()
    if tournament is None:
        return None
    spark_home = os.path.abspath(os.path.join(os.getcwd(), '../sauvegardes'))
    db_file_name = tournament['nom'] or 'sauvegarde' + str(tournament['date'])
    db = TinyDB(spark_home + '/' + db_file_name + '.json')
    tournament_table = db.table('tournament')
    tournament_table.truncate()
    tournament_table.insert(tournament)
    print('Le tournoi a été sauvegardé')

def pick_tournament():
    global gb_tournaments
    if len(gb_tournaments) < 1:
        print("Il n'y a aucun tournoi sauvegardé.")
        print('Relancez le programme pour continuer')
        quit()
    tournoi_idx = pick_tournament_to_load(gb_tournaments)
    tournoi = tournoi_idx
    return tournoi

def quitter():
    quit()
    print('Vous avez quitté le menu')
    pass


def init_tournaments():
    global gb_tournaments
    spark_home = os.path.abspath(os.path.join(os.getcwd(), '../sauvegardes/'))
    if len(os.listdir(spark_home)) < 1:
        print("Il n'y a aucun tournoi sauvegardé.")
        return None
    for tournament_file in os.listdir(spark_home):
        t = TinyDB(spark_home + '/' + tournament_file).table('tournament').all()[0]
        tournament = Tournament(t['nom'], t['lieu'], t['date'], t['tours'], t['temps'], t['desc'])
        gb_tournaments.append(tournament)
        #print(gb_tournaments)
    display('SUCCESS',str(len(gb_tournaments)) + ' tournois trouvés dans la db')

def init_players():
    global gb_players
    db = TinyDB(os.path.abspath(os.path.join(os.getcwd(), '../joueurs/classement.json')))
    if len((db.table('players_classement'))) < 1:
        print("Il n'y a aucun joueur dans le classement.")
   # ply = select_player_to_import(db.table('players_classement'))
    for ply in db.table('players_classement'):
        ply_obj = Player(ply['nom'],ply['prenom'],ply['date'],ply['sexe'])
        gb_players.append(ply_obj)
    display('SUCCESS',str(len(gb_players)) + ' joueurs ont été trouvés dans la db')
    pass

def build_menu():
    menu_options = {
        "1" : {'nom': "Ajouter un joueur dans la DB", 'func': add_player},
        "2": {'nom': "Ajouter un joueur  à un tournoi", 'func': add_player_to_tournament},
        "3" : {'nom': "Créer un tournoi", 'func': create_and_save_tournament},
        "4" : {'nom': "Jouer un tournoi", 'func': play_tournament},
        "5" : {'nom': "Charger les tournois", "func": init_tournaments},
        "6" : {'nom': "Sauvegarder", "func": save}
    }
    menu_options['q'] = {'nom': 'Quitter', 'func': quitter}
    return menu_options


def main():
    init_tournaments()
    init_players()
    running = True
    while running :
        choix = show_menu_view(build_menu())
        if choix is not False:
            choix()
        else:
            running = False

if __name__ == '__main__':
    main()
