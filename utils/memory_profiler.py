import os
import sys
import time
import functools
import tracemalloc
from contextlib import contextmanager

class MemoryProfiler:
    """
    Memory profiler for measuring memory usage.
    
    Can be used as a context manager or standalone.
    
    Example:
        # As a context manager
        with MemoryProfiler() as profiler:
            # Code to profile
            result = solve_puzzle()
        print(f"Peak memory usage: {profiler.peak_usage_mb:.2f} MB")
        
        # As a standalone profiler
        profiler = MemoryProfiler()
        profiler.start()
        # Code to profile
        result = solve_puzzle()
        profiler.stop()
        print(f"Peak memory usage: {profiler.peak_usage_mb:.2f} MB")
    """
    
    def __init__(self, name=None):
        """
        Initialize a new MemoryProfiler.
        
        Args:
            name: Optional name for the profiler
        """
        self.name = name
        self.start_snapshot = None
        self.peak_snapshot = None
        self.current_snapshot = None
        self.peak_usage = 0
        
    def start(self):
        """Start the memory profiler"""
        tracemalloc.start()
        self.start_snapshot = tracemalloc.take_snapshot()
        self.peak_usage = 0
        return self
        
    def stop(self):
        """Stop the memory profiler"""
        self.current_snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        return self.peak_usage
        
    def snapshot(self):
        """Take a memory snapshot"""
        if not tracemalloc.is_tracing():
            return None
            
        snapshot = tracemalloc.take_snapshot()
        current_usage = sum(stat.size for stat in snapshot.statistics('filename'))
        
        if current_usage > self.peak_usage:
            self.peak_usage = current_usage
            self.peak_snapshot = snapshot
            
        return snapshot
        
    def get_usage(self):
        """Get the current memory usage in bytes"""
        if not tracemalloc.is_tracing():
            return 0
            
        snapshot = tracemalloc.take_snapshot()
        return sum(stat.size for stat in snapshot.statistics('filename'))
        
    @property
    def peak_usage_mb(self):
        """Get the peak memory usage in megabytes"""
        return self.peak_usage / (1024 * 1024)
        
    def print_stats(self, limit=10):
        """Print memory usage statistics"""
        if self.peak_snapshot is None:
            print("No memory statistics available")
            return
            
        print(f"{'=' * 40}")
        if self.name:
            print(f"Memory Profile: {self.name}")
        print(f"Peak memory usage: {self.peak_usage_mb:.2f} MB")
        print(f"{'=' * 40}")
        
        if self.start_snapshot:
            print("\nTop memory consumers (compared to start):")
            top_stats = self.peak_snapshot.compare_to(self.start_snapshot, 'lineno')
            for stat in top_stats[:limit]:
                print(f"{stat.size_diff / 1024:.1f} KB: {stat.traceback.format()[0]}")
        
        print("\nTop memory consumers (total):")
        top_stats = self.peak_snapshot.statistics('lineno')
        for stat in top_stats[:limit]:
            print(f"{stat.size / 1024:.1f} KB: {stat.traceback.format()[0]}")
            
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
            return f"{self.name}: {self.peak_usage_mb:.2f} MB"
        else:
            return f"{self.peak_usage_mb:.2f} MB"


def profile_memory(func=None, *, name=None, print_stats=True):
    """
    Decorator to profile a function's memory usage.
    
    Args:
        func: The function to profile
        name: Optional name for the profiler
        print_stats: Whether to print statistics after execution
        
    Returns:
        Decorated function
        
    Example:
        @profile_memory
        def solve_puzzle():
            # Puzzle solving code
            
        @profile_memory(name="A* Search", print_stats=True)
        def astar_search():
            # A* search code
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            profiler_name = name or fn.__name__
            with MemoryProfiler(profiler_name) as profiler:
                # Take snapshots periodically during execution
                result = fn(*args, **kwargs)
                # Take a final snapshot
                profiler.snapshot()
                
            if print_stats:
                profiler.print_stats()
                
            return result, profiler.peak_usage_mb
        return wrapper
        
    if func is None:
        return decorator
    else:
        return decorator(func)


@contextmanager
def profiled_block(name=None, print_stats=True):
    """
    Context manager for profiling a block of code.
    
    Args:
        name: Optional name for the profiler
        print_stats: Whether to print statistics after execution
        
    Example:
        with profiled_block("Puzzle Generation"):
            puzzle = generate_puzzle()
    """
    profiler = MemoryProfiler(name)
    profiler.start()
    try:
        yield profiler
    finally:
        profiler.stop()
        if print_stats:
            profiler.print_stats()