class Player:
    def __init__(self, nom, prenom, date, sexe):
        self.nom = nom
        self.prenom = prenom
        self.date = date
        self.sexe = sexe
        self.classement = 0

    def GetID(self, global_players_list):
        for k, v in enumerate(global_players_list):
            if v.nom == self.nom and v.prenom == self.prenom:
                return k

    def GetName(self):
        name = self.prenom + ' ' + self.nom
        return name
