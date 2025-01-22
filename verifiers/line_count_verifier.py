# line_count_verifier.py
from base_verifier import BaseVerifier

class LineCountVerifier(BaseVerifier):
    def __init__(self):
        # Here we set name, description, and parameters
        super().__init__(
            name="line_count_verifier",
            description="Checks if a poem has the desired number of lines.",
            parameters={
                "desired": {
                    "type": "integer",
                    "default": 5,
                    "description": "Desired number of lines in the poem."
                }
            }
        )

    def verify(self, text: str, desired: int = 5, **kwargs) -> float:
        """
        Return 1.0 if the poem has exactly 'desired' lines,
        0.5 if it's off by 1, else 0.0.
        """
        lines = [l for l in text.strip().split('\n') if l.strip()]
        num = len(lines)
        if num == desired:
            return 1.0
        elif abs(num - desired) == 1:
            return 0.5
        else:
            return 0.0
