"""
Pattern Database Heuristics for Bird Sort Game
"""

import os
import pickle
import hashlib
from collections import defaultdict
from utils.timer import Timer

class PatternDatabase:
    """Pattern database for Bird Sort heuristics"""
    def __init__(self, name, num_branches=7, num_colors=5):
        """
        Initialize a pattern database.
        
        Args:
            name: Name of the database
            num_branches: Number of branches in the game
            num_colors: Number of colors in the game
        """
        self.name = name
        self.num_branches = num_branches
        self.num_colors = num_colors
        self.database = {}
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_path(self):
        """Get the path to the cache file"""
        return os.path.join(
            self.cache_dir, 
            f"{self.name}_b{self.num_branches}_c{self.num_colors}.pkl"
        )
    
    def load(self):
        """
        Load the database from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        cache_path = self.get_cache_path()
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    self.database = pickle.load(f)
                print(f"Loaded pattern database from {cache_path} with {len(self.database)} entries")
                return True
            except Exception as e:
                print(f"Error loading pattern database: {e}")
        return False
    
    def save(self):
        """
        Save the database to disk.
        
        Returns:
            True if saved successfully, False otherwise
        """
        cache_path = self.get_cache_path()
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(self.database, f)
            print(f"Saved pattern database to {cache_path} with {len(self.database)} entries")
            return True
        except Exception as e:
            print(f"Error saving pattern database: {e}")
            return False
    
    def get_pattern_key(self, state, color_subset=None):
        """
        Get a key for the pattern database.
        
        Args:
            state: A BirdSortState object
            color_subset: Optional subset of colors to include in the key
            
        Returns:
            A hashable key for the pattern
        """
        # If no color subset is provided, use all colors
        if color_subset is None:
            color_subset = list(range(1, self.num_colors + 1))
        
        # Create a simplified state representation with only the specified colors
        pattern = []
        for branch in state.branches:
            branch_pattern = []
            for bird in branch:
                if bird in color_subset:
                    branch_pattern.append(bird)
            pattern.append(tuple(branch_pattern))
        
        return tuple(pattern)
    
    def get_value(self, state, color_subset=None):
        """
        Get the value for a state from the pattern database.
        
        Args:
            state: A BirdSortState object
            color_subset: Optional subset of colors to include in the key
            
        Returns:
            The value from the database or None if not found
        """
        key = self.get_pattern_key(state, color_subset)
        return self.database.get(key)
    
    def set_value(self, state, value, color_subset=None):
        """
        Set the value for a state in the pattern database.
        
        Args:
            state: A BirdSortState object
            value: Value to store
            color_subset: Optional subset of colors to include in the key
        """
        key = self.get_pattern_key(state, color_subset)
        self.database[key] = value
    
    def build(self, goal_test_func, operators_func, max_states=1000000):
        """
        Build the pattern database using breadth-first search from the goal state.
        
        Args:
            goal_test_func: Function to check if a state is a goal state
            operators_func: Function to generate child states
            max_states: Maximum number of states to process
            
        Returns:
            Number of states processed
        """
        from collections import deque
        from models.state import BirdSortState
        
        timer = Timer("Build Pattern Database")
        timer.start()
        
        # Start with a goal state
        goal_state = self._create_goal_state()
        
        # Initialize queue with goal state
        queue = deque([(goal_state, 0)])  # (state, distance)
        visited = {self.get_pattern_key(goal_state): 0}
        states_processed = 0
        
        while queue and states_processed < max_states:
            state, distance = queue.popleft()
            states_processed += 1
            
            # Apply operators in reverse to get predecessor states
            for pred_state in self._get_predecessors(state):
                key = self.get_pattern_key(pred_state)
                
                if key not in visited:
                    # Store distance in database
                    visited[key] = distance + 1
                    self.database[key] = distance + 1
                    
                    # Add to queue
                    queue.append((pred_state, distance + 1))
            
            # Print progress
            if states_processed % 10000 == 0:
                print(f"Processed {states_processed} states, database size: {len(self.database)}")
        
        timer.stop()
        print(f"Built pattern database with {len(self.database)} entries in {timer.get_elapsed():.2f} seconds")
        
        # Save the database
        self.save()
        
        return states_processed
    
    def _create_goal_state(self):
        """
        Create a goal state for the pattern database.
        
        Returns:
            A BirdSortState object representing a goal state
        """
        from models.state import BirdSortState
        
        # Create a goal state with each color in its own branch
        branches = []
        
        # Add branches with 4 birds of the same color
        for color in range(1, self.num_colors + 1):
            branches.append([color] * 4)
        
        # Add empty branches to reach the required number
        while len(branches) < self.num_branches:
            branches.append([])
        
        return BirdSortState(branches)
    
    def _get_predecessors(self, state):
        """
        Get predecessor states by applying operators in reverse.
        
        Args:
            state: A BirdSortState object
            
        Returns:
            A list of predecessor states
        """
        predecessors = []
        
        # Try moving a bird from each branch to each other branch
        for from_branch in range(state.num_branches):
            if state.is_branch_empty(from_branch):
                continue  # Skip empty branches
                
            # Get the top bird from the source branch
            bird = state.get_top_bird(from_branch)
            
            for to_branch in range(state.num_branches):
                if from_branch == to_branch:
                    continue  # Can't move to the same branch
                    
                if state.is_branch_full(to_branch):
                    continue  # Can't move to a full branch
                
                # Check if this move would be valid in the forward direction
                # (i.e., the reverse move is valid)
                if not state.is_branch_empty(to_branch):
                    top_bird_target = state.get_top_bird(to_branch)
                    if bird != top_bird_target:
                        continue  # Can only stack same-colored birds
                
                # Create a new state
                new_state = state.copy()
                
                # Move the bird
                bird = new_state.branches[from_branch].pop()
                new_state.branches[to_branch].append(bird)
                
                predecessors.append(new_state)
        
        return predecessors


class DisjointPatternDatabase:
    """Disjoint pattern database for Bird Sort heuristics"""
    def __init__(self, num_branches=7, num_colors=5):
        """
        Initialize a disjoint pattern database.
        
        Args:
            num_branches: Number of branches in the game
            num_colors: Number of colors in the game
        """
        self.num_branches = num_branches
        self.num_colors = num_colors
        self.databases = []
        
        # Create disjoint color groups
        self.color_groups = self._create_color_groups()
        
        # Create a database for each color group
        for i, color_group in enumerate(self.color_groups):
            db = PatternDatabase(f"disjoint_{i}", num_branches, num_colors)
            self.databases.append((color_group, db))
    
    def _create_color_groups(self):
        """
        Create disjoint color groups for the pattern database.
        
        Returns:
            A list of color groups
        """
        # Simple strategy: divide colors into roughly equal groups
        colors = list(range(1, self.num_colors + 1))
        
        # For small number of colors, use individual databases
        if self.num_colors <= 3:
            return [[color] for color in colors]
        
        # For medium number of colors, use two groups
        if self.num_colors <= 6:
            mid = self.num_colors // 2
            return [colors[:mid], colors[mid:]]
        
        # For larger number of colors, use three groups
        third = self.num_colors // 3
        return [colors[:third], colors[third:2*third], colors[2*third:]]
    
    def load_all(self):
        """
        Load all pattern databases.
        
        Returns:
            Number of databases loaded successfully
        """
        loaded = 0
        for color_group, db in self.databases:
            if db.load():
                loaded += 1
        return loaded
    
    def build_all(self, goal_test_func, operators_func, max_states=1000000):
        """
        Build all pattern databases.
        
        Args:
            goal_test_func: Function to check if a state is a goal state
            operators_func: Function to generate child states
            max_states: Maximum number of states to process per database
            
        Returns:
            Total number of states processed
        """
        total_states = 0
        for color_group, db in self.databases:
            print(f"Building database for colors {color_group}...")
            states = db.build(goal_test_func, operators_func, max_states)
            total_states += states
        return total_states
    
    def get_heuristic_value(self, state):
        """
        Get the heuristic value for a state using the disjoint pattern databases.
        
        Args:
            state: A BirdSortState object
            
        Returns:
            The heuristic value (sum of values from disjoint databases)
        """
        total = 0
        for color_group, db in self.databases:
            value = db.get_value(state, color_group)
            if value is not None:
                total += value
        return total


def pattern_database_heuristic(state, pdb=None):
    """
    Heuristic function using pattern databases.
    
    Args:
        state: A BirdSortState object
        pdb: Optional pattern database to use
        
    Returns:
        A heuristic value for the state
    """
    # If no pattern database is provided or the lookup fails, fall back to the admissible heuristic
    if pdb is None:
        from search.heuristics import admissible_bird_sort_heuristic
        return admissible_bird_sort_heuristic(state)
    
    value = pdb.get_heuristic_value(state)
    if value is None or value == 0:
        # Fall back to the admissible heuristic
        from search.heuristics import admissible_bird_sort_heuristic
        return admissible_bird_sort_heuristic(state)
    
    return value