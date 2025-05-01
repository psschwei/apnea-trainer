# Apnea Trainer Timer

A command-line timer for apnea training sessions.

## Features

- Configurable training round length
- Adjustable rest periods
- Support for TOML configuration file
- Progress tracking for multiple rounds

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

After installation, you can run the timer using:

```bash
apnea-trainer
```

Or specify a configuration file:
```bash
apnea-trainer -c path/to/config.toml
```

## Configuration

The timer can be configured using a TOML file. Here's an example configuration:

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

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details. 