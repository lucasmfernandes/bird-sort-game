"""
Color schemes and visual settings for the Bird Sort game
"""

# Define color schemes
COLOR_SCHEMES = {
    "default": {
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
    },
    "dark": {
        "background": (40, 40, 40),
        "branch": (90, 50, 20),
        "text": (220, 220, 220),
        "button": (80, 80, 80),
        "button_text": (220, 220, 220),
        "win_text": (0, 200, 0),
        "bird_colors": [
            (220, 50, 50),    # Red
            (50, 220, 50),    # Green
            (50, 50, 220),    # Blue
            (220, 220, 50),   # Yellow
            (220, 50, 220),   # Magenta
            (50, 220, 220),   # Cyan
            (220, 140, 40),   # Orange
            (140, 50, 140)    # Purple
        ]
    },
    "pastel": {
        "background": (245, 245, 255),
        "branch": (160, 120, 90),
        "text": (60, 60, 80),
        "button": (210, 210, 230),
        "button_text": (60, 60, 80),
        "win_text": (80, 180, 80),
        "bird_colors": [
            (255, 150, 150),  # Pastel Red
            (150, 255, 150),  # Pastel Green
            (150, 150, 255),  # Pastel Blue
            (255, 255, 150),  # Pastel Yellow
            (255, 150, 255),  # Pastel Magenta
            (150, 255, 255),  # Pastel Cyan
            (255, 200, 150),  # Pastel Orange
            (200, 150, 255)   # Pastel Purple
        ]
    }
}

def get_color_scheme(theme_name="default"):
    """
    Get a color scheme by name.
    
    Args:
        theme_name: Name of the theme to use
        
    Returns:
        A dictionary containing color values for the theme
    """
    if theme_name not in COLOR_SCHEMES:
        theme_name = "default"
        
    return COLOR_SCHEMES[theme_name]

def get_available_themes():
    """
    Get a list of available theme names.
    
    Returns:
        A list of theme names
    """
    return list(COLOR_SCHEMES.keys())