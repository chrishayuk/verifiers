# verifiers/reasoning/verifier_answer_verifier.py
import re
import logging
from verifiers.base_verifier import BaseVerifier

class VerifierAnswerVerifier(BaseVerifier):
    """
    Checks if the final answer is within <verifier_answer>...</verifier_answer> 
    and matches the provided 'gold_solution' (a plain string).
    """

    VERIFIER_ANSWER_PATTERN = re.compile(
        r"<verifier_answer>\s*(.*?)\s*</verifier_answer>",
        flags=re.DOTALL | re.IGNORECASE
    )

    def __init__(self, name="verifier_answer_verifier"):
        super().__init__(
            name=name,
            description=(
                "Checks if the final answer is within <verifier_answer>...</verifier_answer> "
                "tags and matches a plain gold solution."
            ),
            parameters={}
        )
        self.logger = logging.getLogger(name)

    def verify(self, text: str, **kwargs) -> float:
        """
        If 'gold_solution' is present in kwargs, compare it.
        Otherwise, we return 0.0 by default (no partial credit).
        """
        result = self.verify_with_feedback(text, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, **kwargs) -> dict:
        """
        Expects 'gold_solution' in kwargs to do strict comparison.
        Returns { "score": float, "feedback": [str, ...] }
        """
        feedback = []
        gold_solution = kwargs.get("gold_solution", None)

        if gold_solution is None:
            feedback.append(
                "No gold_solution provided; skipping strict comparison => score=0.0."
            )
            return {"score": 0.0, "feedback": feedback}

        # 1) Extract <verifier_answer> from the model's text
        match = self.VERIFIER_ANSWER_PATTERN.search(text)
        if not match:
            feedback.append("No <verifier_answer>...</verifier_answer> found in model output.")
            return {"score": 0.0, "feedback": feedback}

        model_answer = match.group(1).strip()

        # 2) Compare
        if model_answer == gold_solution.strip():
            feedback.append(f"Matches exactly => model: '{model_answer}', gold: '{gold_solution}' => score=1.0")
            return {"score": 1.0, "feedback": feedback}
        else:
            feedback.append(f"Differs => model: '{model_answer}', gold: '{gold_solution}' => score=0.0")
            return {"score": 0.0, "feedback": feedback}
