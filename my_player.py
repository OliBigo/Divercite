from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import hashlib

class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game that makes random moves.

    Attributes:
        piece_type (str): piece type of the player
    """

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
        depth_limit = 5  # Set your desired depth limit here
        v, m = self.alphaBetaSearch(current_state, depth_limit)
        return m
    
    def alphaBetaSearch(self, current_state: GameState, depth: int):
        v, m = self.maxValue(current_state, -float('inf'), float('inf'), depth)
        return v, m
    
    def calculate_heuristic(self, current_state: GameState):
        my_score = 0
        opponent_score = 0
        for player in current_state.get_players():
            if player.get_id() == self.get_id():
                my_score = current_state.scores[player.get_id()]
            else:
                opponent_score = current_state.scores[player.get_id()]
        return my_score - opponent_score
    
    def maxValue(self, current_state: GameState, alpha, beta, depth: int):
        if depth == 0 or current_state.is_done():
            return self.calculate_heuristic(current_state), None
        
        v = -float('inf')
        m = None
        actions = current_state.generate_possible_heavy_actions()
        evaluated_actions = []
        for action in actions:
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
            new_state = action.get_next_game_state()
            new_v, new_m = self.minValue(new_state, alpha, beta, depth - 1)
            if new_v > v:
                v = new_v
                m = action
                alpha = max(alpha, v)
            if v >= beta:
                return v, m
        
        return v, m
    
    def minValue(self, current_state: GameState, alpha, beta, depth: int):
        if depth == 0 or current_state.is_done():
            return self.calculate_heuristic(current_state), None
        
        v = float('inf')
        m = None
        actions = current_state.generate_possible_heavy_actions()
        evaluated_actions = []
        for action in actions:
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
            new_state = action.get_next_game_state()
            new_v, new_m = self.maxValue(new_state, alpha, beta, depth - 1)
            if new_v < v:
                v = new_v
                m = action
                beta = min(beta, v)
            if v <= alpha:
                return v, m
        
        return v, m
