# helpers/syllable_utils.py
import pronouncing

def count_syllables(line: str) -> int:
    """
    Counts syllables in a line by summing the syllables of each word.
    Uses pronouncing.phones_for_word() for an accurate count if possible.
    Falls back to naive vowel-group counting if not found in CMU dict.
    """
    words = line.strip().split()
    total_syllables = 0
    
    for word in words:
        # Normalize the word to remove punctuation, etc.
        clean_word = ''.join([c for c in word if c.isalpha()]).lower()
        phones = pronouncing.phones_for_word(clean_word)
        
        if phones:
            # Take the first pronunciation variant
            total_syllables += sum(ch.isdigit() for ch in phones[0])
        else:
            # Fallback: naive vowel-group counting
            vowel_groups = 0
            vowels = "aeiou"
            in_vowel_group = False
            for char in clean_word:
                if char in vowels and not in_vowel_group:
                    vowel_groups += 1
                    in_vowel_group = True
                elif char not in vowels:
                    in_vowel_group = False
            total_syllables += vowel_groups
    
    return total_syllables
