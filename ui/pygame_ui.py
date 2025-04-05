"""
Pygame UI for Bird Sort Game
"""

try:
    import pygame
    import sys
    import time
    from search.astar import astar_search, extract_solution_path, get_child_states
    from ui.themes import get_color_scheme
    from ui.menu_system import MenuSystem
    
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

if PYGAME_AVAILABLE:
    class BirdSortGameUI:
        """
        Pygame-based UI for the Bird Sort game.
        """
        def __init__(self, game, enable_solver=False, theme="default", player=None):
            """
            Initialize the UI.
            
            Args:
                game: A BirdSortGame instance
                enable_solver: Whether to enable the auto-solver
                theme: Color theme to use
                player: Optional player instance (human or AI)
            """
            self.game = game
            self.enable_solver = enable_solver
            self.player = player
            
            # Initialize pygame
            pygame.init()
            
            # Constants
            self.SCREEN_WIDTH = 800
            self.SCREEN_HEIGHT = 600
            self.BRANCH_WIDTH = 70
            self.BRANCH_HEIGHT = 300
            self.BIRD_SIZE = 25  # Radius
            
            # Get color scheme
            self.theme = get_color_scheme(theme)
            self.BIRD_COLORS = self.theme["bird_colors"]
            
            # Create the screen
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.set_caption("Bird Sort Game")
            
            # Create fonts
            self.font = pygame.font.SysFont('Arial', 24)
            self.small_font = pygame.font.SysFont('Arial', 18)
            
            # Create menu system
            self.menu = MenuSystem(self.screen, theme=theme)
            
            # Calculate branch positions
            self.branch_positions = self.calculate_branch_positions()
            
            # Solver variables
            self.solution_path = None
            self.solution_index = 0
            self.auto_solving = False
            self.last_auto_move_time = 0
            
            # AI mode variables
            self.ai_mode = player is not None and hasattr(player, 'make_move')
            self.ai_auto_play = False
            self.ai_move_delay = 0.5  # seconds
            self.last_ai_move_time = 0
        
        def calculate_branch_positions(self):
            """Calculate x-position for each branch"""
            total_width = self.game.num_branches * self.BRANCH_WIDTH
            start_x = (self.SCREEN_WIDTH - total_width) // 2
            
            positions = []
            for i in range(self.game.num_branches):
                x = start_x + i * self.BRANCH_WIDTH
                positions.append(x)
                
            return positions
        
        def draw(self):
            """Draw the game state"""
            # Draw background
            self.screen.fill(self.theme["background"])
            
            # Draw branches
            for i, x in enumerate(self.branch_positions):
                # Draw branch (brown rectangle)
                pygame.draw.rect(self.screen, self.theme["branch"], 
                                (x, self.SCREEN_HEIGHT - self.BRANCH_HEIGHT, 
                                 self.BRANCH_WIDTH, self.BRANCH_HEIGHT))
                
                # Draw birds in this branch
                branch = self.game.state.branches[i]
                for j, bird_color in enumerate(branch):
                    # Calculate bird position (bottom to top)
                    bird_y = self.SCREEN_HEIGHT - 50 - (j * self.BIRD_SIZE * 2)
                    
                    # Draw bird (colored circle)
                    color = self.BIRD_COLORS[bird_color - 1]  # Adjust for 1-based indexing
                    pygame.draw.circle(self.screen, color, 
                                      (x + self.BRANCH_WIDTH // 2, bird_y), 
                                      self.BIRD_SIZE)
                    
                    # Draw bird outline
                    pygame.draw.circle(self.screen, (0, 0, 0), 
                                      (x + self.BRANCH_WIDTH // 2, bird_y), 
                                      self.BIRD_SIZE, 2)
            
            # Draw selected bird (if any)
            if self.game.selected_bird is not None:
                # Draw at mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                color = self.BIRD_COLORS[self.game.selected_bird - 1]  # Adjust for 1-based indexing
                pygame.draw.circle(self.screen, color, 
                                  (mouse_x, mouse_y), self.BIRD_SIZE)
                pygame.draw.circle(self.screen, (0, 0, 0), 
                                  (mouse_x, mouse_y), self.BIRD_SIZE, 2)
            
            # Draw UI elements
            moves_text = self.font.render(f"Moves: {self.game.moves}", True, self.theme["text"])
            self.screen.blit(moves_text, (20, 20))
            
            # Draw buttons
            button_bg = self.theme["button"]
            button_text_color = self.theme["button_text"]
            
            pygame.draw.rect(self.screen, button_bg, (20, 60, 100, 40))
            undo_text = self.small_font.render("Undo", True, button_text_color)
            self.screen.blit(undo_text, (50, 70))
            
            pygame.draw.rect(self.screen, button_bg, (130, 60, 100, 40))
            reset_text = self.small_font.render("Reset", True, button_text_color)
            self.screen.blit(reset_text, (160, 70))
            
            if self.enable_solver:
                pygame.draw.rect(self.screen, button_bg, (240, 60, 100, 40))
                hint_text = self.small_font.render("Hint", True, button_text_color)
                self.screen.blit(hint_text, (270, 70))
                
                pygame.draw.rect(self.screen, button_bg, (350, 60, 100, 40))
                solve_text = self.small_font.render("Solve", True, button_text_color)
                self.screen.blit(solve_text, (380, 70))
            
            if self.ai_mode:
                pygame.draw.rect(self.screen, button_bg, (460, 60, 100, 40))
                ai_text = self.small_font.render(
                    "AI Play" if not self.ai_auto_play else "AI Stop", 
                    True, button_text_color
                )
                self.screen.blit(ai_text, (480, 70))
            
            # Draw menu if active
            self.menu.draw()
        
        def handle_click(self, pos):
            """Handle mouse click events"""
            # If menu is active, let it handle the click
            if self.menu.active:
                return
                
            mouse_x, mouse_y = pos
            
            # Check if click is on a button
            if 20 <= mouse_x <= 120 and 60 <= mouse_y <= 100:
                # Undo button
                self.game.undo()
                return
                
            if 130 <= mouse_x <= 230 and 60 <= mouse_y <= 100:
                # Reset button
                self.game.reset()
                self.solution_path = None
                self.auto_solving = False
                self.ai_auto_play = False
                return
                
            if self.enable_solver:
                if 240 <= mouse_x <= 340 and 60 <= mouse_y <= 100:
                    # Hint button
                    self.get_hint()
                    return
                    
                if 350 <= mouse_x <= 450 and 60 <= mouse_y <= 100:
                    # Solve button
                    self.auto_solving = not self.auto_solving
                    if self.auto_solving and not self.solution_path:
                        self.solve_game()
                    return
            
            if self.ai_mode and 460 <= mouse_x <= 560 and 60 <= mouse_y <= 100:
                # AI Play/Stop button
                self.ai_auto_play = not self.ai_auto_play
                return
            
            # Check if click is on a branch
            for i, x in enumerate(self.branch_positions):
                if x <= mouse_x <= x + self.BRANCH_WIDTH and \
                   self.SCREEN_HEIGHT - self.BRANCH_HEIGHT <= mouse_y <= self.SCREEN_HEIGHT:
                    # Click is on this branch
                    if self.player and hasattr(self.player, 'make_move') and not self.ai_auto_play:
                        self.player.make_move(i)
                    else:
                        self.game.select_branch(i)
                    break
        
        def get_hint(self):
            """Get a hint for the next move"""
            if not self.solution_path:
                self.solve_game()
                
            if self.solution_path and len(self.solution_path) > 1:
                # Highlight the branch to select
                current_state = self.game.state
                next_state = self.solution_path[1]
                
                # Find the branch that changed
                for i in range(len(current_state.branches)):
                    if len(current_state.branches[i]) > len(next_state.branches[i]):
                        # This branch lost a bird
                        print(f"Hint: Select a bird from branch {i+1}")
                        
                        # Highlight the branch
                        pygame.draw.rect(self.screen, (255, 255, 0), 
                                        (self.branch_positions[i], 
                                         self.SCREEN_HEIGHT - self.BRANCH_HEIGHT, 
                                         self.BRANCH_WIDTH, self.BRANCH_HEIGHT), 3)
                        pygame.display.flip()
                        pygame.time.delay(1000)  # Highlight for 1 second
                        break
        
        def solve_game(self):
            """Solve the game using A* search"""
            print("Solving game...")
            start_time = time.time()
            
            # Use A* search to find a solution
            goal_node = astar_search(
                self.game.state,
                lambda state: state.is_goal_state(),
                get_child_states,
                weight=1.5  # Use weighted A* for faster solutions
            )
            
            if goal_node:
                self.solution_path = extract_solution_path(goal_node)
                self.solution_index = 0
                print(f"Solution found in {len(self.solution_path)-1} moves")
                print(f"Solving time: {time.time() - start_time:.2f} seconds")
            else:
                print("No solution found")
        
        def apply_auto_move(self):
            """Apply the next move from the solution path"""
            if not self.solution_path or self.solution_index >= len(self.solution_path) - 1:
                self.auto_solving = False
                return
                
            current_time = time.time()
            if current_time - self.last_auto_move_time < 0.5:
                return  # Wait before making the next move
                
            current_state = self.game.state
            next_state = self.solution_path[self.solution_index + 1]
            
            # Find the branches that changed
            from_branch = None
            to_branch = None
            
            for i in range(len(current_state.branches)):
                if len(current_state.branches[i]) > len(next_state.branches[i]):
                    from_branch = i
                elif len(current_state.branches[i]) < len(next_state.branches[i]):
                    to_branch = i
            
            if from_branch is not None and to_branch is not None:
                # Make the move
                self.game.select_branch(from_branch)
                self.game.select_branch(to_branch)
                self.solution_index += 1
                self.last_auto_move_time = current_time
        
        def apply_ai_move(self):
            """Apply an AI move"""
            if not self.ai_mode or not self.ai_auto_play:
                return
                
            current_time = time.time()
            if current_time - self.last_ai_move_time < self.ai_move_delay:
                return  # Wait before making the next move
                
            # Let the AI make a move
            if self.player and hasattr(self.player, 'make_move'):
                self.player.make_move()
                self.last_ai_move_time = current_time
        
        def run(self):
            """Main game loop"""
            running = True
            clock = pygame.time.Clock()
            
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_click(pygame.mouse.get_pos())
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.menu.toggle()
                        elif self.menu.active:
                            if event.key == pygame.K_UP:
                                self.menu.navigate(-1)
                            elif event.key == pygame.K_DOWN:
                                self.menu.navigate(1)
                            elif event.key == pygame.K_RETURN:
                                action = self.menu.select()
                                if action == "quit":
                                    running = False
                                elif action == "new_game":
                                    self.game.reset()
                                    self.menu.toggle()
                
                # Apply auto move if auto-solving
                if self.auto_solving:
                    self.apply_auto_move()
                
                # Apply AI move if in AI mode
                if self.ai_mode:
                    self.apply_ai_move()
                
                # Check for win
                if self.game.is_solved():
                    pygame.display.set_caption("Bird Sort Game - Solved!")
                    
                    # Draw everything
                    self.draw()
                    pygame.display.flip()
                    
                    # Wait a bit before showing the win message
                    pygame.time.delay(500)
                    
                    # Show win message
                    font = pygame.font.SysFont('Arial', 48)
                    win_text = font.render("You Win!", True, self.theme["win_text"])
                    text_rect = win_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2))
                    self.screen.blit(win_text, text_rect)
                    pygame.display.flip()
                    
                    # Wait for a click to continue
                    waiting = True
                    while waiting:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                waiting = False
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                waiting = False
                    
                    # Reset the game
                    self.game.reset()
                    self.solution_path = None
                    self.auto_solving = False
                    self.ai_auto_play = False
                
                # Draw everything
                self.draw()
                
                # Update the display
                pygame.display.flip()
                
                # Control game speed
                clock.tick(60)
            
            # Quit pygame
            pygame.quit()
            return 0
else:
    # Fallback class if pygame is not available
    class BirdSortGameUI:
        """Fallback UI class when pygame is not available"""
        def __init__(self, game, enable_solver=False, theme="default", player=None):
            print("Error: Pygame is not installed. Please install it with:")
            print("  pip install pygame")
            
        def run(self):
            """Fallback run method"""
            return 1