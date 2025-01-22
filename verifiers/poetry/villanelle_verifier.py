# villanelle_verifier.py
from verifiers.base_verifier import BaseVerifier
from verifiers.poetry.helpers.rhyme_utils import lines_rhyme

class VillanelleVerifier(BaseVerifier):
    def __init__(self):
        """
        A naive villanelle checker with partial-credit approach:

         1) line_count_fraction = min(num_lines,19) / 19
         2) repetition_fraction: among the 6 required refrain lines, how many exist & match?
         3) rhyme_fraction: among the A/B lines, how many exist & match?

        Weighted sum:
          final_score = line_count_weight * line_count_fraction
                      + repetition_weight * repetition_fraction
                      + rhyme_weight * rhyme_fraction
        """
        super().__init__(
            name="villanelle_verifier",
            description=("Checks if a poem follows a basic 19-line villanelle structure, with partial credit: "
                         "line count, refrain repetition, naive A/B rhyme scheme."),
            parameters={
                "repetition_weight": {
                    "type": "float",
                    "default": 0.4,
                    "description": "Weight for scoring the line-repetition requirement."
                },
                "rhyme_weight": {
                    "type": "float",
                    "default": 0.4,
                    "description": "Weight for scoring the rhyme scheme requirement."
                },
                "line_count_weight": {
                    "type": "float",
                    "default": 0.2,
                    "description": "Weight for scoring the (partial) line count requirement."
                }
            }
        )
    
    def verify(self, text: str,
               repetition_weight: float = 0.4,
               rhyme_weight: float = 0.4,
               line_count_weight: float = 0.2,
               **kwargs) -> float:
        """
        Returns only the final float score in [0,1].
        """
        result = self.verify_with_feedback(
            text,
            repetition_weight=repetition_weight,
            rhyme_weight=rhyme_weight,
            line_count_weight=line_count_weight,
            **kwargs
        )
        return result["score"]

    def verify_with_feedback(self, text: str,
                             repetition_weight: float = 0.4,
                             rhyme_weight: float = 0.4,
                             line_count_weight: float = 0.2,
                             **kwargs) -> dict:
        """
        Returns a dict: {
          "score": float in [0,1],
          "feedback": list of strings describing partial results.
        }

        PARTIAL CREDIT:
          - line_count_fraction = min(num_lines,19)/19
          - repetition_fraction = (correct_repetitions)/(6)
          - rhyme_fraction = (correct A + correct B) / (total A + total B)

        final_score = line_count_weight*line_count_fraction
                    + repetition_weight*repetition_fraction
                    + rhyme_weight*rhyme_fraction
        (capped at 1.0 if the sum goes above 1? Or let it exceed 1 if weights sum >1. 
        We'll keep it unbounded by default, or you can clamp if desired.)
        """
        lines = [l for l in text.strip().split('\n') if l.strip()]
        feedback = []
        num_lines = len(lines)

        # 1) Partial line_count_fraction
        line_count_fraction = min(num_lines, 19) / 19.0
        feedback.append(
            f"Line count fraction: {line_count_fraction:.2f} (found {num_lines} lines)."
        )

        # 2) Repetition fraction
        #    (1,6), (1,12), (1,18), (3,9), (3,15), (3,19)
        required_repetitions = [
            (1, 6), (1, 12), (1, 18),
            (3, 9), (3, 15), (3, 19),
        ]
        correct_repetitions = 0
        valid_checks = 0  # how many repetition checks we can actually perform

        for (src, dest) in required_repetitions:
            if src <= num_lines and dest <= num_lines:
                valid_checks += 1
                line_src = lines[src - 1].strip().lower()
                line_dest = lines[dest - 1].strip().lower()
                if line_src == line_dest:
                    correct_repetitions += 1

        # If the poem doesn't have lines 6, 12, 18, etc., those checks can't pass => remain 0.
        # fraction = correct / 6 if we do a strict approach 
        # or fraction = correct / valid_checks if we only hold the poem responsible for lines that do exist. 
        # We'll do the strict approach: each missing line is an automatic fail.
        repetition_fraction = correct_repetitions / len(required_repetitions)
        feedback.append(
            f"Repetition fraction: {repetition_fraction:.2f} "
            f"({correct_repetitions} matched out of 6 total checks)."
        )

        # 3) Rhyme fraction
        #    A lines => 1,3,4,6,7,9,10,12,13,15,16,18,19
        #    B lines => 2,5,8,11,14,17
        a_indices = [1,3,4,6,7,9,10,12,13,15,16,18,19]
        b_indices = [2,5,8,11,14,17]
        
        a_correct = 0
        b_correct = 0
        for idx in a_indices:
            # If line doesn't exist, can't pass
            if idx <= num_lines:
                if lines_rhyme(lines[0], lines[idx - 1]):
                    a_correct += 1
        
        for idx in b_indices:
            if idx <= num_lines:
                if lines_rhyme(lines[1], lines[idx - 1]):
                    b_correct += 1
        
        total_a = len(a_indices)
        total_b = len(b_indices)
        # fraction = (a_correct + b_correct) / (total_a + total_b) 
        # missing lines => no partial
        rhyme_fraction = (a_correct + b_correct) / (total_a + total_b)
        feedback.append(
            f"Rhyme fraction: {rhyme_fraction:.2f} "
            f"(A matches={a_correct}/{total_a}, B matches={b_correct}/{total_b})."
        )

        # Weighted sum
        final_score = (
            line_count_weight * line_count_fraction
            + repetition_weight * repetition_fraction
            + rhyme_weight * rhyme_fraction
        )

        return {
            "score": final_score,
            "feedback": feedback
        }
