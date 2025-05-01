# Apnea Trainer Timer

A command-line timer for apnea training sessions with configurable training rounds and rest periods.

## Features

- Configurable training round length (MM:SS format)
- Adjustable rest periods between rounds
- Progressive training with customizable time deltas
- Visual and audio notifications for round transitions
- Support for multiple training rounds

## Usage

Run the timer script:
```bash
python timer.py
```

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
- No external dependencies required

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details. 