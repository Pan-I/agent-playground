# Agent Playground

A small repo to try learning using API calls to LLM/Gen-AI services. It features a simple autonomous agent capable of reasoning and using tools to accomplish goals.

## Features

- **Autonomous Agent**: Core logic in `agent.py` that implements a "Think-Act-Observe" loop.
- **LLM Abstraction**: Supports multiple LLM providers (currently focused on OpenAI).
- **Tool Use**: Extensible tool system (e.g., file writing, stubbed search).
- **Logging**: Comprehensive logging of agent steps and tool results in the `runs/` directory.

## Prerequisites

- Python 3.11 or higher.
- API keys for LLM providers (e.g., `OPENAI_API_KEY`).

## Installation

1. Clone the repository.
2. It is recommended to use a virtual environment:

   **Windows (PowerShell):**
```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
```

   **Linux/macOS (Bash):**
```bash
   python3 -m venv venv
   source venv/bin/activate
```

3. Install dependencies:

   **Windows (PowerShell):**
```powershell
   pip install -e .
```

   **Linux/macOS (Bash):**
```bash
   pip install -e .
```

## Usage

### Running the Agent

You can run the agent using the `agent-shell` command (available after installation) or by running the script directly:

***Windows (Pow*erShell):**
```powershell
python shell.py
```

**Linux/macOS (Bash):**
```bash
python3 shell.py
```

To set up the command, add the following to your `pyproject.toml`:
```
[project.scripts]
agent-shell = "shell:main"
```
as well as something like the following to your `.vscode/launch.json`, depending on your IDE:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Shell",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/shell.py",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

## Testing
The agent's user-goal is defined in `prompts/prompt.yaml`.
Ther larger context is defined in `prompts/system_prompt.yaml`.`

## Project Structure

- `agent.py`: Core agent logic and execution loop.
- `llm_provider.py`: Interface and implementations for LLM providers.
- `workflow_tools.py`: Utility functions for JSON parsing, file I/O, and logging.
- `search_tools.py` & `mock_db.py`: Stubbed search functionality for demonstration and testing.
- `shell.py`: Command-line entry point.
- `prompts/`: Directory containing system and user prompts in YAML format.
- `output/`: Directory where the agent writes its generated files.
- `runs/`: Directory where execution logs are stored.

## Development

For detailed development guidelines, please refer to [.junie/guidelines.md](.junie/guidelines.md).