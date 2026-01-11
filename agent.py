import json
import yaml
import workflow_tools
from openai import OpenAI

client = OpenAI()

def agent_step(state) -> dict:
    with open("./prompts/prompt.yaml") as f:
        prompt = yaml.safe_load(f)
    with open("./prompts/system_prompt.yaml") as f:
        system_prompt = yaml.safe_load(f)

    full_prompt = system_prompt | prompt
    prompt = f"""
{full_prompt['system_prompt']}

Goal:
{state['goal']}

History:
{state['events']}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    raw = response.output_text.strip()

    try:
        return workflow_tools.extract_json(raw)
    except json.JSONDecodeError:
        workflow_tools.log_event(state, "json_error", raw)
        run_file = workflow_tools.save_run(state)
        print(f"Run saved to {run_file}")
        raise RuntimeError(f"Invalid JSON from agent:\n{raw}")

def run_agent(goal: str, max_steps=10):
    state = {
        "goal": goal,
        "step": 0,
        "events": [],
    }

    for step in range(max_steps):
        state["step"] = step + 1
        print(f"\n--- Step {state["step"]} ---")
        output = agent_step(state)
        workflow_tools.log_event(state, "model_output", output)
        print(output)

        if output["type"] == "think":
            workflow_tools.log_event(state, "think", output["content"])

        elif output["type"] == "act":
            if output["tool"]["name"] not in workflow_tools.TOOLS:
                raise RuntimeError(
                    f"Tool '{output['tool']['name']}' is not allowed. "
                    f"Allowed tools: {list(workflow_tools.TOOLS.keys())}"
                )

            tool_name = output["tool"]["name"]
            if tool_name not in workflow_tools.TOOLS:
                raise RuntimeError(f"Unknown tool: {tool_name}")

            args = output["tool"]["args"]
            args = workflow_tools.normalize_args(tool_name, args)

            workflow_tools.log_event(state, "act", {
                "tool": tool_name,
                "args": args,
            })

            tool = workflow_tools.TOOLS[tool_name]
            workflow_tools.validate_args(tool["schema"], args)
            result = tool["fn"](**args)

            workflow_tools.log_event(state, "tool_result", result)

        elif output["type"] == "done":
            workflow_tools.log_event(state, "done", output["content"])
            run_file = workflow_tools.save_run(state)
            print(f"Run saved to {run_file}")

            print("\nDONE:")
            print(output["content"])

            return output["content"]

        else:
            workflow_tools.log_event(state, "done", output['type'])
            run_file = workflow_tools.save_run(state)
            print(f"Run saved to {run_file}")
            raise RuntimeError(f"Unknown output type: {output['type']}")

    raise RuntimeError("Agent exceeded max steps")