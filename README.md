# 2048-LLM

A 2048 game that can be played with various AI agents, including LLM models. This project integrates multiple AI agents to play the classic 2048 game, providing a platform for experimenting with different AI strategies and models.

## Codebase Overview

The codebase is organized into the following main directories and files:

### Directories

1. **agents/**
   - Contains implementations of various AI agents, including:
     - `a_star_agent.py`: Implements the A* search algorithm.
     - `alpha_beta_expectimax_agent.py`: Combines alpha-beta pruning with expectimax.
     - `deepseekv3_agent.py`: Integrates the DeepSeek v3 LLM model.
     - `gemini_agent.py`: Integrates Google's Gemini Pro model.
     - `gemma3_agent.py`: Integrates Google's Gemma 3 model.
     - `gpt4o_mini_agent.py`: Integrates OpenAI's GPT-4o Mini model.
     - `llm_base_agent.py`: Base class for LLM-based agents.
     - Other agents implementing various strategies like Monte Carlo Tree Search (MCTS), random moves, and more.

2. **app/**
   - Contains the Flask application for running the game in a web interface.
   - Includes static files and templates for the frontend.

3. **simulation/**
   - Contains utilities and workers for simulating the game and training agents.
   - Key files:
     - `game.py`: Core game logic for 2048.
     - `game_utils.py`: Helper functions for game operations.
     - `simulation_worker.py`: Manages game simulations.
     - `training_td_worker.py`: Handles training using temporal difference learning.

4. **tests/**
   - Contains test scripts for verifying the functionality of the agents and the game.
   - Includes specific tests for each LLM agent and a general test script (`test_all_llms.py`).

5. **wandb/**
   - Stores logs and configurations for experiments tracked using Weights & Biases.

### Key Files

- `run.py`: Entry point for running the game. Launches the Flask application.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `pyproject.toml`: Contains metadata about the project and its dependencies.
- `README.md`: Documentation for the project.

## LLM Agents

The game supports the following LLM models as agents:

1. **Gemini** - Google's Gemini Pro model
2. **GPT-4o Mini** - OpenAI's GPT-4o Mini model
3. **DeepSeek v3** - DeepSeek's v3 model
4. **Gemma 3** - Google's Gemma 3 model

### Setup

To use the LLM agents, you need to set up the following environment variables with your API keys:

```bash
# For Gemini and Gemma 3
export GEMINI_API_KEY=your_google_api_key

# For GPT-4o Mini
export OPENAI_API_KEY=your_openai_api_key

# For DeepSeek v3
export DEEPSEEK_API_KEY=your_deepseek_api_key
```

You can set these environment variables in a `.env` file in the project root directory.

### Installing Dependencies

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

### Running the Game

Start the game by running:

```bash
python run.py
```

Then open your browser and navigate to `http://localhost:5001` to play the game.

### Testing LLM Agents

You can test if your LLM API keys are properly configured using the test scripts:

```bash
# Test all LLM agents
python tests/test_all_llms.py

# Test a specific LLM agent
python tests/test_all_llms.py --llm gemini
python tests/test_all_llms.py --llm gpt4o_mini
python tests/test_all_llms.py --llm deepseekv3
python tests/test_all_llms.py --llm gemma3
```

See the [tests/README.md](tests/README.md) file for more details on testing.