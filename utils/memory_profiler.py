"""
Memory profiling for Bird Sort Game
"""

import tracemalloc
import linecache
import os

class MemoryProfiler:
    """Track memory usage during algorithm execution"""
    def __init__(self):
        self.tracking = False
        
    def start(self):
        """Start tracking memory usage"""
        tracemalloc.start()
        self.tracking = True
        
    def stop(self):
        """Stop tracking memory usage"""
        if self.tracking:
            tracemalloc.stop()
            self.tracking = False
            
    def get_current_usage(self):
        """
        Get current memory usage.
        
        Returns:
            A tuple of (current, peak) memory usage in bytes
        """
        if self.tracking:
            current, peak = tracemalloc.get_traced_memory()
            return current, peak
        return 0, 0
        
    def get_snapshot(self):
        """
        Get a snapshot of memory usage.
        
        Returns:
            A tracemalloc snapshot or None if not tracking
        """
        if self.tracking:
            return tracemalloc.take_snapshot()
        return None
        
    def compare_snapshots(self, snapshot1, snapshot2):
        """
        Compare two memory snapshots.
        
        Args:
            snapshot1: First snapshot
            snapshot2: Second snapshot
            
        Returns:
            A list of statistics comparing the two snapshots
        """
        if snapshot1 and snapshot2:
            stats = snapshot2.compare_to(snapshot1, 'lineno')
            return stats
        return None
    
    def display_top(self, snapshot, key_type='lineno', limit=10):
        """
        Display the top memory users.
        
        Args:
            snapshot: Memory snapshot to analyze
            key_type: Type of grouping ('lineno', 'traceback', etc.)
            limit: Number of top entries to display
            
        Returns:
            A string containing the top memory users
        """
        if not snapshot:
            return "No snapshot available"
            
        top_stats = snapshot.statistics(key_type)
        
        result = []
        result.append("Top memory users:")
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            filename = os.path.basename(frame.filename)
            line = linecache.getline(frame.filename, frame.lineno).strip()
            size_kb = stat.size / 1024
            result.append(f"#{index}: {filename}:{frame.lineno}: {size_kb:.1f} KB - {line}")
            
        return "\n".join(result)