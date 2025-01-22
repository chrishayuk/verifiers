import json
import importlib
import argparse
import os

def load_registry(json_path: str) -> dict:
    """
    Reads the JSON file, returns a dict like:
      {
        "haiku": {
          "module": "verifiers.poetry.haiku_verifier",
          "class": "HaikuVerifier",
          "description": "Checks if text is ~5-7-5...",
          "arguments": [
             { "name": "--tolerance", "type": "int", "default": 1, "help": "..." }
          ]
        }, ...
      }
    """
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"Registry file not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def load_verifier_class(verifier_name: str, registry_data: dict):
    if verifier_name not in registry_data:
        raise KeyError(f"Verifier '{verifier_name}' not in registry.")
    
    info = registry_data[verifier_name]
    module_name = info["module"]
    class_name = info["class"]
    module = importlib.import_module(module_name)
    verifier_cls = getattr(module, class_name)
    return verifier_cls

def add_verifier_arguments(parser: argparse.ArgumentParser, verifier_info: dict):
    """
    Dynamically adds arguments from verifier_info["arguments"] to the parser.
    Each argument is a dict with keys like:
     - "name": string (e.g. "--tolerance")
     - "type": one of "int", "float", "str", etc.
     - "default": default value
     - "help": help text
    """
    arguments = verifier_info.get("arguments", [])
    for arg in arguments:
        name = arg["name"]
        arg_type_str = arg.get("type", "str")
        default_val = arg.get("default", None)
        help_text = arg.get("help", "")
        
        # Convert "int"/"float"/"str" to actual Python types
        if arg_type_str == "int":
            pytype = int
        elif arg_type_str == "float":
            pytype = float
        else:
            pytype = str
        
        parser.add_argument(
            name,
            type=pytype,
            default=default_val,
            help=help_text
        )
