# verifiers/poetry/rhyme_verifier.py
import re
import pronouncing

from verifiers.base_verifier import BaseVerifier
from verifiers.poetry.helpers.syllable_utils import (
    count_syllables,
    breakdown_syllables
)
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

    def verify(self, text: str,
               partial_threshold: float = 0.5,
               fallback_credit: float = 0.5,
               **kwargs) -> float:
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
          "feedback": list of strings describing how well the lines rhyme,
                      plus per-line syllable details.
        }

        Steps:
         1. Split text into non-empty lines; need >=2 to compare rhyme.
         2. Provide line-by-line feedback (words, syllable counts, breakdowns).
         3. Check rhyme endings:
            - If perfect => 1.0
            - If partial overlap >= partial_threshold => overlap ratio
            - Else fallback to last-letter check => fallback_credit or 0.0
        """
        lines = [l for l in text.strip().split('\n') if l.strip()]
        feedback = []

        # ---- 1) Check that we have at least 2 lines ----
        if len(lines) < 2:
            feedback.append("Need at least 2 lines to check rhyme.")
            return {"score": 0.0, "feedback": feedback}

        # ---- 2) Per-line breakdown feedback ----
        # Provide the same style as Haiku/Limerick: total syllables, words, breakdowns.
        for i, line in enumerate(lines):
            words = line.strip().split()
            total_syl_count = count_syllables(line)
            word_syl_counts = [count_syllables(w) for w in words]
            word_syll_breakdowns = [
                f"{w} ({'-'.join(breakdown_syllables(w))})"
                for w in words
            ]
            feedback.append(
                f"Line {i+1} (\"{line}\"): {total_syl_count} syllables.\n"
                f"  Words: {', '.join(words)}\n"
                f"  Syllables per word: {word_syl_counts}\n"
                f"  Syllable breakdown: {', '.join(word_syll_breakdowns)}"
            )

        # We'll only analyze lines[0] and lines[1] for rhyme, as specified.
        line1 = lines[0]
        line2 = lines[1]

        # ---- 3) Extract rhyme endings ----
        end1 = get_rhyme_ending(line1)
        end2 = get_rhyme_ending(line2)
        if not end1 or not end2:
            feedback.append("Could not extract rhyme endings (maybe empty last words?).")
            return {"score": 0.0, "feedback": feedback}
        
        feedback.append(f"Line 1 rhyme ending: {end1}")
        feedback.append(f"Line 2 rhyme ending: {end2}")

        # Perfect rhyme check
        if end1 == end2:
            feedback.append(f"Perfect rhyme: both lines share '{end1}'.")
            return {"score": 1.0, "feedback": feedback}

        # Compute phoneme overlap ratio
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
            score, fallback_msg = self._check_last_letter_fallback(line1, line2, fallback_credit)
            feedback.append(fallback_msg)
            return {"score": score, "feedback": feedback}

        overlap_ratio = overlap_count / max_possible
        feedback.append(f"Overlap ratio: {overlap_ratio:.2f} (threshold={partial_threshold}).")

        # Compare overlap ratio to threshold
        if overlap_ratio >= partial_threshold:
            # partial rhyme => score = overlap_ratio (or some logic you prefer)
            feedback.append("Overlap ratio meets threshold => partial rhyme credit.")
            return {"score": overlap_ratio, "feedback": feedback}
        
        # fallback letter
        score, fallback_msg = self._check_last_letter_fallback(line1, line2, fallback_credit)
        feedback.append(fallback_msg)
        return {"score": score, "feedback": feedback}

    def _check_last_letter_fallback(self, line1: str, line2: str, fallback_credit: float) -> tuple:
        """
        If the last letters match, return (fallback_credit, message), else (0.0, msg).
        """
        word1 = line1.split()[-1].lower() if line1.split() else ""
        word2 = line2.split()[-1].lower() if line2.split() else ""

        if word1 and word2 and word1[-1] == word2[-1]:
            msg = (
                f"Last letters match ('{word1[-1]}'), awarding fallback credit={fallback_credit}."
            )
            return (fallback_credit, msg)
        else:
            return (0.0, "No letter match; 0.0 score.")
