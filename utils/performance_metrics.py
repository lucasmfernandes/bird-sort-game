"""
Performance metrics tracking for Bird Sort Game
"""

import time
import os
import psutil

class PerformanceMetrics:
    """Track and analyze algorithm performance"""
    def __init__(self):
        self.metrics = {}
        self.process = psutil.Process(os.getpid())
        
    def start_timer(self, name):
        """
        Start timing an operation.
        
        Args:
            name: Name of the operation to time
        """
        self.metrics[name] = {
            "start_time": time.time(),
            "start_memory": self.process.memory_info().rss,
            "nodes_expanded": 0,
            "max_memory": 0
        }
        
    def stop_timer(self, name):
        """
        Stop timing an operation and record elapsed time.
        
        Args:
            name: Name of the operation to stop timing
        """
        if name in self.metrics:
            self.metrics[name]["elapsed_time"] = time.time() - self.metrics[name]["start_time"]
            self.metrics[name]["memory_used"] = self.process.memory_info().rss - self.metrics[name]["start_memory"]
            
    def record_nodes_expanded(self, name, count):
        """
        Record number of nodes expanded during search.
        
        Args:
            name: Name of the operation
            count: Number of nodes expanded
        """
        if name in self.metrics:
            self.metrics[name]["nodes_expanded"] = count
            
    def record_memory_usage(self, name, usage=None):
        """
        Record memory usage during search.
        
        Args:
            name: Name of the operation
            usage: Memory usage in bytes, or None to measure current usage
        """
        if name in self.metrics:
            if usage is None:
                usage = self.process.memory_info().rss
            self.metrics[name]["max_memory"] = max(self.metrics[name].get("max_memory", 0), usage)
            
    def get_report(self):
        """
        Generate a performance report.
        
        Returns:
            A string containing the performance report
        """
        report = ["Performance Metrics:"]
        for name, data in self.metrics.items():
            report.append(f"\n{name}:")
            report.append(f"  Time: {data.get('elapsed_time', 'N/A'):.4f} seconds")
            report.append(f"  Nodes expanded: {data.get('nodes_expanded', 'N/A')}")
            
            # Format memory usage
            max_memory = data.get('max_memory', 0)
            if max_memory > 1024 * 1024 * 1024:
                memory_str = f"{max_memory / (1024 * 1024 * 1024):.2f} GB"
            elif max_memory > 1024 * 1024:
                memory_str = f"{max_memory / (1024 * 1024):.2f} MB"
            elif max_memory > 1024:
                memory_str = f"{max_memory / 1024:.2f} KB"
            else:
                memory_str = f"{max_memory} bytes"
                
            report.append(f"  Max memory: {memory_str}")
            
            # Calculate nodes per second
            if 'elapsed_time' in data and data['elapsed_time'] > 0 and 'nodes_expanded' in data:
                nodes_per_second = data['nodes_expanded'] / data['elapsed_time']
                report.append(f"  Nodes per second: {nodes_per_second:.2f}")
                
        return "\n".join(report)