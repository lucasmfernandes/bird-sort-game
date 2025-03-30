"""
Pygame UI for Bird Sort Game
"""

import pygame
import sys
import time
from search.astar import astar_search, extract_solution_path, get_child_states

class BirdSortGameUI:
    """
    Pygame-based UI for the Bird Sort game.
    """
    def __init__(self, game, enable_solver=False, screen=None, show_controls=True):
        """
        Initialize the UI.
        
        Args:
            game: A BirdSortGame instance
            enable_solver: Whether to enable the auto-solver
            screen: Existing pygame screen to use (if None, creates a new one)
            show_controls: Whether to show control buttons
        """
        self.game = game
        self.enable_solver = enable_solver
        self.show_controls = show_controls
        self.return_callback = None
        
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        
        # Constants
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.BRANCH_WIDTH = 70
        self.BRANCH_HEIGHT = 300
        self.BIRD_SIZE = 50
        self.BIRD_COLORS = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128)   # Purple
        ]
        
        # Create or use existing screen
        if screen:
            self.screen = screen
            self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
            self.external_screen = True
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.set_caption("Bird Sort Game")
            self.external_screen = False
        
        # Create fonts
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Calculate branch positions
        self.branch_positions = self.calculate_branch_positions()
        
        # Solver variables
        self.solution_path = None
        self.solution_index = 0
        self.auto_solving = False
        self.last_auto_move_time = 0
    
    def set_return_callback(self, callback):
        """Set callback for returning to menu"""
        self.return_callback = callback
    
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
        self.screen.fill((240, 240, 240))
        
        # Draw branches
        for i, x in enumerate(self.branch_positions):
            # Draw branch (brown rectangle)
            pygame.draw.rect(self.screen, (139, 69, 19), 
                            (x, self.SCREEN_HEIGHT - self.BRANCH_HEIGHT, 
                             self.BRANCH_WIDTH, self.BRANCH_HEIGHT))
            
            # Draw birds in this branch
            branch = self.game.state.branches[i]
            for j, bird_color in enumerate(branch):
                # Calculate bird position (bottom to top)
                bird_y = self.SCREEN_HEIGHT - 50 - (j * self.BIRD_SIZE)
                
                # Draw bird (colored circle)
                color = self.BIRD_COLORS[bird_color - 1]  # Adjust for 1-based indexing
                pygame.draw.circle(self.screen, color, 
                                  (x + self.BRANCH_WIDTH // 2, bird_y), 
                                  self.BIRD_SIZE // 2)
                
                # Draw bird outline
                pygame.draw.circle(self.screen, (0, 0, 0), 
                                  (x + self.BRANCH_WIDTH // 2, bird_y), 
                                  self.BIRD_SIZE // 2, 2)
        
        # Draw selected bird (if any)
        if self.game.selected_bird is not None:
            # Draw at mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            color = self.BIRD_COLORS[self.game.selected_bird - 1]  # Adjust for 1-based indexing
            pygame.draw.circle(self.screen, color, 
                              (mouse_x, mouse_y), self.BIRD_SIZE // 2)
            pygame.draw.circle(self.screen, (0, 0, 0), 
                              (mouse_x, mouse_y), self.BIRD_SIZE // 2, 2)
        
        # Draw UI elements
        moves_text = self.font.render(f"Moves: {self.game.moves}", True, (0, 0, 0))
        self.screen.blit(moves_text,(20, 20))
        
        if self.show_controls:
            # Draw buttons
            pygame.draw.rect(self.screen, (200, 200, 200), (20, 60, 100, 40))
            undo_text = self.small_font.render("Undo", True, (0, 0, 0))
            self.screen.blit(undo_text, (50, 70))
            
            pygame.draw.rect(self.screen, (200, 200, 200), (130, 60, 100, 40))
            reset_text = self.small_font.render("Reset", True, (0, 0, 0))
            self.screen.blit(reset_text, (160, 70))
            
            if self.enable_solver:
                pygame.draw.rect(self.screen, (200, 200, 200), (240, 60, 100, 40))
                hint_text = self.small_font.render("Hint", True, (0, 0, 0))
                self.screen.blit(hint_text, (270, 70))
                
                pygame.draw.rect(self.screen, (200, 200, 200), (350, 60, 100, 40))
                solve_text = self.small_font.render("Solve", True, (0, 0, 0))
                self.screen.blit(solve_text, (380, 70))
            
            # Draw menu button
            pygame.draw.rect(self.screen, (200, 200, 200), (self.SCREEN_WIDTH - 120, 60, 100, 40))
            menu_text = self.small_font.render("Menu", True, (0, 0, 0))
            self.screen.blit(menu_text, (self.SCREEN_WIDTH - 90, 70))
    
    def handle_click(self, pos):
        """Handle mouse click events"""
        mouse_x, mouse_y = pos
        
        if self.show_controls:
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
            
            # Check if menu button was clicked
            if self.SCREEN_WIDTH - 120 <= mouse_x <= self.SCREEN_WIDTH - 20 and 60 <= mouse_y <= 100:
                if self.return_callback:
                    self.return_callback()
                return
        
        # Check if click is on a branch
        for i, x in enumerate(self.branch_positions):
            if x <= mouse_x <= x + self.BRANCH_WIDTH and \
               self.SCREEN_HEIGHT - self.BRANCH_HEIGHT <= mouse_y <= self.SCREEN_HEIGHT:
                # Click is on this branch
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
    
    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if not self.external_screen:
                        pygame.quit()
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
            
            # Apply auto move if auto-solving
            if self.auto_solving:
                self.apply_auto_move()
            
            # Check for win
            if self.game.is_solved():
                if not self.external_screen:
                    pygame.display.set_caption("Bird Sort Game - Solved!")
                
                # Draw everything
                self.draw()
                pygame.display.flip()
                
                # Wait a bit before showing the win message
                pygame.time.delay(500)
                
                # Show win message
                font = pygame.font.SysFont('Arial', 48)
                win_text = font.render("You Win!", True, (0, 128, 0))
                text_rect = win_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2))
                self.screen.blit(win_text, text_rect)
                pygame.display.flip()
                
                # Wait for a click to continue
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            if not self.external_screen:
                                pygame.quit()
                            return False
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            waiting = False
                
                # Reset the game
                self.game.reset()
                self.solution_path = None
                self.auto_solving = False
            
            # Draw everything
            self.draw()
            
            # Update the display
            pygame.display.flip()
            
            # Control game speed
            clock.tick(60)
        
        # Quit pygame if we created the screen
        if not self.external_screen:
            pygame.quit()
        
        return True