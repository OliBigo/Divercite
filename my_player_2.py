from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import time

class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game that makes random moves.

    Attributes:
        piece_type (str): piece type of the player
    """
    #python main_divercite.py -t local my_player_2.py my_player.py

    def __init__(self, piece_type: str, name: str = "MyPlayer"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type, name)
        self.is_first_move = True
        self.move_number = 0

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use the minimax algorithm to choose the best action based on the heuristic evaluation of game states.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The best action as determined by minimax.
        """

        #TODO
        self.move_number += 1
        start_time = time.time()
        best_move = None
        max_depth = 0
        # Vérifification de la profondeur maximale que le joueur pourra atteindre
        for player_pieces_left in current_state.players_pieces_left.values():
            for pieces_by_color in player_pieces_left.values():
                max_depth += pieces_by_color
        if self.is_first_move:
            # Aucune recherche pour le premier coup
            for action in current_state.generate_possible_heavy_actions():
                self.is_first_move = False
                return action
        else:
            # Initialisation de la profondeur de recherche à 1
            depth = 1
            while True:
                # Vérifier s'il reste du temps
                self.check_time(start_time, remaining_time)
                try:
                    # S'il reste du temps, lancer la recherche avec la depth actuelle
                    v, m = self.alphaBetaSearch(current_state, depth, start_time, remaining_time)
                    best_move = m
                except TimeoutError:
                    # Retroune le meilleur coup si on atteint la limite de temps
                    return best_move
                # Incrémentation de la profondeur si on a pas atteint la profondeur max (IDS)
                if depth < max_depth:
                    depth += 1
                else:
                    break
        # Retourne le meilleur coup si on atteint la profondeur maximale
        return best_move
    
    def check_time(self, start_time: float, remaining_time: int):
        elapsed_time = time.time() - start_time
        if elapsed_time >= remaining_time / 5:
            raise TimeoutError
    
    def alphaBetaSearch(self, current_state: GameState, depth: int, start_time: float, remaining_time: float):
        v, m = self.maxValue(current_state, -float('inf'), float('inf'), depth, start_time, remaining_time)
        return v, m
    
    def calculate_heuristic(self, current_state: GameState) -> int:
        my_score = 0
        opponent_score = 0
        for player in current_state.get_players():
            player_id = player.get_id()
            if player_id == self.get_id():
                # Résultat de l'heuristique en deux parties : score actuel et Divercité index
                my_score = current_state.scores[player_id] + self.calculate_diverciteIndex(current_state, player_id)
            else:
                opponent_score = current_state.scores[player_id] + self.calculate_diverciteIndex(current_state, player_id)

        # On retroune la différence des deux scores comme résultat de l'heuristique
        return my_score - opponent_score

    def calculate_diverciteIndex(self, current_state: GameState, player_id) -> int:
        # Retorune une liste des cités
        cite_pieces = self.get_cite_piece(current_state)
        diverciteIndex = 0
        # Pour chaque cité du joueur actuel, on regarde combien de ressources de couleurs différentes y sont collées
        for cite in cite_pieces:
            if cite[1].get_owner_id() != player_id:
                continue
            else:
                # format des neighbours : (neighbour_name: (neighbour_type, (i,j)))
                # format des cités : ("(x, y)", Piece)
                neighbours = current_state.get_neighbours(int(cite[0][1]), int(cite[0][4]))
                colors = set()
                # Pour chaque voisin de la cité évaluée, on ajoute la couleur a colors si la couleur
                # Ne s'y retrouve pas déjà
                for neighbour in neighbours.values():
                    if neighbour[0] != "OUTSIDE" and neighbour[0] != "EMPTY":
                        neighbour_color = neighbour[0].get_type()[0]
                        if neighbour_color not in colors:
                            colors.add(neighbour_color)
                        else:
                            # Si la couleur s'y trouve déjà -> Divercité impossible
                            colors.clear()
                            break

            # Vérification de la disponibilité des pièces nécessaire à la complétion d'un Divercité
            if len(colors) > 0 and len(colors) < 4:
                all_colors = {'R','G','B','Y'}
                missing_colors = all_colors - colors
                for color in missing_colors:
                    resource_index = color + 'R'
                    nb_resources_left = current_state.players_pieces_left[player_id][resource_index]
                    if nb_resources_left == 0:
                        colors.clear()
                        break

            # Si une éventuelle Divercité est possible avec cette cité et que le joueur a les pièces nécessaires, 
            # on ajoute à l'index le score de la cité actuelle
            diverciteIndex += self.calculate_diverciteIndex_score(colors)
        return diverciteIndex
    
    # Fonction utilisée pour obtenir les cité sur le board
    def get_cite_piece(self, current_state: GameState) -> list:
        cite_pieces = []
        current_board_json = current_state.get_rep().to_json()
        for coord, piece in current_board_json["env"].items():
            if piece.get_type()[1] == 'C':
                cite_pieces.append((coord, piece))
        return cite_pieces
    
    def calculate_diverciteIndex_score(self, colors:set) -> int:
        score_mapping = {1: 0, 2: 2, 3: 3, 4: 5}
        return score_mapping.get(len(colors), 0)
        
    def utility(self, current_state: GameState):
        my_score = 0
        opponent_score = 0
        for player in current_state.get_players():
            if player.get_id() == self.get_id():
                my_score = current_state.scores[player.get_id()]
            else:
                opponent_score = current_state.scores[player.get_id()]
        return my_score - opponent_score
    
    def maxValue(self, current_state: GameState, alpha, beta, depth: int, start_time: float, remaining_time: float):
        self.check_time(start_time, remaining_time)
        
        # Vérification 
        if depth == 0:
            return self.calculate_heuristic(current_state), None
        elif current_state.is_done():
            return self.utility(current_state), None

        # Évaluation des actions possibles
        v = -float('inf')
        m = None
        actions = current_state.generate_possible_heavy_actions()
        evaluated_actions = []
        for action in actions:
            self.check_time(start_time, remaining_time)
            new_state = action.get_next_game_state()
            heuristic_value = self.calculate_heuristic(new_state)
            evaluated_actions.append((heuristic_value, action))

         # Tri des actions 
        evaluated_actions.sort(reverse=True, key=lambda x: x[0])
    
        # Division par 3 des actions à évaluer
        number_of_actions = len(evaluated_actions) // 3
        if number_of_actions == 0:
            number_of_actions = 1
        top_actions = evaluated_actions[:number_of_actions]

        for heuristic_value, action in top_actions:
            self.check_time(start_time, remaining_time)
            new_state = action.get_next_game_state()
            new_v, new_m = self.minValue(new_state, alpha, beta, depth - 1, start_time, remaining_time)
            if new_v > v:
                v = new_v
                m = action
                alpha = max(alpha, v)
            if v >= beta:
                return v, m
        
        return v, m
    
    def minValue(self, current_state: GameState, alpha, beta, depth: int, start_time: float, remaining_time: float):
        self.check_time(start_time, remaining_time)
        
        if depth == 0:
            return self.calculate_heuristic(current_state), None
        elif current_state.is_done():
            return self.utility(current_state), None
        
        # Évaluation des actions possibles
        v = float('inf')
        m = None
        actions = current_state.generate_possible_heavy_actions()
        evaluated_actions = []
        for action in actions:
            self.check_time(start_time, remaining_time)
            new_state = action.get_next_game_state()
            heuristic_value = self.calculate_heuristic(new_state)
            evaluated_actions.append((heuristic_value, action))
    
        # Tri des actions 
        evaluated_actions.sort(key=lambda x: x[0])
    
        # Division par 3 des actions à évaluer
        number_of_actions = len(evaluated_actions) // 3
        if number_of_actions == 0:
            number_of_actions = 1
        top_actions = evaluated_actions[:number_of_actions]

        for heuristic_value, action in top_actions:
            self.check_time(start_time, remaining_time)
            new_state = action.get_next_game_state()
            new_v, new_m = self.maxValue(new_state, alpha, beta, depth - 1, start_time, remaining_time)
            if new_v < v:
                v = new_v
                m = action
                beta = min(beta, v)
            if v <= alpha:
                return v, m
        
        return v, m