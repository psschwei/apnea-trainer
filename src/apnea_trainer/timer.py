import time
import datetime
import tomli
import os
import sys
import argparse

def load_config(config_path="config.toml"):
    """
    Load configuration from TOML file.
    
    Args:
        config_path (str): Path to the config file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, "rb") as f:
            return tomli.load(f)
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Using default values.")
        return None
    except tomli.TOMLDecodeError as e:
        print(f"Error parsing config file: {e}")
        sys.exit(1)

def parse_time(time_str):
    """
    Parse a time string in MM:SS format into minutes and seconds.
    Supports negative values for deltas.
    
    Args:
        time_str (str): Time string in MM:SS format
        
    Returns:
        tuple: (minutes, seconds)
        
    Raises:
        ValueError: If the time format is invalid
    """
    try:
        # Handle negative values
        is_negative = time_str.startswith('-')
        if is_negative:
            time_str = time_str[1:]  # Remove the minus sign
            
        # Split and convert to integers
        parts = time_str.split(':')
        if len(parts) != 2:
            raise ValueError("Time must be in MM:SS format")
            
        minutes = int(parts[0])
        seconds = int(parts[1])
        
        if seconds < 0 or seconds >= 60:
            raise ValueError("Seconds must be between 0 and 59")
            
        # Apply negative sign if needed
        if is_negative:
            minutes = -minutes
            seconds = -seconds
            
        return minutes, seconds
    except (ValueError, TypeError):
        raise ValueError("Time must be in MM:SS format (e.g., '1:30' for 1 minute and 30 seconds, '-0:05' for -5 seconds)")

def time_to_seconds(minutes, seconds):
    """
    Convert minutes and seconds to total seconds.
    
    Args:
        minutes (int): Number of minutes
        seconds (int): Number of seconds
        
    Returns:
        int: Total seconds
    """
    return (minutes * 60) + seconds

def seconds_to_time(total_seconds):
    """
    Convert total seconds to minutes and seconds.
    
    Args:
        total_seconds (int): Total number of seconds
        
    Returns:
        tuple: (minutes, seconds)
    """
    if total_seconds < 0:
        return 0, 0
    return divmod(total_seconds, 60)

def apply_delta(minutes, seconds, delta_minutes, delta_seconds):
    """
    Apply a delta in MM:SS format to the given time, handling overflow/underflow.
    
    Args:
        minutes (int): Current minutes
        seconds (int): Current seconds
        delta_minutes (int): Delta minutes
        delta_seconds (int): Delta seconds
        
    Returns:
        tuple: (new_minutes, new_seconds)
    """
    total_seconds = time_to_seconds(minutes, seconds)
    delta_total = time_to_seconds(delta_minutes, delta_seconds)
    return seconds_to_time(total_seconds + delta_total)

def format_time(minutes, seconds):
    """
    Format minutes and seconds as MM:SS, handling negative values.
    
    Args:
        minutes (int): Number of minutes
        seconds (int): Number of seconds
        
    Returns:
        str: Formatted time string
    """
    if minutes < 0 or seconds < 0:
        return f"-{abs(minutes):02d}:{abs(seconds):02d}"
    return f"{minutes:02d}:{seconds:02d}"

def countdown_timer(minutes, seconds):
    """
    Countdown timer that counts down from the specified minutes and seconds to 0.
    
    Args:
        minutes (int): Number of minutes to count down from
        seconds (int): Number of seconds to count down from
    """
    # Convert minutes to seconds and add remaining seconds
    total_seconds = time_to_seconds(minutes, seconds)
    
    while total_seconds > 0:
        # Calculate minutes and seconds
        mins, secs = seconds_to_time(total_seconds)
        
        # Format the time display
        timer_display = f'{mins:02d}:{secs:02d}'
        
        # Print the timer display and overwrite the previous line
        print(timer_display, end='\r')
        
        # Wait for 1 second
        time.sleep(1)
        
        # Decrease total seconds
        total_seconds -= 1
    
    # Visual indicator when timer ends
    print("\n🔔 Time's up! 🔔")
    print('\a')

def get_input_with_default(prompt, default_value):
    """
    Get user input with a default value.
    
    Args:
        prompt (str): Input prompt
        default_value: Default value to use if user just presses Enter
        
    Returns:
        The user's input or the default value
    """
    if default_value is not None:
        user_input = input(f"{prompt} [{default_value}]: ")
        return user_input if user_input else default_value
    return input(f"{prompt}: ")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Apnea Trainer Timer')
    parser.add_argument('-c', '--config', 
                      default='config.toml',
                      help='Path to configuration file (default: config.toml)')
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)
        
        # Get training round settings
        if config:
            time_str = get_input_with_default(
                "Enter the length of each training round (MM:SS format)",
                str(config["training"]["initial_length"])
            )
            training_delta = get_input_with_default(
                "Enter the change in training round length per round (MM:SS format, e.g., '-0:05' to decrease by 5 seconds)",
                str(config["training"]["delta"])
            )
            rounds_str = get_input_with_default(
                "Enter the number of rounds",
                str(config["session"]["rounds"])
            )
            rest_str = get_input_with_default(
                "Enter the rest period between rounds (MM:SS format)",
                str(config["rest"]["initial_length"])
            )
            rest_delta = get_input_with_default(
                "Enter the change in rest period length per round (MM:SS format, e.g., '-0:02' to decrease by 2 seconds)",
                str(config["rest"]["delta"])
            )
        else:
            time_str = input("Enter the length of each training round (MM:SS format, e.g., '1:30' for 1 minute and 30 seconds): ")
            training_delta = input("Enter the change in training round length per round (MM:SS format, e.g., '-0:05' to decrease by 5 seconds): ")
            rounds_str = input("Enter the number of rounds: ")
            rest_str = input("Enter the rest period between rounds (MM:SS format, e.g., '0:30' for 30 seconds): ")
            rest_delta = input("Enter the change in rest period length per round (MM:SS format, e.g., '-0:02' to decrease by 2 seconds): ")
        
        # Parse inputs
        minutes, seconds = parse_time(time_str)
        training_delta_mins, training_delta_secs = parse_time(training_delta)
        rounds = int(rounds_str)  # Convert rounds string to integer only once
        rest_minutes, rest_seconds = parse_time(rest_str)
        rest_delta_mins, rest_delta_secs = parse_time(rest_delta)
        
        if rounds <= 0:
            print("Please enter a positive number for rounds.")
            return
            
        print(f"\nStarting {rounds} training rounds...")
        print(f"Initial training round length: {format_time(minutes, seconds)}")
        print(f"Training round length change per round: {format_time(training_delta_mins, training_delta_secs)}")
        print(f"Initial rest period: {format_time(rest_minutes, rest_seconds)}")
        print(f"Rest period change per round: {format_time(rest_delta_mins, rest_delta_secs)}")
        
        for round_num in range(1, rounds + 1):
            # Calculate current round times
            current_minutes, current_seconds = apply_delta(
                minutes, seconds,
                training_delta_mins * (round_num - 1),
                training_delta_secs * (round_num - 1)
            )
            current_rest_minutes, current_rest_seconds = apply_delta(
                rest_minutes, rest_seconds,
                rest_delta_mins * (round_num - 1),
                rest_delta_secs * (round_num - 1)
            )
            
            # Visual indicator when round starts
            print(f"\n🔔 Training Round {round_num} of {rounds} starting! 🔔")
            print('\a')
            print(f"Round length: {format_time(current_minutes, current_seconds)}")
            countdown_timer(current_minutes, current_seconds)
            
            # Add a rest period after each round (including the last one)
            print(f"\n💤 Rest period starting...")
            print('\a')
            print(f"Rest length: {format_time(current_rest_minutes, current_rest_seconds)}")
            countdown_timer(current_rest_minutes, current_rest_seconds)
        
        # Final visual indicator when all rounds are complete
        print("\n🎉 All rounds completed! 🎉")
        print('\a')
        
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 