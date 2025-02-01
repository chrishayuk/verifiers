# fastapi_server.py
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union

# Import your existing logic
from registry_loader import load_registry, load_verifier_class

app = FastAPI()

# Define a request model
class VerifyRequest(BaseModel):
    text: str         # The text to analyse (e.g. poem)
    verifier: str     # Which verifier to use, e.g. "limerick"
    feedback: bool = False

# Define a response model
class VerifyResponse(BaseModel):
    score: float
    feedback: Union[List[str], None] = None

@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest):
    """
    POST a JSON payload like:
      {
        "text": "There once was a man from Peru...",
        "verifier": "limerick",
        "feedback": true
      }
    Returns JSON with "score" and, if requested, "feedback".
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

    # 4) If your verifiers support additional dynamic args, parse them here:
    #    For example, if your JSON or registry has lines like:
    #       "arguments": [{"name": "--tolerance", "default": 0.5}, ...]
    #    You can re-use the same logic as in your CLI code to build a dict
    #    of arguments and pass them to verifier_obj.verify(...).
    
    if req.feedback:
        result = verifier_obj.verify_with_feedback(req.text)
        return {
            "score": result["score"],
            "feedback": result["feedback"]
        }
    else:
        score = verifier_obj.verify(req.text)
        return {
            "score": score,
            "feedback": None
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
