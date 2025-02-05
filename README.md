# Multi-Agent Treasure Collection

## Description
A multi-agent system designed for efficient treasure collection through collaboration and strategy. This project demonstrates how agents can work together in a simulated environment to maximize their efficiency, utilizing advanced algorithms and graphical visualization.

## Features

- **Multi-Agent Collaboration**: Simulates multiple agents working together to collect treasures in a shared environment.
- **Strategic Planning**: Implements intelligent decision-making for agents to optimize their paths and actions.
- **Graphical Visualization**: Uses `pygame` to display the environment, agent movements, and collected treasures in real-time.
- **Customizable Parameters**: Easily modify the environment, number of agents, treasure locations, and other settings.

## Customizing Display Refresh Rate
The display refresh rate can be adjusted by modifying the `pygame.time.delay` value in the `update_display` function of the `Graphics.py` script. By default, it is set to `200 ms`, but you can increase or decrease it depending on the desired performance.

## Installation

### Prerequisites
Ensure you have the following installed on your system:

- **Python 3.8+**: The project requires Python version 3.8 or higher.
- **pygame**: A Python library for creating graphical visualizations.

You can install `pygame` by running:

```bash
pip install pygame
```

## Run the Simulation
   Launch the simulation by running the main script:
   ```bash
   python main.py
   ```

## How It Works

1. **Environment Setup**:
   The environment is a grid-based map with treasures randomly placed across it.

2. **Agent Behavior**:
   Each agent is designed to collaboratively explore the environment, avoid obstacles, and collect treasures efficiently.

3. **Visualization**:
   The `pygame` library provides a real-time graphical representation of the environment, showing agent movements and collected treasures.
