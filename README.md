# Apnea Trainer

## ⚠️ SAFETY WARNING ⚠️

**WARNING: Breath-holding training can be dangerous and should only be performed under proper supervision.**

This application is provided for educational purposes only. The user assumes all risks and responsibilities associated with breath-holding activities.

**DO NOT use this application if you:**
- Have any medical conditions
- Are not in good physical condition
- Are not familiar with proper breath-holding techniques
- Are not under proper supervision

By using this application, you acknowledge that you understand these risks and will use it responsibly.

## Description

A command-line and graphical timer for apnea training sessions.

## Features

- Configurable training round length
- Adjustable rest periods
- Support for TOML configuration file
- Progress tracking for multiple rounds
- Graphical user interface (GUI) with visual countdown
- Command-line interface (CLI) for terminal use
- Save/Load configuration files

## Installation

1. Clone this repository
2. Create and activate a virtual environment using uv:
   ```bash
   # Create a new virtual environment
   uv venv

   # Activate the virtual environment
   # On Linux/macOS:
   source .venv/bin/activate
   # On Windows:
   .venv\Scripts\activate
   ```

3. Install the project using uv:
   ```bash
   # Install in development mode
   uv pip install -e .
   ```

## Usage

### Graphical Interface

To run the graphical version:

```bash
apnea-trainer-gui
```

The GUI provides:
- Input fields for all timer settings
- Visual countdown display
- Start/Stop controls
- Round progress tracking
- Audio notifications for round transitions
- Save/Load configuration files

### Command Line Interface

To run the command-line version:

```bash
apnea-trainer
```

Or specify a configuration file:
```bash
apnea-trainer -c path/to/config.toml
```

### Building a Standalone Binary

To build a standalone binary of the GUI application:

```bash
# Make sure you're in your virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Build the binary
./scripts/build.sh
```

The binary will be created in the `dist` directory. You can then run it directly:
```bash
./dist/apnea-trainer-gui
```

## Development

### Dependencies

This project uses `pyproject.toml` for package metadata and dependencies.

## Configuration

The timer can be configured using a TOML file. Configuration files are stored in `~/.apnea-trainer/` by default. Here's an example configuration:

```toml
# Training round settings
[training]
# Initial length of each training round (MM:SS format)
initial_length = "1:30"
# Change in training round length per round (MM:SS format)
# Use negative values to decrease time (e.g., "-0:05" for -5 seconds)
# Use positive values to increase time (e.g., "0:05" for +5 seconds)
delta = "-0:05"

# Rest period settings
[rest]
# Initial length of rest period (MM:SS format)
initial_length = "0:30"
# Change in rest period length per round (MM:SS format)
# Use negative values to decrease time (e.g., "-0:02" for -2 seconds)
# Use positive values to increase time (e.g., "0:02" for +2 seconds)
delta = "-0:02"

# Session settings
[session]
# Number of training rounds
rounds = 3
```

## Requirements

- Python 3.x
- uv (for package management)
- tomli (for TOML file parsing)
- tkinter (for GUI, included with Python)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details. 