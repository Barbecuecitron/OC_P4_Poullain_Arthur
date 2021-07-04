from tinydb import TinyDB, Query
from model.player import Player
from model.tournament import Tournament


def add_player(nom, prenom, date, sexe):
    ply = {'nom': nom,
           'prenom': prenom,
           'date': date,
           'sexe': sexe,
           'points': 0
           }
    newplayer = Player(ply)

    # TinyDB('db.json').table('players').insert(ply)
    print(ply['nom'] + ' ' + ply['prenom'] + ' ajouté avec succés !')
    return ply


def update_player(players, nom, prenom):
    for player in players:
        print(player.nom)


# Load Json DB
def load_db(database):
    playersdb = []
    for ply in database:
        playersdb.append(Player(ply))
    return playersdb


# Quickly create players
def add_fake_players(num):
    fakeplayers = []
    players_ex = [['De Gaulle', 'Charles', '11/02/1965', 'homme'],
                  ['Bonaparte', 'Napoleon', '11/02/1925', 'homme'],
                  ['Hudson', 'Saul', '11/02/1815', 'homme'],
                  ['Duchamps', 'Marcel', '11/02/1815', 'homme'],
                  ['Carson', 'Anne', '11/02/1815', 'femme'],
                  ['Smith', 'Patti', '11/02/1815', 'femme'],
                  ['Carson', 'Anne', '11/02/1815', 'femme'],
                  ['Legros', 'LouisVI', '11/02/1815', 'homme'],
                  ['Bigeard', 'Marcel', '11/02/1815', 'homme'],
                  ]

    for i in range(0, num):
        fakeplayers.append(add_player(players_ex[i][0], players_ex[i][1], players_ex[i][2], players_ex[i][3]))
    print(str(num) + ' personnages ont été générés')
    return fakeplayers


def create_tournament():
    questions = ['Nom du tournoi :', 'Lieu du tournoi :', 'Date du tournoi :', 'Nombre de tours :',
                 'Nombre de tournées :']
    reponses = []

    for i in range(0, len(questions)):
        print('Création des caractéristiques :\n' + str(i + 1) + '/' + str(len(questions)))
        print(questions[i])
        rep = input()
        reponses.insert(i, rep)

    print('Vous vous apprêtez à créer un tournoi avec les caracteristiques suivantes :')

    for i in range(0, len(questions)):
        print(questions[i], reponses[i])

    print("Entrez 'ok' pour passer à l'ajout des joueurs, n'importe quelle autre entrée vous permettra de recommencer")

    choix = input()
    if choix.lower() == 'ok':
        tournament_specs = {'nom': reponses[0],
                            'lieu ': reponses[1],
                            'date': reponses[2],
                            'tours': reponses[3],
                            'tournees': reponses[4],
                            }
        active_tournament = Tournament(tournament_specs)
        TinyDB(str(reponses[0]) + '.json').table('tournoi').insert(tournament_specs)
    else:
        create_tournament()

    print('Le Tournoi ' + reponses[0] + ' a bien été crée !')

    players = []  # Our total players
    plycarac = ['Nom du joueur :', 'Prenom du joueur :', 'Date de naissance :', 'Sexe']

    for plynum in range(0, 8):
        ply = []
        print('Joueur ' + str(plynum + 1) + ' / ' + str(8))
        for idxquestion in range(0, len(plycarac)):
            print(plycarac[idxquestion])
            ply.insert(idxquestion, input())
        players.insert(plynum, ply)  # Add our local 'ply' to our players
    print(players)


def main():
    db = TinyDB('db.json').table('players')
    players = add_fake_players(8)
    # create_tournament()
    # print(players[0].points)
    # print(db.get(doc_id=1)['points'])
    for player in players:
        res = db.insert(player)
        pass


if __name__ == '__main__':
    main()
