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

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use the minimax algorithm to choose the best action based on the heuristic evaluation of game states.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The best action as determined by minimax.
        """

        #TODO
        start_time = time.time()
        best_move = None
        depth_limit = 5 # Set your desired depth limit here
        depth = 1
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= remaining_time / 5:
                print("===============================")
                print(depth)
                break
            try:
                v, m = self.alphaBetaSearch(current_state, depth, start_time, remaining_time)
                best_move = m
            except TimeoutError:
                return best_move
            depth += 1
        #v, m = self.alphaBetaSearch(current_state, depth_limit)
        return best_move
    
    def check_time(self, start_time: float, remaining_time: int):
        elapsed_time = (time.time() - start_time)
        if elapsed_time >= remaining_time:
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
                my_score = current_state.scores[player_id] + self.calculate_diverciteIndex(current_state, player_id)
            else:
                opponent_score = current_state.scores[player_id] + self.calculate_diverciteIndex(current_state, player_id)
        
        return my_score - opponent_score

    def calculate_diverciteIndex(self, current_state: GameState, payer_id) -> int:
        cite_pieces = self.get_cite_piece(current_state)
        diverciteIndex = 0
        for cite in cite_pieces:
            if cite[1].get_owner_id() != payer_id:
                continue
            else:
                # format des neighbours : (neighbour_name: (neighbour_type, (i,j)))
                # format des cités : ("(x, y)", Piece)
                neighbours = current_state.get_neighbours(int(cite[0][1]), int(cite[0][4]))
                colors = set()
                for _, neighbour in neighbours.items():
                    if neighbour[0] != "OUTSIDE" and neighbour[0] != "EMPTY":
                        neighbour_color = neighbour[0].get_type()[0]
                        if neighbour_color not in colors:
                            colors.add(neighbour_color)
                        else:
                            colors.clear()
                            break

            diverciteIndex += self.calculate_diverciteIndex_score(colors)
        return diverciteIndex
    
    def get_cite_piece(self, current_state: GameState) -> list:
        cite_pieces = []
        current_board_json = current_state.get_rep().to_json()
        for coord, piece in current_board_json["env"].items():
            if piece.get_type()[1] == 'C':
                cite_pieces.append((coord, piece))
        return cite_pieces
    
    def calculate_diverciteIndex_score(self, colors:set) -> int:
        # scores to be adjusted
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
        
        if depth == 0:
            return self.calculate_heuristic(current_state), None
        elif current_state.is_done():
            return self.utility(current_state), None

        v = -float('inf')
        m = None
        actions = current_state.generate_possible_heavy_actions()
        evaluated_actions = []
        for action in actions:
            self.check_time(start_time, remaining_time)
            new_state = action.get_next_game_state()
            heuristic_value = self.calculate_heuristic(new_state)
            evaluated_actions.append((heuristic_value, action))

        evaluated_actions.sort(reverse=True, key=lambda x: x[0])
    
        # Choose the number of actions to evaluate
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
        
        v = float('inf')
        m = None
        actions = current_state.generate_possible_heavy_actions()
        evaluated_actions = []
        for action in actions:
            self.check_time(start_time, remaining_time)
            new_state = action.get_next_game_state()
            heuristic_value = self.calculate_heuristic(new_state)
            evaluated_actions.append((heuristic_value, action))
    
        evaluated_actions.sort(key=lambda x: x[0])
    
        # Choose the number of actions to evaluate
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