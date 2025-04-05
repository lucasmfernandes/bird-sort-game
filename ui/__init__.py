"""
User interface package for Bird Sort Game
"""

# Import UI modules
try:
    from .themes import get_color_scheme, get_available_themes
except ImportError:
    # Fallback if themes module is not available
    def get_color_scheme(theme_name="default"):
        """Fallback color scheme function"""
        default_colors = {
            "background": (240, 240, 240),
            "branch": (139, 69, 19),
            "text": (0, 0, 0),
            "button": (200, 200, 200),
            "button_text": (0, 0, 0),
            "win_text": (0, 128, 0),
            "bird_colors": [
                (255, 0, 0),    # Red
                (0, 255, 0),    # Green
                (0, 0, 255),    # Blue
                (255, 255, 0),  # Yellow
                (255, 0, 255),  # Magenta
                (0, 255, 255),  # Cyan
                (255, 165, 0),  # Orange
                (128, 0, 128)   # Purple
            ]
        }
        return default_colors
        
    def get_available_themes():
        """Fallback themes function"""
        return ["default"]

# Try to import menu system
try:
    from .menu_system import MenuSystem
except ImportError:
    # Define a minimal MenuSystem class if the module is not available
    class MenuSystem:
        """Minimal menu system implementation"""
        def __init__(self, *args, **kwargs):
            self.active = False
            
        def toggle(self):
            """Toggle menu visibility"""
            self.active = not self.active
            
        def draw(self, *args, **kwargs):
            """Draw the menu"""
            pass

# Import UI implementations based on availability
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import tkinter
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from PyQt5.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Define available UI frameworks
UI_FRAMEWORKS = []
if PYGAME_AVAILABLE:
    UI_FRAMEWORKS.append("pygame")
if TKINTER_AVAILABLE:
    UI_FRAMEWORKS.append("tkinter")
if PYQT_AVAILABLE:
    UI_FRAMEWORKS.append("pyqt")