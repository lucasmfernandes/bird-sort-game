"""
Base AI player implementation for Bird Sort Game
"""

class AIPlayer:
    """Base class for AI players"""
    def __init__(self, game):
        """
        Initialize the AI player.
        
        Args:
            game: A BirdSortGame instance
        """
        self.game = game
        
    def make_move(self):
        """
        Make a move based on AI algorithm.
        
        Returns:
            True if a move was made, False otherwise
        """
        from_branch, to_branch = self.get_next_move()
        if from_branch is not None and to_branch is not None:
            # Make the move
            self.game.select_branch(from_branch)
            return self.game.select_branch(to_branch)
        return False
        
    def get_next_move(self):
        """
        Calculate the next move without applying it.
        
        Returns:
            A tuple of (from_branch, to_branch) or (None, None) if no move is available
        """
        raise NotImplementedError("Subclasses must implement this method")