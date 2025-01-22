# syllable_verifier.py
from base_verifier import BaseVerifier

class SyllableVerifier(BaseVerifier):
    def __init__(self):
        super().__init__(
            name="syllable_verifier",
            description="Checks approximate syllable counts against a desired value.",
            parameters={
                "desired_syllables": {
                    "type": "integer",
                    "default": 8,
                    "description": "Approximate number of syllables per line."
                }
            }
        )
    
    def verify(self, text: str, desired_syllables: int = 8, **kwargs) -> float:
        lines = [l for l in text.strip().split('\n') if l.strip()]
        if not lines:
            return 0.0
        
        total_score = 0.0
        for line in lines:
            # naive vowel count
            count = sum(ch.lower() in 'aeiou' for ch in line)
            diff = abs(count - desired_syllables)
            
            if diff <= 2:
                total_score += 1.0
            elif diff <= 4:
                total_score += 0.5
            # else 0.0
        return total_score / len(lines)
