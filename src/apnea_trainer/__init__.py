"""Apnea Trainer Timer - A command-line timer for apnea training sessions."""

__version__ = "0.1.0"

# Import the main function from timer module
from .timer import main as timer_main

# Define main as an alias to timer_main
def main():
    """Run the apnea trainer timer."""
    return timer_main() 