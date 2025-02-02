# reasoning/reasoning_format_verifier.py
import re
from verifiers.base_verifier import BaseVerifier

class ReasoningFormatVerifier(BaseVerifier):
    def __init__(self):
        super().__init__(
            name="reasoning_format_tag_verifier",
            description="Checks if the text follows the required reasoning format with <think> and <answer> tags.",
            parameters={}
        )

    def verify(self, text: str, **kwargs) -> float:
        result = self.verify_with_feedback(text, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, **kwargs) -> dict:
        """
        Returns a dict with:
          {
            "score": float in [0.0, 1.0],
            "feedback": list of strings
          }

        This verifier ensures that the text adheres to a strict format by checking:
          - The text starts with <think> and ends with </answer>.
          - It contains a properly closed <think> tag followed by an <answer> tag.
          - The reasoning content is non-empty.
          - The answer content is non-empty.
        """
        feedback = []
        pattern = r"^\s*<think>(.*?)</think>\s*<answer>(.*?)</answer>\s*$"
        match = re.match(pattern, text, re.DOTALL)  # Case-sensitive match

        if not match:
            feedback.append(
                "Text does not conform to the required format. Ensure it follows: "
                "<think>reasoning...</think><answer>final answer...</answer>."
            )
            return {"score": 0.0, "feedback": feedback}

        think_content, answer_content = match.groups()

        if not think_content.strip():
            feedback.append("The <think> section is empty. It must contain reasoning steps.")
            return {"score": 0.0, "feedback": feedback}

        if not answer_content.strip():
            feedback.append("The <answer> section is empty. It must contain a final answer.")
            return {"score": 0.0, "feedback": feedback}

        feedback.append("✅ Text correctly includes both <think> and <answer> tags with valid content.")
        return {"score": 1.0, "feedback": feedback}
