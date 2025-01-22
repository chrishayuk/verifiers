# helpers/rhyme_utils.py
import pronouncing

def get_rhyme_ending(line: str) -> str:
    """
    Get a rough 'rhyming tail' for a line by taking the last word's
    phonetic tail (last stressed vowel + subsequent sounds).
    Fallback is the last 2 letters if no pronouncing data is found.
    """
    words = line.strip().split()
    if not words:
        return ""
    
    last_word = ''.join([c for c in words[-1] if c.isalpha()]).lower()
    phones = pronouncing.phones_for_word(last_word)
    
    if not phones:
        # Fallback: just return the last word’s last 2 letters
        return last_word[-2:]
    
    phone = phones[0]
    syllables = phone.strip().split()
    
    # Find the last stressed vowel index (digit indicates vowel w/ stress info)
    stressed_vowel_index = -1
    for i, syl in enumerate(syllables):
        if any(ch.isdigit() for ch in syl):
            stressed_vowel_index = i
    
    # Fallback if none found
    if stressed_vowel_index == -1:
        stressed_vowel_index = max(0, len(syllables) - 2)
    
    # Take everything from the last stressed vowel onward
    rhyming_tail = syllables[stressed_vowel_index:]
    return '-'.join(rhyming_tail)

def lines_rhyme(line1: str, line2: str) -> bool:
    """
    Check if two lines rhyme by comparing their 'rhyming tail'.
    """
    end1 = get_rhyme_ending(line1)
    end2 = get_rhyme_ending(line2)
    return (end1 == end2) and (end1 != "")
