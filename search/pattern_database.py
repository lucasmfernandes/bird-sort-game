"""
Pattern Database for Bird Sort Heuristics
"""

class PatternDatabaseHeuristic:
    """
    A pattern database heuristic for Bird Sort.
    Pre-computes and caches heuristic values for common patterns.
    """
    def __init__(self):
        # Initialize pattern database
        self.pattern_cache = {}
        
    def get_pattern_key(self, state):
        """Convert state to a pattern key for the database"""
        # Create a simplified representation of the state
        # Focus on color distribution, not exact positions
        color_distribution = {}
        
        for branch_idx, branch in enumerate(state.branches):
            for bird in branch:
                if bird not in color_distribution:
                    color_distribution[bird] = {}
                
                if branch_idx not in color_distribution[bird]:
                    color_distribution[bird][branch_idx] = 0
                
                color_distribution[bird][branch_idx] += 1
        
        # Convert to a hashable representation
        key_parts = []
        for color in sorted(color_distribution.keys()):
            color_part = [color]
            for branch in range(len(state.branches)):
                color_part.append(color_distribution[color].get(branch, 0))
            key_parts.append(tuple(color_part))
        
        return tuple(key_parts)
    
    def calculate_heuristic(self, state):
        """Calculate the heuristic value for a state"""
        # Similar to iterative_deepening_heuristic but more focused on patterns
        birds_to_move = 0
        
        # Find best branch for each color
        color_best_branch = {}
        color_counts = {}
        
        for branch_idx, branch in enumerate(state.branches):
            for bird in branch:
                if bird not in color_counts:
                    color_counts[bird] = {}
                
                if branch_idx not in color_counts[bird]:
                    color_counts[bird][branch_idx] = 0
                
                color_counts[bird][branch_idx] += 1
        
        for color, branches in color_counts.items():
            best_branch = max(branches.items(), key=lambda x: x[1])[0]
            color_best_branch[color] = best_branch
        
        # Count birds that need to be moved
        for branch_idx, branch in enumerate(state.branches):
            for bird in branch:
                if branch_idx != color_best_branch.get(bird, branch_idx):
                    birds_to_move += 1
        
        return birds_to_move
    
    def __call__(self, state):
        """Get heuristic value, using cache if available"""
        key = self.get_pattern_key(state)
        
        if key not in self.pattern_cache:
            self.pattern_cache[key] = self.calculate_heuristic(state)
            
        return self.pattern_cache[key]