"""
Bird Sort Game Logic
"""

from models.state import BirdSortState
from models.generator import create_random_initial_state

class BirdSortGame:
    """
    Manages the game state and rules for Bird Sort.
    """
    def __init__(self, num_branches=7, num_colors=5, initial_state=None):
        """
        Initialize a new game.
        
        Args:
            num_branches: Number of branches (4-10)
            num_colors: Number of colors (3-8)
            initial_state: Optional initial state, if None a random state is generated
        """
        self.num_branches = num_branches
        self.num_colors = num_colors
        
        if initial_state:
            self.state = initial_state
        else:
            self.state = create_random_initial_state(num_branches, num_colors)
            
        self.selected_bird = None
        self.selected_branch = None
        self.moves = 0
        self.history = []  # For undo functionality
    
    def select_branch(self, branch_idx):
        """
        Handle selection of a branch.
        
        Args:
            branch_idx: Index of the branch to select
            
        Returns:
            True if a move was made, False otherwise
        """
        if branch_idx < 0 or branch_idx >= self.num_branches:
            return False
            
        if self.selected_bird is None:
            # Try to select a bird
            if not self.state.is_branch_empty(branch_idx):
                # Save current state for undo
                self.history.append(self.state.copy())
                
                # Select the top bird
                self.selected_bird = self.state.branches[branch_idx].pop()
                self.selected_branch = branch_idx
                return True
        else:
            # Try to place the selected bird
            if self.state.is_branch_full(branch_idx):
                # Branch is full, return bird to original branch
                self.state.branches[self.selected_branch].append(self.selected_bird)
                self.selected_bird = None
                self.selected_branch = None
                return False
                
            # Check if move is valid (empty branch or same color on top)
            if (self.state.is_branch_empty(branch_idx) or 
                self.state.get_top_bird(branch_idx) == self.selected_bird):
                # Valid move
                self.state.branches[branch_idx].append(self.selected_bird)
                self.selected_bird = None
                self.selected_branch = None
                self.moves += 1
                return True
            else:
                # Invalid move, return bird to original branch
                self.state.branches[self.selected_branch].append(self.selected_bird)
                self.selected_bird = None
                self.selected_branch = None
                return False
                
        return False
    
    def undo(self):
        """
        Undo the last move.
        
        Returns:
            True if a move was undone, False otherwise
        """
        if not self.history:
            return False
            
        self.state = self.history.pop()
        self.selected_bird = None
        self.selected_branch = None
        self.moves -= 1
        return True
    
    def is_solved(self):
        """
        Check if the game is solved.
        
        Returns:
            True if the game is solved, False otherwise
        """
        return self.state.is_goal_state()
    
    def reset(self):
        """Reset the game with a new random state"""
        self.state = create_random_initial_state(self.num_branches, self.num_colors)
        self.selected_bird = None
        self.selected_branch = None
        self.moves = 0
        self.history = []