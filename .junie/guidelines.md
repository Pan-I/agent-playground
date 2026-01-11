# Project Development Guidelines

This document provides essential information for developers working on the `agent-playground` project.

### 1. Build and Configuration

The project uses a standard Python structure with `pyproject.toml`.

#### Prerequisites
- Python 3.11 or higher.

#### Installation
1. Clone the repository.
2. It is recommended to use a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -e .
   ```
   Note: Dependencies include `openai` and `anthropic`.

#### Environment Variables
The project uses LLM providers which require API keys. Ensure you have the necessary environment variables set (e.g., `OPENAI_API_KEY`).

### 2. Testing

#### Running Tests
The project uses the built-in `unittest` framework. To run all tests, use the following command from the root directory:
```powershell
python -m unittest discover
```

#### Adding New Tests
When adding new features or fixing bugs, create a new test file prefixed with `test_` in the root directory (or a `tests/` directory if preferred).

**Example Test Case (`test_workflow_tools.py`):**

```python
import unittest
from script_files.tools import workflow_tools


class TestWorkflowTools(unittest.TestCase):
   def test_repair_json(self):
      dirty_json = '{"key": "value",}'
      repaired = workflow_tools.repair_json(dirty_json)
      self.assertEqual(repaired, '{"key": "value"}')

   def test_extract_json(self):
      text = '```json\n{"type": "think", "content": "hello"}\n```'
      extracted = workflow_tools.extract_json(text)
      self.assertEqual(extracted["type"], "think")


if __name__ == "__main__":
   unittest.main()
```

### 3. Additional Development Information

#### Code Style
- Follow PEP 8 guidelines.
- Use 4 spaces for indentation in Python files.
- The project uses `pathlib` for file system operations.
- Configuration and prompts are stored in YAML format within the `prompts/` directory.

#### Project Architecture
- `agent.py`: Contains the core agent logic and loop.
- `llm_provider.py`: Abstracted LLM provider interface.
- `workflow_tools.py`: Utility functions for JSON handling and logging.
- `search_tools.py` / `mock_db.py`: Stubbed search functionality for testing without external API calls.
- `shell.py`: Main entry point to run the agent from the command line.

#### Running the Agent
You can run the agent using the `agent-shell` script (after installation) or by running:
```powershell
python shell.py
```
