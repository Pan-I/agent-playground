import re
import json
import yaml
from openai import OpenAI

with open('./prompts/prompt.yaml', 'r') as f:
    config = yaml.safe_load(f)
    original_prompt = config['user_goal']

def extract_json(text: str) -> dict:
    """
    Extract the first JSON object from a string.
    Rejects output if no valid JSON object is found.
    """
    # Remove markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())

    return json.loads(text)

client = OpenAI()

def agent_step(state) -> dict:
    with open("./prompts/prompt.yaml") as f:
        prompts = yaml.safe_load(f)

    prompt = f"""
{prompts['system_prompt']}

Goal:
{state['goal']}

History:
{json.dumps(state['history'], indent=2)}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    raw = response.output_text.strip()

    try:
        return extract_json(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON from agent:\n{raw}")

def run_agent(goal: str, max_steps=10):
    state = {
        "goal": goal,
        "history": [],
    }

    for step in range(max_steps):
        print(f"\n--- Step {step + 1} ---")

        output = agent_step(state)
        print(output)

        if output["type"] == "think":
            state["history"].append(output)

        elif output["type"] == "act":
            if output["tool"]["name"] not in TOOLS:
                raise RuntimeError(
                    f"Tool '{output['tool']['name']}' is not allowed. "
                    f"Allowed tools: {list(TOOLS.keys())}"
                )
            tool_name = output["tool"]["name"]
            args = output["tool"]["args"]

            if tool_name not in TOOLS:
                raise RuntimeError(f"Unknown tool: {tool_name}")

            args = normalize_args(tool_name, args)
            #result = TOOLS[tool_name](**args)
            tool = TOOLS[tool_name]
            validate_args(tool["schema"], args)
            result = tool["fn"](**args)

            state["history"].append({
                "type": "tool_result",
                "tool": tool_name,
                "result": result,
            })

        elif output["type"] == "done":
            print("\nDONE:")
            print(output["content"])
            return output["content"]

        else:
            raise RuntimeError(f"Unknown output type: {output['type']}")

    raise RuntimeError("Agent exceeded max steps")

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

if __name__ == "__main__":
    run_agent(original_prompt)