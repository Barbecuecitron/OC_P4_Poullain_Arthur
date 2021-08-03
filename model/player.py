class Player:
    def __init__(self, nom, prenom, date, sexe):
        self.nom = nom
        self.prenom = prenom
        self.date = date
        self.sexe = sexe
        self.classement = 0

    def get_name(self):
        name = self.prenom + ' ' + self.nom
        return name
