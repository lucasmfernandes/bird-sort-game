try:
    from .pygame_ui import BirdSortGameUI as PygameUI
    __all__ = ['PygameUI']
except ImportError:
    pass

try:
    from .tkinter_ui import BirdSortGameUI as TkinterUI
    __all__ = ['TkinterUI']
except ImportError:
    pass

try:
    from .pyqt_ui import BirdSortGameUI as PyQtUI
    __all__ = ['PyQtUI']
except ImportError:
    pass

# Import themes
from .themes import get_color_scheme

__all__ = ['get_color_scheme'] + __all__