from datetime import datetime
from pick import pick
from controller.chest_management_controller import quitter, save, load, \
    play_tournament, handle_match, clear, add_round, get_all_players, \
    add_player_to_tournament, pick_tournament, get_all_tournaments,\
    add_player, create_tournament

from helpers.notify_func import notify


def build_menu():
    menu_options = {
        "1": {'nom': "Ajouter un joueur", 'func': enter_new_player},
        "2": {'nom': "Ajouter un joueur  à un tournoi",
              'func': add_player_to_tournament_view},
        "3": {'nom': "Créer un tournoi", 'func': tournament_creator_view},
        "4": {'nom': "Jouer un tournoi", 'func': play_tournament_view},
        "5": {'nom': "Charger", "func": load},
        "6": {'nom': "Sauvegarder", "func": save},
        "7": {'nom': "Lister les joueurs", "func": list_players},
        "8": {'nom': "Lister les joueurs d'un tournoi",
              "func": list_players_from_tournament},
        "9": {'nom': "Lister tous les tournois", "func": list_tournaments},
        "10": {'nom': "Lister les rounds d'un tournoi", "func": list_rounds},
        "11": {'nom': "Lister les matchs d'un tournoi", "func": list_matches},
        "12": {'nom': "Modifier le classement", "func": classment_manager_view}
    }
    menu_options['q'] = {'nom': 'Quitter', 'func': quitter}
    return menu_options


def play_tournament_view():
    tournoi = pick_tournament_view()
    try:
        matches, tournoi_res = play_tournament(tournoi)
        chess_round = handle_match(matches, tournoi)
        handle_match_scores(chess_round, tournoi)

    except TypeError:
        pass


def display_round_winners(games):
    # print(chess_round)
    for result in games:
        if result[0][1] == 1:
            print(result[0][0].nom + ' ' + result[0][0].prenom + ' VICTOIRE')
        elif result[0][1] == 0.5:
            print(result[0][0].nom + ' ' + result[0][0].prenom + ', '
                  + result[1][0].nom + ' ' + result[1][0].prenom + ' EGALITE')
        else:
            print(result[1][0].nom + ' ' + result[1][0].prenom + ' VICTOIRE')

    print("\n Appuyez sur une touche pour continuer")
    input()
    clear()
    return None


def handle_match_scores(chess_round, tournoi):
    clear()
    for i in range(0, len(tournoi.players) // 2):
        try:
            # print(chess_round.games[i][0], chess_round.games[i][1])
            a, b = pick_results(
                (chess_round.games[i][0], chess_round.games[i][1]))
            chess_round.games[i][0][1] = a
            chess_round.games[i][1][1] = b
        except IndexError:
            pass
    now = datetime.now()
    chess_round.end = str(now.hour) + ':' + str(now.minute)
    a = display_round_winners(chess_round.games)
    add_round(tournoi, chess_round)


def add_player_to_tournament_view():
    tournoi = pick_tournament_view()
    if tournoi is None:
        return False
    if len(tournoi.rounds) > 0:
        clear()
        notify("ERROR",
               "Impossible d'ajouter un joueur à un tournoi déja commencé.")
        return False

    ply_picker = pick_player(get_all_players(), tournoi)
    if ply_picker is None:
        return False
    new_ply = add_player_to_tournament(tournoi, ply_picker)
    if new_ply is True:
        ply = get_all_players()[ply_picker]
        clear()
        print(
            'Vous avez ajouté ' + ply.prenom + ' ' + ply.nom + "" +
            ' au tournoi : ' + tournoi.nom)
        print('Le tournoi ' + tournoi.nom + ' comporte désormais ' + str(
            len(tournoi.players)) + ' / 8 ' + ' joueurs.')


# Build the menu view & choices
def show_menu_view(menu):
    for option, valeur in menu.items():
        print(option.upper() + ' ' + menu[option]['nom'])
    res = input(" Choisissez une option" + '\n')
    if res not in menu:
        clear()
        notify('ERROR', "ERREUR : Option invalide")
        return None
    return menu[res]['func']


# Valid debugged
def pick_tournament_view():
    tournoi_idx = pick_tournament_to_load()
    if tournoi_idx is None:
        return None
    tournoi = pick_tournament(tournoi_idx)
    return tournoi


# Prints every match from a defined tournament
def print_matches(tournament):
    clear()
    if not tournament:
        notify('ERROR', "Il n'y a pas de tournois valides.")
        return None
    try:
        clear()
        compteur = 1
        print(
            '---------------- ' + tournament.nom.upper() +
            ' -----------------------')
        for chess_round in tournament.rounds:
            for game in chess_round.games:
                print("                 MATCH " + str(compteur) + ' | ' +
                      game[0][0].prenom + " " + game[0][0].nom + " " + str(
                    game[0][1]) + ' VS ' +
                      game[1][0].prenom + " " + game[1][0].nom + " " + str(
                    game[1][1]))
                compteur += 1
        print("\n")
    except TypeError:
        notify("ERROR",
               "Assurez-vous qu'un tournoi existe et que les rounds aient été "
               "joués.")


# Prints every round & match from a tournament
def print_rounds(tournament):
    clear()
    if not tournament:
        notify('ERROR', "Il n'y a pas de tournois valides.")
        return None
    try:
        clear()
        print(
            '---------------- ' + tournament.nom.upper() +
            ' -----------------------')
        for chess_round in tournament.rounds:
            print("- " + chess_round.idx.upper())
            print(
                "- Début du Round : " + chess_round.start + " | Fin du Round "
                +
                chess_round.end)
            compteur = 1

            for game in chess_round.games:
                print("                 MATCH " + str(compteur) + ' | ' +
                      game[0][0].prenom + " " + game[0][0].nom + " " + str(
                    game[0][1]) + ' VS ' +
                      game[1][0].prenom + " " + game[1][0].nom + " " + str(
                    game[1][1]))
                compteur += 1
        print("\n")
    except TypeError:
        notify("ERROR",
               "Assurez-vous qu'un tournoi existe et que les rounds aient " +
               "été joués.")


# Chose a player
def pick_player(gb_player_list, tournament):
    picking_player = True
    index = None
    while picking_player:
        question = 'Choisissez le joueur à ajouter à ' + tournament.nom
        clean_options = []
        for ply in gb_player_list:
            if ply not in tournament.players:
                clean_options.append(str(ply.nom + ' ' + ply.prenom))
            else:
                clean_options.append(
                    str(ply.nom + ' ' + ply.prenom + '  PARTICIPE'))

        options = clean_options
        options.append('Retour')
        option, index = pick(options, question)
        if option != 'Retour':
            if gb_player_list[index] in tournament.players:
                pass
            else:
                picking_player = False
        else:
            index = None
            picking_player = False

    return index


# Chose a tournament from the tournaments list, returns the ID of it
def pick_tournament_to_load():
    gb_tournament_liste = get_all_tournaments()
    if len(gb_tournament_liste) < 1:
        clear()
        notify("ERROR",
               "Aucun tournoi trouvé. "
               "Créez-en un, ou chargez-en un pour continuer.")
        return None
    question = 'Choisissez un tournoi'
    clean_options = []
    for tournament in gb_tournament_liste:
        tournament_with_ext = tournament.nom
        clean_options.extend([tournament_with_ext])

    options = clean_options
    options.append('Retour')
    option, index = pick(options, question)
    if option == 'Retour':
        return None
    return index


# Add a new player
def enter_new_player():
    clear()
    caracteristiques = {'nom': 'Nom du Joueur :',
                        'prenom': 'Prenom du joueur :',
                        'date': 'Date de naissance :', 'sexe':
                            'Sexe :'}
    new_player = {}
    for i, v in caracteristiques.items():
        clear()
        print(caracteristiques[i])
        rep = input()
        new_player[i] = rep
    clear()
    print("Joueur crée: " + new_player['nom'] + ' ' + new_player[
        'prenom'] + ' ' + new_player['date'] + ' ' + new_player['sexe'] + '\n')
    add_player(new_player)


def is_digit(str_input):
    if str_input.strip().isdigit():
        return True


# Pick a way to display
def how_should_we_list():
    choix = ["Alphabet", "Classement"]
    question = "Afficher les joueurs par :"
    option, index = pick(choix, question)
    return option


# Pick the results of a match, returns score as ints
def pick_results(match):
    choix = [match[0][0], match[1][0], "Match nul"]
    question = 'Attribuez les points du round '
    notify("SUCCESS", match[0][0].get_name() + ' VS ' + match[1][0].get_name())
    option, index = pick([choix[0].get_name(), choix[1].get_name(), choix[2]],
                         question)
    resa = False
    resb = False
    if index == 2:
        resa = 0.5
        resb = 0.5
    elif index == 0:
        resa = 1
        resb = 0
    elif index == 1:
        resa = 0
        resb = 1
    return resa, resb


# Display the match list
def display_match(games):
    clear()
    compteur = 1
    for match in games:
        print('Match ' + str(compteur))
        print(match[0][0].nom + ' va affronter ' +
              match[1][0].nom)
        compteur += 1
    input("Appuyez sur Entrée pour ajouter les résultats.")


# Handles player classment edits
def classment_manager_view():
    players_list = get_all_players()
    setting_classment = True

    while setting_classment:
        choix_dispos = []
        clear()
        for i, v in enumerate(players_list):
            choix_dispos.append(
                v.nom + ' ' + v.prenom + ' : ' + str(v.classement))
        choix_dispos.append("-> Retour")
        question = "Choisissez un joueur pour lui attribuer un classement"
        option, index = pick(choix_dispos, question)
        if option != '-> Retour':
            try:
                players_list[index].classement = int(
                    input("Insérer le classement de " + option + ' :\n'))
            except ValueError:
                notify('ERROR', "Le classement doit se faire avec des entiers")

        else:
            setting_classment = False


# Ask for information in order to create our tournament, returns them as a
# dict for the controller to instantiate it.
def tournament_creator_view():
    questions = {'nom': 'Nom du tournoi :', 'lieu': 'Lieu du tournoi :',
                 'date': 'Date du tournoi ( JJ/MM/AA ):',
                 'tours':
                     'Nombre de tours :', 'temps': 'Contrôle du temps :',
                 'desc': 'Description / Remarques :'}
    reponses = {}
    types = {'nom': str, 'lieu': str, 'date': str, 'tours':
             int, 'temps': str, 'desc': str}

    for i, v in questions.items():
        clear()
        print(questions[i])
        rep = input()

        while not is_digit(rep) and types[i] == int:
            print(questions[i])
            rep = input()
        reponses[i] = rep

    tournament_specs = {'nom': reponses['nom'],
                        'lieu': reponses['lieu'],
                        'date': reponses['date'],
                        'tours': int(reponses['tours']),
                        'rounds': [],
                        'players': [],
                        'temps': reponses['temps'],
                        'desc': reponses['desc'],
                        }
    question = "Valider la création du tournoi ?"
    reponses = ['Valider le tournoi', 'Quitter']
    option, index = pick(reponses, question)
    if index == 0:
        create_tournament(tournament_specs)
    else:
        return None


# List every gb_players's player in a convenient manner
def list_players():
    players = get_all_players()
    if len(players) < 1:
        notify("ERROR", "Il n'y a aucun joueur à afficher")
        return None
    list_type = how_should_we_list()
    if list_type == "Alphabet":
        sorted_players = sorted(players, key=lambda ply: ply.nom)
    elif list_type == "Classement":
        sorted_players = sorted(players, key=lambda ply: ply.classement,
                                reverse=True)
    else:
        sorted_players = players
    clear()
    print("-----------------------------------")
    for pl in sorted_players:
        print(
            pl.prenom + " " + pl.nom + " | Classement : " + str(pl.classement))
    print("-----------------------------------")


# List every player from a chosen tournament
def list_players_from_tournament():
    tournament = pick_tournament_view()
    if tournament is None:
        return None
    if len(tournament.players) < 1:
        notify("ERROR", "Il n'y a aucun joueur à afficher")
        return None

    list_type = how_should_we_list()

    players_list = []
    for pl in tournament.players:
        if pl in players_list:
            pass
        else:
            players_list.append(pl)

    if list_type == "Alphabet":
        sorted_players = sorted(players_list, key=lambda ply: ply.nom)
    elif list_type == "Classement":
        sorted_players = sorted(players_list, key=lambda ply: ply.classement,
                                reverse=True)
    else:
        sorted_players = tournament.players
    clear()
    print("-----------------------------------")
    for pl in sorted_players:
        print(
            pl.prenom + " " + pl.nom + " | Classement : " + str(pl.classement))
    print("-----------------------------------")


# List every tournament in a convenient manner
def list_tournaments():
    tournaments = get_all_tournaments()
    if len(tournaments) < 1:
        clear()
        print("Aucun tournoi n'a été trouvé")
        return None
    clear()
    for t in tournaments:
        print("-----------------------------------")
        print("          " + t.nom.upper())
        print('')
        print("Lieu : ", t.lieu)
        print("date : ", t.date)
        print("tours : ", t.tours)
        print("joueurs : ", len(t.players))
        print("c.d.t : ", t.temps)
        print("description : ", t.desc)
        print("---------------------------------")
        print("\n\n")


# List rounds / matches tree of a chosen tournament
def list_rounds():
    tournament = pick_tournament_view()
    clear()
    print_rounds(tournament)


# List matches from a chosen tournament
def list_matches():
    tournament = pick_tournament_view()
    clear()
    print_matches(tournament)
