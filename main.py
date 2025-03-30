#!/usr/bin/env python3
"""
Bird Sort Game - Main Entry Point
"""

import argparse
import sys
from models.game import BirdSortGame
from ui.menu_system import MenuSystem

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Bird Sort Game')
    parser.add_argument('--branches', type=int, default=7, 
                        help='Number of branches (4-10)')
    parser.add_argument('--colors', type=int, default=5, 
                        help='Number of colors (3-8)')
    parser.add_argument('--mode', choices=['player', 'ai'], 
                        default=None, help='Game mode')
    parser.add_argument('--ui', choices=['pygame', 'tkinter', 'pyqt'], 
                        default='pygame', help='UI framework to use')
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Launch menu system
    if args.ui == 'pygame':
        from ui.menu_system import MenuSystem
        menu = MenuSystem(default_mode=args.mode)
        return menu.run()
    else:
        print("Only pygame UI is currently supported")
        return 1

if __name__ == "__main__":
    sys.exit(main())