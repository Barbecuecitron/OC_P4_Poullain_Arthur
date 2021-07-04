#print('**************tournament.py a été importé correctement')
from model.player import Player
class Tournament:
    def __init__(self, nom, lieu, date, tours,temps,desc):
        self.nom = nom
        self.lieu = lieu
        self.date = date
        self.tours = tours
        self.rounds = []
        self.players = []
        self.phase = 1
        self.temps = temps
        self.desc = desc

    def AddPlayer(self, nom, prenom, date, sexe):
        added_player = Player(nom,prenom,date,sexe)
        self.players.append(added_player)

    def Serialize(self):
        serialized_t = {
            'nom' : self.nom,
            'lieu' : self.lieu,
            'date' : self.date,
            'tours' : self.tours,
            'rounds' : self.rounds,
            'temps' : self.temps,
            'desc' : self.desc

        }

        return serialized_t

    def exists(self):
        return True