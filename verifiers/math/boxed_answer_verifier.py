# verifiers/math/boxed_answer_verifier.py
import re
import logging
from verifiers.base_verifier import BaseVerifier

class BoxedAnswerVerifier(BaseVerifier):
    """
    Enforces that the final answer is in a LaTeX box \(\boxed{...}\)
    and matches the gold solution's box content (after stripping whitespace).
    """

    # Regex to find something like: \(\boxed{42}\)
    # The capturing group (.*?) gives us the box content
    BOX_PATTERN = re.compile(
        r"\\\(\s*\\boxed\s*\{\s*(.*?)\s*\}\s*\\\)",
        flags=re.DOTALL
    )

    def __init__(self, name="boxed_answer_verifier"):
        super().__init__(
            name=name,
            description="Enforces that the final answer is in a LaTeX box and matches the gold solution.",
            parameters={}
        )
        self.logger = logging.getLogger(name)

    def verify(self, text: str, **kwargs) -> float:
        """
        Convenience method returning just the numeric score.
        """
        result = self.verify_with_feedback(text, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, **kwargs) -> dict:
        """
        Requires 'gold_solution' in kwargs for a strict comparison.
        Returns { "score": float, "feedback": [str, ...] }.
        """
        feedback = []
        gold_solution = kwargs.get("gold_solution", None)

        # If no gold_solution => set to 0.0 or 1.0 based on your policy
        # The test suite does not show a specific scenario for no gold_solution,
        # but we'll do 0.0 by default unless you want to handle differently.
        if gold_solution is None:
            feedback.append("No gold_solution provided; skipping strict comparison => score=0.0.")
            return {"score": 0.0, "feedback": feedback}

        # 1) Extract the box content from the gold solution
        gold_match = self.BOX_PATTERN.search(gold_solution)
        if not gold_match:
            # The test expects returning score=1.0 plus a message if the gold solution has no box
            feedback.append("Gold solution has no \\(\\boxed{...}\\) => no strict comparison => score=1.0.")
            return {"score": 1.0, "feedback": feedback}

        gold_content = gold_match.group(1).strip()

        # 2) Extract the box content from the model output
        model_match = self.BOX_PATTERN.search(text)
        if not model_match:
            feedback.append("No \\(\\boxed{...}\\) found in model output => score=0.0.")
            return {"score": 0.0, "feedback": feedback}

        model_content = model_match.group(1).strip()

        # 3) Compare the stripped content
        if model_content == gold_content:
            feedback.append(f"matches exactly => model: '{model_content}', gold: '{gold_content}' => score=1.0")
            return {"score": 1.0, "feedback": feedback}
        else:
            feedback.append(f"differs => model: '{model_content}', gold: '{gold_content}' => score=0.0")
            return {"score": 0.0, "feedback": feedback}
