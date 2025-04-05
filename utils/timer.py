"""
Timer utility for Bird Sort Game
"""

import time
from functools import wraps

class Timer:
    """Utility for timing operations"""
    def __init__(self, name=None):
        """
        Initialize a timer.
        
        Args:
            name: Optional name for the timer
        """
        self.name = name or "Timer"
        self.start_time = None
        self.elapsed = 0
        self.running = False
        
    def start(self):
        """Start the timer"""
        if not self.running:
            self.start_time = time.time()
            self.running = True
        return self
        
    def stop(self):
        """Stop the timer and record elapsed time"""
        if self.running:
            self.elapsed += time.time() - self.start_time
            self.running = False
        return self
        
    def reset(self):
        """Reset the timer"""
        self.start_time = None
        self.elapsed = 0
        self.running = False
        return self
        
    def restart(self):
        """Reset and start the timer"""
        self.reset()
        return self.start()
        
    def get_elapsed(self):
        """
        Get the elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if self.running:
            return self.elapsed + (time.time() - self.start_time)
        return self.elapsed
        
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
        
    def __exit__(self, *args):
        """Context manager exit"""
        self.stop()
        
    def __str__(self):
        """String representation"""
        return f"{self.name}: {self.get_elapsed():.4f} seconds"


def timed(func=None, *, name=None, logger=None):
    """
    Decorator for timing function execution.
    
    Args:
        func: Function to time
        name: Optional name for the timer
        logger: Optional logger to log timing information
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            timer_name = name or f.__name__
            timer = Timer(timer_name)
            timer.start()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                timer.stop()
                if logger:
                    logger.info(f"{timer}")
                else:
                    print(f"{timer}")
        return wrapper
        
    if func is None:
        return decorator
    return decorator(func)


class TimingStats:
    """Collect and analyze timing statistics"""
    def __init__(self):
        self.timings = {}
        
    def record(self, name, elapsed):
        """
        Record a timing.
        
        Args:
            name: Name of the operation
            elapsed: Elapsed time in seconds
        """
        if name not in self.timings:
            self.timings[name] = []
        self.timings[name].append(elapsed)
        
    def get_stats(self, name):
        """
        Get statistics for a named operation.
        
        Args:
            name: Name of the operation
            
        Returns:
            Dictionary of statistics
        """
        if name not in self.timings or not self.timings[name]:
            return None
            
        times = self.timings[name]
        return {
            "count": len(times),
            "total": sum(times),
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / len(times)
        }
        
    def get_report(self):
        """
        Generate a timing report.
        
        Returns:
            A string containing the timing report
        """
        report = ["Timing Statistics:"]
        for name in sorted(self.timings.keys()):
            stats = self.get_stats(name)
            if stats:
                report.append(f"\n{name}:")
                report.append(f"  Count: {stats['count']}")
                report.append(f"  Total: {stats['total']:.4f} seconds")
                report.append(f"  Min: {stats['min']:.4f} seconds")
                report.append(f"  Max: {stats['max']:.4f} seconds")
                report.append(f"  Avg: {stats['avg']:.4f} seconds")
                
        return "\n".join(report)