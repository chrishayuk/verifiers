# fastapi_server.py
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union, Dict, Any

# Import your existing logic
from registry_loader import load_registry, load_verifier_class

app = FastAPI()

# Updated request model
class VerifyRequest(BaseModel):
    text: str
    verifier: str
    feedback: bool = False
    args: Dict[str, Any] = {}

class VerifyResponse(BaseModel):
    score: float
    feedback: Union[List[str], None] = None

@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest):
    """
    POST a JSON payload like:
    {
      "text": "\\(\\boxed{4}\\)",
      "verifier": "boxed_answer",
      "feedback": true,
      "args": {
        "gold_solution": "\\(\\boxed{4}\\)"
      }
    }
    """

    # 1) Load the registry
    registry_data = load_registry("verifier_registry.json")

    # 2) Check if requested verifier is known
    if req.verifier not in registry_data:
        return {
            "score": 0.0,
            "feedback": [f"Unknown verifier: {req.verifier}"]
        }

    # 3) Load & instantiate the chosen verifier
    verifier_cls = load_verifier_class(req.verifier, registry_data)
    verifier_obj = verifier_cls()

    # 4) Collect & cast dynamic arguments from registry defaults + request args
    #    (only if the registry defines "arguments" for this verifier)
    dynamic_args = {}
    verifier_info = registry_data[req.verifier]
    registry_args = verifier_info.get("arguments", [])  # list of { name, type, default, help, ... }
    user_args = req.args or {}

    for arg_def in registry_args:
        # Trim leading '--'
        arg_name = arg_def["name"].lstrip("--")
        arg_type = arg_def["type"]
        default_val = arg_def.get("default", None)

        # If user provided the arg, use that; otherwise fallback to default
        val = user_args.get(arg_name, default_val)

        # Cast to the correct type
        if val is not None:
            if arg_type == "int":
                val = int(val)
            elif arg_type == "float":
                val = float(val)
            elif arg_type == "str":
                val = str(val)
            # add other cases if needed (bool, etc.)

        dynamic_args[arg_name] = val

    # 5) Call the verifier with optional arguments
    if req.feedback:
        # Pass `req.text` plus any dynamic arguments
        result = verifier_obj.verify_with_feedback(req.text, **dynamic_args)
        return {
            "score": result["score"],
            "feedback": result["feedback"]
        }
    else:
        score = verifier_obj.verify(req.text, **dynamic_args)
        return {
            "score": score,
            "feedback": None
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
