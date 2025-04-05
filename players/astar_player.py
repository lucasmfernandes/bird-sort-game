"""
A* AI player implementation for Bird Sort Game
"""

from players.ai_player import AIPlayer
from search.astar import astar_search, extract_solution_path, get_child_states

class AStarPlayer(AIPlayer):
    """AI player that uses A* search to find optimal moves"""
    def __init__(self, game, weight=1.5):
        """
        Initialize the A* AI player.
        
        Args:
            game: A BirdSortGame instance
            weight: Weight for the heuristic (1.0 = standard A*, >1.0 = weighted A*)
        """
        super().__init__(game)
        self.weight = weight
        self.solution_path = None
        self.solution_index = 0
        
    def get_next_move(self):
        """
        Calculate the next move using A* search.
        
        Returns:
            A tuple of (from_branch, to_branch) or (None, None) if no move is available
        """
        # Check if we need to find a solution
        if not self.solution_path or self.solution_index >= len(self.solution_path) - 1:
            self._find_solution()
            self.solution_index = 0
            
        # If we have a solution, get the next move
        if self.solution_path and self.solution_index < len(self.solution_path) - 1:
            current_state = self.game.state
            next_state = self.solution_path[self.solution_index + 1]
            
            # Find the branches that changed
            from_branch = None
            to_branch = None
            
            for i in range(len(current_state.branches)):
                if len(current_state.branches[i]) > len(next_state.branches[i]):
                    from_branch = i
                elif len(current_state.branches[i]) < len(next_state.branches[i]):
                    to_branch = i
            
            self.solution_index += 1
            return from_branch, to_branch
            
        return None, None
    
    def _find_solution(self):
        """Find a solution using A* search"""
        goal_node = astar_search(
            self.game.state,
            lambda state: state.is_goal_state(),
            get_child_states,
            weight=self.weight
        )
        
        if goal_node:
            self.solution_path = extract_solution_path(goal_node)
        else:
            self.solution_path = None