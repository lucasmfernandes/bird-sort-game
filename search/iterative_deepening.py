"""
Iterative Deepening Search for Bird Sort
"""

from search.heuristics import iterative_deepening_heuristic

def iterative_deepening_search(initial_state, goal_state_func, operators_func, max_depth=30):
    """
    Iterative Deepening A* search for the Bird Sort problem.
    
    Args:
        initial_state: The initial state
        goal_state_func: Function to check if a state is a goal state
        operators_func: Function to generate child states
        max_depth: Maximum depth to search
        
    Returns:
        A solution path or None if no solution is found
    """
    # For each depth limit
    for depth_limit in range(1, max_depth + 1):
        print(f"Searching depth {depth_limit}...")
        
        # Initialize the search
        stack = [(initial_state, [], 0)]  # (state, path, g_cost)
        visited = set()
        
        while stack:
            state, path, g = stack.pop()
            state_hash = hash(state)
            
            # Skip if we've seen this state before
            if state_hash in visited:
                continue
                
            visited.add(state_hash)
            
            # Check if we've reached the goal
            if goal_state_func(state):
                return path + [state]
            
            # Skip if we've reached the depth limit
            if len(path) >= depth_limit:
                continue
            
            # Generate children and sort by f-value (g + h)
            children = []
            for child_state in operators_func(state):
                child_hash = hash(child_state)
                
                if child_hash not in visited:
                    h = iterative_deepening_heuristic(child_state)
                    f = g + 1 + h  # g_cost of child + heuristic
                    children.append((child_state, f))
            
            # Sort children by f-value (ascending)
            children.sort(key=lambda x: x[1], reverse=True)  # Reverse for stack
            
            # Add children to stack
            for child_state, _ in children:
                stack.append((child_state, path + [state], g + 1))
    
    return None  # No solution found within depth limit