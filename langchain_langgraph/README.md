# Langchain/Langgraph Autonomous Development System

This project implements an autonomous development system using Langgraph that can run a 20B parameter local LLM to build applications based on specifications. The system follows the "Two-Agent System" architecture with Initializer and Coder agents.

## Architecture

The system implements the following architecture:

1. **Initializer Agent**: Runs only on the first session to set up the project foundation
   - Reads the project specification
   - Creates feature_list.json with 50+ detailed test cases
   - Creates init.sh for environment setup
   - Initializes git repository
   - Sets up the initial project structure

2. **Coder Agent**: Runs on all subsequent sessions to implement features
   - Performs "Get Your Bearings" routine to understand current state
   - Selects the next incomplete feature to implement
   - Implements the feature with thorough testing
   - Updates feature_list.json to mark tests as passing
   - Commits changes and updates progress logs

## Key Features

- **Context Management**: Proper handling of context for 20B parameter models
- **State Persistence**: External memory through feature_list.json, progress logs, and git
- **Tool Integration**: File operations, bash commands, git operations, and browser automation
- **Safety & Guardrails**: Loop limits, directory confinement, and validation
- **Testing**: Browser automation tools for end-to-end verification

## Components

- `config.py`: Configuration for the system, optimized for 20B local models
- `state.py`: State management for LangGraph with all necessary fields
- `tools.py`: Implementation of all tools available to agents
- `prompts.py`: Optimized prompts for both initializer and coder agents
- `agents.py`: Implementation of initializer and coder agents
- `workflow.py`: LangGraph workflow orchestrating the two-agent system
- `main.py`: Main entry point for running the system

## Usage

To run the autonomous development system:

```bash
cd /workspace/langchain_langgraph
python main.py --project-dir ./my-project --model local-20b-model
```

### Command Line Options

- `--project-dir`: Directory for the project (default: ./project)
- `--app-spec`: Path to app specification file (default: uses example)
- `--model`: Model name for the LLM (default: local-20b-model)
- `--frontend-port`: Frontend port (default: 3000)
- `--backend-port`: Backend port (default: 8000)

### Configuration

The system can be configured via environment variables:

```bash
export LLM_MODEL_NAME="your-local-model"
export LLM_TEMPERATURE=0.1
export PROJECT_DIR="./my-project"
export FRONTEND_PORT=3000
export BACKEND_PORT=8000
```

## Running with Local LLM

The system is configured to work with local LLMs (like those served by LM Studio) at `http://localhost:1234/v1`. To use a different endpoint, modify the `base_url` in `agents.py`.

## File Structure

The system maintains the following external memory files:

- `feature_list.json`: JSON list of all features with test steps and completion status
- `claude-progress.txt`: Append-only log of progress made by agents
- `init.sh`: Environment setup script
- Git repository: Version control of all changes

## Safety Features

- Loop limit of 50 attempts per feature to prevent infinite token burning
- Strict validation that only "passes" field can be modified in feature_list.json
- Comprehensive error handling and logging
- Directory confinement to project directory