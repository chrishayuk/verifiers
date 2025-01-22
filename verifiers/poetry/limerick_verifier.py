# poetry/limerick_verifier.py
from verifiers.base_verifier import BaseVerifier
from verifiers.poetry.helpers.syllable_utils import count_syllables
from verifiers.poetry.helpers.rhyme_utils import lines_rhyme

class LimerickVerifier(BaseVerifier):
    def __init__(self):
        super().__init__(
            name="limerick_verifier",
            description="Checks if a text meets a rough limerick structure (AABBA rhyme + syllable ranges).",
            parameters={
                "line_count_required": {
                    "type": "integer",
                    "default": 5,
                    "description": "Number of non-empty lines required."
                },
                "long_line_range": {
                    "type": "tuple/list",
                    "default": [7, 11],
                    "description": "Min/Max syllables allowed in lines 1,2,5."
                },
                "short_line_range": {
                    "type": "tuple/list",
                    "default": [4, 8],
                    "description": "Min/Max syllables allowed in lines 3,4."
                }
            }
        )

    def verify(self, text: str,
               line_count_required: int = 5,
               long_line_range: list = None,
               short_line_range: list = None,
               **kwargs) -> float:
        """
        Return a partial-credit score in [0, 1].
        Each of the following 4 checks is worth 1 point:
          1) line_count_required
          2) A-rhyme (lines 1,2,5)
          3) B-rhyme (lines 3,4)
          4) syllable counts (lines 1,2,5 + lines 3,4)

        So a poem passing all checks yields 1.0, partial compliance might be 0.75, 0.5, etc.
        """
        result = self.verify_with_feedback(
            text,
            line_count_required=line_count_required,
            long_line_range=long_line_range,
            short_line_range=short_line_range,
            **kwargs
        )
        return result["score"]

    def verify_with_feedback(self, text: str,
                             line_count_required: int = 5,
                             long_line_range: list = None,
                             short_line_range: list = None,
                             **kwargs) -> dict:
        """
        Returns a dict with:
          {
            "score": float in [0,1],
            "feedback": list of strings describing each check's pass/fail
          }

        The partial-credit approach is as follows:
          - checks_passed = 0
          - total_checks = 4 (line count, A-rhyme, B-rhyme, syllable checks)
          - score = checks_passed / total_checks
        """
        if long_line_range is None:
            long_line_range = [7, 11]
        if short_line_range is None:
            short_line_range = [4, 8]

        feedback = []
        checks_passed = 0
        total_checks = 4

        lines = [ln for ln in text.strip().split('\n') if ln.strip()]
        num_lines = len(lines)

        # 1) Line Count
        if num_lines == line_count_required:
            checks_passed += 1
            feedback.append(f"Line count check passed ({num_lines} lines).")
        else:
            feedback.append(f"Line count check failed. Expected {line_count_required}, got {num_lines}.")

        # 2) A-rhyme => lines[0], lines[1], lines[4]
        a_rhyme_ok = False
        if num_lines >= 5:
            a_rhyme_ok = (lines_rhyme(lines[0], lines[1]) and lines_rhyme(lines[0], lines[4]))
        if a_rhyme_ok:
            checks_passed += 1
            feedback.append("A-rhyme check passed (lines 1,2,5).")
        else:
            feedback.append("A-rhyme check failed (lines 1,2,5).")

        # 3) B-rhyme => lines[2], lines[3]
        b_rhyme_ok = False
        if num_lines >= 4:
            b_rhyme_ok = lines_rhyme(lines[2], lines[3])
        if b_rhyme_ok:
            checks_passed += 1
            feedback.append("B-rhyme check passed (lines 3,4).")
        else:
            feedback.append("B-rhyme check failed (lines 3,4).")

        # 4) Syllable Checks (only if we have >=5 lines)
        syllables_ok = False
        if num_lines >= 5:
            sylls = [count_syllables(ln) for ln in lines]
            l1, l2, l3, l4, l5 = sylls[:5]

            min_long, max_long = long_line_range
            min_short, max_short = short_line_range

            # lines 1,2,5 => "long" lines
            lines_1_2_5_ok = (
                min_long <= l1 <= max_long and
                min_long <= l2 <= max_long and
                min_long <= l5 <= max_long
            )
            # lines 3,4 => "short" lines
            lines_3_4_ok = (
                min_short <= l3 <= max_short and
                min_short <= l4 <= max_short
            )
            if lines_1_2_5_ok and lines_3_4_ok:
                syllables_ok = True
                checks_passed += 1
                feedback.append("Syllable count check passed.")
            else:
                if not lines_1_2_5_ok:
                    feedback.append(
                        f"Lines 1,2,5 syllable check failed: "
                        f"(Line1={l1}, Line2={l2}, Line5={l5}) "
                        f"Expected {min_long}-{max_long}."
                    )
                if not lines_3_4_ok:
                    feedback.append(
                        f"Lines 3,4 syllable check failed: "
                        f"(Line3={l3}, Line4={l4}) "
                        f"Expected {min_short}-{max_short}."
                    )
        else:
            feedback.append("Not enough lines to check syllable counts properly.")

        # Final partial-credit score
        score = checks_passed / total_checks

        return {
            "score": score,
            "feedback": feedback
        }
