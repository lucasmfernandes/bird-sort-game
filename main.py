#!/usr/bin/env python3
"""
Bird Sort Game - Main Entry Point
"""

import argparse
import sys
import os

# Ensure all packages are in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import after path setup
from models.game import BirdSortGame
from utils.logger import Logger, GameLogger
from utils.timer import Timer

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Bird Sort Game')
    parser.add_argument('--branches', type=int, default=7, 
                        help='Number of branches (4-10)')
    parser.add_argument('--colors', type=int, default=5, 
                        help='Number of colors (3-8)')
    parser.add_argument('--solver', action='store_true',
                        help='Enable auto-solver')
    parser.add_argument('--ui', choices=['pygame', 'tkinter', 'pyqt'], 
                        default='pygame', help='UI framework to use')
    parser.add_argument('--theme', choices=['default', 'dark', 'pastel'],
                        default='default', help='Color theme to use')
    parser.add_argument('--ai-mode', action='store_true',
                        help='Run in AI mode instead of player mode')
    parser.add_argument('--profile', action='store_true',
                        help='Enable performance profiling')
    parser.add_argument('--ai-type', choices=['random', 'greedy', 'astar', 'ida'],
                        default='astar', help='AI algorithm to use')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO', help='Logging level')
    parser.add_argument('--log-file', type=str, default=None,
                        help='Log file path (default: logs/game_TIMESTAMP.log)')
    parser.add_argument('--build-pdb', action='store_true',
                        help='Build pattern database before starting')
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Set up logging
    logger = Logger(level=args.log_level, log_file=args.log_file)
    logger.info("Bird Sort Game starting...")
    
    # Validate arguments
    if not 4 <= args.branches <= 10:
        logger.error("Number of branches must be between 4 and 10")
        return 1
    
    if not 3 <= args.colors <= 8:
        logger.error("Number of colors must be between 3 and 8")
        return 1
    
    if args.colors > args.branches:
        logger.error("Number of colors cannot exceed number of branches")
        return 1
    
    # Initialize performance metrics if requested
    if args.profile:
        try:
            from utils.performance_metrics import PerformanceMetrics
            from utils.memory_profiler import MemoryProfiler
            metrics = PerformanceMetrics()
            memory_profiler = MemoryProfiler()
            memory_profiler.start()
            profiling_enabled = True
            logger.info("Performance profiling enabled")
        except ImportError:
            logger.warning("Performance profiling modules not found. Profiling disabled.")
            profiling_enabled = False
    else:
        profiling_enabled = False
    
    # Build pattern database if requested
    if args.build_pdb:
        try:
            from search.pattern_database import DisjointPatternDatabase
            from models.state import BirdSortState
            
            logger.info("Building pattern database...")
            pdb = DisjointPatternDatabase(args.branches, args.colors)
            
            # Define goal test and operators functions
            def goal_test(state):
                return state.is_goal_state()
                
            def operators(state):
                from search.astar import get_child_states
                return get_child_states(state)
            
            # Build the databases
            with Timer("Build PDB") as timer:
                pdb.build_all(goal_test, operators)
            
            logger.info(f"Pattern database built in {timer.get_elapsed():.2f} seconds")
        except ImportError:
            logger.warning("Pattern database modules not found. Skipping database build.")
    
    # Create game instance
    game = BirdSortGame(num_branches=args.branches, num_colors=args.colors)
    
    # Set up game logger
    game_logger = GameLogger(game, args.log_file)
    
    # Set up player mode
    if args.ai_mode:
        try:
            if args.ai_type == 'random':
                from players.random_player import RandomPlayer
                player = RandomPlayer(game)
                logger.info("Using Random AI player")
            elif args.ai_type == 'greedy':
                from players.greedy_player import GreedyPlayer
                player = GreedyPlayer(game)
                logger.info("Using Greedy AI player")
            elif args.ai_type == 'ida':
                from players.ida_player import IDAStarPlayer
                player = IDAStarPlayer(game)
                logger.info("Using IDA* AI player")
            else:  # default to astar
                from players.astar_player import AStarPlayer
                player = AStarPlayer(game)
                logger.info("Using A* AI player")
        except ImportError as e:
            logger.warning(f"AI player modules not found: {e}. Defaulting to human player.")
            from players.human_player import HumanPlayer
            player = HumanPlayer(game)
    else:
        try:
            from players.human_player import HumanPlayer
            player = HumanPlayer(game)
            logger.info("Using Human player")
        except ImportError:
            logger.warning("Human player module not found. Game may not function properly.")
            player = None
    
    # Launch appropriate UI with error handling for theme parameter
    try:
        if args.ui == 'pygame':
            try:
                from ui.pygame_ui import BirdSortGameUI
                ui = BirdSortGameUI(game, enable_solver=args.solver, theme=args.theme, player=player)
                logger.info("Using Pygame UI")
            except TypeError as e:
                if "unexpected keyword argument" in str(e):
                    # Try without problematic parameters
                    if "theme" in str(e):
                        ui = BirdSortGameUI(game, enable_solver=args.solver)
                        logger.warning("Theme parameter not supported by Pygame UI")
                    elif "player" in str(e):
                        ui = BirdSortGameUI(game, enable_solver=args.solver, theme=args.theme)
                        logger.warning("Player parameter not supported by Pygame UI")
                    else:
                        ui = BirdSortGameUI(game)
                        logger.warning("Some parameters not supported by Pygame UI")
                else:
                    raise
        elif args.ui == 'tkinter':
            try:
                from ui.tkinter_ui import BirdSortGameUI
                ui = BirdSortGameUI(game, enable_solver=args.solver, theme=args.theme, player=player)
                logger.info("Using Tkinter UI")
            except TypeError as e:
                if "unexpected keyword argument" in str(e):
                    # Try without problematic parameters
                    if "theme" in str(e):
                        ui = BirdSortGameUI(game, enable_solver=args.solver)
                        logger.warning("Theme parameter not supported by Tkinter UI")
                    elif "player" in str(e):
                        ui = BirdSortGameUI(game, enable_solver=args.solver, theme=args.theme)
                        logger.warning("Player parameter not supported by Tkinter UI")
                    else:
                        ui = BirdSortGameUI(game)
                        logger.warning("Some parameters not supported by Tkinter UI")
                else:
                    raise
        elif args.ui == 'pyqt':
            try:
                from ui.pyqt_ui import BirdSortGameUI
                ui = BirdSortGameUI(game, enable_solver=args.solver, theme=args.theme, player=player)
                logger.info("Using PyQt UI")
            except TypeError as e:
                if "unexpected keyword argument" in str(e):
                    # Try without problematic parameters
                    if "theme" in str(e):
                        ui = BirdSortGameUI(game, enable_solver=args.solver)
                        logger.warning("Theme parameter not supported by PyQt UI")
                    elif "player" in str(e):
                        ui = BirdSortGameUI(game, enable_solver=args.solver, theme=args.theme)
                        logger.warning("Player parameter not supported by PyQt UI")
                    else:
                        ui = BirdSortGameUI(game)
                        logger.warning("Some parameters not supported by PyQt UI")
                else:
                    raise
    except ImportError as e:
        logger.error(f"Could not import UI module: {e}")
        logger.error("Make sure you have installed the required dependencies:")
        logger.error("  pip install -r requirements.txt")
        return 1
    
    # Start the game
    logger.info("Starting game UI")
    result = ui.run()
    
    # Output performance metrics if requested
    if profiling_enabled:
        memory_profiler.stop()
        metrics_report = metrics.get_report()
        logger.info(metrics_report)
        print(metrics_report)
    
    logger.info(f"Game exited with code {result}")
    return result

if __name__ == "__main__":
    sys.exit(main())