"""
Logging utility for Bird Sort Game
"""

import logging
import os
import sys
import time
from datetime import datetime

class Logger:
    """Custom logger for Bird Sort Game"""
    
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    def __init__(self, name="bird_sort", level="INFO", log_file=None, console=True):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for logging
            console: Whether to log to console
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVELS.get(level.upper(), logging.INFO))
        self.logger.propagate = False
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler if requested
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler if log_file is provided
        if log_file:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)
        
    def info(self, message):
        """Log an info message"""
        self.logger.info(message)
        
    def warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)
        
    def error(self, message):
        """Log an error message"""
        self.logger.error(message)
        
    def critical(self, message):
        """Log a critical message"""
        self.logger.critical(message)
        
    def exception(self, message):
        """Log an exception with traceback"""
        self.logger.exception(message)


class GameLogger:
    """Game-specific logger for tracking game events"""
    def __init__(self, game, log_file=None):
        """
        Initialize the game logger.
        
        Args:
            game: BirdSortGame instance
            log_file: Optional file path for logging
        """
        self.game = game
        
        # Create default log file if none provided
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_file = os.path.join(log_dir, f"game_{timestamp}.log")
            
        self.logger = Logger(name="game_events", level="INFO", log_file=log_file)
        self.move_count = 0
        self.start_time = time.time()
        
        # Log game start
        self.logger.info(f"Game started with {game.num_branches} branches and {game.num_colors} colors")
        self.log_state("Initial state")
        
    def log_move(self, from_branch, to_branch):
        """
        Log a move.
        
        Args:
            from_branch: Source branch index
            to_branch: Target branch index
        """
        self.move_count += 1
        self.logger.info(f"Move {self.move_count}: Branch {from_branch+1} -> Branch {to_branch+1}")
        self.log_state(f"After move {self.move_count}")
        
    def log_state(self, label="Current state"):
        """
        Log the current game state.
        
        Args:
            label: Label for the state
        """
        state_str = str(self.game.state).replace("\n", " | ")
        self.logger.info(f"{label}: {state_str}")
        
    def log_undo(self):
        """Log an undo operation"""
        self.move_count -= 1
        self.logger.info(f"Undo to move {self.move_count}")
        self.log_state(f"After undo (move {self.move_count})")
        
    def log_reset(self):
        """Log a game reset"""
        self.move_count = 0
        self.start_time = time.time()
        self.logger.info("Game reset")
        self.log_state("New initial state")
        
    def log_win(self):
        """Log a game win"""
        elapsed = time.time() - self.start_time
        self.logger.info(f"Game solved in {self.move_count} moves and {elapsed:.2f} seconds")
        
    def log_algorithm_stats(self, algorithm, nodes_expanded, time_taken):
        """
        Log algorithm statistics.
        
        Args:
            algorithm: Algorithm name
            nodes_expanded: Number of nodes expanded
            time_taken: Time taken in seconds
        """
        self.logger.info(f"Algorithm: {algorithm}")
        self.logger.info(f"Nodes expanded: {nodes_expanded}")
        self.logger.info(f"Time taken: {time_taken:.4f} seconds")
        self.logger.info(f"Nodes per second: {nodes_expanded/time_taken:.2f}")