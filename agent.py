import re
import json
import yaml
import datetime
from pathlib import Path
from openai import OpenAI

with open('./prompts/prompt.yaml', 'r') as f:
    config = yaml.safe_load(f)
    original_prompt = config['user_goal']

def write_file(path: str, content: str) -> str:
    with open(path, "w") as f:
        f.write(content)
    return f"Wrote {len(content)} characters to {path}"

TOOLS = {
    "write_file": {
        "fn": write_file,
        "schema": {
            "path": str,
            "content": str,
        }
    }
}

def extract_json(text: str) -> dict:
    """
    Extract the first JSON object from a string.
    Rejects output if no valid JSON object is found.
    """
    # Remove Markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())

    repaired = repair_json(text)
    return json.loads(repaired)

def repair_json(text: str) -> str:
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*(\}|\])", r"\1", text)
    return text

def log_event(state, event_type, payload):
    state["events"].append({
        "step": state["step"],
        "type": event_type,
        "payload": payload,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    })

def normalize_args(tool_name: str, args: dict) -> dict:
    if tool_name == "write_file":
        if "filename" in args:
            args["path"] = args.pop("filename")
    return args

def validate_args(schema: dict, args: dict):
    for key, typ in schema.items():
        if key not in args:
            raise RuntimeError(f"Missing arg: {key}")
        if not isinstance(args[key], str):
            raise RuntimeError(f"Arg {key} must be {typ}")

def save_run(state):
    Path("runs").mkdir(exist_ok=True)
    filename = f"runs/run_{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(state, f, indent=2)
    return filename

client = OpenAI()

def agent_step(state) -> dict:
    with open("./prompts/prompt.yaml") as f:
        prompts = yaml.safe_load(f)

    prompt = f"""
{prompts['system_prompt']}

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
        return extract_json(raw)
    except json.JSONDecodeError:
        log_event(state, "json_error", raw)
        run_file = save_run(state)
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
        log_event(state, "model_output", output)
        print(output)



        if output["type"] == "think":
            log_event(state, "think", output["content"])

        elif output["type"] == "act":
            if output["tool"]["name"] not in TOOLS:
                raise RuntimeError(
                    f"Tool '{output['tool']['name']}' is not allowed. "
                    f"Allowed tools: {list(TOOLS.keys())}"
                )

            tool_name = output["tool"]["name"]
            if tool_name not in TOOLS:
                raise RuntimeError(f"Unknown tool: {tool_name}")

            args = output["tool"]["args"]
            args = normalize_args(tool_name, args)

            log_event(state, "act", {
                "tool": tool_name,
                "args": args,
            })

            tool = TOOLS[tool_name]
            validate_args(tool["schema"], args)
            result = tool["fn"](**args)

            log_event(state, "tool_result", result)

        elif output["type"] == "done":
            log_event(state, "done", output["content"])
            run_file = save_run(state)
            print(f"Run saved to {run_file}")

            print("\nDONE:")
            print(output["content"])

            return output["content"]

        else:
            log_event(state, "done", output['type'])
            run_file = save_run(state)
            print(f"Run saved to {run_file}")
            raise RuntimeError(f"Unknown output type: {output['type']}")

    raise RuntimeError("Agent exceeded max steps")

if __name__ == "__main__":
    run_agent(original_prompt)