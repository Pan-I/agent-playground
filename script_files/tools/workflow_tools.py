import re
import json
import yaml
import datetime
from pathlib import Path

# Configuration and data paths relative to the project root
BASE_DIR = Path(__file__).parent.parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "output"
RUNS_DIR = BASE_DIR / "runs"

def _load_config():
    config_path = PROMPTS_DIR / "prompt.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

config = _load_config()
original_prompt = config.get('user_goal', '')

def write_file(path: str, content: str) -> str:
    OUTPUT_DIR.mkdir(exist_ok=True)
    filename = OUTPUT_DIR / path

    if filename.exists():
        stem = filename.stem
        suffix = filename.suffix

        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
        filename = OUTPUT_DIR / f"{stem}_{timestamp}{suffix}"

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


TYPE_MAP = {
    "int": int,
    "str": str,
    "float": float,
    "string": str,
    "bool": bool,
    "list": list,
    "dict": dict
}

def validate_args(schema: dict, args: dict):
    for key, typ in schema.items():
        if key not in args:
            raise RuntimeError(f"Missing arg: {key}")

        # Ensure we have an actual type, not a string
        if isinstance(typ, str):
            actual_type = TYPE_MAP.get(typ)
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
    return {**dict1, **dict2}

def save_run(state):
    RUNS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')
    filename = RUNS_DIR / f"run_{timestamp}.json"
    with open(filename, "w") as f3:
        json.dump(state, f3, indent=2)
    return str(filename)