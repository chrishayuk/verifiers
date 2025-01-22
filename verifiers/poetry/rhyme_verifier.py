# rhyme_verifier.py
from verifiers.base_verifier import BaseVerifier
from verifiers.poetry.helpers.rhyme_utils import get_rhyme_ending

class RhymeVerifier(BaseVerifier):
    def __init__(self):
        super().__init__(
            name="rhyme_verifier",
            description="Checks if line 1 and line 2 rhyme via phoneme overlap, with a last-letter fallback.",
            parameters={
                "partial_threshold": {
                    "type": "float",
                    "default": 0.5,
                    "description": (
                        "Minimum fraction of overlapping phonemes "
                        "required at the tail for partial rhyme."
                    )
                },
                "fallback_credit": {
                    "type": "float",
                    "default": 0.5,
                    "description": (
                        "Score assigned if phonetic overlap fails but the last letters match."
                    )
                }
            }
        )

    def verify(self, text: str, partial_threshold: float = 0.5, fallback_credit: float = 0.5, **kwargs) -> float:
        """
        Calls verify_with_feedback, returning only the numeric score.
        """
        result = self.verify_with_feedback(
            text,
            partial_threshold=partial_threshold,
            fallback_credit=fallback_credit,
            **kwargs
        )
        return result["score"]

    def verify_with_feedback(self, text: str,
                             partial_threshold: float = 0.5,
                             fallback_credit: float = 0.5,
                             **kwargs) -> dict:
        """
        Returns:
        {
          "score": float in [0,1],
          "feedback": list of strings describing how well the lines rhyme.
        }

        Example feedback approach:
         - If fewer than 2 lines => 0.0 score, 1 feedback message.
         - If perfect => 1.0, say "Perfect rhyme."
         - If partial => e.g. overlap ratio or fallback credit
         - else => 0.0
        """
        lines = [l for l in text.strip().split('\n') if l.strip()]
        feedback = []
        
        if len(lines) < 2:
            feedback.append("Need at least 2 lines to check rhyme.")
            return {"score": 0.0, "feedback": feedback}

        end1 = get_rhyme_ending(lines[0])
        end2 = get_rhyme_ending(lines[1])
        if not end1 or not end2:
            feedback.append("Could not extract rhyme endings (maybe empty last words?).")
            return {"score": 0.0, "feedback": feedback}

        # Check for perfect match
        if end1 == end2:
            feedback.append(f"Perfect rhyme: both lines share '{end1}'.")
            return {"score": 1.0, "feedback": feedback}

        # Compute overlap
        tail1 = end1.split('-')
        tail2 = end2.split('-')
        overlap_count = 0
        i1, i2 = len(tail1) - 1, len(tail2) - 1
        
        while i1 >= 0 and i2 >= 0 and tail1[i1] == tail2[i2]:
            overlap_count += 1
            i1 -= 1
            i2 -= 1
        
        max_possible = min(len(tail1), len(tail2))
        if max_possible == 0:
            # fallback last letter
            score, fallback_msg = self._check_last_letter_fallback(lines, fallback_credit)
            feedback.append(fallback_msg)
            return {"score": score, "feedback": feedback}

        overlap_ratio = overlap_count / max_possible
        feedback.append(f"Overlap ratio: {overlap_ratio:.2f} (threshold={partial_threshold}).")

        if overlap_ratio >= partial_threshold:
            feedback.append("Overlap ratio meets threshold => partial rhyme credit.")
            return {"score": overlap_ratio, "feedback": feedback}
        
        # fallback letter
        score, fallback_msg = self._check_last_letter_fallback(lines, fallback_credit)
        feedback.append(fallback_msg)
        return {"score": score, "feedback": feedback}

    def _check_last_letter_fallback(self, lines, fallback_credit: float) -> tuple:
        """
        If the last letters match, return (fallback_credit, message), else (0.0, msg).
        """
        word1 = lines[0].split()[-1].lower() if lines[0].split() else ""
        word2 = lines[1].split()[-1].lower() if lines[1].split() else ""

        if word1 and word2 and word1[-1] == word2[-1]:
            msg = f"Last letters match ('{word1[-1]}'), awarding fallback credit={fallback_credit}."
            return (fallback_credit, msg)
        else:
            return (0.0, "No letter match; 0.0 score.")
