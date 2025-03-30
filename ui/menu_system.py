"""
Menu System for Bird Sort Game
"""

import pygame
import sys
import os
from models.game import BirdSortGame
from models.generator import create_random_initial_state
from ui.pygame_ui import BirdSortGameUI
from ui.ai_mode import AIModePage
from ui.player_mode import PlayerModePage

class MenuSystem:
    """
    Menu system for the Bird Sort Game.
    Provides options to choose between AI and Player modes.
    """
    
    def __init__(self, default_mode=None):
        """
        Initialize the menu system.
        
        Args:
            default_mode: Optional default mode to start with ('player' or 'ai')
        """
        # Initialize pygame
        pygame.init()
        
        # Constants
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.BUTTON_WIDTH = 300
        self.BUTTON_HEIGHT = 60
        self.BUTTON_MARGIN = 20
        self.TITLE_FONT_SIZE = 48
        self.BUTTON_FONT_SIZE = 24
        
        # Create the screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Bird Sort Game")
        
        # Create fonts
        self.title_font = pygame.font.SysFont('Arial', self.TITLE_FONT_SIZE)
        self.button_font = pygame.font.SysFont('Arial', self.BUTTON_FONT_SIZE)
        
        # Colors
        self.BACKGROUND_COLOR = (240, 240, 240)
        self.BUTTON_COLOR = (200, 200, 200)
        self.BUTTON_HOVER_COLOR = (180, 180, 180)
        self.TEXT_COLOR = (0, 0, 0)
        self.TITLE_COLOR = (50, 50, 150)
        
        # State
        self.current_page = "main_menu"
        self.ai_mode_page = AIModePage(self.screen, self.return_to_main_menu)
        self.player_mode_page = PlayerModePage(self.screen, self.return_to_main_menu)
        
        # If default mode is provided, go directly to that mode
        if default_mode == "player":
            self.current_page = "player_mode"
        elif default_mode == "ai":
            self.current_page = "ai_mode"
    
    def return_to_main_menu(self):
        """Return to the main menu"""
        self.current_page = "main_menu"
    
    def draw_main_menu(self):
        """Draw the main menu"""
        # Clear the screen
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Draw title
        title_text = self.title_font.render("Bird Sort Game", True, self.TITLE_COLOR)
        title_rect = title_text.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw buttons
        button_y = 200
        
        # Player Mode button
        player_button_rect = pygame.Rect(
            (self.SCREEN_WIDTH - self.BUTTON_WIDTH) // 2,
            button_y,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        mouse_pos = pygame.mouse.get_pos()
        player_button_color = self.BUTTON_HOVER_COLOR if player_button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, player_button_color, player_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, player_button_rect, 2, border_radius=10)
        
        player_text = self.button_font.render("Player Mode", True, self.TEXT_COLOR)
        player_text_rect = player_text.get_rect(center=player_button_rect.center)
        self.screen.blit(player_text, player_text_rect)
        
        # AI Mode button
        button_y += self.BUTTON_HEIGHT + self.BUTTON_MARGIN
        ai_button_rect = pygame.Rect(
            (self.SCREEN_WIDTH - self.BUTTON_WIDTH) // 2,
            button_y,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        ai_button_color = self.BUTTON_HOVER_COLOR if ai_button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, ai_button_color, ai_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, ai_button_rect, 2, border_radius=10)
        
        ai_text = self.button_font.render("AI Mode", True, self.TEXT_COLOR)
        ai_text_rect = ai_text.get_rect(center=ai_button_rect.center)
        self.screen.blit(ai_text, ai_text_rect)
        
        # Exit button
        button_y += self.BUTTON_HEIGHT + self.BUTTON_MARGIN
        exit_button_rect = pygame.Rect(
            (self.SCREEN_WIDTH - self.BUTTON_WIDTH) // 2,
            button_y,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        exit_button_color = self.BUTTON_HOVER_COLOR if exit_button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, exit_button_color, exit_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, exit_button_rect, 2, border_radius=10)
        
        exit_text = self.button_font.render("Exit", True, self.TEXT_COLOR)
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
        
        return player_button_rect, ai_button_rect, exit_button_rect
    
    def handle_main_menu_click(self, pos, player_button, ai_button, exit_button):
        """Handle clicks on the main menu"""
        if player_button.collidepoint(pos):
            self.current_page = "player_mode"
            self.player_mode_page.reset()
            return True
        elif ai_button.collidepoint(pos):
            self.current_page = "ai_mode"
            self.ai_mode_page.reset()
            return True
        elif exit_button.collidepoint(pos):
            return False
        return True
    
    def run(self):
        """Main loop for the menu system"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            if self.current_page == "main_menu":
                # Draw main menu
                player_button, ai_button, exit_button = self.draw_main_menu()
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        running = self.handle_main_menu_click(
                            event.pos, player_button, ai_button, exit_button
                        )
            
            elif self.current_page == "player_mode":
                # Run player mode
                running = self.player_mode_page.run()
                if running:
                    self.current_page = "main_menu"
            
            elif self.current_page == "ai_mode":
                # Run AI mode
                running = self.ai_mode_page.run()
                if running:
                    self.current_page = "main_menu"
            
            # Update the display
            pygame.display.flip()
            
            # Control game speed
            clock.tick(60)
        
        # Quit pygame
        pygame.quit()
        return 0