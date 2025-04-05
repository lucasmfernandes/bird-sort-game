"""
IDA* AI player implementation for Bird Sort Game
"""

from players.ai_player import AIPlayer
from search.iterative_deepening import iterative_deepening_a_star, extract_solution_moves
from utils.timer import Timer

class IDAStarPlayer(AIPlayer):
    """AI player that uses IDA* search to find optimal moves"""
    def __init__(self, game, max_depth=50):
        """
        Initialize the IDA* AI player.
        
        Args:
            game: A BirdSortGame instance
            max_depth: Maximum search depth
        """
        super().__init__(game)
        self.max_depth = max_depth
        self.solution_moves = None
        self.solution_index = 0
        
    def get_next_move(self):
        """
        Calculate the next move using IDA* search.
        
        Returns:
            A tuple of (from_branch, to_branch) or (None, None) if no move is available
        """
        # Check if we need to find a solution
        if not self.solution_moves or self.solution_index >= len(self.solution_moves):
            self._find_solution()
            self.solution_index = 0
            
        # If we have a solution, get the next move
        if self.solution_moves and self.solution_index < len(self.solution_moves):
            move = self.solution_moves[self.solution_index]
            self.solution_index += 1
            return move
            
        return None, None
    
    def _find_solution(self):
        """Find a solution using IDA* search"""
        timer = Timer("IDA* Search")
        timer.start()
        
        # Track statistics
        stats = {"nodes_expanded": 0, "max_depth_reached": 0, "iterations": 0}
        
        # Run IDA* search
        goal_node = iterative_deepening_a_star(
            self.game.state,
            lambda state: state.is_goal_state(),
            self.max_depth,
            stats
        )
        
        timer.stop()
        
        if goal_node:
            self.solution_moves = extract_solution_moves(goal_node)
            print(f"IDA* found solution with {len(self.solution_moves)} moves")
            print(f"Nodes expanded: {stats['nodes_expanded']}")
            print(f"Max depth reached: {stats['max_depth_reached']}")
            print(f"Iterations: {stats['iterations']}")
            print(f"Time: {timer.get_elapsed():.4f} seconds")
        else:
            self.solution_moves = None
            print("IDA* could not find a solution")