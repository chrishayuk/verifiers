# poetry/tanka_verifier.py
from verifiers.base_verifier import BaseVerifier
from verifiers.poetry.helpers.syllable_utils import count_syllables

class TankaVerifier(BaseVerifier):
    def __init__(self):
        super().__init__(
            name="tanka_verifier",
            description="Checks if text is a tanka with 5 lines ~5-7-5-7-7 syllables.",
            parameters={
                "tolerance": {
                    "type": "integer",
                    "default": 1,
                    "description": "Allowed +/- deviation from the line's expected syllable count."
                }
            }
        )

    def verify(self, text: str, tolerance: int = 1, **kwargs) -> float:
        """
        Returns a partial-credit score in [0,1].
        If there aren't exactly 5 lines, we return 0.0 immediately (like a strict approach).
        Otherwise, each line that meets its target (5 or 7 ± tolerance) yields 1 point.
        final_score = correct_lines / 5
        """
        result = self.verify_with_feedback(text, tolerance=tolerance, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, tolerance: int = 1, **kwargs) -> dict:
        """
        Returns a dict with:
          - "score": float in [0,1]
          - "feedback": list of messages describing each line's pass/fail

        Tanka: 5 lines => 5,7,5,7,7 each (± tolerance).
        """
        lines = [ln for ln in text.strip().split('\n') if ln.strip()]
        feedback = []
        
        # Must have exactly 5 lines for a standard tanka
        if len(lines) != 5:
            feedback.append(f"You have {len(lines)} line(s), but a standard tanka needs exactly 5.")
            return {
                "score": 0.0,
                "feedback": feedback
            }

        desired_syllables = [5, 7, 5, 7, 7]
        correct_lines = 0
        line_feedback = []

        for i, line in enumerate(lines):
            syl_count = count_syllables(line)
            target = desired_syllables[i]
            low = target - tolerance
            high = target + tolerance

            if low <= syl_count <= high:
                correct_lines += 1
                line_feedback.append(
                    f"Line {i+1}: Good ({syl_count} syllables, expected ~{target})."
                )
            else:
                line_feedback.append(
                    f"Line {i+1}: {syl_count} syllables (expected ~{target})."
                )

        # partial-credit score
        final_score = correct_lines / 5.0

        feedback.extend(line_feedback)
        return {
            "score": final_score,
            "feedback": feedback
        }
