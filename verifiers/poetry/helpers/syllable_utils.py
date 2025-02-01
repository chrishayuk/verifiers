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
            # Each digit in the ARPAbet phone string indicates a vowel nucleus,
            # so counting digits approximates counting syllables.
            total_syllables += sum(ch.isdigit() for ch in phones[0])
        else:
            # Fallback: naive vowel-group counting
            total_syllables += _count_syllables_naive(clean_word)

    return total_syllables

def breakdown_syllables(word: str) -> list[str]:
    """
    Returns a naive, best-effort breakdown of a single word into
    syllable-like chunks by grouping consonants and adjacent vowels.
    Example:
        "beautiful" -> ["beau", "ti", "ful"]
    This approach will not always match correct English syllabification.
    If an accurate breakdown is needed, consider a more advanced method
    or parsing the ARPAbet phones in 'pronouncing'.
    """
    # Strip punctuation and lowercase
    w = ''.join(c for c in word if c.isalpha()).lower()
    if not w:
        return []

    # Attempt a pronunciation-based approach first, if available
    phones = pronouncing.phones_for_word(w)
    if phones:
        # Example strategy (very simplified):
        # 1) Parse the ARPAbet phones
        # 2) Attempt to align phone clusters with letters
        # 3) Create textual chunks
        # 
        # However, ARPAbet-to-text alignment can get complicated.
        # Here, we’ll just do a naive fallback to keep things simple.
        return _breakdown_syllables_naive(w)

    # If not in CMU dictionary, do the naive approach
    return _breakdown_syllables_naive(w)

def _count_syllables_naive(word: str) -> int:
    """
    Naive syllable count by counting vowel groups.
    E.g., 'beautiful' -> 3 vowel groups: 'eau', 'i', 'u'
    """
    vowels = "aeiou"
    count = 0
    in_vowel_group = False

    for char in word:
        if char in vowels:
            # When we first encounter a vowel group, increment count
            if not in_vowel_group:
                count += 1
                in_vowel_group = True
        else:
            in_vowel_group = False

    return count

def _breakdown_syllables_naive(word: str) -> list[str]:
    """
    A naive way to split a word into syllable-like chunks by grouping everything
    from the start index up through the current vowel group.
    Example:
      'beautiful' -> ['beau', 'ti', 'ful']
    """
    vowels = "aeiou"
    chunks = []
    start_idx = 0
    i = 0
    length = len(word)

    # Scan through the word. Whenever we hit a vowel group,
    # we create a chunk from the last start_idx up through
    # the end of that vowel group.
    while i < length:
        if word[i] in vowels:
            # Found the start of a vowel group.
            j = i
            # Move j until we leave the vowel group
            while j < length and word[j] in vowels:
                j += 1
            # This chunk is everything from start_idx to j
            chunk = word[start_idx:j]
            chunks.append(chunk)
            start_idx = j
            i = j
        else:
            i += 1

    # If there's leftover consonants after the last vowel group, append them.
    # E.g., "testing" -> last chunk might be "ng" if we ended on a vowel group.
    if start_idx < length:
        if chunks:
            # Append leftover to the last chunk so that we
            # group trailing consonants with the final vowel chunk
            chunks[-1] += word[start_idx:]
        else:
            # If no chunks at all (no vowels?), the entire word is one chunk
            chunks.append(word[start_idx:])

    return chunks
