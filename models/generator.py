import random
from models.state import BirdSortState

def create_random_initial_state(num_branches=7, num_colors=5):
    """
    Create a random initial state for the Bird Sort game.
    
    Args:
        num_branches: Number of branches (4-10)
        num_colors: Number of colors (3-8)
        
    Returns:
        A BirdSortState object representing the random initial state
    """
    # Ensure constraints are met
    num_branches = max(4, min(10, num_branches))
    min_colors = max(3, num_branches - 1)
    max_colors = min(8, num_branches)
    num_colors = max(min_colors, min(max_colors, num_colors))
    
    # Create a list of all birds (4 of each color)
    all_birds = []
    for color in range(1, num_colors + 1):
        all_birds.extend([color] * 4)
    
    # Shuffle the birds
    random.shuffle(all_birds)
    
    # Distribute birds across branches
    branches = [[] for _ in range(num_branches)]
    
    # First, ensure each branch has at least one bird (except for empty branches)
    num_empty_branches = random.randint(0, num_branches - num_colors)
    non_empty_branches = list(range(num_branches))
    empty_branches = random.sample(non_empty_branches, num_empty_branches)
    
    for branch_idx in empty_branches:
        non_empty_branches.remove(branch_idx)
    
    # Distribute one bird to each non-empty branch
    for branch_idx in non_empty_branches:
        if all_birds:
            branches[branch_idx].append(all_birds.pop())
    
    # Distribute remaining birds randomly, ensuring no branch exceeds 4 birds
    while all_birds:
        # Choose a random branch that isn't full
        available_branches = [i for i in range(num_branches) if len(branches[i]) < 4]
        if not available_branches:
            break  # This shouldn't happen with our constraints
        
        branch_idx = random.choice(available_branches)
        branches[branch_idx].append(all_birds.pop())
    
    return BirdSortState(branches)

def validate_bird_sort_state(state):
    """
    Validate that a Bird Sort state meets all requirements.
    
    Args:
        state: A BirdSortState object
        
    Returns:
        True if valid, False otherwise
    """
    # Count birds of each color
    color_counts = {}
    total_birds = 0
    
    for branch in state.branches:
        if len(branch) > 4:
            print(f"Invalid: Branch has more than 4 birds: {branch}")
            return False
        
        for bird in branch:
            total_birds += 1
            if bird in color_counts:
                color_counts[bird] += 1
            else:
                color_counts[bird] = 1
    
    # Check each color has exactly 4 birds
    for color, count in color_counts.items():
        if count != 4:
            print(f"Invalid: Color {color} has {count} birds instead of 4")
            return False
    
    # Check number of colors is at least (num_branches - 1)
    num_colors = len(color_counts)
    if num_colors < state.num_branches - 1:
        print(f"Invalid: {num_colors} colors is less than required minimum {state.num_branches - 1}")
        return False
    
    print(f"Valid state with {state.num_branches} branches and {num_colors} colors")
    return True