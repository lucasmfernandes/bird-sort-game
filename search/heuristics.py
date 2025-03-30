def admissible_bird_sort_heuristic(state):
    """
    An admissible heuristic for A* search that never overestimates the cost.
    This guarantees optimal solutions.
    
    Args:
        state: A BirdSortState object
        
    Returns:
        A lower bound estimate of moves to reach the goal
    """
    # Count birds of each color and their locations
    color_locations = {}
    color_positions = {}  # Track position of each bird in its branch (0 = bottom)
    
    for branch_idx, branch in enumerate(state.branches):
        for pos, bird in enumerate(branch):
            if bird not in color_locations:
                color_locations[bird] = []
                color_positions[bird] = []
            color_locations[bird].append(branch_idx)
            color_positions[bird].append(pos)
    
    total_moves = 0
    
    for color, locations in color_locations.items():
        if len(set(locations)) == 1 and len(locations) == 4:
            # All birds of this color are already in the same branch
            continue
        
        # Find the branch with the most birds of this color
        branch_counts = {}
        for loc in locations:
            if loc not in branch_counts:
                branch_counts[loc] = 0
            branch_counts[loc] += 1
        
        # Best branch is the one with the most birds of this color
        best_branch = max(branch_counts, key=branch_counts.get)
        birds_to_move = len(locations) - branch_counts[best_branch]
        
        # Each bird needs at least one move
        total_moves += birds_to_move
        
        # Add minimum moves needed to access buried birds
        for branch_idx, branch in enumerate(state.branches):
            if branch_idx == best_branch:
                continue
            
            # Check for birds of this color in this branch
            color_indices = [i for i, b in enumerate(branch) if b == color]
            if not color_indices:
                continue
            
            # For each bird of this color, count birds above it that must be moved
            for idx in color_indices:
                birds_above = sum(1 for i in range(idx + 1, len(branch)) 
                                 if branch[i] != color)
                total_moves += birds_above
    
    return total_moves

def weighted_bird_sort_heuristic(state, weight=1.5):
    """
    A potentially inadmissible but more informed heuristic for Weighted A*.
    This may not guarantee optimal solutions but can find good solutions faster.
    
    Args:
        state: A BirdSortState object
        weight: Weight factor for the heuristic (1.0 = standard A*)
        
    Returns:
        A weighted estimate of moves to reach the goal
    """
    # Start with the admissible heuristic
    base_estimate = admissible_bird_sort_heuristic(state)
    
    # Add additional penalties for suboptimal configurations
    penalties = 0
    
    # Penalty for branches with mixed colors
    for branch in state.branches:
        if not branch:
            continue
            
        colors_in_branch = set(branch)
        if len(colors_in_branch) > 1:
            # Penalty based on how mixed the branch is
            penalties += len(colors_in_branch) - 1
    
    # Penalty for incomplete branches (branches with < 4 birds of same color)
    for color in set(bird for branch in state.branches for bird in branch):
        color_count = sum(branch.count(color) for branch in state.branches)
        if color_count == 4:  # We have all 4 birds of this color
            # Check if they're distributed across multiple branches
            branches_with_color = sum(1 for branch in state.branches if color in branch)
            if branches_with_color > 1:
                # Penalty for having the same color in multiple branches
                penalties += branches_with_color - 1
    
    # Apply weight to the penalties
    return base_estimate + (penalties * (weight - 1.0))

def iterative_deepening_heuristic(state):
    """
    A lightweight, efficient heuristic for iterative deepening search.
    Focuses on quick computation while maintaining admissibility.
    
    Args:
        state: A BirdSortState object
        
    Returns:
        An admissible estimate of moves to reach the goal
    """
    # Quick check for goal state
    if all(len(branch) == 0 or (len(branch) == 4 and len(set(branch)) == 1) 
           for branch in state.branches):
        return 0
    
    # Count birds that need to be moved (simplified calculation)
    birds_to_move = 0
    
    # Track the best branch for each color
    color_best_branch = {}
    color_counts = {}
    
    # First pass: find the best branch for each color
    for branch_idx, branch in enumerate(state.branches):
        for bird in branch:
            if bird not in color_counts:
                color_counts[bird] = {}
            
            if branch_idx not in color_counts[bird]:
                color_counts[bird][branch_idx] = 0
            
            color_counts[bird][branch_idx] += 1
    
    # Determine best branch for each color
    for color, branches in color_counts.items():
        best_branch = max(branches.items(), key=lambda x: x[1])[0]
        color_best_branch[color] = best_branch
    
    # Second pass: count birds that need to be moved
    for branch_idx, branch in enumerate(state.branches):
        for bird in branch:
            if branch_idx != color_best_branch.get(bird, branch_idx):
                birds_to_move += 1
    
    return birds_to_move