import time
import datetime

def countdown_timer(minutes, seconds):
    """
    Countdown timer that counts down from the specified minutes and seconds to 0.
    
    Args:
        minutes (int): Number of minutes to count down from
        seconds (int): Number of seconds to count down from
    """
    # Convert minutes to seconds and add remaining seconds
    total_seconds = (minutes * 60) + seconds
    
    while total_seconds > 0:
        # Calculate minutes and seconds
        mins, secs = divmod(total_seconds, 60)
        
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

def parse_time(time_str):
    """
    Parse a time string in MM:SS format into minutes and seconds.
    
    Args:
        time_str (str): Time string in MM:SS format
        
    Returns:
        tuple: (minutes, seconds)
        
    Raises:
        ValueError: If the time format is invalid
    """
    try:
        minutes, seconds = map(int, time_str.split(':'))
        if minutes < 0 or seconds < 0 or seconds >= 60:
            raise ValueError
        return minutes, seconds
    except (ValueError, TypeError):
        raise ValueError("Time must be in MM:SS format (e.g., '1:30' for 1 minute and 30 seconds)")

def apply_delta(minutes, seconds, delta_seconds):
    """
    Apply a delta in seconds to the given time, handling overflow/underflow.
    
    Args:
        minutes (int): Current minutes
        seconds (int): Current seconds
        delta_seconds (int): Delta to apply in seconds
        
    Returns:
        tuple: (new_minutes, new_seconds)
    """
    total_seconds = (minutes * 60) + seconds + delta_seconds
    if total_seconds < 0:
        return 0, 0
    return divmod(total_seconds, 60)

def main():
    try:
        # Get input from user for training round length in MM:SS format
        time_str = input("Enter the length of each training round (MM:SS format, e.g., '1:30' for 1 minute and 30 seconds): ")
        minutes, seconds = parse_time(time_str)
        
        # Get training round delta
        training_delta = int(input("Enter the change in training round length per round (in seconds, e.g., -5 to decrease by 5 seconds each round): "))
        
        rounds = int(input("Enter the number of rounds: "))
        
        # Get rest period in MM:SS format
        rest_str = input("Enter the rest period between rounds (MM:SS format, e.g., '0:30' for 30 seconds): ")
        rest_minutes, rest_seconds = parse_time(rest_str)
        
        # Get rest period delta
        rest_delta = int(input("Enter the change in rest period length per round (in seconds, e.g., -5 to decrease by 5 seconds each round): "))
        
        if rounds <= 0:
            print("Please enter a positive number for rounds.")
            return
            
        print(f"\nStarting {rounds} training rounds...")
        print(f"Initial training round length: {minutes} minutes and {seconds} seconds")
        print(f"Training round length change per round: {training_delta} seconds")
        print(f"Initial rest period: {rest_minutes} minutes and {rest_seconds} seconds")
        print(f"Rest period change per round: {rest_delta} seconds")
        
        for round_num in range(1, rounds + 1):
            # Calculate current round times
            current_minutes, current_seconds = apply_delta(minutes, seconds, training_delta * (round_num - 1))
            current_rest_minutes, current_rest_seconds = apply_delta(rest_minutes, rest_seconds, rest_delta * (round_num - 1))
            
            # Visual indicator when round starts
            print(f"\n🔔 Training Round {round_num} of {rounds} starting! 🔔")
            print('\a')
            print(f"Round length: {current_minutes}:{current_seconds:02d}")
            countdown_timer(current_minutes, current_seconds)
            
            # Add a rest period after each round (including the last one)
            print(f"\n💤 Rest period starting...")
            print('\a')
            print(f"Rest length: {current_rest_minutes}:{current_rest_seconds:02d}")
            countdown_timer(current_rest_minutes, current_rest_seconds)
        
        # Final visual indicator when all rounds are complete
        print("\n🎉 All rounds completed! 🎉")
        print('\a')
        
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 