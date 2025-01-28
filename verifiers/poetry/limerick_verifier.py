# poetry/limerick_verifier.py
import re
import pronouncing

from verifiers.base_verifier import BaseVerifier
from verifiers.poetry.helpers.syllable_utils import (
    count_syllables,
    breakdown_syllables
)
from verifiers.poetry.helpers.rhyme_utils import lines_rhyme

def _get_last_word_and_phones(line: str) -> tuple[str, list[str]]:
    """
    Returns (last_word, phones_list) for a given line.
    - last_word: the last alphabetic word in lowercase (no punctuation).
    - phones_list: list of possible ARPAbet pronunciations from pronouncing.
    """
    words = line.strip().split()
    if not words:
        return ("", [])

    # Take the last token, strip punctuation, lowercase it
    raw_last = words[-1].lower()
    clean_last = re.sub(r'[^a-z]', '', raw_last)

    # Get ARPAbet pronunciations from pronouncing
    if clean_last:
        phones = pronouncing.phones_for_word(clean_last)
    else:
        phones = []

    return (clean_last, phones)


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
            "feedback": list of strings describing each check's pass/fail,
                        plus additional per-line details and rhyme breakdowns.
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

        # Split text into non-empty lines
        lines = [ln for ln in text.strip().split('\n') if ln.strip()]
        num_lines = len(lines)

        # 1) LINE COUNT CHECK
        if num_lines == line_count_required:
            checks_passed += 1
            feedback.append(f"Line count check passed ({num_lines} lines).")
        else:
            feedback.append(
                f"Line count check failed. "
                f"Expected {line_count_required}, got {num_lines}."
            )

        # 2) A-RHYME CHECK => lines[0], lines[1], lines[4]
        # (Only possible if we have >=5 lines)
        a_rhyme_ok = False
        if num_lines >= 5:
            a_rhyme_ok = (
                lines_rhyme(lines[0], lines[1]) and
                lines_rhyme(lines[0], lines[4])
            )
        if a_rhyme_ok:
            checks_passed += 1
            feedback.append("A-rhyme check passed (lines 1,2,5).")
        else:
            feedback.append("A-rhyme check failed (lines 1,2,5).")

        # 3) B-RHYME CHECK => lines[2], lines[3]
        # (Only possible if we have >=4 lines)
        b_rhyme_ok = False
        if num_lines >= 4:
            b_rhyme_ok = lines_rhyme(lines[2], lines[3])
        if b_rhyme_ok:
            checks_passed += 1
            feedback.append("B-rhyme check passed (lines 3,4).")
        else:
            feedback.append("B-rhyme check failed (lines 3,4).")

        # 4) SYLLABLE CHECKS (only if we have >=5 lines)
        if num_lines >= 5:
            # Count syllables for the first 5 lines
            sylls = [count_syllables(ln) for ln in lines[:5]]
            l1, l2, l3, l4, l5 = sylls

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
                checks_passed += 1
                feedback.append("Syllable count check passed.")
            else:
                if not lines_1_2_5_ok:
                    feedback.append(
                        f"Lines 1,2,5 syllable check failed. "
                        f"Line 1 = {l1}, Line 2 = {l2}, Line 5 = {l5}; "
                        f"Expected {min_long}–{max_long} for each."
                    )
                if not lines_3_4_ok:
                    feedback.append(
                        f"Lines 3,4 syllable check failed. "
                        f"Line 3 = {l3}, Line 4 = {l4}; "
                        f"Expected {min_short}–{max_short} for each."
                    )
        else:
            feedback.append("Not enough lines to check syllable counts properly.")

        # -- ADDITIONAL PER-LINE SYLLABLE DETAILS --
        # This mirrors the haiku style of feedback, giving a breakdown for each line:
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

        # -- ADDITIONAL RHYME BREAKDOWN --
        # Show the last word and phonetic representations for lines that matter.
        # A-rhyme lines: 1, 2, 5 => indices 0, 1, 4
        if num_lines >= 5:
            lw0, phones0 = _get_last_word_and_phones(lines[0])
            lw1, phones1 = _get_last_word_and_phones(lines[1])
            lw4, phones4 = _get_last_word_and_phones(lines[4])
            feedback.append(
                "A-rhyme detail (lines 1,2,5):\n"
                f"  - Line 1 last word: '{lw0}' | Phones: {phones0}\n"
                f"  - Line 2 last word: '{lw1}' | Phones: {phones1}\n"
                f"  - Line 5 last word: '{lw4}' | Phones: {phones4}\n"
                f"  => PASS? {a_rhyme_ok}"
            )

        # B-rhyme lines: 3, 4 => indices 2, 3
        if num_lines >= 4:
            lw2, phones2 = _get_last_word_and_phones(lines[2])
            lw3, phones3 = _get_last_word_and_phones(lines[3])
            feedback.append(
                "B-rhyme detail (lines 3,4):\n"
                f"  - Line 3 last word: '{lw2}' | Phones: {phones2}\n"
                f"  - Line 4 last word: '{lw3}' | Phones: {phones3}\n"
                f"  => PASS? {b_rhyme_ok}"
            )

        # Final partial-credit score
        score = checks_passed / total_checks

        return {
            "score": score,
            "feedback": feedback
        }
