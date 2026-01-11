import json
from typing import Dict, Any, Optional

import yaml

from script_files.llm_agent_scripts.llm_provider import get_llm_provider
from script_files.tools import search_tools
from script_files.tools import workflow_tools


# Standard tools definition
def _get_tools():
    with open(workflow_tools.PROMPTS_DIR / "tools.yaml") as f:
        config = yaml.safe_load(f)

    # Map tool names to actual functions
    tool_functions = {
        "write_file": workflow_tools.write_file,
        "search": search_tools.search,
    }

    tools = {}
    for name, details in config.items():
        if name in tool_functions:
            tools[name] = {
                **details,
                "fn": tool_functions[name]
            }
    return tools


TOOLS = _get_tools()

# Global LLM provider instance
llm = get_llm_provider()


class Agent:
    def __init__(
            self,
            llm_provider=None,
            tools: Optional[Dict[str, Any]] = None,
            max_steps: int = 10,
            max_search: int = 2
    ):
        self.llm = llm_provider or llm
        self.tools = tools or TOOLS
        self.max_steps = max_steps
        self.max_search = max_search

        # Load and cache prompts during initialization
        self.system_prompt = self._load_system_prompt(self.tools)

    @staticmethod
    def _load_system_prompt(tools: Dict[str, Any]) -> str:
        """Loads system and user prompts and merges them, extracting the system prompt string."""
        with open(workflow_tools.PROMPTS_DIR / "prompt.yaml") as f:
            prompt_data = yaml.safe_load(f)
        with open(workflow_tools.PROMPTS_DIR / "system_prompt.yaml") as f:
            system_prompt_data = yaml.safe_load(f)

        full_prompt = workflow_tools.merge_prompts(system_prompt_data, prompt_data)
        system_prompt = full_prompt.get('system_prompt', '')

        # Format tools for the prompt
        # Create a copy without the 'fn' key (which is a Python object)
        clean_tools = {}
        for name, details in tools.items():
            clean_tools[name] = {k: v for k, v in details.items() if k != 'fn'}

        tools_description = yaml.dump(clean_tools, sort_keys=False)
        # Indent the tools description for the prompt, except for the first line
        # which will be indented by the placeholder's indentation in the template.
        indented_tools = "\n".join(["  " + line for line in tools_description.splitlines()]).lstrip()

        # Format the allowed tools list
        tools_list = "\n".join([f"  - {name}" for name in clean_tools.keys()]).lstrip()

        return (system_prompt
                .replace("{tools_definition}", indented_tools)
                .replace("{tools_list}", tools_list))

    def _format_prompt(self, state: Dict[str, Any]) -> str:
        """Formats the prompt for the LLM based on the current state."""
        return f"""
{self.system_prompt}

Goal:
{state['goal']}

History:
{state['events']}
"""

    def step(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a single step of the agent: prompt LLM, extract JSON, and log input."""
        prompt_text = self._format_prompt(state)
        raw = self.llm.complete(prompt_text)

        try:
            workflow_tools.log_event(state, "model_input", raw)
            return workflow_tools.extract_json(raw)
        except (json.JSONDecodeError, ValueError):
            workflow_tools.log_event(state, "json_error", raw)
            run_file = workflow_tools.save_run(state)
            print(f"Run saved to {run_file}")
            raise RuntimeError(f"Invalid JSON from agent:\n{raw}")

    def run(self, goal: str) -> str:
        """Runs the main agent loop until the goal is achieved or max steps reached."""
        state = {
            "goal": goal,
            "step": 0,
            "search-count": 0,
            "events": [],
            "note": "",
        }

        for step_idx in range(self.max_steps):
            state["step"] = step_idx + 1
            print(f"\n--- Step {state['step']} ---")

            output = self.step(state)
            workflow_tools.log_event(state, "model_output", output)
            print(output)

            result = self._process_output(state, output)
            if result is not None:
                return result

        raise RuntimeError("Agent exceeded max steps")

    def _process_output(self, state: Dict[str, Any], output: Dict[str, Any]) -> Optional[str]:
        """Processes the agent's output based on its type."""
        output_type = output.get("type")

        if output_type == "think":
            workflow_tools.log_event(state, "think", output.get("content"))
            return None

        if output_type == "act":
            self._execute_tool(state, output.get("tool", {}))
            return None

        if output_type == "done":
            content = output.get("content")
            workflow_tools.log_event(state, "done", content)
            run_file = workflow_tools.save_run(state)
            print(f"Run saved to {run_file}")
            print("\nDONE:")
            print(content)
            return content

        # Unknown output type
        workflow_tools.log_event(state, "done", output_type)
        run_file = workflow_tools.save_run(state)
        print(f"Run saved to {run_file}")
        raise RuntimeError(f"Unknown output type: {output_type}")

    def _execute_tool(self, state: Dict[str, Any], tool_call: Dict[str, Any]) -> None:
        """Handles tool selection, argument validation, and execution."""
        tool_name = tool_call.get("name")
        args = tool_call.get("args", {})

        if tool_name not in self.tools:
            raise RuntimeError(
                f"Unknown tool: {tool_name}. "
                f"Tool '{tool_name}' is not allowed. "
                f"Allowed tools: {list(self.tools.keys())}"
            )

        args = workflow_tools.normalize_args(tool_name, args)

        if tool_name == "search":
            state["search-count"] += 1
            if state["search-count"] >= self.max_search:
                state["note"] = "Runner reporting search engine limit has reached. Please process results."

        workflow_tools.log_event(state, "act", {
            "tool": tool_name,
            "args": args,
        })

        tool_config = self.tools[tool_name]
        workflow_tools.validate_args(tool_config["schema"], args)

        result = tool_config["fn"](**args)

        workflow_tools.log_event(state, "tool_result", {
            "tool": tool_name,
            "result": result,
        })


# Functions for backward compatibility
def agent_step(state) -> dict:
    return Agent().step(state)


def run_agent(goal: str, max_steps=10, max_search=2):
    return Agent(max_steps=max_steps, max_search=max_search).run(goal)
