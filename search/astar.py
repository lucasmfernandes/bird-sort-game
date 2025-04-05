"""
A* and Weighted A* Search Algorithms
"""

import heapq
from search.heuristics import admissible_bird_sort_heuristic, weighted_bird_sort_heuristic

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

class PriorityNode:
    """Node for priority queue in A* search"""
    def __init__(self, state, parent=None, g_cost=0, weight=1.0):
        self.state = state
        self.parent = parent
        self.g_cost = g_cost  # Cost from start to this node
        
        # Calculate f_cost = g_cost + weight*h_cost
        if weight == 1.0:
            self.h_cost = admissible_bird_sort_heuristic(state)
        else:
            self.h_cost = weighted_bird_sort_heuristic(state, weight)
            
        self.f_cost = self.g_cost + (weight * self.h_cost)
    
    def __lt__(self, other):
        # For priority queue comparison
        return self.f_cost < other.f_cost

def astar_search(initial_state, goal_state_func, operators_func, weight=1.0):
    """
    A* search algorithm for the Bird Sort problem.
    
    Args:
        initial_state: The initial state
        goal_state_func: Function to check if a state is a goal state
        operators_func: Function to generate child states
        weight: Weight for the heuristic (1.0 = standard A*, >1.0 = weighted A*)
        
    Returns:
        A solution node or None if no solution is found
    """
    # Initialize the open and closed sets
    open_set = []
    closed_set = set()
    
    # Add the initial state to the open set
    start_node = PriorityNode(initial_state, weight=weight)
    heapq.heappush(open_set, (start_node.f_cost, id(start_node), start_node))
    
    # Track the best path to each state
    best_g = {hash(initial_state): 0}
    
    while open_set:
        # Get the node with the lowest f_cost
        _, _, current = heapq.heappop(open_set)
        
        # Check if we've reached the goal
        if goal_state_func(current.state):
            return current
        
        # Add the current state to the closed set
        state_hash = hash(current.state)
        if state_hash in closed_set:
            continue
        closed_set.add(state_hash)
        
        # Generate all possible child states
        for child_state in operators_func(current.state):
            child_hash = hash(child_state)
            
            # Calculate the cost to reach this child
            child_g = current.g_cost + 1  # Each move costs 1
            
            # Skip if we've seen this state with a better path
            if child_hash in best_g and best_g[child_hash] <= child_g:
                continue
                
            # This is the best path to this state so far
            best_g[child_hash] = child_g
            
            # Create a new node and add it to the open set
            child_node = PriorityNode(child_state, current, child_g, weight)
            heapq.heappush(open_set, (child_node.f_cost, id(child_node), child_node))
    
    # No solution found
    return None

def extract_solution_path(goal_node):
    """
    Extract the solution path from the goal node.
    
    Args:
        goal_node: The goal node from A* search
        
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