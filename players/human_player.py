"""
Human player implementation for Bird Sort Game
"""

class HumanPlayer:
    """Human player implementation that handles user input"""
    def __init__(self, game):
        """
        Initialize the human player.
        
        Args:
            game: A BirdSortGame instance
        """
        self.game = game
        
    def make_move(self, branch_idx):
        """
        Make a move by selecting a branch.
        
        Args:
            branch_idx: Index of the branch to select
            
        Returns:
            True if a move was made, False otherwise
        """
        return self.game.select_branch(branch_idx)
        
    def get_hint(self, solver=None):
        """
        Get a hint using the provided solver.
        
        Args:
            solver: Optional solver to use for hints
            
        Returns:
            A hint message or None
        """
        if solver:
            return solver.get_hint(self.game.state)
        return None