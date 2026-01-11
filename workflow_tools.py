import re
import json
import yaml
import datetime
from pathlib import Path

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