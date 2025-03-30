import os
import sys
import logging
import datetime
import json
from pathlib import Path

class Logger:
    """
    Logger for recording metrics and events.
    
    Example:
        logger = Logger("astar_search")
        logger.log_start({"branches": 7, "colors": 5})
        # Run algorithm
        logger.log_result({
            "solution_found": True,
            "moves": 25,
            "time": 1.234,
            "memory": 45.6
        })
    """
    
    def __init__(self, name, log_dir="logs"):
        """
        Initialize a new Logger.
        
        Args:
            name: Name for the logger
            log_dir: Directory to store log files
        """
        self.name = name
        self.log_dir = log_dir
        self.start_time = None
        self.end_time = None
        self.metrics = {}
        
        # Create log directory if it doesn't exist
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Set up Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{log_dir}/{name}_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_start(self, params=None):
        """
        Log the start of an algorithm run.
        
        Args:
            params: Dictionary of parameters for the run
        """
        self.start_time = datetime.datetime.now()
        self.metrics = {
            "start_time": self.start_time.isoformat(),
            "params": params or {}
        }
        
        self.logger.info(f"Starting {self.name} with params: {json.dumps(params or {})}")
        
    def log_result(self, results):
        """
        Log the results of an algorithm run.
        
        Args:
            results: Dictionary of results
        """
        self.end_time = datetime.datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        self.metrics.update({
            "end_time": self.end_time.isoformat(),
            "duration": duration,
            "results": results
        })
        
        self.logger.info(f"Results: {json.dumps(results)}")
        self.logger.info(f"Total duration: {duration:.4f} seconds")
        
        # Save metrics to JSON file
        metrics_file = f"{self.log_dir}/{self.name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
    def log_event(self, event_type, data=None):
        """
        Log an event during an algorithm run.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        event = {
            "time": datetime.datetime.now().isoformat(),
            "type": event_type,
            "data": data or {}
        }
        
        if "events" not in self.metrics:
            self.metrics["events"] = []
            
        self.metrics["events"].append(event)
        
        self.logger.info(f"Event {event_type}: {json.dumps(data or {})}")
        
    def log_error(self, error, traceback=None):
        """
        Log an error during an algorithm run.
        
        Args:
            error: Error message or exception
            traceback: Optional traceback
        """
        self.logger.error(f"Error: {error}")
        if traceback:
            self.logger.error(f"Traceback: {traceback}")
            
        self.metrics["error"] = {
            "message": str(error),
            "traceback": traceback
        }
        
    def __str__(self):
        """String representation"""
        return f"Logger({self.name})"


def setup_logger(name, log_dir="logs"):
    """
    Set up a logger with the given name.
    
    Args:
        name: Name for the logger
        log_dir: Directory to store log files
        
    Returns:
        Logger instance
    """
    return Logger(name, log_dir)