# reasoning/reasoning_format_with_verifier_answer_verifier.py
import re
from verifiers.base_verifier import BaseVerifier

class ReasoningFormatWithVerifierAnswerVerifier(BaseVerifier):
    """
    Strict format verifier requiring:
      1) The entire text must be <think>...</think><answer>...</answer><verifier_answer>...</verifier_answer>
      2) All three tags must be non-empty
      => Returns 1.0 if strictly matched, else 0.0
    """

    STRICT_PATTERN = re.compile(
        r"^\s*<think>(.*?)</think>\s*<answer>(.*?)</answer>\s*<verifier_answer>(.*?)</verifier_answer>\s*$",
        re.DOTALL
    )

    def __init__(self):
        super().__init__(
            name="strict_full_format_verifier",
            description=(
                "Strictly checks <think>...</think><answer>...</answer><verifier_answer>...</verifier_answer> "
                "with no partial credit."
            ),
            parameters={}
        )

    def verify(self, text: str, **kwargs) -> float:
        result = self.verify_with_feedback(text, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, **kwargs) -> dict:
        feedback = []
        match = self.STRICT_PATTERN.match(text)

        if match:
            think_content, answer_content, verifier_answer_content = match.groups()
            # Check all are non-empty after trimming whitespace
            if think_content.strip() and answer_content.strip() and verifier_answer_content.strip():
                feedback.append("Strict match for <think>, <answer>, <verifier_answer> => score=1.0.")
                return {"score": 1.0, "feedback": feedback}
            else:
                feedback.append("One or more tags are empty => score=0.0.")
                return {"score": 0.0, "feedback": feedback}
        else:
            feedback.append(
                "Does not strictly match <think>...</think><answer>...</answer><verifier_answer>...</verifier_answer> => score=0.0."
            )
            return {"score": 0.0, "feedback": feedback}
