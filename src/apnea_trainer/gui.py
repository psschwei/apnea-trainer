import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import os
import platform
from .timer import parse_time, format_time, time_to_seconds, seconds_to_time, load_config

class ApneaTrainerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Apnea Trainer")
        self.root.geometry("400x600")
        
        # Center the window
        self.root.update_idletasks()  # Update the window to get its dimensions
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # Timer state
        self.is_running = False
        self.current_round = 0
        self.total_rounds = 0
        self.remaining_seconds = 0
        self.timer_thread = None
        
        # Load default configuration
        self.config = load_config()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Timer display at the top
        self.timer_frame = ttk.Frame(main_frame)
        self.timer_frame.pack(pady=20)
        
        self.timer_label = ttk.Label(self.timer_frame, text="00:00", font=('Helvetica', 48))
        self.timer_label.pack()
        
        self.status_label = ttk.Label(self.timer_frame, text="Ready", font=('Helvetica', 12))
        self.status_label.pack()
        
        # Control buttons below timer
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Settings section below controls
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Training settings
        ttk.Label(settings_frame, text="Training Settings", font=('Helvetica', 12, 'bold')).pack(pady=5)
        
        # Initial training length
        training_length_frame = ttk.Frame(settings_frame)
        training_length_frame.pack(pady=2)
        ttk.Label(training_length_frame, text="Initial Training Length (MM:SS):", width=30, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        self.training_length = ttk.Entry(training_length_frame, width=10)
        self.training_length.insert(0, self.config["training"]["initial_length"])
        self.training_length.pack(side=tk.LEFT, padx=5)
        
        # Training delta
        training_delta_frame = ttk.Frame(settings_frame)
        training_delta_frame.pack(pady=2)
        ttk.Label(training_delta_frame, text="Training Delta (MM:SS):", width=30, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        self.training_delta = ttk.Entry(training_delta_frame, width=10)
        self.training_delta.insert(0, self.config["training"]["delta"])
        self.training_delta.pack(side=tk.LEFT, padx=5)
        
        # Rest settings
        ttk.Label(settings_frame, text="Rest Settings", font=('Helvetica', 12, 'bold')).pack(pady=5)
        
        # Initial rest length
        rest_length_frame = ttk.Frame(settings_frame)
        rest_length_frame.pack(pady=2)
        ttk.Label(rest_length_frame, text="Initial Rest Length (MM:SS):", width=30, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        self.rest_length = ttk.Entry(rest_length_frame, width=10)
        self.rest_length.insert(0, self.config["rest"]["initial_length"])
        self.rest_length.pack(side=tk.LEFT, padx=5)
        
        # Rest delta
        rest_delta_frame = ttk.Frame(settings_frame)
        rest_delta_frame.pack(pady=2)
        ttk.Label(rest_delta_frame, text="Rest Delta (MM:SS):", width=30, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        self.rest_delta = ttk.Entry(rest_delta_frame, width=10)
        self.rest_delta.insert(0, self.config["rest"]["delta"])
        self.rest_delta.pack(side=tk.LEFT, padx=5)
        
        # Session settings
        ttk.Label(settings_frame, text="Session Settings", font=('Helvetica', 12, 'bold')).pack(pady=5)
        
        # Number of rounds
        rounds_frame = ttk.Frame(settings_frame)
        rounds_frame.pack(pady=2)
        ttk.Label(rounds_frame, text="Number of Rounds:", width=30, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        self.rounds = ttk.Entry(rounds_frame, width=10)
        self.rounds.insert(0, str(self.config["session"]["rounds"]))
        self.rounds.pack(side=tk.LEFT, padx=5)
    
    def validate_inputs(self):
        try:
            # Validate all time inputs
            parse_time(self.training_length.get())
            parse_time(self.training_delta.get())
            parse_time(self.rest_length.get())
            parse_time(self.rest_delta.get())
            
            # Validate rounds
            rounds = int(self.rounds.get())
            if rounds <= 0:
                raise ValueError("Number of rounds must be positive")
            
            return True
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return False
    
    def start_timer(self):
        if not self.validate_inputs():
            return
            
        self.is_running = True
        self.current_round = 0  # Start at 0 to indicate pre-training rest
        self.total_rounds = int(self.rounds.get())
        
        # Disable inputs and start button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start with initial rest period
        self.status_label.config(text="Initial Rest Period")
        self.timer_label.config(foreground="green")  # Green for rest
        rest_mins, rest_secs = parse_time(self.rest_length.get())
        self.remaining_seconds = time_to_seconds(rest_mins, rest_secs)
        self.timer_thread = threading.Thread(target=self.run_timer, args=(rest_mins, rest_secs))
        self.timer_thread.start()
    
    def stop_timer(self):
        self.is_running = False
        if self.timer_thread:
            self.timer_thread.join()
        
        # Reset UI
        self.timer_label.config(text="00:00", foreground="black")  # Reset to black
        self.status_label.config(text="Ready")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def start_round(self):
        if not self.is_running:
            return
            
        # Calculate current round times
        training_mins, training_secs = parse_time(self.training_length.get())
        training_delta_mins, training_delta_secs = parse_time(self.training_delta.get())
        rest_mins, rest_secs = parse_time(self.rest_length.get())
        rest_delta_mins, rest_delta_secs = parse_time(self.rest_delta.get())
        
        # Apply deltas based on current round
        current_training_mins, current_training_secs = self.apply_delta(
            training_mins, training_secs,
            training_delta_mins * (self.current_round - 1),
            training_delta_secs * (self.current_round - 1)
        )
        current_rest_mins, current_rest_secs = self.apply_delta(
            rest_mins, rest_secs,
            rest_delta_mins * (self.current_round - 1),
            rest_delta_secs * (self.current_round - 1)
        )
        
        # Start training round
        self.status_label.config(text=f"Training Round {self.current_round} of {self.total_rounds}")
        self.timer_label.config(foreground="red")  # Red for training
        self.remaining_seconds = time_to_seconds(current_training_mins, current_training_secs)
        self.timer_thread = threading.Thread(target=self.run_timer, args=(current_rest_mins, current_rest_secs))
        self.timer_thread.start()
    
    def run_timer(self, rest_mins, rest_secs):
        while self.remaining_seconds > 0 and self.is_running:
            mins, secs = seconds_to_time(self.remaining_seconds)
            self.timer_label.config(text=format_time(mins, secs))
            time.sleep(1)
            self.remaining_seconds -= 1
        
        if not self.is_running:
            return
            
        # If this was the initial rest period, start first training round
        if self.current_round == 0:
            self.root.bell()  # Bell for initial rest period end
            self.current_round = 1
            self.start_round()
            return
            
        # Training round complete - double bell
        self.root.bell()
        time.sleep(0.2)  # 200ms delay
        self.root.bell()
        
        # Start rest period
        self.status_label.config(text=f"Rest Period {self.current_round} of {self.total_rounds}")
        self.timer_label.config(foreground="green")  # Green for rest
        self.remaining_seconds = time_to_seconds(rest_mins, rest_secs)
        
        while self.remaining_seconds > 0 and self.is_running:
            mins, secs = seconds_to_time(self.remaining_seconds)
            self.timer_label.config(text=format_time(mins, secs))
            time.sleep(1)
            self.remaining_seconds -= 1
        
        if not self.is_running:
            return
            
        # Rest period complete - single bell
        self.root.bell()
        
        # Move to next round or finish
        self.current_round += 1
        if self.current_round <= self.total_rounds:
            self.start_round()
        else:
            self.status_label.config(text="Session Complete")
            # Play three bells for session completion
            counter = 0
            while counter < 5:
                self.root.bell()
                time.sleep(0.2)
                counter += 1
            # Schedule stop_timer to run on the main thread
            self.root.after(0, self.stop_timer)
    
    def apply_delta(self, minutes, seconds, delta_minutes, delta_seconds):
        """Apply a delta in MM:SS format to the given time."""
        total_seconds = time_to_seconds(minutes, seconds)
        delta_total = time_to_seconds(delta_minutes, delta_seconds)
        return seconds_to_time(total_seconds + delta_total)

def main():
    root = tk.Tk()
    
    # Show warning dialog
    warning_text = """WARNING: Breath-holding training can be dangerous and should only be performed under proper supervision.

This application is provided for educational purposes only. The user assumes all risks and responsibilities associated with breath-holding activities.

DO NOT use this application if you:
- Have any medical conditions
- Are not in good physical condition
- Are not familiar with proper breath-holding techniques
- Are not under proper supervision

By clicking OK, you acknowledge that you understand these risks and will use this application responsibly."""
    
    # Create a toplevel window for the warning
    warning_window = tk.Toplevel(root)
    warning_window.title("Safety Warning")
    warning_window.transient(root)  # Make it stay on top of the main window
    warning_window.grab_set()  # Make it modal
    
    # Center the warning window
    warning_window.geometry("600x400")  # Set a reasonable size
    warning_window.update_idletasks()  # Update the window to get its dimensions
    x = (warning_window.winfo_screenwidth() - warning_window.winfo_width()) // 2
    y = (warning_window.winfo_screenheight() - warning_window.winfo_height()) // 2
    warning_window.geometry(f"+{x}+{y}")
    
    # Add warning text
    warning_label = ttk.Label(warning_window, text=warning_text, wraplength=550, justify=tk.CENTER, padding=20)
    warning_label.pack(expand=True, fill=tk.BOTH)
    
    # Add OK button
    ok_button = ttk.Button(warning_window, text="OK", command=warning_window.destroy)
    ok_button.pack(pady=20)
    
    # Wait for the warning window to be closed
    root.wait_window(warning_window)
    
    app = ApneaTrainerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 