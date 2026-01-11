# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 1/10/2026 9:27pm

### Added
- **Project Guidelines**: Created `.junie/guidelines.md` to provide comprehensive development, build, and testing instructions.
- **Mock Database**: Introduced a mock database (`mock_db.py`) and `search_tools.py` for testing search functionality without external API calls.
- **Event Logging**: Implemented JSON-based event logging to track the history of API calls and agent steps in the `runs/` directory.
- **Output Schema**: Added `prompts/output_schema.json` to define the expected structure for agent responses.
- **JSON Pipeline**: Established a structured JSON data pipeline for more reliable communication between the agent and LLM.
- **Repo Changelog**: Added `changelog.md` to capture changes in repo.

### Changed
- **Project Restructuring**: Reorganized the project directory, moving core scripts and tools into a `script_files/` directory for better maintainability.
- **Refactored LLM Provider**: Improved the LLM provider abstraction in `llm_provider.py` to support multiple backends more easily.
- **Enhanced README**: Updated `README.md` with detailed installation, usage, and project structure information.
- **Refactored Agent Logic**: Significantly refactored `agent.py` to streamline the "Think-Act-Observe" loop and improve modularity.
- **Prompt Updates**: Updated system and user prompts in `prompts/` to use YAML format and provide clearer instructions to the agent.

### Fixed
- **JSON Robustness**: Added JSON repairing logic and extra logging to handle and debug malformed LLM outputs more effectively.
