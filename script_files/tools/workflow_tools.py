import re
import json
import yaml
import datetime
from pathlib import Path

with open('../../prompts/prompt.yaml', 'r') as f:
    config = yaml.safe_load(f)
    original_prompt = config['user_goal']

def write_file(path: str, content: str) -> str:
    Path("../../output").mkdir(exist_ok=True)
    filename = f"output/{path}"

    if Path(filename).exists():
        path_obj = Path(path)
        stem = path_obj.stem
        suffix = path_obj.suffix

        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
        new_filename = f"{stem}_{timestamp}{suffix}"
        filename = f"output/{new_filename}"

    with open(filename, "w") as f2:
        f2.write(content)
    return f"Wrote {len(content)} characters to {path}"

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
    text = re.sub(r",\s*([}\]])", r"\1", text)
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

        # Convert string type names to actual types
        type_map = {
            "int": int,
            "str": str,
            "float": float,
            "string": str,
            "bool": bool,
            "list": list,
            "dict": dict
        }

        # Ensure we have an actual type, not a string
        if isinstance(typ, str):
            actual_type = type_map.get(typ)
            if actual_type is None:
                raise RuntimeError(f"Unknown type string: {typ}")
        else:
            actual_type = typ

        # If already the correct type, continue
        if isinstance(args[key], actual_type):
            continue

        # If the required type is int and the arg is a string, try to convert
        if actual_type == int and isinstance(args[key], str):
            try:
                args[key] = int(args[key])
            except ValueError:
                raise RuntimeError(f"Arg {key} must be int but cannot convert '{args[key]}' to int")
        else:
            raise RuntimeError(f"Arg {key} must be {actual_type.__name__} but got {type(args[key]).__name__}")

def merge_prompts(dict1, dict2):
    merged = {**dict1, **dict2}
    return merged

def save_run(state):
    Path("../../runs").mkdir(exist_ok=True)
    filename = f"runs/run_{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f3:
        json.dump(state, f3, indent=2)
    return filename