"""
Player Mode for Bird Sort Game
"""

import pygame
import random
from models.game import BirdSortGame
from models.generator import create_random_initial_state
from ui.pygame_ui import BirdSortGameUI

class PlayerModePage:
    """
    Player Mode page for the Bird Sort Game.
    Allows the player to play the game manually.
    """
    
    def __init__(self, screen, return_callback):
        """
        Initialize the player mode page.
        
        Args:
            screen: Pygame screen
            return_callback: Callback to return to the main menu
        """
        self.screen = screen
        self.return_callback = return_callback
        self.game = None
        self.game_ui = None
    
    def reset(self):
        """Reset the player mode page"""
        # Generate random configuration
        num_branches = random.randint(5, 8)
        num_colors = random.randint(3, min(6, num_branches - 1))
        
        # Create game
        self.game = BirdSortGame(num_branches=num_branches, num_colors=num_colors)
        
        # Create game UI
        self.game_ui = BirdSortGameUI(self.game, enable_solver=True, screen=self.screen)
        self.game_ui.set_return_callback(self.return_callback)
    
    def run(self):
        """Run the player mode"""
        if not self.game or not self.game_ui:
            self.reset()
        
        # Run the game UI
        return self.game_ui.run()