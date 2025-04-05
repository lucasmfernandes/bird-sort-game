"""
Iterative Deepening Search for Bird Sort Game
"""

from collections import deque
from search.heuristics import iterative_deepening_heuristic
from utils.timer import Timer

def get_child_states(state):
    """
    Generate all possible child states by applying valid operators.
    
    Args:
        state: A BirdSortState object
        
    Returns:
        A list of valid child states
    """
    children = []
    
    # Try moving a bird from each branch to each other branch
    for from_branch in range(state.num_branches):
        if state.is_branch_empty(from_branch):
            continue  # Skip empty branches
            
        for to_branch in range(state.num_branches):
            if from_branch == to_branch:
                continue  # Can't move to the same branch
                
            if state.is_branch_full(to_branch):
                continue  # Can't move to a full branch
                
            # Get the top bird from the source branch
            bird = state.get_top_bird(from_branch)
            
            # If target branch is not empty, check if the top bird matches
            if not state.is_branch_empty(to_branch):
                top_bird_target = state.get_top_bird(to_branch)
                if bird != top_bird_target:
                    continue  # Can only stack same-colored birds
            
            # Create a new state
            new_state = state.copy()
            
            # Move the bird
            bird = new_state.branches[from_branch].pop()
            new_state.branches[to_branch].append(bird)
            
            children.append(new_state)
    
    return children

class IDSNode:
    """Node for Iterative Deepening Search"""
    def __init__(self, state, parent=None, depth=0, from_branch=None, to_branch=None):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.from_branch = from_branch
        self.to_branch = to_branch
        self.h_value = iterative_deepening_heuristic(state)
    
    def __lt__(self, other):
        # For priority queue comparison
        return self.h_value < other.h_value

def depth_limited_search(initial_state, goal_test_func, max_depth, stats=None):
    """
    Depth-limited search algorithm.
    
    Args:
        initial_state: The initial state
        goal_test_func: Function to check if a state is a goal state
        max_depth: Maximum search depth
        stats: Optional dictionary to track statistics
        
    Returns:
        A solution node or None if no solution is found
    """
    if stats is None:
        stats = {"nodes_expanded": 0, "max_depth_reached": 0}
    
    # Check if initial state is goal state
    if goal_test_func(initial_state):
        return IDSNode(initial_state)
    
    # Initialize stack with initial state
    stack = [IDSNode(initial_state)]
    visited = set()
    
    while stack:
        # Get the next node
        node = stack.pop()
        
        # Skip if we've seen this state before
        state_hash = hash(node.state)
        if state_hash in visited:
            continue
        visited.add(state_hash)
        
        # Track statistics
        stats["nodes_expanded"] += 1
        stats["max_depth_reached"] = max(stats["max_depth_reached"], node.depth)
        
        # Check if we've reached the maximum depth
        if node.depth >= max_depth:
            continue
        
        # Generate child states
        children = []
        for i, from_branch in enumerate(node.state.branches):
            if not from_branch:
                continue  # Skip empty branches
                
            for j in range(len(node.state.branches)):
                if i == j:
                    continue  # Can't move to the same branch
                    
                # Check if move is valid
                if (node.state.is_branch_full(j) or 
                    (not node.state.is_branch_empty(j) and 
                     node.state.get_top_bird(i) != node.state.get_top_bird(j))):
                    continue
                
                # Create new state
                new_state = node.state.copy()
                bird = new_state.branches[i].pop()
                new_state.branches[j].append(bird)
                
                # Create child node
                child = IDSNode(new_state, node, node.depth + 1, i, j)
                
                # Check if this is a goal state
                if goal_test_func(child.state):
                    return child
                
                # Add to children
                children.append(child)
        
        # Sort children by heuristic value (most promising first)
        children.sort()
        
        # Add children to stack (in reverse order so most promising is popped first)
        stack.extend(reversed(children))
    
    # No solution found within depth limit
    return None

def iterative_deepening_search(initial_state, goal_test_func, max_depth=100, stats=None):
    """
    Iterative deepening search algorithm.
    
    Args:
        initial_state: The initial state
        goal_test_func: Function to check if a state is a goal state
        max_depth: Maximum search depth
        stats: Optional dictionary to track statistics
        
    Returns:
        A solution node or None if no solution is found
    """
    if stats is None:
        stats = {"nodes_expanded": 0, "max_depth_reached": 0, "iterations": 0}
    
    timer = Timer("IDS")
    timer.start()
    
    for depth in range(1, max_depth + 1):
        stats["iterations"] += 1
        
        # Run depth-limited search
        result = depth_limited_search(initial_state, goal_test_func, depth, stats)
        
        if result:
            # Solution found
            timer.stop()
            stats["time"] = timer.get_elapsed()
            return result
    
    # No solution found within max_depth
    timer.stop()
    stats["time"] = timer.get_elapsed()
    return None

def iterative_deepening_a_star(initial_state, goal_test_func, max_depth=100, stats=None):
    """
    Iterative deepening A* search algorithm.
    
    Args:
        initial_state: The initial state
        goal_test_func: Function to check if a state is a goal state
        max_depth: Maximum search depth
        stats: Optional dictionary to track statistics
        
    Returns:
        A solution node or None if no solution is found
    """
    if stats is None:
        stats = {"nodes_expanded": 0, "max_depth_reached": 0, "iterations": 0}
    
    timer = Timer("IDA*")
    timer.start()
    
    # Initialize with the heuristic value of the initial state
    f_limit = iterative_deepening_heuristic(initial_state)
    
    while f_limit < float('inf'):
        # Track minimum f-value that exceeds current limit
        next_f_limit = float('inf')
        
        # Create initial node
        initial_node = IDSNode(initial_state)
        
        # Run depth-first search with f-limit
        result, next_f = ida_star_search(initial_node, goal_test_func, f_limit, stats)
        
        if result:
            # Solution found
            timer.stop()
            stats["time"] = timer.get_elapsed()
            return result
        
        # Update f-limit for next iteration
        f_limit = next_f
        stats["iterations"] += 1
        
        # Break if we've reached the maximum depth
        if stats["max_depth_reached"] >= max_depth:
            break
    
    # No solution found
    timer.stop()
    stats["time"] = timer.get_elapsed()
    return None

def ida_star_search(node, goal_test_func, f_limit, stats):
    """
    Helper function for IDA* search.
    
    Args:
        node: Current search node
        goal_test_func: Function to check if a state is a goal state
        f_limit: Current f-limit
        stats: Dictionary to track statistics
        
    Returns:
        Tuple of (solution_node, next_f_limit)
    """
    # Calculate f-value for current node
    f_value = node.depth + node.h_value
    
    # If f-value exceeds limit, return the f-value as the next limit
    if f_value > f_limit:
        return None, f_value
    
    # Check if this is a goal state
    if goal_test_func(node.state):
        return node, f_limit
    
    # Track statistics
    stats["nodes_expanded"] += 1
    stats["max_depth_reached"] = max(stats["max_depth_reached"], node.depth)
    
    # Initialize minimum f-value for next iteration
    min_f = float('inf')
    
    # Generate and explore child nodes
    for child_state in get_child_states(node.state):
        # Find the branches that changed
        from_branch = None
        to_branch = None
        
        for i in range(len(node.state.branches)):
            if len(node.state.branches[i]) > len(child_state.branches[i]):
                from_branch = i
            elif len(node.state.branches[i]) < len(child_state.branches[i]):
                to_branch = i
        
        # Create child node
        child = IDSNode(child_state, node, node.depth + 1, from_branch, to_branch)
        
        # Recursively search from this child
        result, new_f = ida_star_search(child, goal_test_func, f_limit, stats)
        
        if result:
            # Solution found
            return result, f_limit
        
        # Update minimum f-value
        min_f = min(min_f, new_f)
    
    # No solution found within current f-limit
    return None, min_f

def extract_solution_path(goal_node):
    """
    Extract the solution path from the goal node.
    
    Args:
        goal_node: The goal node from search
        
    Returns:
        A list of states from the initial state to the goal state
    """
    if not goal_node:
        return None
        
    path = []
    node = goal_node
    
    while node:
        path.append(node.state)
        node = node.parent
    
    return list(reversed(path))

def extract_solution_moves(goal_node):
    """
    Extract the solution moves from the goal node.
    
    Args:
        goal_node: The goal node from search
        
    Returns:
        A list of moves (from_branch, to_branch) from the initial state to the goal state
    """
    if not goal_node:
        return None
        
    moves = []
    node = goal_node
    
    while node and node.parent:
        moves.append((node.from_branch, node.to_branch))
        node = node.parent
    
    return list(reversed(moves))