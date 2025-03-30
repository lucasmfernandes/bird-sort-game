import time
import functools
from contextlib import contextmanager

class Timer:
    """
    Timer class for measuring execution time.
    
    Can be used as a context manager or standalone.
    
    Example:
        # As a context manager
        with Timer() as timer:
            # Code to time
            result = solve_puzzle()
        print(f"Execution time: {timer.elapsed:.4f} seconds")
        
        # As a standalone timer
        timer = Timer()
        timer.start()
        # Code to time
        result = solve_puzzle()
        timer.stop()
        print(f"Execution time: {timer.elapsed:.4f} seconds")
    """
    
    def __init__(self, name=None):
        """
        Initialize a new Timer.
        
        Args:
            name: Optional name for the timer
        """
        self.name = name
        self.start_time = None
        self.end_time = None
        self._elapsed = None
        
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self._elapsed = None
        return self
        
    def stop(self):
        """Stop the timer"""
        self.end_time = time.time()
        self._elapsed = self.end_time - self.start_time
        return self._elapsed
        
    def reset(self):
        """Reset the timer"""
        self.start_time = None
        self.end_time = None
        self._elapsed = None
        
    @property
    def elapsed(self):
        """Get the elapsed time in seconds"""
        if self._elapsed is not None:
            return self._elapsed
        elif self.start_time is not None:
            # Timer is still running
            return time.time() - self.start_time
        else:
            return 0
            
    @property
    def elapsed_ms(self):
        """Get the elapsed time in milliseconds"""
        return self.elapsed * 1000
        
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
        
    def __str__(self):
        """String representation"""
        if self.name:
            return f"{self.name}: {self.elapsed:.4f} seconds"
        else:
            return f"{self.elapsed:.4f} seconds"


def time_function(func=None, *, name=None):
    """
    Decorator to time a function's execution.
    
    Args:
        func: The function to time
        name: Optional name for the timer
        
    Returns:
        Decorated function
        
    Example:
        @time_function
        def solve_puzzle():
            # Puzzle solving code
            
        @time_function(name="A* Search")
        def astar_search():
            # A* search code
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            timer_name = name or fn.__name__
            with Timer(timer_name) as timer:
                result = fn(*args, **kwargs)
            print(f"{timer_name} execution time: {timer.elapsed:.4f} seconds")
            return result, timer.elapsed
        return wrapper
        
    if func is None:
        return decorator
    else:
        return decorator(func)


@contextmanager
def timed_block(name=None):
    """
    Context manager for timing a block of code.
    
    Args:
        name: Optional name for the timer
        
    Example:
        with timed_block("Puzzle Generation"):
            puzzle = generate_puzzle()
    """
    timer = Timer(name)
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()
        if name:
            print(f"{name} execution time: {timer.elapsed:.4f} seconds")
        else:
            print(f"Block execution time: {timer.elapsed:.4f} seconds")