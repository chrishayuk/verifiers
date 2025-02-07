# verifiers/reasoning/reasoning_format_verifier.py
import re
from verifiers.base_verifier import BaseVerifier

class ReasoningFormatVerifier(BaseVerifier):
    """
    Strict format verifier requiring:
      1) The entire text must be <think>...</think><answer>...</answer>,
         with optional leading/trailing whitespace only.
      2) Both <think> and <answer> tags must be non-empty (after trimming).
      => Returns score=1.0 if strictly matched, else 0.0
    """

    STRICT_PATTERN = re.compile(
        r"^\s*<think>(.*?)</think>\s*<answer>(.*?)</answer>\s*$",
        re.DOTALL
    )

    def __init__(self):
        super().__init__(
            name="strict_think_answer_verifier",
            description=(
                "Strictly checks <think>...</think><answer>...</answer> with no partial credit."
            ),
            parameters={}
        )

    def verify(self, text: str, **kwargs) -> float:
        result = self.verify_with_feedback(text, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, **kwargs) -> dict:
        feedback = []
        match = self.STRICT_PATTERN.match(text)

        if not match:
            # Entire text must match <think>...</think><answer>...</answer> pattern
            feedback.append("Text does not conform to the required format.")
            feedback.append(
                "Ensure it follows: <think>reasoning...</think><answer>final answer...</answer>."
            )
            return {"score": 0.0, "feedback": feedback}

        # Pattern matched => extract the think and answer contents
        think_content, answer_content = match.groups()

        # Check for empty <think> section
        if not think_content.strip():
            feedback.append("The <think> section is empty. It must contain reasoning steps.")
            return {"score": 0.0, "feedback": feedback}

        # Check for empty <answer> section
        if not answer_content.strip():
            feedback.append("The <answer> section is empty. It must contain a final answer.")
            return {"score": 0.0, "feedback": feedback}

        # If we reach here, both sections are non-empty
        feedback.append("✅ Text correctly includes both <think> and <answer> tags with valid content.")
        return {"score": 1.0, "feedback": feedback}
