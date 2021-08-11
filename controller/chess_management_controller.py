import datetime

from helpers.notify_func import notify
from helpers.clear_func import clear
from model.player import Player
from model.round import Round
from model.tournament import Tournament
from model.functions import save, load

gb_tournaments = []
gb_players = []


# Création de la classe Controller pour le MVC
class ChessManagementController:

    def load_chess_management(self):
        global gb_tournaments, gb_players
        load(gb_tournaments, gb_players)

    def save_chess_management(self):
        global gb_tournaments, gb_players
        save(gb_tournaments, gb_players)

    # Check if a player already fought another one
    def did_player_already_gamed(self, player1, player2, tournament):
        for chess_round in tournament.rounds:
            for game in chess_round.games:
                if game[0][0] == player1 and game[1][0] == player2 \
                        or game[1][0] == player1 and game[0][0] == player2:
                    return True
        return False

    # Is the player already set for a match ?
    def is_player_already_in_a_game(self, player, games):
        for game in games:
            if game[0][0] == player or game[1][0] == player:
                return True
        return False

    # Let's use player pairing for our matches
    def create_pairs(self, t):
        global gb_players
        # Premier tour :
        if len(t.rounds) == 0:
            # Sorting players by classement

            sorted_players = sorted(t.players, key=lambda ply: ply.classement,
                                    reverse=True)
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
        # Second tour et +
        else:
            # Sort according to points
            sorted_players = sorted(t.players, key=lambda ply: ply.points,
                                    reverse=True)

            for player_idx in range(len(sorted_players)):
                # Don't start at 0 since we are going to check the previous idx
                if player_idx == 0:
                    pass
                else:
                    # Check if both have the same ammount of points than the previous player
                    if sorted_players[player_idx].points == sorted_players[player_idx-1].points:
                        # Check If our actual classement is better than the previous player
                        if sorted_players[player_idx].classement < sorted_players[player_idx-1].classement:
                            # Swap their position
                            sorted_players[player_idx-1], sorted_players[player_idx] \
                                = sorted_players[player_idx], sorted_players[player_idx-1]
            games = []

            for player_index in range(0, len(sorted_players)):
                if self.is_player_already_in_a_game(sorted_players[player_index],
                                                    games):
                    continue
                for opposite_player_index in range(0, len(sorted_players)):
                    # Not the same player
                    # Opposite player not already in a game this round
                    # Both player not already matched together
                    if sorted_players[player_index] != sorted_players[
                        opposite_player_index] and not self.is_player_already_in_a_game(
                        sorted_players[opposite_player_index],
                        games) and not self.did_player_already_gamed(sorted_players[player_index],
                                                                     sorted_players[opposite_player_index], t):
                        games.append(
                            ([sorted_players[player_index], 0],
                             [sorted_players[opposite_player_index], 0]))

                        break
            return games

    # Create & handle our round matches
    def handle_match(self, games, tournoi):
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
    def play_tournament(self, tournoi):
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
        chess_round = self.create_pairs(tournoi)
        if len(chess_round) < 2:
            notify("ERROR",
                   "Tous les matchs de " + tournoi.nom + " ont été joué.")
            notify("SUCCESS", tournoi.nom + " est terminé")
            return None
        notify('SUCCESS',
               str(len(tournoi.rounds)) + " rounds trouvés dans le tournoi")
        return chess_round, tournoi

    # Adds a round to a tournament
    def add_round(self, tournoi, chess_round):
        tournoi.rounds.append(chess_round)

    # Add a new player
    def add_player(self, ply):
        ply_obj = Player(ply['nom'], ply['prenom'], ply['date'], ply['sexe'], 0)
        gb_players.append(ply_obj)

    # Add an existing player to a tournament
    def add_player_to_tournament(self, tournoi, ply_picker):
        global gb_players
        ply = gb_players[ply_picker]
        if len(tournoi.players) > 7:
            notify("ERROR", "Ce tournoi comporte dèja 8 joueurs")
            return False
        else:
            tournoi.players.append(ply)
            return True

    def get_all_tournaments(self):
        global gb_tournaments
        return gb_tournaments

    def get_all_players(self):
        global gb_players
        return gb_players

    def create_tournament(self, tournament):
        global gb_tournaments
        if tournament is None:
            return None
        tournament_obj = Tournament(tournament['nom'], tournament['lieu'],
                                    tournament['date'], tournament['tours'],
                                    tournament['rounds'],
                                    tournament['players'],
                                    tournament['temps'], tournament['desc'])
        gb_tournaments.append(tournament_obj)
        notify("SUCCESS", tournament_obj.nom + ' a bien été crée !')

    # valide debugged
    def pick_tournament(self, tournoi_idx):
        global gb_tournaments
        if tournoi_idx is None:
            return None
        return gb_tournaments[tournoi_idx]

    def quitter(self):
        notify('SUCCESS', 'Vous avez quitté le menu')
        quit()
        pass
