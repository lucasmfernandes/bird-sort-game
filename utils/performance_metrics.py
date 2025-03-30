import time
import tracemalloc
import traceback
import gc
import psutil
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from .timer import Timer
from .memory_profiler import MemoryProfiler
from .logger import Logger

class PerformanceMetrics:
    """
    Performance metrics for benchmarking algorithms.
    
    Example:
        metrics = PerformanceMetrics("algorithm_comparison")
        
        # Benchmark A* search
        metrics.benchmark(
            "A*",
            lambda: astar_search(initial_state, is_goal, get_successors),
            {"heuristic": "admissible", "weight": 1.0}
        )
        
        # Benchmark Weighted A*
        metrics.benchmark(
            "Weighted A*",
            lambda: astar_search(initial_state, is_goal, get_successors, weight=1.5),
            {"heuristic": "weighted", "weight": 1.5}
        )
        
        # Generate comparison report
        metrics.generate_report()
    """
    
    def __init__(self, name, results_dir="results"):
        """
        Initialize a new PerformanceMetrics instance.
        
        Args:
            name: Name for the benchmark
            results_dir: Directory to store results
        """
        self.name = name
        self.results_dir = results_dir
        self.results = []
        self.logger = Logger(name, log_dir=results_dir)
        
        # Create results directory if it doesn't exist
        Path(results_dir).mkdir(parents=True, exist_ok=True)
        
    def benchmark(self, algorithm_name, algorithm_func, params=None, runs=1):
        """
        Benchmark an algorithm.
        
        Args:
            algorithm_name: Name of the algorithm
            algorithm_func: Function that runs the algorithm
            params: Dictionary of parameters for the algorithm
            runs: Number of runs to average over
        
        Returns:
            Dictionary of benchmark results
        """
        params = params or {}
        
        self.logger.log_event("benchmark_start", {
            "algorithm": algorithm_name,
            "params": params,
            "runs": runs
        })
        
        # Collect garbage before benchmarking
        gc.collect()
        
        # Initialize metrics
        total_time = 0
        total_memory = 0
        total_moves = 0
        solutions_found = 0
        
        # Run the algorithm multiple times
        for run in range(runs):
            # Measure time and memory
            with Timer() as timer, MemoryProfiler() as memory_profiler:
                # Run the algorithm
                try:
                    result = algorithm_func()
                    
                    # Extract solution information
                    if isinstance(result, tuple) and len(result) >= 2:
                        solution, solution_info = result[0], result[1:]
                    else:
                        solution = result
                        solution_info = {}
                        
                    # Count moves if solution is a path
                    if solution and hasattr(solution, '__len__'):
                        moves = len(solution) - 1
                    elif isinstance(solution_info, dict) and 'moves' in solution_info:
                        moves = solution_info['moves']
                    else:
                        moves = 0
                        
                    solution_found = solution is not None
                    
                    # Update totals
                    total_time += timer.elapsed
                    total_memory += memory_profiler.peak_usage_mb
                    total_moves += moves
                    solutions_found += 1 if solution_found else 0
                    
                    # Log run results
                    self.logger.log_event(f"benchmark_run_{run}", {
                        "time": timer.elapsed,
                        "memory": memory_profiler.peak_usage_mb,
                        "moves": moves,
                        "solution_found": solution_found
                    })
                    
                except Exception as e:
                    self.logger.log_error(str(e), traceback.format_exc())
                    
        # Calculate averages
        avg_time = total_time / runs if runs > 0 else 0
        avg_memory = total_memory / runs if runs > 0 else 0
        avg_moves = total_moves / solutions_found if solutions_found > 0 else 0
        success_rate = solutions_found / runs if runs > 0 else 0
        
        # Get process information
        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # Create result dictionary
        result = {
            "algorithm": algorithm_name,
            "params": params,
            "runs": runs,
            "avg_time": avg_time,
            "avg_memory": avg_memory,
            "avg_moves": avg_moves,
            "success_rate": success_rate,
            "cpu_percent": cpu_percent
        }
        
        # Add to results list
        self.results.append(result)
        
        # Log benchmark results
        self.logger.log_event("benchmark_result", result)
        
        return result
        
    def save_results(self):
        """
        Save benchmark results to a JSON file.
        
        Returns:
            Path to the results file
        """
        results_file = f"{self.results_dir}/{self.name}_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        return results_file
        
    def generate_report(self, include_plots=True):
        """
        Generate a report of benchmark results.
        
        Args:
            include_plots: Whether to include plots in the report
            
        Returns:
            Path to the report file
        """
        # Save results
        self.save_results()
        
        # Create DataFrame from results
        df = pd.DataFrame(self.results)
        
        # Generate report
        report_file = f"{self.results_dir}/{self.name}_report.html"
        
        with open(report_file, 'w') as f:
            f.write("<html><head>")
            f.write(f"<title>{self.name} Benchmark Report</title>")
            f.write("<style>")
            f.write("body { font-family: Arial, sans-serif; margin: 20px; }")
            f.write("table { border-collapse: collapse; width: 100%; }")
            f.write("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
            f.write("th { background-color: #f2f2f2; }")
            f.write("tr:nth-child(even) { background-color: #f9f9f9; }")
            f.write("h1, h2 { color: #333; }")
            f.write("</style>")
            f.write("</head><body>")
            
            f.write(f"<h1>{self.name} Benchmark Report</h1>")
            
            # Summary table
            f.write("<h2>Summary</h2>")
            f.write("<table>")
            f.write("<tr><th>Algorithm</th><th>Avg Time (s)</th><th>Avg Memory (MB)</th><th>Avg Moves</th><th>Success Rate</th></tr>")
            
            for result in self.results:
                f.write("<tr>")
                f.write(f"<td>{result['algorithm']}</td>")
                f.write(f"<td>{result['avg_time']:.4f}</td>")
                f.write(f"<td>{result['avg_memory']:.2f}</td>")
                f.write(f"<td>{result['avg_moves']:.1f}</td>")
                f.write(f"<td>{result['success_rate']*100:.1f}%</td>")
                f.write("</tr>")
                
            f.write("</table>")
            
            # Detailed results
            f.write("<h2>Detailed Results</h2>")
            f.write("<table>")
            f.write("<tr><th>Algorithm</th><th>Parameters</th><th>Runs</th><th>Avg Time (s)</th><th>Avg Memory (MB)</th><th>Avg Moves</th><th>Success Rate</th><th>CPU %</th></tr>")
            
            for result in self.results:
                f.write("<tr>")
                f.write(f"<td>{result['algorithm']}</td>")
                f.write(f"<td>{json.dumps(result['params'])}</td>")
                f.write(f"<td>{result['runs']}</td>")
                f.write(f"<td>{result['avg_time']:.4f}</td>")
                f.write(f"<td>{result['avg_memory']:.2f}</td>")
                f.write(f"<td>{result['avg_moves']:.1f}</td>")
                f.write(f"<td>{result['success_rate']*100:.1f}%</td>")
                f.write(f"<td>{result['cpu_percent']:.1f}%</td>")
                f.write("</tr>")
                
            f.write("</table>")
            
            # Generate plots
            if include_plots and len(self.results) > 0:
                # Time comparison
                plt.figure(figsize=(10, 6))
                plt.bar([r['algorithm'] for r in self.results], [r['avg_time'] for r in self.results])
                plt.title('Average Execution Time')
                plt.xlabel('Algorithm')
                plt.ylabel('Time (seconds)')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                time_plot = f"{self.results_dir}/{self.name}_time.png"
                plt.savefig(time_plot)
                
                # Memory comparison
                plt.figure(figsize=(10, 6))
                plt.bar([r['algorithm'] for r in self.results], [r['avg_memory'] for r in self.results])
                plt.title('Average Memory Usage')
                plt.xlabel('Algorithm')
                plt.ylabel('Memory (MB)')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                memory_plot = f"{self.results_dir}/{self.name}_memory.png"
                plt.savefig(memory_plot)
                
                # Moves comparison
                plt.figure(figsize=(10, 6))
                plt.bar([r['algorithm'] for r in self.results], [r['avg_moves'] for r in self.results])
                plt.title('Average Number of Moves')
                plt.xlabel('Algorithm')
                plt.ylabel('Moves')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                moves_plot = f"{self.results_dir}/{self.name}_moves.png"
                plt.savefig(moves_plot)
                
                # Add plots to report
                f.write("<h2>Plots</h2>")
                f.write("<div style='display: flex; flex-wrap: wrap; justify-content: space-around;'>")
                f.write(f"<div><h3>Execution Time</h3><img src='{os.path.basename(time_plot)}' width='400'></div>")
                f.write(f"<div><h3>Memory Usage</h3><img src='{os.path.basename(memory_plot)}' width='400'></div>")
                f.write(f"<div><h3>Number of Moves</h3><img src='{os.path.basename(moves_plot)}' width='400'></div>")
                f.write("</div>")
                
            f.write("</body></html>")
            
        return report_file
        
    def __str__(self):
        """String representation"""
        return f"PerformanceMetrics({self.name}, {len(self.results)} results)"


def benchmark_algorithm(algorithm_func, name=None, params=None, runs=1):
    """
    Benchmark a single algorithm.
    
    Args:
        algorithm_func: Function that runs the algorithm
        name: Name of the algorithm
        params: Dictionary of parameters for the algorithm
        runs: Number of runs to average over
        
    Returns:
        Dictionary of benchmark results
    """
    name = name or algorithm_func.__name__
    metrics = PerformanceMetrics(f"benchmark_{name}")
    result = metrics.benchmark(name, algorithm_func, params, runs)
    metrics.save_results()
    return result