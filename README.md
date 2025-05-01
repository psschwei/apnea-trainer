# Apnea Trainer Timer

A command-line timer for apnea training sessions with configurable training rounds and rest periods.

## Features

- Configurable training round length (MM:SS format)
- Adjustable rest periods between rounds
- Progressive training with customizable time deltas
- Visual and audio notifications for round transitions
- Support for multiple training rounds
- Configuration via TOML file with interactive overrides
- Support for multiple configuration files

## Installation

1. Clone the repository
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

### Using Configuration File

The timer can be configured using a TOML file. You can create multiple configuration files for different training setups. Here's an example configuration:

```toml
[training]
initial_length = "1:30"  # MM:SS format
delta = -5              # seconds per round

[rest]
initial_length = "0:30"  # MM:SS format
delta = -2              # seconds per round

[session]
rounds = 3
```

### Running the Timer

Run the timer script with the default configuration file:
```bash
python -m apnea_trainer.timer
```

Or specify a different configuration file:
```bash
python -m apnea_trainer.timer -c my_config.toml
# or
python -m apnea_trainer.timer --config my_config.toml
```

If a config file is present, you'll be prompted with default values that you can accept by pressing Enter, or override by entering new values.

You'll be prompted to enter:
1. Training round length (MM:SS format, e.g., "1:30" for 1 minute and 30 seconds)
2. Change in training round length per round (in seconds, e.g., -5 to decrease by 5 seconds each round)
3. Number of rounds
4. Rest period length (MM:SS format)
5. Change in rest period length per round (in seconds)

## Example

For a 3-round session:
- Starting with 1:30 training rounds, decreasing by 5 seconds each round
- 0:30 rest periods, decreasing by 2 seconds each round

The sequence would be:
1. Training: 1:30, Rest: 0:30
2. Training: 1:25, Rest: 0:28
3. Training: 1:20, Rest: 0:26

## Requirements

- Python 3.x
- uv (for package management)
- tomli>=2.0.1 (for TOML configuration file support)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details. 