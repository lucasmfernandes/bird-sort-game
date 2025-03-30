"""
AI Mode for Bird Sort Game
"""

import pygame
import sys
import time
import tracemalloc
from models.game import BirdSortGame
from models.generator import create_random_initial_state
from search.astar import astar_search, extract_solution_path, get_child_states
from search.iterative_deepening import iterative_deepening_search
from ui.pygame_ui import BirdSortGameUI

class AIModePage:
    """
    AI Mode page for the Bird Sort Game.
    Allows comparing different AI algorithms.
    """
    
    def __init__(self, screen, return_callback):
        """
        Initialize the AI mode page.
        
        Args:
            screen: Pygame screen
            return_callback: Callback to return to the main menu
        """
        self.screen = screen
        self.return_callback = return_callback
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        
        # Constants
        self.BUTTON_WIDTH = 200
        self.BUTTON_HEIGHT = 40
        self.BUTTON_MARGIN = 10
        self.SLIDER_WIDTH = 300
        self.SLIDER_HEIGHT = 20
        self.CHECKBOX_SIZE = 20
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 36)
        self.subtitle_font = pygame.font.SysFont('Arial', 24)
        self.text_font = pygame.font.SysFont('Arial', 18)
        
        # Colors
        self.BACKGROUND_COLOR = (240, 240, 240)
        self.BUTTON_COLOR = (200, 200, 200)
        self.BUTTON_HOVER_COLOR = (180, 180, 180)
        self.TEXT_COLOR = (0, 0, 0)
        self.TITLE_COLOR = (50, 50, 150)
        self.SLIDER_COLOR = (150, 150, 150)
        self.SLIDER_HANDLE_COLOR = (100, 100, 100)
        self.CHECKBOX_COLOR = (150, 150, 150)
        self.CHECKBOX_CHECK_COLOR = (50, 50, 150)
        
        # State
        self.state = "config"  # config, running, results
        self.num_branches = 7
        self.num_colors = 5
        self.algorithms = {
            "A* (Admissible)": True,
            "Weighted A* (1.5)": True,
            "Weighted A* (2.0)": False,
            "Iterative Deepening": True
        }
        self.results = {}
        self.current_algorithm = None
        self.current_game = None
        self.current_game_ui = None
        self.visualization_speed = 0.3  # seconds between moves
        self.last_move_time = 0
        self.solution_path = None
        self.solution_index = 0
    
    def reset(self):
        """Reset the AI mode page"""
        self.state = "config"
        self.results = {}
        self.current_algorithm = None
        self.current_game = None
        self.current_game_ui = None
        self.solution_path = None
        self.solution_index = 0
    
    def draw_config_page(self):
        """Draw the configuration page"""
        # Clear the screen
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Draw title
        title_text = self.title_font.render("AI Mode Configuration", True, self.TITLE_COLOR)
        title_rect = title_text.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw branch slider
        branch_label = self.subtitle_font.render(f"Number of Branches: {self.num_branches}", True, self.TEXT_COLOR)
        self.screen.blit(branch_label, (self.SCREEN_WIDTH // 2 - 150, 100))
        
        branch_slider_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 150,
            130,
            self.SLIDER_WIDTH,
            self.SLIDER_HEIGHT
        )
        pygame.draw.rect(self.screen, self.SLIDER_COLOR, branch_slider_rect, border_radius=5)
        
        # Draw branch slider handle
        branch_handle_pos = self.SCREEN_WIDTH // 2 - 150 + (self.num_branches - 4) * (self.SLIDER_WIDTH / 6)
        branch_handle_rect = pygame.Rect(
            branch_handle_pos - 5,
            125,
            10,
            30
        )
        pygame.draw.rect(self.screen, self.SLIDER_HANDLE_COLOR, branch_handle_rect, border_radius=5)
        
        # Draw color slider
        color_label = self.subtitle_font.render(f"Number of Colors: {self.num_colors}", True, self.TEXT_COLOR)
        self.screen.blit(color_label, (self.SCREEN_WIDTH // 2 - 150, 170))
        
        color_slider_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 150,
            200,
            self.SLIDER_WIDTH,
            self.SLIDER_HEIGHT
        )
        pygame.draw.rect(self.screen, self.SLIDER_COLOR, color_slider_rect, border_radius=5)
        
        # Draw color slider handle
        color_handle_pos = self.SCREEN_WIDTH // 2 - 150 + (self.num_colors - 3) * (self.SLIDER_WIDTH / 5)
        color_handle_rect = pygame.Rect(
            color_handle_pos - 5,
            195,
            10,
            30
        )
        pygame.draw.rect(self.screen, self.SLIDER_HANDLE_COLOR, color_handle_rect, border_radius=5)
        
        # Draw algorithm checkboxes
        algo_label = self.subtitle_font.render("Algorithms to Compare:", True, self.TEXT_COLOR)
        self.screen.blit(algo_label, (self.SCREEN_WIDTH // 2 - 150, 250))
        
        checkbox_y = 290
        checkbox_rects = {}
        
        for algo_name, selected in self.algorithms.items():
            # Draw checkbox
            checkbox_rect = pygame.Rect(
                self.SCREEN_WIDTH // 2 - 150,
                checkbox_y,
                self.CHECKBOX_SIZE,
                self.CHECKBOX_SIZE
            )
            pygame.draw.rect(self.screen, self.CHECKBOX_COLOR, checkbox_rect, border_radius=3)
            
            if selected:
                # Draw check mark
                pygame.draw.rect(self.screen, self.CHECKBOX_CHECK_COLOR, 
                                pygame.Rect(
                                    self.SCREEN_WIDTH // 2 - 145,
                                    checkbox_y + 5,
                                    self.CHECKBOX_SIZE - 10,
                                    self.CHECKBOX_SIZE - 10
                                ), border_radius=2)
            
            # Draw algorithm name
            algo_text = self.text_font.render(algo_name, True, self.TEXT_COLOR)
            self.screen.blit(algo_text, (self.SCREEN_WIDTH // 2 - 120, checkbox_y))
            
            checkbox_rects[algo_name] = checkbox_rect
            checkbox_y += 30
        
        # Draw start button
        start_button_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 100,
            checkbox_y + 20,
            200,
            40
        )
        mouse_pos = pygame.mouse.get_pos()
        start_button_color = self.BUTTON_HOVER_COLOR if start_button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, start_button_color, start_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, start_button_rect, 2, border_radius=10)
        
        start_text = self.subtitle_font.render("Start Comparison", True, self.TEXT_COLOR)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_text, start_text_rect)
        
        # Draw back button
        back_button_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 100,
            checkbox_y + 80,
            200,
            40
        )
        back_button_color = self.BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, back_button_color, back_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, back_button_rect, 2, border_radius=10)
        
        back_text = self.subtitle_font.render("Back to Menu", True, self.TEXT_COLOR)
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
        return {
            "branch_slider": branch_slider_rect,
            "branch_handle": branch_handle_rect,
            "color_slider": color_slider_rect,
            "color_handle": color_handle_rect,
            "checkboxes": checkbox_rects,
            "start_button": start_button_rect,
            "back_button": back_button_rect
        }
    
    def handle_config_click(self, pos, ui_elements):
        """Handle clicks on the configuration page"""
        # Check if start button was clicked
        if ui_elements["start_button"].collidepoint(pos):
            # Ensure at least one algorithm is selected
            if any(self.algorithms.values()):
                self.start_comparison()
                return True
        
        # Check if back button was clicked
        if ui_elements["back_button"].collidepoint(pos):
            self.return_callback()
            return True
        
        # Check if a checkbox was clicked
        for algo_name, checkbox_rect in ui_elements["checkboxes"].items():
            if checkbox_rect.collidepoint(pos):
                self.algorithms[algo_name] = not self.algorithms[algo_name]
                return True
        
        return True
    
    def handle_config_drag(self, pos, ui_elements, dragging):
        """Handle dragging on the configuration page"""
        # Branch slider
        if dragging == "branch_slider" or ui_elements["branch_slider"].collidepoint(pos):
            # Calculate branch value from position
            slider_x = max(ui_elements["branch_slider"].left, min(pos[0], ui_elements["branch_slider"].right))
            slider_percent = (slider_x - ui_elements["branch_slider"].left) / ui_elements["branch_slider"].width
            self.num_branches = max(4, min(10, int(4 + slider_percent * 6)))
            
            # Ensure num_colors <= num_branches - 1
            if self.num_colors > self.num_branches - 1:
                self.num_colors = self.num_branches - 1
            
            return "branch_slider"
        
        # Color slider
        if dragging == "color_slider" or ui_elements["color_slider"].collidepoint(pos):
            # Calculate color value from position
            slider_x = max(ui_elements["color_slider"].left, min(pos[0], ui_elements["color_slider"].right))
            slider_percent = (slider_x - ui_elements["color_slider"].left) / ui_elements["color_slider"].width
            self.num_colors = max(3, min(8, int(3 + slider_percent * 5)))
            
            # Ensure num_colors <= num_branches - 1
            if self.num_colors > self.num_branches - 1:
                self.num_colors = self.num_branches - 1
            
            return "color_slider"
        
        return dragging
    
    def start_comparison(self):
        """Start the algorithm comparison"""
        self.state = "running"
        self.results = {}
        
        # Create initial state
        self.initial_state = create_random_initial_state(self.num_branches, self.num_colors)
        
        # Get list of selected algorithms
        selected_algorithms = [name for name, selected in self.algorithms.items() if selected]
        self.algorithms_to_run = selected_algorithms.copy()
        
        # Start with the first algorithm
        self.run_next_algorithm()
    
    def run_next_algorithm(self):
        """Run the next algorithm in the list"""
        if not self.algorithms_to_run:
            # All algorithms have been run
            self.state = "results"
            return
        
        # Get the next algorithm
        self.current_algorithm = self.algorithms_to_run.pop(0)
        
        # Create a new game with the same initial state
        self.current_game = BirdSortGame(
            num_branches=self.num_branches, 
            num_colors=self.num_colors,
            initial_state=self.initial_state.copy()
        )
        
        # Create game UI
        self.current_game_ui = BirdSortGameUI(
            self.current_game, 
            enable_solver=False, 
            screen=self.screen,
            show_controls=False
        )
        
        # Run the algorithm
        start_time = time.time()
        tracemalloc.start()
        
        if self.current_algorithm == "A* (Admissible)":
            result = astar_search(
                self.initial_state,
                lambda state: state.is_goal_state(),
                get_child_states,
                weight=1.0
            )
        elif self.current_algorithm == "Weighted A* (1.5)":
            result = astar_search(
                self.initial_state,
                lambda state: state.is_goal_state(),
                get_child_states,
                weight=1.5
            )
        elif self.current_algorithm == "Weighted A* (2.0)":
            result = astar_search(
                self.initial_state,
                lambda state: state.is_goal_state(),
                get_child_states,
                weight=2.0
            )
        elif self.current_algorithm == "Iterative Deepening":
            result = iterative_deepening_search(
                self.initial_state,
                lambda state: state.is_goal_state(),
                get_child_states
            )
            # Convert result to match A* format
            if result:
                class DummyNode:
                    def __init__(self, state, parent=None):
                        self.state = state
                        self.parent = parent
                
                # Convert path to linked nodes
                prev_node = None
                for state in reversed(result):
                    node = DummyNode(state, prev_node)
                    prev_node = node
                
                result = prev_node
        
        # Measure time and memory
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Extract solution path
        if result:
            self.solution_path = extract_solution_path(result)
            solution_length = len(self.solution_path) - 1  # Number of moves
        else:
            self.solution_path = None
            solution_length = "N/A"
        
        # Store results
        self.results[self.current_algorithm] = {
            "time": end_time - start_time,
            "memory": peak / (1024 * 1024),  # Convert to MB
            "moves": solution_length,
            "solution_found": result is not None
        }
        
        # Reset for visualization
        self.solution_index = 0
        self.last_move_time = time.time()
    
    def draw_running_page(self):
        """Draw the running page with algorithm visualization"""
        # Draw the game UI
        self.current_game_ui.draw()
        
        # Draw algorithm info overlay
        overlay_rect = pygame.Rect(
            10,
            10,
            300,
            80
        )
        pygame.draw.rect(self.screen, (240, 240, 240, 200), overlay_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), overlay_rect, 2)
        
        # Draw algorithm name
        algo_text = self.subtitle_font.render(f"Running: {self.current_algorithm}", True, (0, 0, 0))
        self.screen.blit(algo_text, (20, 20))
        
        # Draw progress
        if self.solution_path:
            progress_text = self.text_font.render(
                f"Move {self.solution_index}/{len(self.solution_path)-1}", 
                True, 
                (0, 0, 0)
            )
            self.screen.blit(progress_text, (20, 50))
        else:
            no_solution_text = self.text_font.render("No solution found", True, (200, 0, 0))
            self.screen.blit(no_solution_text, (20, 50))
    
    def update_visualization(self):
        """Update the algorithm visualization"""
        current_time = time.time()
        
        if self.solution_path and self.solution_index < len(self.solution_path) - 1:
            # Check if it's time for the next move
            if current_time - self.last_move_time >= self.visualization_speed:
                # Apply the next state
                self.current_game.state = self.solution_path[self.solution_index + 1]
                self.solution_index += 1
                self.last_move_time = current_time
        else:
            # Visualization complete, wait a bit before moving to next algorithm
            if current_time - self.last_move_time >= 2.0:
                self.run_next_algorithm()
    
    def draw_results_page(self):
        """Draw the results page"""
        # Clear the screen
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Draw title
        title_text = self.title_font.render("Algorithm Comparison Results", True, self.TITLE_COLOR)
        title_rect = title_text.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw configuration info
        config_text = self.subtitle_font.render(
            f"Configuration: {self.num_branches} branches, {self.num_colors} colors", 
            True, 
            self.TEXT_COLOR
        )
        self.screen.blit(config_text, (self.SCREEN_WIDTH // 2 - 200, 100))
        
        # Draw results table
        table_y = 150
        col_widths = [250, 120, 120, 120]
        
        # Draw table header
        header_x = self.SCREEN_WIDTH // 2 - sum(col_widths) // 2
        headers = ["Algorithm", "Time (s)", "Memory (MB)", "Moves"]
        
        for i, header in enumerate(headers):
            header_text = self.subtitle_font.render(header, True, self.TEXT_COLOR)
            self.screen.blit(header_text, (header_x, table_y))
            header_x += col_widths[i]
        
        # Draw horizontal line
        line_y = table_y + 30
        pygame.draw.line(
            self.screen,
            self.TEXT_COLOR,
            (self.SCREEN_WIDTH // 2 - sum(col_widths) // 2, line_y),
            (self.SCREEN_WIDTH // 2 + sum(col_widths) // 2, line_y),
            2
        )
        
        # Draw results rows
        row_y = line_y + 10
        
        for algo_name, result in self.results.items():
            # Draw algorithm name
            algo_text = self.text_font.render(algo_name, True, self.TEXT_COLOR)
            self.screen.blit(algo_text, (self.SCREEN_WIDTH // 2 - sum(col_widths) // 2, row_y))
            
            # Draw time
            time_text = self.text_font.render(f"{result['time']:.4f}", True, self.TEXT_COLOR)
            self.screen.blit(time_text, (self.SCREEN_WIDTH // 2 - sum(col_widths) // 2 + col_widths[0], row_y))
            
            # Draw memory
            memory_text = self.text_font.render(f"{result['memory']:.2f}", True, self.TEXT_COLOR)
            self.screen.blit(memory_text, (self.SCREEN_WIDTH // 2 - sum(col_widths) // 2 + col_widths[0] + col_widths[1], row_y))
            
            # Draw moves
            moves_text = self.text_font.render(f"{result['moves']}", True, self.TEXT_COLOR)
            self.screen.blit(moves_text, (self.SCREEN_WIDTH // 2 - sum(col_widths) // 2 + col_widths[0] + col_widths[1] + col_widths[2], row_y))
            
            row_y += 30
        
        # Draw back button
        back_button_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 100,
            row_y + 30,
            200,
            40
        )
        mouse_pos = pygame.mouse.get_pos()
        back_button_color = self.BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, back_button_color, back_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, back_button_rect, 2, border_radius=10)
        
        back_text = self.subtitle_font.render("Back to Menu", True, self.TEXT_COLOR)
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Draw new comparison button
        new_comp_button_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 150,
            row_y + 90,
            300,
            40
        )
        new_comp_button_color = self.BUTTON_HOVER_COLOR if new_comp_button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, new_comp_button_color, new_comp_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, new_comp_button_rect, 2, border_radius=10)
        
        new_comp_text = self.subtitle_font.render("New Comparison", True, self.TEXT_COLOR)
        new_comp_text_rect = new_comp_text.get_rect(center=new_comp_button_rect.center)
        self.screen.blit(new_comp_text, new_comp_text_rect)
        
        return {
            "back_button": back_button_rect,
            "new_comp_button": new_comp_button_rect
        }
    
    def handle_results_click(self, pos, ui_elements):
        """Handle clicks on the results page"""
        # Check if back button was clicked
        if ui_elements["back_button"].collidepoint(pos):
            self.return_callback()
            return True
        
        # Check if new comparison button was clicked
        if ui_elements["new_comp_button"].collidepoint(pos):
            self.reset()
            return True
        
        return True
    
    def run(self):
        """Run the AI mode page"""
        running = True
        clock = pygame.time.Clock()
        dragging = None
        
        while running:
            if self.state == "config":
                # Draw configuration page
                ui_elements = self.draw_config_page()
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left mouse button
                            running = self.handle_config_click(event.pos, ui_elements)
                            dragging = self.handle_config_drag(event.pos, ui_elements, None)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:  # Left mouse button
                            dragging = None
                    elif event.type == pygame.MOUSEMOTION:
                        if dragging:
                            dragging = self.handle_config_drag(event.pos, ui_elements, dragging)
            
            elif self.state == "running":
                # Draw running page
                self.draw_running_page()
                
                # Update visualization
                self.update_visualization()
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
            
            elif self.state == "results":
                # Draw results page
                ui_elements = self.draw_results_page()
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left mouse button
                            running = self.handle_results_click(event.pos, ui_elements)
            
            # Update the display
            pygame.display.flip()
            
            # Control game speed
            clock.tick(60)
        
        return False