"""
Menu system for the Bird Sort game
"""

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    
from .themes import get_color_scheme, get_available_themes

class MenuSystem:
    """
    Handles menus for the Bird Sort game.
    """
    def __init__(self, screen, font=None, theme="default"):
        """
        Initialize the menu system.
        
        Args:
            screen: Pygame screen surface or equivalent
            font: Font object (or None to create default)
            theme: Theme name to use
        """
        self.screen = screen
        self.theme = get_color_scheme(theme)
        
        # Create fonts if pygame is available
        if PYGAME_AVAILABLE and font is None:
            pygame.font.init()
            self.title_font = pygame.font.SysFont('Arial', 36)
            self.menu_font = pygame.font.SysFont('Arial', 24)
            self.small_font = pygame.font.SysFont('Arial', 18)
        else:
            self.title_font = font
            self.menu_font = font
            self.small_font = font
        
        # Menu state
        self.active = False
        self.current_menu = "main"
        self.menu_items = {
            "main": [
                {"text": "New Game", "action": "new_game"},
                {"text": "Settings", "action": "settings"},
                {"text": "Help", "action": "help"},
                {"text": "Quit", "action": "quit"}
            ],
            "settings": [
                {"text": "Branches: 7", "action": "branches", "value": 7},
                {"text": "Colors: 5", "action": "colors", "value": 5},
                {"text": "Theme: Default", "action": "theme", "value": "default"},
                {"text": "Back", "action": "main"}
            ],
            "help": [
                {"text": "Click a bird to select it", "action": None},
                {"text": "Click a branch to place it", "action": None},
                {"text": "Sort all birds by color", "action": None},
                {"text": "Back", "action": "main"}
            ]
        }
        self.selected_item = 0
    
    def toggle(self):
        """Toggle the menu on/off"""
        self.active = not self.active
        if self.active:
            self.current_menu = "main"
            self.selected_item = 0
    
    def navigate(self, direction):
        """
        Navigate the menu.
        
        Args:
            direction: 1 for down, -1 for up
        """
        if not self.active:
            return
            
        items = self.menu_items[self.current_menu]
        self.selected_item = (self.selected_item + direction) % len(items)
    
    def select(self):
        """
        Select the current menu item.
        
        Returns:
            Action string or None
        """
        if not self.active:
            return None
            
        item = self.menu_items[self.current_menu][self.selected_item]
        action = item["action"]
        
        if action in self.menu_items:
            # Navigate to submenu
            self.current_menu = action
            self.selected_item = 0
            return None
        
        return action
    
    def update_setting(self, action, value):
        """
        Update a setting value.
        
        Args:
            action: Setting to update
            value: New value
        """
        for item in self.menu_items["settings"]:
            if item["action"] == action:
                item["value"] = value
                
                # Update display text
                if action == "branches":
                    item["text"] = f"Branches: {value}"
                elif action == "colors":
                    item["text"] = f"Colors: {value}"
                elif action == "theme":
                    item["text"] = f"Theme: {value.capitalize()}"
    
    def draw(self):
        """Draw the menu"""
        if not self.active or not PYGAME_AVAILABLE:
            return
            
        # Draw semi-transparent background
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw menu title
        title_text = self.title_font.render(self.current_menu.capitalize(), True, self.theme["text"])
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw menu items
        items = self.menu_items[self.current_menu]
        for i, item in enumerate(items):
            # Highlight selected item
            color = self.theme["text"]
            if i == self.selected_item:
                # Draw selection rectangle
                rect = pygame.Rect(0, 0, 300, 40)
                rect.center = (self.screen.get_width() // 2, 180 + i * 50)
                pygame.draw.rect(self.screen, self.theme["button"], rect)
                pygame.draw.rect(self.screen, color, rect, 2)
            
            # Draw item text
            item_text = self.menu_font.render(item["text"], True, color)
            item_rect = item_text.get_rect(center=(self.screen.get_width() // 2, 180 + i * 50))
            self.screen.blit(item_text, item_rect)