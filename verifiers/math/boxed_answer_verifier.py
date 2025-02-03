# verifiers/math/boxed_answer_verifier.py
import re
import logging
from verifiers.base_verifier import BaseVerifier

class BoxedAnswerVerifier(BaseVerifier):
    BOX_PATTERN = re.compile(
        r"\\\(\s*\\boxed\s*\{\s*(.*?)\s*\}\s*\\\)",
        flags=re.DOTALL
    )

    def __init__(self, name="boxed_answer_verifier"):
        super().__init__(
            name=name,
            description="Checks if the final answer is in a LaTeX box and matches the gold solution.",
            parameters={}
        )
        self.logger = logging.getLogger(name)

    def verify(self, text: str, **kwargs) -> float:
        result = self.verify_with_feedback(text, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, **kwargs) -> dict:
        """
        Requires 'gold_solution' in kwargs to do a strict comparison.
        Returns { "score": float, "feedback": [str, ...] }
        """
        feedback = []
        gold_solution = kwargs.get("gold_solution", None)

        # If no gold_solution => default to 0.0 instead of 1.0
        if gold_solution is None:
            feedback.append("No gold_solution provided; skipping strict comparison => score=0.0.")
            return {"score": 0.0, "feedback": feedback}

        # 1) Extract box from gold_solution
        gold_match = self.BOX_PATTERN.search(gold_solution)
        if not gold_match:
            feedback.append("Gold solution has no \\(\\boxed{...}\\) => no strict comparison => score=1.0.")
            # Alternatively, you could set this to 0.0 if you want to enforce a strict format in the gold solution.
            return {"score": 1.0, "feedback": feedback}

        gold_content = gold_match.group(1).strip()

        # 2) Extract box from model text
        model_match = self.BOX_PATTERN.search(text)
        if not model_match:
            feedback.append("No \\(\\boxed{...}\\) found in model output => score=0.0.")
            return {"score": 0.0, "feedback": feedback}

        model_content = model_match.group(1).strip()

        # 3) Compare
        if model_content == gold_content:
            feedback.append(f"Matches exactly => model: '{model_content}', gold: '{gold_content}' => score=1.0")
            return {"score": 1.0, "feedback": feedback}
        else:
            feedback.append(f"Differs => model: '{model_content}', gold: '{gold_content}' => score=0.0")
            return {"score": 0.0, "feedback": feedback}
