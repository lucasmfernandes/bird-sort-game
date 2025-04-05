"""
Bird Sort State Representation
"""

class BirdSortState:
    """
    Represents a state in the Bird Sort game.
    """
    def __init__(self, branches):
        """
        Initialize a state with the given branches configuration.
        
        Args:
            branches: A list of lists, where each inner list represents a branch
                     and contains integers representing bird colors (e.g., 1, 2, 3, etc.)
                     The last element in each list is the top bird.
        """
        self.branches = branches
        self.num_branches = len(branches)
        
    def __eq__(self, other):
        """Needed for the visited list to avoid loops"""
        if isinstance(other, self.__class__):
            return self.branches == other.branches
        return False
    
    def __hash__(self):
        """Needed for the visited list to avoid loops"""
        # Convert lists to tuples for hashing
        return hash(tuple(tuple(branch) for branch in self.branches))
    
    def __str__(self):
        """String representation of the state"""
        result = ""
        for i, branch in enumerate(self.branches):
            result += f"Branch {i+1}: {branch}\n"
        return result
    
    def copy(self):
        """Create a deep copy of the state"""
        return BirdSortState([branch.copy() for branch in self.branches])
    
    def is_branch_complete(self, branch_idx):
        """Check if a branch is complete (has 4 birds of the same color)"""
        branch = self.branches[branch_idx]
        return len(branch) == 4 and all(bird == branch[0] for bird in branch)
    
    def is_branch_empty(self, branch_idx):
        """Check if a branch is empty"""
        return len(self.branches[branch_idx]) == 0
    
    def is_branch_full(self, branch_idx):
        """Check if a branch is full (has 4 birds)"""
        return len(self.branches[branch_idx]) == 4
    
    def get_top_bird(self, branch_idx):
        """Get the top bird from a branch"""
        if self.is_branch_empty(branch_idx):
            return None
        return self.branches[branch_idx][-1]
    
    def is_goal_state(self):
        """Check if this is a goal state"""
        for branch in self.branches:
            if not branch:
                continue  # Empty branch is fine
                
            # Check if all birds in branch are the same color
            if len(branch) == 4 and all(bird == branch[0] for bird in branch):
                continue  # This branch is good
            elif len(branch) > 0:
                return False  # Branch has birds but is not complete
        
        return True  # All branches are either empty or complete