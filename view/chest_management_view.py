from pick import pick
import os


# print('View imported correctly')

def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def show_menu_view(menu):
    for option, valeur in menu.items():
        print(option.upper() + ' ' + menu[option]['nom'])
    res = input(" Choisissez une option" + '\n')
    if not res in menu:
        print('ERREUR : Option invalide')
        return None
    return menu[res]['func']


def display(type, text):
    balise = ""
    if type == 'ERROR':
        balise = ' ⚠️'
    elif type == "SUCCESS":
        balise = ' ▼ '

    print('\n' + balise + text + balise + '\n')


def pick_player(gb_player_list, tournament):
    picking_player = True
    while picking_player:
        question = 'Choisissez le joueur à ajouter à ' + tournament.nom
        clean_options = []
        for ply in gb_player_list:
            if not ply in tournament.players:
                clean_options.append(str(ply.nom + ' ' + ply.prenom))
            else:
                clean_options.append(str(ply.nom + '' + ply.prenom + '  ✓'))

        options = clean_options
        options.append('Retour')
        option, index = pick(options, question, indicator="➤ ")
        if option != 'Retour':
            if gb_player_list[index] in tournament.players:
                pass
            else:
                picking_player = False
        else:
            index = None
            picking_player = False

    return index


def pick_tournament_to_load(gb_tournament_liste):
    question = 'Choisissez un tournoi'
    clean_options = []
    for tournament in gb_tournament_liste:
        tournament_with_ext = tournament.nom
        clean_options.extend([tournament_with_ext])

    options = clean_options
    options.append('Retour')
    option, index = pick(options, question, indicator="➤ ")
    if option == 'Retour':
        return None
    return index


def enter_new_player():
    caracteristiques = {'nom': 'Nom du Joueur :', 'prenom': 'Prenom du joueur :',
                        'date': 'Date de naissance :', 'sexe':
                            'Sexe :'}
    new_player = {}
    for i, v in caracteristiques.items():
        print(caracteristiques[i])
        rep = input()
        new_player[i] = rep
    return new_player


def is_digit(input):
    if input.strip().isdigit():
        return True


def pick_results(match, players_list):
    choix = [players_list[match[0][0]], players_list[match[1][0]], "Match nul"]
    question = 'Attribuez les points du round '
    print(players_list[match[0][0]].GetName() + ' VS ' + players_list[match[1][0]].GetName())
    option, index = pick([choix[0].GetName(), choix[1].GetName(), choix[2]], question)
    resa = False
    resb = False
    if index == 2:
        resa = .5
        resb = .5
    elif index == 0:
        resa = 1
        resb = 0
    elif index == 1:
        resa = 0
        resb = 1
    return (resa, resb)


def display_match(games, liste_joueurs):
    clear()
    compteur = 1
    for match in (games):
        print('Match ' + str(compteur))
        print(liste_joueurs[match[0][0]].nom + ' ' + str(liste_joueurs[match[0][0]].points) + ' va affronter ' +
              liste_joueurs[match[1][0]].nom + ' ' + str(
            liste_joueurs[match[1][0]].points) + '\n')
        compteur += 1
    input("Appuyez sur Entrée pour ajouter les résultats.")


def tournament_creator_view():
    questions = {'nom': 'Nom du tournoi :', 'lieu': 'Lieu du tournoi :', 'date': 'Date du tournoi ( JJ/MM/AA ):',
                 'tours':
                     'Nombre de tours :', 'temps': 'Contrôle du temps :', 'desc': 'Description / Remarques :'}
    reponses = {}
    types = {'nom': str, 'lieu': str, 'date': str, 'tours':
        int, 'temps': str, 'desc': str}

    for i, v in questions.items():
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
                        'temps': reponses['temps'],
                        'desc': reponses['desc'],
                        'players': []
                        }
    question = "Souhaitez vous créer un tournoi avec les caractéristiques listées ci-dessus ?"
    reponses = ['Valider le tournoi', 'Quitter']
    option, index = pick(reponses, question, indicator="➤ ")
    if index == 0:
        return tournament_specs
    else:
        return None
