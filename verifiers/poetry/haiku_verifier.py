# poetry/haiku_verifier.py
from verifiers.base_verifier import BaseVerifier
from verifiers.poetry.helpers.syllable_utils import count_syllables, breakdown_syllables

class HaikuVerifier(BaseVerifier):
    def __init__(self):
        super().__init__(
            name="haiku_verifier",
            description="Checks if text is a haiku with 3 lines and ~5-7-5 syllables.",
            parameters={
                "tolerance": {
                    "type": "integer",
                    "default": 1,
                    "description": "Allowed syllable deviation from 5 or 7."
                }
            }
        )

    def verify(self, text: str, tolerance: int = 1, **kwargs) -> float:
        """
        Returns a float in [0.0, 1.0] giving partial credit for each line
        that meets its syllable requirement, but ONLY if line_count == 3.
        Otherwise, immediate 0.0.
        """
        result = self.verify_with_feedback(text, tolerance=tolerance, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, tolerance: int = 1, **kwargs) -> dict:
        """
        Returns a dict with:
          {
            "score": float in [0.0, 1.0],
            "feedback": list of strings
          }

        We have exactly 3 checks total (one per line):
          - If the text does NOT have 3 lines, we immediately fail (score=0.0),
            with 1 feedback message about line count.

          - If it DOES have exactly 3 lines, we do a syllable check for each line:
            line1 ~5, line2 ~7, line3 ~5, each correct line adds 1/3 to final score.

        The tests expect exactly 3 feedback lines if line_count == 3,
        or 1 feedback line if line_count != 3.
        """
        lines = [l for l in text.strip().split('\n') if l.strip()]
        feedback = []
        
        # Must be exactly 3 lines for a standard haiku
        if len(lines) != 3:
            feedback.append(
                f"You have {len(lines)} line(s), but a standard haiku needs exactly 3."
            )
            return {
                "score": 0.0,
                "feedback": feedback
            }

        # If we do have 3 lines, partial credit across them
        desired_syllables = [5, 7, 5]
        correct_lines = 0
        line_feedback = []

        for i, line in enumerate(lines):
            # Break out the words
            words = line.strip().split()

            # Total syllables in the entire line
            syl_count = count_syllables(line)

            # Number of syllables in each individual word
            word_syll_counts = [count_syllables(w) for w in words]

            # (New) Actual syllable breakdown for each word (requires a custom function)
            # e.g. breakdown_syllables("beautiful") -> ["beau", "ti", "ful"]
            word_syllable_breakdowns = [
                f"{w} ({'-'.join(breakdown_syllables(w))})" for w in words
            ]

            # Determine acceptable syllable range
            low = desired_syllables[i] - tolerance
            high = desired_syllables[i] + tolerance

            # Build feedback
            if low <= syl_count <= high:
                correct_lines += 1
                line_feedback.append(
                    f"Line {i+1} (\"{line}\"): Good ({syl_count} syllables).\n"
                    f"  Words: {', '.join(words)}\n"
                    f"  Syllables per word: {word_syll_counts}\n"
                    f"  Syllable breakdown: {', '.join(word_syllable_breakdowns)}"
                )
            else:
                line_feedback.append(
                    f"Line {i+1} (\"{line}\"): {syl_count} syllables (expected ~{desired_syllables[i]}).\n"
                    f"  Words: {', '.join(words)}\n"
                    f"  Syllables per word: {word_syll_counts}\n"
                    f"  Syllable breakdown: {', '.join(word_syllable_breakdowns)}"
                )
        
        final_score = correct_lines / 3.0
        feedback.extend(line_feedback)

        return {
            "score": final_score,
            "feedback": feedback
        }
