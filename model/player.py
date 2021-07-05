from tinydb import TinyDB


# print('**************player.py a été importé correctement')


class Player:
    def __init__(self, nom, prenom, date, sexe):
        self.nom = nom
        self.prenom = prenom
        self.date = date
        self.sexe = sexe
        self.points = 0
        self.classement = 0

        # print(self.nom + ' ' + self.prenom + ' a reçu ' + str(points) + ' points.')
        # db.update({'points' : self.points }, Query().prenom == self.prenom and Query().nom   == self.nom)
        # print()

    def Serialize(self):
        serialized_ply = {}
        for attr, value in vars(self).items():
            serialized_ply[attr] = value
        return serialized_ply

    def GetID(self, global_players_list):
        for k, v in enumerate(global_players_list):
            if v.nom == self.nom and v.prenom == self.prenom:
                return k

    def GetName(self):
        name = self.prenom + ' ' + self.nom
        return name
